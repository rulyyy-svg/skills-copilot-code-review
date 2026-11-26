"""Authentication helpers for protected API endpoints."""

import hashlib
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, Header, HTTPException

from .database import sessions_collection, teachers_collection


def get_session_token(authorization: Optional[str] = Header(default=None)) -> str:
    """Extract a bearer token from the Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")

    token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    return token


def get_current_teacher(token: str = Depends(get_session_token)) -> dict:
    """Return the teacher associated with a valid, unexpired login token."""
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    session = sessions_collection.find_one({
        "_id": token_hash,
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    if not session:
        raise HTTPException(status_code=401, detail="Authentication required")

    teacher = teachers_collection.find_one({"_id": session["username"]})
    if not teacher:
        raise HTTPException(status_code=401, detail="Authentication required")
    return teacher
