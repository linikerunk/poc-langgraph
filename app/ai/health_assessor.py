import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.schemas.health import HealthAssessment


def fallback_assessment(base_status: str, check: dict) -> HealthAssessment:
    if base_status == "HEALTHY":
        return HealthAssessment(
            status="HEALTHY",
            summary="The monitored endpoint is operating normally.",
            probable_cause="No active fault detected.",
            impact="No current customer impact is expected.",
            remedies=["Continue monitoring normal service indicators."],
            confidence=1.0,
        )

    if not check.get("reachable"):
        cause = "The endpoint could not be reached within the monitoring request."
    elif (check.get("status_code") or 0) >= 500:
        cause = "The service returned a server-side error."
    else:
        cause = "The service is responding with degraded performance."

    return HealthAssessment(
        status=base_status,
        summary=f"{check['service_name']} is {base_status.lower()}.",
        probable_cause=cause,
        impact="Users may experience failed requests or degraded response times.",
        remedies=[
            "Inspect application and infrastructure logs.",
            "Check downstream dependencies and database connectivity.",
            "Review recent deployments and configuration changes.",
            "Verify resource saturation and service instance health.",
        ],
        confidence=0.8,
    )


async def assess_health(
    base_status: str,
    current_check: dict,
    recent_checks: list[dict],
) -> HealthAssessment:
    if not settings.openai_api_key:
        return fallback_assessment(base_status, current_check)

    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=0,
        api_key=settings.openai_api_key,
    ).with_structured_output(HealthAssessment)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are an SRE incident analysis assistant for a banking technology POC.

The deterministic monitoring status is the source of truth.
You MUST NOT downgrade it.

Severity order:
HEALTHY < WARNING < CRITICAL.

Analyze the current check and recent history.
Return a concise operational assessment with probable cause,
customer/business impact, practical remediation actions, and confidence.

Do not invent facts not supported by the supplied telemetry.
""",
            ),
            (
                "human",
                """
Deterministic status:
{base_status}

Current check:
{current_check}

Recent checks:
{recent_checks}
""",
            ),
        ]
    )

    chain = prompt | llm

    assessment = await chain.ainvoke(
        {
            "base_status": base_status,
            "current_check": json.dumps(current_check, default=str),
            "recent_checks": json.dumps(recent_checks, default=str),
        }
    )

    severity_rank = {"HEALTHY": 0, "WARNING": 1, "CRITICAL": 2}
    if severity_rank[assessment.status] < severity_rank[base_status]:
        assessment.status = base_status

    return assessment
