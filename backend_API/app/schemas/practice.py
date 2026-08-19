from datetime import datetime
from pydantic import BaseModel, Field


class PracticeSessionStart(BaseModel):
    user_id: str = Field(..., description="UUID of the user starting the practice")
    lesson_id: int = Field(..., description="ID of the lesson to practice")


class PracticeSessionStartResponse(BaseModel):
    session_id: str = Field(..., description="UUID of the created practice session")
    message: str = Field(..., description="Confirmation message")


class PracticeAttemptSubmit(BaseModel):
    session_id: str = Field(..., description="UUID of the practice session")
    expected_sign: str = Field(..., description="Expected sign language gesture")
    image_blob: str = Field(..., description="Base64-encoded image data")
    attempt_started_at: datetime = Field(..., description="Timestamp when attempt started")


class PracticeAttemptSubmitResponse(BaseModel):
    attempt_id: str = Field(..., description="UUID of the recorded attempt")
    message: str = Field(..., description="Confirmation message")


class AssessmentSubmit(BaseModel):
    session_id: str = Field(..., description="UUID of the practice session")
    expected_sign: str = Field(..., description="Expected sign language gesture")
    predicted_sign: str = Field(..., description="AI-predicted sign language gesture")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")


class AssessmentSubmitResponse(BaseModel):
    assessment_id: str = Field(..., description="UUID of the recorded assessment")
    message: str = Field(..., description="Confirmation message")
