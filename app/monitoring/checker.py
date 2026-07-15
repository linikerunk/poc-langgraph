import time

import httpx


async def check_endpoint(
    service_name: str,
    url: str,
    timeout_seconds: float = 5.0,
) -> dict:
    started = time.perf_counter()

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.get(url)

        latency_ms = (time.perf_counter() - started) * 1000

        return {
            "service_name": service_name,
            "endpoint": url,
            "status_code": response.status_code,
            "latency_ms": round(latency_ms, 2),
            "reachable": True,
            "error_message": None,
        }
    except Exception as exc:
        return {
            "service_name": service_name,
            "endpoint": url,
            "status_code": None,
            "latency_ms": None,
            "reachable": False,
            "error_message": str(exc),
        }


def calculate_base_status(
    check: dict,
    recent_failure_count: int = 0,
) -> str:
    if not check["reachable"]:
        return "CRITICAL"

    status_code = check["status_code"] or 0
    latency_ms = check["latency_ms"] or 0

    if status_code >= 500:
        return "CRITICAL"

    if latency_ms > 3000:
        return "CRITICAL"

    if status_code >= 400:
        # Escalate repeated soft failures (4xx / prior warnings) to CRITICAL.
        if recent_failure_count >= 2:
            return "CRITICAL"
        return "WARNING"

    if latency_ms > 1000:
        if recent_failure_count >= 2:
            return "CRITICAL"
        return "WARNING"

    return "HEALTHY"
