from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime
from typing import List
from app.schemas.feedback import FeedbackItem


@dataclass
class SessionFeedback:
    session_id: UUID
    items: List[FeedbackItem] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now())