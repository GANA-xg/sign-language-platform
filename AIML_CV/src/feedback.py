"""
feedback.py

Generates user-friendly feedback based on the model's confidence score.
"""

def generate_feedback(confidence):
    """
    Parameters:
        confidence (float): Prediction confidence (0.0 - 1.0)

    Returns:
        dict: Contains confidence level, status,
              feedback message and possible issue.
    """

    confidence_percent = confidence * 100

    # High Confidence
    if confidence_percent >= 95:
        return {
            "confidence_level": "High",
            "status": "Correct",
            "feedback": "Excellent! Gesture detected clearly.",
            "possible_issue": "No major issues detected."
        }

    # Medium Confidence
    elif confidence_percent >= 85:
        return {
            "confidence_level": "Medium",
            "status": "Good",
            "feedback": "Gesture detected successfully. Keep your hand steady for even better accuracy.",
            "possible_issue": "Minor finger alignment could be improved."
        }

    # Low Confidence
    elif confidence_percent >= 70:
        return {
            "confidence_level": "Low",
            "status": "Needs Improvement",
            "feedback": "Move your hand closer to the camera and improve lighting.",
            "possible_issue": "Hand position or finger placement may be incorrect."
        }

    # Very Low Confidence
    else:
        return {
            "confidence_level": "Very Low",
            "status": "Uncertain",
            "feedback": "Gesture could not be recognized clearly. Please try again with a clear hand gesture.",
            "possible_issue": "Hand not clearly visible. Ensure good lighting and keep your entire hand inside the camera frame."
        }