import httpx
from typing import Optional

from app.core.config import AI_SERVICE_URL, USE_MOCK_AI, AI_SERVICE_TIMEOUT_SECONDS

# Kept as module-level names for backwards compatibility with any code
# that imports AI_PREDICT_URL / USE_MOCK_AI directly from this module.
AI_PREDICT_URL = AI_SERVICE_URL

class AIPredictionResult:
    def __init__(
        self,
        success: bool,
        predicted_sign: Optional[str] = None,
        confidence: Optional[float] = None,
        message: Optional[str] = None,
        # New fields from Abhinaya's updated /predict response
        confidence_level: Optional[str] = None,   # "High" / "Medium" / "Low"
        gesture_quality: Optional[str] = None,    # "Good" / "Poor" etc.
        suggestion: Optional[str] = None,         # the possible_issue hint we needed
        hand_position: Optional[str] = None,
        hand_distance: Optional[str] = None,
        status: Optional[str] = None,             # "Excellent" / etc.
        ai_feedback: Optional[str] = None,        # her own feedback text
        processing_time_ms: Optional[float] = None,
    ):
        self.success = success
        self.predicted_sign = predicted_sign
        self.confidence = confidence
        self.message = message
        self.confidence_level = confidence_level
        self.gesture_quality = gesture_quality
        self.suggestion = suggestion
        self.hand_position = hand_position
        self.hand_distance = hand_distance
        self.status = status
        self.ai_feedback = ai_feedback
        self.processing_time_ms = processing_time_ms


def get_prediction(
    image_bytes: bytes,
    auth_token: Optional[str] = None
) -> AIPredictionResult:
    """
    Calls Abhinaya's AI service and normalizes the full response.

    Current response shape (as of her latest commits):
    {
        "success": true,
        "prediction": "A",
        "confidence": 0.9997,
        "confidence_level": "High",
        "status": "Excellent",
        "feedback": "...",
        "processing_time_ms": 45.2,
        "hand_position": "...",
        "hand_distance": "...",
        "gesture_quality": "Good",
        "suggestion": "Move hand closer to camera"
    }

    "suggestion" is the possible_issue hint flagged as needed since M2 Day 1.
    """
    if USE_MOCK_AI:
        return AIPredictionResult(
            success=True,
            predicted_sign="A",
            confidence=0.87,
            confidence_level="High",
            gesture_quality="Good",
            suggestion=None,
        )

    files = {"file": ("frame.jpg", image_bytes, "image/jpeg")}

    try:
        response = httpx.post(AI_PREDICT_URL, files=files, timeout=AI_SERVICE_TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
    except httpx.TimeoutException:
        return AIPredictionResult(success=False, message="AI service timed out")
    except httpx.RequestError as e:
        return AIPredictionResult(success=False, message=f"AI service unreachable: {str(e)}")
    except Exception as e:
        return AIPredictionResult(success=False, message=f"Unexpected error: {str(e)}")

    if not data.get("success", False):
        return AIPredictionResult(
            success=False,
            message=data.get("message", "Prediction failed")
        )

    return AIPredictionResult(
        success=True,
        predicted_sign=data.get("prediction"),
        confidence=min(1.0, max(0.0, (data.get("confidence") or 0.0) / 100.0)),
        confidence_level=data.get("confidence_level"),
        gesture_quality=data.get("gesture_quality"),
        suggestion=data.get("suggestion"),
        hand_position=data.get("hand_position"),
        hand_distance=data.get("hand_distance"),
        status=data.get("status"),
        ai_feedback=data.get("feedback"),
        processing_time_ms=data.get("processing_time_ms"),
    )