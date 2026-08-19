from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class LessonBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str
    difficulty: str

class LessonCreate(LessonBase):
    pass

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None

class LessonResponse(LessonBase):
    id: UUID

    class Config:
        from_attributes = True