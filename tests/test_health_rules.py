from app.monitoring.checker import calculate_base_status


def test_healthy():
    check = {
        "reachable": True,
        "status_code": 200,
        "latency_ms": 100,
    }
    assert calculate_base_status(check) == "HEALTHY"


def test_warning_latency():
    check = {
        "reachable": True,
        "status_code": 200,
        "latency_ms": 1500,
    }
    assert calculate_base_status(check) == "WARNING"


def test_critical_5xx():
    check = {
        "reachable": True,
        "status_code": 503,
        "latency_ms": 200,
    }
    assert calculate_base_status(check) == "CRITICAL"


def test_critical_unreachable():
    check = {
        "reachable": False,
        "status_code": None,
        "latency_ms": None,
    }
    assert calculate_base_status(check) == "CRITICAL"


def test_healthy_despite_recent_failures():
    check = {
        "reachable": True,
        "status_code": 200,
        "latency_ms": 200,
    }
    assert calculate_base_status(check, recent_failure_count=2) == "HEALTHY"


def test_repeated_soft_failure_escalates():
    check = {
        "reachable": True,
        "status_code": 200,
        "latency_ms": 1500,
    }
    assert calculate_base_status(check, recent_failure_count=2) == "CRITICAL"
