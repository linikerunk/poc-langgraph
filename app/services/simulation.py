from threading import Lock

_lock = Lock()
_mode = "healthy"

VALID_MODES = {"healthy", "slow", "error"}


def set_mode(mode: str) -> str:
    global _mode
    if mode not in VALID_MODES:
        raise ValueError(f"Unsupported mode: {mode}")
    with _lock:
        _mode = mode
    return _mode


def get_mode() -> str:
    with _lock:
        return _mode
