"""
Practice Service — Pydantic Schemas

These mirror the PracticeSession field design from Day 1
(AI Sign Lang - Business Logic (Intern 4) Notion doc).

NOTE: user_id / lesson_id are plain strings for now since Intern 2's
User Service and Course Service aren't live yet. Once real auth (Day 6)
and seeded lessons (Day 5) exist, these should become validated FKs
(e.g. checked against the User/Lesson tables) rather than free-form strings.
"""

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from enum import Enum
from typing import Optional


class SessionStatus(str, Enum):
    in_progress = "in_progress"
    completed = "completed"
    abandoned = "abandoned"


class PracticeSessionStartRequest(BaseModel):
    user_id: UUID
    lesson_id: int          # was string — now matches DB's INT lesson_id


class PracticeSessionEndRequest(BaseModel):
    session_id: UUID
    status: SessionStatus = SessionStatus.completed  # completed or abandoned


class PracticeSessionOut(BaseModel):
    session_id: UUID
    user_id: UUID
    lesson_id: int
    status: SessionStatus
    started_at: datetime          # renamed from start_time
    ended_at: Optional[datetime] = None   # renamed from end_time
    duration_seconds: Optional[int] = None  # computed, never stored

class AttemptResultOut(BaseModel):
    predicted_sign: Optional[str] = None
    confidence: Optional[float] = None
    success: bool
    message: Optional[str] = None
    hold_seconds: Optional[float] = None
    gesture_quality: Optional[str] = None      # NEW
    suggestion: Optional[str] = None           # NEW — possible_issue hint
    confidence_level: Optional[str] = None     # NEW
    assessment: Optional[dict] = None