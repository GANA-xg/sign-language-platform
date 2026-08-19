from datetime import datetime
from pydantic import BaseModel, Field


class LessonCreate(BaseModel):
    module_id: int
    title: str = Field(..., max_length=150)
    description: str | None = None
    sequence_order: int
    estimated_duration_minutes: int | None = None
    difficulty_level: str = "beginner"
    category: str = "Alphabet"
    is_published: bool = False


class LessonResponse(BaseModel):
    lesson_id: int
    module_id: int
    title: str
    description: str | None
    sequence_order: int
    difficulty_level: str
    category: str
    is_published: bool
    created_at: datetime

    class Config:
        from_attributes = True