"""
Authentication endpoints for the High School Management System API
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException

from ..database import sessions_collection, teachers_collection, verify_password
from ..security import get_current_teacher, get_session_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/login")
def login(username: str, password: str) -> Dict[str, Any]:
    """Login a teacher account"""
    # Find the teacher in the database
    teacher = teachers_collection.find_one({"_id": username})

    # Verify password using Argon2 verifier from database.py
    if not teacher or not verify_password(teacher.get("password", ""), password):
        raise HTTPException(
            status_code=401, detail="Invalid username or password")

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    sessions_collection.insert_one({
        "_id": token_hash,
        "username": teacher["username"],
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7)
    })

    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"],
        "token": token
    }


@router.get("/check-session")
def check_session(teacher: dict = Depends(get_current_teacher)) -> Dict[str, Any]:
    """Return the signed-in teacher for a valid bearer token."""
    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"]
    }


@router.post(
    "/logout", dependencies=[Depends(get_current_teacher)])
def logout(token: str = Depends(get_session_token)) -> Dict[str, str]:
    """Invalidate the current login token."""
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    sessions_collection.delete_one({"_id": token_hash})
    return {"message": "Logged out"}
