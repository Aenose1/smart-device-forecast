import threading
import time
from collections import defaultdict, deque

from fastapi import Request

from .config import get_settings
from .errors import AppError

_hits: dict[str, deque] = defaultdict(deque)
_lock = threading.Lock()


def client_ip(request: Request) -> str:
    """Client address for rate limiting.

    Behind Render (or any reverse proxy) request.client is the PROXY, so without this every visitor would share one
    rate-limit bucket. With TRUST_PROXY=true we take the address the trusted proxy appended to X-Forwarded-For
    (the n-th entry from the right; the left-most entries can be forged by the client). Leave TRUST_PROXY off when the
    app is reachable directly, otherwise anyone could spoof the header.
    """
    st = get_settings()
    if st.trust_proxy:
        parts = [p.strip() for p in request.headers.get("x-forwarded-for", "").split(",") if p.strip()]
        hops = max(1, st.trusted_proxy_hops)
        if len(parts) >= hops:
            return parts[-hops]
    return request.client.host if request.client else "unknown"


def limiter(name: str, limit: int, window_s: int):
    """Sliding-window limiter per client IP (in-memory; use Redis/gateway when scaling out)."""

    def dep(request: Request):
        if not get_settings().rate_limit_enabled:
            return
        key = f"{name}:{client_ip(request)}"
        now = time.monotonic()
        with _lock:
            q = _hits[key]
            while q and now - q[0] > window_s:
                q.popleft()
            if len(q) >= limit:
                raise AppError(429, "rate_limited", "Too many requests. Please wait a moment and try again.")
            q.append(now)

    return dep


def reset_limits() -> None:
    with _lock:
        _hits.clear()
