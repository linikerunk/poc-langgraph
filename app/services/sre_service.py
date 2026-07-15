from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.ai.health_assessor import assess_health
from app.alerts.email import send_incident_email
from app.core.config import settings
from app.database.models import (
    Alert,
    APICheck,
    HealthAssessmentRecord,
    Incident,
)
from app.monitoring.checker import calculate_base_status, check_endpoint


MONITORED_SERVICES = [
    {
        "service_name": "products-api",
        "url": f"{settings.monitored_base_url}/api/products",
    },
    {
        "service_name": "health-api",
        "url": f"{settings.monitored_base_url}/api/health",
    },
]


def _recent_checks(db: Session, service_name: str, limit: int = 5):
    rows = db.scalars(
        select(APICheck)
        .where(APICheck.service_name == service_name)
        .order_by(desc(APICheck.checked_at))
        .limit(limit)
    ).all()

    return [
        {
            "status_code": row.status_code,
            "latency_ms": row.latency_ms,
            "reachable": row.reachable,
            "deterministic_status": row.deterministic_status,
            "error_message": row.error_message,
            "checked_at": row.checked_at,
        }
        for row in rows
    ]


async def run_service_check(db: Session, service: dict) -> dict:
    raw_check = await check_endpoint(
        service_name=service["service_name"],
        url=service["url"],
    )

    history_before = _recent_checks(db, service["service_name"])
    recent_failure_count = sum(
        1
        for item in history_before[:2]
        if item["deterministic_status"] != "HEALTHY"
    )

    base_status = calculate_base_status(
        raw_check,
        recent_failure_count=recent_failure_count,
    )

    check_record = APICheck(
        service_name=raw_check["service_name"],
        endpoint=raw_check["endpoint"],
        status_code=raw_check["status_code"],
        latency_ms=raw_check["latency_ms"],
        reachable=raw_check["reachable"],
        deterministic_status=base_status,
        error_message=raw_check["error_message"],
    )
    db.add(check_record)
    db.commit()
    db.refresh(check_record)

    current_payload = {
        **raw_check,
        "deterministic_status": base_status,
    }

    assessment = await assess_health(
        base_status=base_status,
        current_check=current_payload,
        recent_checks=history_before,
    )

    assessment_record = HealthAssessmentRecord(
        api_check_id=check_record.id,
        status=assessment.status,
        summary=assessment.summary,
        probable_cause=assessment.probable_cause,
        impact=assessment.impact,
        remedies=assessment.remedies,
        confidence=assessment.confidence,
    )
    db.add(assessment_record)

    open_incident = db.scalar(
        select(Incident)
        .where(
            Incident.service_name == service["service_name"],
            Incident.status == "OPEN",
        )
        .order_by(desc(Incident.started_at))
    )

    if assessment.status != "HEALTHY":
        if not open_incident:
            open_incident = Incident(
                service_name=service["service_name"],
                severity=assessment.status,
                status="OPEN",
                summary=assessment.summary,
            )
            db.add(open_incident)
            db.commit()
            db.refresh(open_incident)

        if not open_incident.alert_sent:
            sent, error = send_incident_email(
                service_name=service["service_name"],
                severity=assessment.status,
                summary=assessment.summary,
                probable_cause=assessment.probable_cause,
                impact=assessment.impact,
                remedies=assessment.remedies,
            )

            alert = Alert(
                incident_id=open_incident.id,
                service_name=service["service_name"],
                severity=assessment.status,
                recipient=settings.alert_recipient,
                subject=f"[{assessment.status}] {service['service_name']} health incident",
                sent=sent,
                error_message=error,
            )
            db.add(alert)

            if sent:
                open_incident.alert_sent = True
    elif open_incident:
        open_incident.status = "RESOLVED"
        open_incident.resolved_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "check_id": check_record.id,
        "service_name": service["service_name"],
        "check": current_payload,
        "assessment": assessment.model_dump(),
    }


async def run_all_checks(db: Session) -> list[dict]:
    results = []
    for service in MONITORED_SERVICES:
        results.append(await run_service_check(db, service))
    return results
