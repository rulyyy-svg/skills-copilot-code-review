"""Public announcement display and authenticated announcement management."""

from datetime import date
from typing import Any, Dict, List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..database import announcements_collection
from ..security import get_current_teacher

router = APIRouter(prefix="/announcements", tags=["announcements"])


class AnnouncementInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=2000)
    start_date: Optional[date] = None
    expiration_date: date


def _announcement_values(announcement: AnnouncementInput) -> Dict[str, Any]:
    values = announcement.model_dump()
    values["title"] = values["title"].strip()
    values["message"] = values["message"].strip()
    if not values["title"] or not values["message"]:
        raise HTTPException(
            status_code=422, detail="Title and message cannot be blank")
    if (values["start_date"] and
            values["start_date"] > values["expiration_date"]):
        raise HTTPException(
            status_code=422,
            detail="Start date must be on or before the expiration date")

    values["start_date"] = (
        values["start_date"].isoformat() if values["start_date"] else None)
    values["expiration_date"] = values["expiration_date"].isoformat()
    return values


def _serialize(announcement: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(announcement["_id"]),
        "title": announcement["title"],
        "message": announcement["message"],
        "start_date": announcement.get("start_date"),
        "expiration_date": announcement["expiration_date"]
    }


def _find_announcement(announcement_id: str) -> Dict[str, Any]:
    try:
        object_id = ObjectId(announcement_id)
    except InvalidId as error:
        raise HTTPException(
            status_code=404, detail="Announcement not found") from error

    announcement = announcements_collection.find_one({"_id": object_id})
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return announcement


@router.get("", response_model=List[Dict[str, Any]])
@router.get("/", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """Return announcements that are currently within their display dates."""
    today = date.today().isoformat()
    query = {
        "expiration_date": {"$gte": today},
        "$or": [
            {"start_date": None},
            {"start_date": {"$lte": today}}
        ]
    }
    return [
        _serialize(announcement)
        for announcement in announcements_collection.find(query).sort(
            "expiration_date", 1)
    ]


@router.get(
    "/manage",
    response_model=List[Dict[str, Any]],
    dependencies=[Depends(get_current_teacher)]
)
def get_all_announcements() -> List[Dict[str, Any]]:
    """Return all announcements to a signed-in teacher."""
    return [
        _serialize(announcement)
        for announcement in announcements_collection.find().sort(
            "expiration_date", -1)
    ]


@router.post(
    "",
    response_model=Dict[str, Any],
    status_code=201,
    dependencies=[Depends(get_current_teacher)]
)
def create_announcement(
    announcement: AnnouncementInput
) -> Dict[str, Any]:
    """Create an announcement as a signed-in teacher."""
    result = announcements_collection.insert_one(
        _announcement_values(announcement))
    return _serialize(announcements_collection.find_one(
        {"_id": result.inserted_id}))


@router.put(
    "/{announcement_id}",
    response_model=Dict[str, Any],
    dependencies=[Depends(get_current_teacher)]
)
def update_announcement(
    announcement_id: str,
    announcement: AnnouncementInput
) -> Dict[str, Any]:
    """Replace an existing announcement as a signed-in teacher."""
    existing = _find_announcement(announcement_id)
    values = _announcement_values(announcement)
    announcements_collection.update_one(
        {"_id": existing["_id"]}, {"$set": values})
    return _serialize(announcements_collection.find_one(
        {"_id": existing["_id"]}))


@router.delete(
    "/{announcement_id}",
    response_model=Dict[str, str],
    dependencies=[Depends(get_current_teacher)]
)
def delete_announcement(
    announcement_id: str
) -> Dict[str, str]:
    """Delete an announcement as a signed-in teacher."""
    existing = _find_announcement(announcement_id)
    announcements_collection.delete_one({"_id": existing["_id"]})
    return {"message": "Announcement deleted"}
