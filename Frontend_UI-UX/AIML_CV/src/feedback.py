"""
feedback.py

Generates user-friendly feedback based on the model's confidence score.
"""

def generate_feedback(confidence):
    """
    Parameters:
        confidence (float): Prediction confidence (0.0 - 1.0)

    Returns:
        dict: Contains confidence level, status and feedback message.
    """

    confidence_percent = confidence * 100

    # High Confidence
    if confidence_percent >= 95:
        return {
            "confidence_level": "High",
            "status": "Correct",
            "feedback": "Excellent! Gesture detected clearly."
        }

    # Medium Confidence
    elif confidence_percent >= 85:
        return {
            "confidence_level": "Medium",
            "status": "Good",
            "feedback": "Gesture detected successfully. Keep your hand steady for even better accuracy."
        }

    # Low Confidence
    elif confidence_percent >= 70:
        return {
            "confidence_level": "Low",
            "status": "Needs Improvement",
            "feedback": "Move your hand closer to the camera and improve lighting."
        }

    # Very Low Confidence
    else:
        return {
            "confidence_level": "Very Low",
            "status": "Uncertain",
            "feedback": "Gesture could not be recognized clearly. Please try again with a clear hand gesture."
        }