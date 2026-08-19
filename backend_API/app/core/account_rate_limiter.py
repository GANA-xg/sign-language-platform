"""
Simple sliding-window rate limiter, keyed by account identifier (email)
rather than IP address. In-memory only — resets on server restart, which
is acceptable for Milestone 3 (no paid Redis needed, matches SRS's
"free tools only" rule). Swap for Redis in Milestone 4 if multi-instance
deployment is introduced.
"""
import time
from collections import defaultdict
from threading import Lock

# { "login:email@example.com": [timestamp1, timestamp2, ...] }
_attempts: dict[str, list[float]] = defaultdict(list)
_lock = Lock()


def is_rate_limited(key: str, max_attempts: int, window_seconds: int) -> bool:
    """
    Returns True if `key` has exceeded max_attempts within window_seconds.
    Also records this attempt as part of the check (call once per request).
    """
    now = time.time()
    with _lock:
        # Drop attempts outside the sliding window
        _attempts[key] = [t for t in _attempts[key] if now - t < window_seconds]

        if len(_attempts[key]) >= max_attempts:
            return True

        _attempts[key].append(now)
        return False


def reset_attempts(key: str) -> None:
    """Call this after a successful login to clear the failed-attempt count."""
    with _lock:
        _attempts.pop(key, None)