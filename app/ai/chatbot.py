from sqlalchemy import text
from sqlalchemy.orm import Session

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.core.config import settings


ALLOWED_TABLES = {
    "api_checks",
    "health_assessments",
    "incidents",
    "alerts",
}


def _database_context(db: Session) -> str:
    checks = db.execute(
        text(
            """
            SELECT
                service_name,
                endpoint,
                status_code,
                latency_ms,
                reachable,
                deterministic_status,
                error_message,
                checked_at
            FROM api_checks
            ORDER BY checked_at DESC
            LIMIT 50
            """
        )
    ).mappings().all()

    incidents = db.execute(
        text(
            """
            SELECT
                service_name,
                severity,
                status,
                summary,
                started_at,
                resolved_at
            FROM incidents
            ORDER BY started_at DESC
            LIMIT 30
            """
        )
    ).mappings().all()

    assessments = db.execute(
        text(
            """
            SELECT
                h.status,
                h.summary,
                h.probable_cause,
                h.impact,
                h.remedies,
                h.confidence,
                h.created_at,
                c.service_name
            FROM health_assessments h
            JOIN api_checks c ON c.id = h.api_check_id
            ORDER BY h.created_at DESC
            LIMIT 50
            """
        )
    ).mappings().all()

    return (
        f"RECENT CHECKS:\n{[dict(x) for x in checks]}\n\n"
        f"RECENT INCIDENTS:\n{[dict(x) for x in incidents]}\n\n"
        f"RECENT ASSESSMENTS:\n{[dict(x) for x in assessments]}"
    )


async def ask_sre_chatbot(db: Session, question: str) -> str:
    context = _database_context(db)

    if not settings.openai_api_key:
        return (
            "OPENAI_API_KEY is not configured. The operational data is being "
            "stored correctly, but AI chatbot responses require an LLM key."
        )

    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=0,
        api_key=settings.openai_api_key,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are an SRE operations assistant.

Answer only from the supplied database context.
Do not invent incidents, metrics, causes, timestamps, or remedies.
If the answer is not available, say that clearly.

Be concise, operational, and useful to an SRE engineer.
""",
            ),
            (
                "human",
                """
DATABASE CONTEXT:
{context}

QUESTION:
{question}
""",
            ),
        ]
    )

    response = await (prompt | llm).ainvoke(
        {
            "context": context,
            "question": question,
        }
    )

    return response.content
