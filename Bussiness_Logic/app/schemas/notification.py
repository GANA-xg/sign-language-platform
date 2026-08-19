from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    badge_earned = "badge_earned"
    certificate_ready = "certificate_ready"
    new_recommendation = "new_recommendation"
    general = "general"


class NotificationOut(BaseModel):
    notification_id: str
    user_id: UUID
    notification_type: NotificationType
    title: str
    message: str
    is_read: bool
    created_at: datetime


class NotificationListOut(BaseModel):
    user_id: UUID
    notifications: List[NotificationOut]
    unread_count: int
    total: int