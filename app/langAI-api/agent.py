import os
from typing import Any

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:  # pragma: no cover - fallback for environments without the package
    ChatOpenAI = None
    ChatPromptTemplate = None

SYSTEM_PROMPT = """You are an SRE monitoring assistant specialized in analyzing API logs and system events.

Your responsibilities:
1. Receive logs, traces, errors, metrics, or incident context and evaluate whether the system is healthy or unstable.
2. Identify signs of failures or divergences such as outages, elevated error rates, timeouts, latency spikes, service unavailability, authentication failures, database connection issues, or unexpected behavior.
3. Save important observations as structured incident context with severity, summary, evidence, and an SRE alert when needed.
4. Classify the incident as info, warning, or critical.
5. If the issue is critical or potentially severe, prepare an SRE email message with context, evidence, impact, and next actions.

Rules:
- Be objective and evidence-based.
- If the logs are insufficient, clearly say the status is uncertain.
- Prioritize operational impact and customer-facing risk.
- The output must be concise, actionable, and useful for operations.
"""


def _heuristic_analysis(logs: str, service_name: str) -> dict[str, Any]:
    normalized_logs = logs.lower()
    evidence: list[str] = []

    if any(token in normalized_logs for token in ["traceback", "exception", "internal server error", "500", "connection refused"]):
        evidence.append("Critical error pattern detected in the logs")
    if any(token in normalized_logs for token in ["timeout", "timed out", "latency", "slow"]):
        evidence.append("Latency or timeout symptoms were observed")
    if any(token in normalized_logs for token in ["401", "403", "unauthorized", "forbidden", "auth"]):
        evidence.append("Authentication or authorization failures were detected")
    if not evidence:
        evidence.append("No obvious failure pattern was found in the provided logs")

    if any(token in normalized_logs for token in ["critical", "fatal", "panic", "database connection", "service unavailable", "502", "503", "504"]):
        severity = "critical"
        status = "unstable"
        summary = f"{service_name} shows a critical failure pattern and may be unavailable."
    elif any(token in normalized_logs for token in ["error", "warning", "timeout", "latency", "401", "403"]):
        severity = "warning"
        status = "degraded"
        summary = f"{service_name} is showing signs of instability or degraded behavior."
    else:
        severity = "info"
        status = "healthy"
        summary = f"{service_name} appears healthy based on the provided logs."

    email_subject = f"[SRE Alert] {service_name} - {severity.upper()}"
    email_body = (
        f"Service: {service_name}\n"
        f"Severity: {severity}\n"
        f"Status: {status}\n\n"
        f"Summary: {summary}\n\n"
        f"Observed evidence:\n- " + "\n- ".join(evidence)
    )

    return {
        "status": status,
        "severity": severity,
        "summary": summary,
        "evidence": evidence,
        "sre_email": {
            "subject": email_subject,
            "body": email_body,
        },
    }


def analyze_logs(logs: str, service_name: str = "unknown") -> dict[str, Any]:
    if not logs or not logs.strip():
        return {
            "status": "unknown",
            "severity": "info",
            "summary": "No logs were provided for analysis.",
            "evidence": [],
            "sre_email": {
                "subject": "[SRE Alert] No logs provided",
                "body": "No logs were received to evaluate.",
            },
        }

    if os.getenv("OPENAI_API_KEY") and ChatOpenAI is not None and ChatPromptTemplate is not None:
        try:
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", SYSTEM_PROMPT),
                    (
                        "human",
                        "Service: {service_name}\n\nLogs:\n{logs}\n\nRespond with a JSON object containing: status, severity, summary, evidence, and sre_email with subject and body.",
                    ),
                ]
            )
            llm = ChatOpenAI(model="gpt-4o", temperature=0)
            chain = prompt | llm
            response = chain.invoke({"service_name": service_name, "logs": logs})
            content = response.content if hasattr(response, "content") else str(response)
            return {
                "status": "unknown",
                "severity": "info",
                "summary": content,
                "evidence": [],
                "sre_email": {
                    "subject": f"[SRE Alert] {service_name}",
                    "body": content,
                },
            }
        except Exception:
            pass

    return _heuristic_analysis(logs, service_name)
