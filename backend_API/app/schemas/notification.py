import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict,field_validator
from app.utils.validators import sanitize_text_field

class NotificationCreate(BaseModel):
    user_id: uuid.UUID
    notification_type: str
    title: str
    message: str
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        return sanitize_text_field(v, "title", max_length=150)

    @field_validator("message")
    @classmethod
    def validate_message(cls, v):
        return sanitize_text_field(v, "message", max_length=500)

    @field_validator("notification_type")
    @classmethod
    def validate_type(cls, v):
        allowed = {"badge_earned", "streak_milestone", "certificate_ready", "new_recommendation"}
        if v not in allowed:
            raise ValueError(f"notification_type must be one of {allowed}")
        return v


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notification_id: int
    user_id: uuid.UUID
    notification_type: str
    title: str
    message: str
    is_read: bool
    read_at: Optional[datetime]
    related_entity_type: Optional[str]
    related_entity_id: Optional[str]
    created_at: datetime