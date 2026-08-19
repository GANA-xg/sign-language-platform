"""
predict.py

Loads the trained XGBoost model and predicts the ASL gesture
along with confidence and user-friendly feedback.
"""

import os
import joblib
import numpy as np

from feedback import generate_feedback

# ==================================================
# Paths
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_DIR = os.path.join(
    BASE_DIR,
    "..",
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "xgboost_landmark.pkl"
)

ENCODER_PATH = os.path.join(
    MODEL_DIR,
    "label_encoder.pkl"
)

# ==================================================
# Load Model
# ==================================================

print("Loading XGBoost Model...")

model = joblib.load(MODEL_PATH)
encoder = joblib.load(ENCODER_PATH)

print("Model Loaded Successfully!")

# ==================================================
# Prediction Function
# ==================================================

def predict_gesture(features):
    """
    Predict ASL gesture using extracted landmarks.

    Parameters
    ----------
    features : list
        63 landmark values (21 landmarks × x,y,z)

    Returns
    -------
    dict
        Prediction result with confidence and feedback.
    """

    if len(features) != 63:
        raise ValueError(
            f"Expected 63 features but got {len(features)}"
        )

    # Convert to NumPy
    features = np.array(features).reshape(1, -1)

    # Predict class
    prediction = model.predict(features)

    # Decode label
    gesture = encoder.inverse_transform(prediction)[0]

    # Prediction confidence (0.0 - 1.0)
    confidence = float(model.predict_proba(features).max())

    # Generate feedback
    feedback = generate_feedback(confidence)

    # Final response
    return {
        "gesture": gesture,
        "confidence": round(confidence * 100, 2),
        "confidence_level": feedback["confidence_level"],
        "status": feedback["status"],
        "feedback": feedback["feedback"],
        "possible_issue": feedback["possible_issue"]
    }