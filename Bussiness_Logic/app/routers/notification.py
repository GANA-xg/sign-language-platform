from fastapi import APIRouter
from uuid import UUID
from app.schemas.notification import NotificationListOut
from app.services.notification_service import (
    get_notifications,
    mark_all_read,
    trigger_notifications,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/{user_id}", response_model=NotificationListOut)
def get_user_notifications(user_id: UUID):
    return get_notifications(user_id)


@router.post("/{user_id}/read", response_model=NotificationListOut)
def mark_notifications_read(user_id: UUID):
    return mark_all_read(user_id)


@router.post("/{user_id}/trigger", response_model=NotificationListOut)
def trigger_user_notifications(user_id: UUID):
    """
    Checks all key events for a user and creates any new notifications.
    Call this after a session ends or when the Frontend polls for updates.
    """
    trigger_notifications(user_id)
    return get_notifications(user_id)