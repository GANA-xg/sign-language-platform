from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Dict, Optional

from app.models.practice import PracticeSession
from app.schemas.practice import SessionStatus, PracticeSessionOut


class InMemoryPracticeSessionStore:
    """
    Standing in for the real practice_sessions table until Intern 5's
    DB integration lands. Field names/types now mirror the actual schema
    (see Notion: Day 1 Data Model — REVISED).
    """

    def __init__(self):
        self._sessions: Dict[UUID, PracticeSession] = {}

    def start_session(self, user_id: UUID, lesson_id: int) -> PracticeSession:
        session = PracticeSession(
            session_id=uuid4(),
            user_id=user_id,
            lesson_id=lesson_id,
            status=SessionStatus.in_progress,
            started_at=datetime.now(timezone.utc),
        )
        self._sessions[session.session_id] = session
        return session

    def end_session(self, session_id: UUID, status: SessionStatus) -> Optional[PracticeSession]:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        if session.status != SessionStatus.in_progress:
            raise ValueError(f"Session already ended (current status: {session.status.value})")
        session.ended_at = datetime.now(timezone.utc)
        session.status = status
        return session
    def get_sessions_by_user(self, user_id) -> list:
        return [s for s in self._sessions.values() if s.user_id == user_id]

    def get_session(self, session_id: UUID) -> Optional[PracticeSession]:
        return self._sessions.get(session_id)

    @staticmethod
    def compute_duration_seconds(session: PracticeSession) -> Optional[int]:
        if session.ended_at is None:
            return None
        return int((session.ended_at - session.started_at).total_seconds())

    def to_out(self, session: PracticeSession) -> PracticeSessionOut:
        return PracticeSessionOut(
            session_id=session.session_id,
            user_id=session.user_id,
            lesson_id=session.lesson_id,
            status=session.status,
            started_at=session.started_at,
            ended_at=session.ended_at,
            duration_seconds=self.compute_duration_seconds(session),
        )


practice_store = InMemoryPracticeSessionStore()