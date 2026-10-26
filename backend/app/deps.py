"""Request dependencies. There is no login: visitors are anonymous, administration needs a key."""
import hmac
import re

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .db import get_db
from .errors import AppError
from .models import User

VISITOR_RE = re.compile(r"^[A-Za-z0-9_-]{16,64}$")
SHARED_VISITOR = "anonymous"
VISITOR_DOMAIN = "visitors.invalid"  # reserved TLD: can never be a real mailbox


def _visitor_id(request: Request) -> str:
    """The browser's random, anonymous id (created by the frontend, stored in localStorage). Not a credential: it only
    groups one browser's forecast history. Clients that send none share one 'anonymous' history."""
    raw = request.headers.get("x-visitor-id", "").strip()
    if not raw:
        return SHARED_VISITOR
    if not VISITOR_RE.match(raw):
        raise AppError(400, "invalid_visitor_id", "X-Visitor-Id must be 16-64 letters, digits, '-' or '_'.")
    return raw


def _email(vid: str) -> str:
    return f"visitor-{vid.lower()}@{VISITOR_DOMAIN}"


def find_visitor(request: Request, db: Session = Depends(get_db)) -> User | None:
    """The visitor's record if they have made forecasts before; never creates one (read-only requests)."""
    return db.execute(select(User).where(User.email == _email(_visitor_id(request)))).scalar_one_or_none()


def get_visitor(request: Request, db: Session = Depends(get_db)) -> User:
    """The visitor's record, created on first use (when saving a forecast). The row has no usable password."""
    email = _email(_visitor_id(request))
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is None:
        user = User(email=email, full_name="Visitor", password_hash="!", role="user")
        db.add(user)
        db.commit()
    return user


def admin_status(request: Request) -> tuple[str, bool]:
    st = get_settings()
    mode = st.admin_mode
    if mode == "open":
        return mode, True
    if mode == "disabled":
        return mode, False
    supplied = request.headers.get("x-admin-key", "")
    return mode, hmac.compare_digest(supplied.encode(), st.admin_api_key.encode())


def require_admin(request: Request) -> None:
    mode, ok = admin_status(request)
    if mode == "disabled":
        raise AppError(403, "admin_disabled", "Administration is disabled on this server (ADMIN_API_KEY is not set).")
    if not ok:
        raise AppError(401, "admin_key_required", "A valid administrator key is required for this action.")
