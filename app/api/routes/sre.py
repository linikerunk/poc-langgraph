from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.ai.chatbot import ask_sre_chatbot
from app.database.models import APICheck, Incident
from app.database.session import get_db
from app.schemas.health import ChatRequest
from app.services.sre_service import run_all_checks

router = APIRouter(prefix="/api/sre", tags=["SRE"])


@router.post("/run-check")
async def run_check(db: Session = Depends(get_db)):
    return {"results": await run_all_checks(db)}


@router.get("/checks")
def list_checks(
    limit: int = 50,
    db: Session = Depends(get_db),
):
    rows = db.scalars(
        select(APICheck)
        .order_by(desc(APICheck.checked_at))
        .limit(min(limit, 200))
    ).all()

    return [
        {
            "id": row.id,
            "service_name": row.service_name,
            "endpoint": row.endpoint,
            "status_code": row.status_code,
            "latency_ms": row.latency_ms,
            "reachable": row.reachable,
            "status": row.deterministic_status,
            "error_message": row.error_message,
            "checked_at": row.checked_at,
        }
        for row in rows
    ]


# @router.get("/incidents")
# def list_incidents(
#     limit: int = 50,
#     db: Session = Depends(get_db),
# ):
#     rows = db.scalars(
#         select(Incident)
#         .order_by(desc(Incident.started_at))
#         .limit(min(limit, 200))
#     ).all()

#     return [
#         {
#             "id": row.id,
#             "service_name": row.service_name,
#             "severity": row.severity,
#             "status": row.status,
#             "summary": row.summary,
#             "started_at": row.started_at,
#             "resolved_at": row.resolved_at,
#             "alert_sent": row.alert_sent,
#         }
#         for row in rows
#     ]


@router.post("/chat")
async def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
):
    answer = await ask_sre_chatbot(db, payload.question)
    return {
        "question": payload.question,
        "answer": answer,
    }
