import smtplib
from email.message import EmailMessage

from app.core.config import settings


def send_incident_email(
    service_name: str,
    severity: str,
    summary: str,
    probable_cause: str,
    impact: str,
    remedies: list[str],
) -> tuple[bool, str | None]:
    if not settings.enable_email_alerts:
        return False, "Email alerts are disabled"

    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = settings.alert_recipient
    message["Subject"] = f"[{severity}] {service_name} health incident"

    remedy_text = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(remedies, start=1)
    )

    message.set_content(
        f"""
Service: {service_name}
Status: {severity}

Summary:
{summary}

Probable cause:
{probable_cause}

Potential impact:
{impact}

Recommended actions:
{remedy_text}
""".strip()
    )

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
        return True, None
    except Exception as exc:
        return False, str(exc)
