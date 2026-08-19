from fastapi import FastAPI, UploadFile, File
import cv2
import mediapipe as mp
import numpy as np
import joblib
import os

import time
from .feedback import generate_feedback
from .quality import analyze_hand_quality
from .history import add_prediction, get_history, clear_history
from .analytics import get_analytics
from .dashboard import get_dashboard
from fastapi.middleware.cors import CORSMiddleware

# ==================================================
# FastAPI App
# ==================================================

app = FastAPI(title="Sign Language Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================================================
# Paths
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "xgboost_landmark.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "..", "models", "label_encoder.pkl")

# ==================================================
# Load Model
# ==================================================

model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)

print("Model Loaded Successfully!")

# ==================================================
# MediaPipe
# ==================================================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5
)

# ==================================================
# Home API
# ==================================================

@app.get("/")
def home():
    return {
        "message": "Sign Language Prediction API is Running"
    }

# ==================================================
# Feature Extraction
# ==================================================

def extract_features(image):

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb)

    print("Detection Result :", results.multi_hand_landmarks)

    if not results.multi_hand_landmarks:
        return None

    hand = results.multi_hand_landmarks[0]
    quality = analyze_hand_quality(hand)

    # Draw landmarks for debugging
    debug = image.copy()
    mp_draw.draw_landmarks(
        debug,
        hand,
        mp_hands.HAND_CONNECTIONS
    )

    cv2.imwrite("detected_hand.jpg", debug)

    features = []

    for lm in hand.landmark:
        features.extend([
            lm.x,
            lm.y,
            lm.z
        ])

    return features, quality

# ==================================================
# Prediction
# ==================================================

def predict(features):

    features = np.array(features).reshape(1, -1)

    prediction = model.predict(features)[0]

    confidence = float(model.predict_proba(features).max())

    label = label_encoder.inverse_transform([prediction])[0]

    return label, confidence
# ==================================================
# Predict API
# ==================================================

@app.post("/predict")
async def predict_sign(file: UploadFile = File(...)):

    start_time = time.time()

    image_bytes = await file.read()

    image_array = np.frombuffer(image_bytes, np.uint8)

    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        return {
            "success": False,
            "message": "Invalid image"
        }

    # Save uploaded image for debugging
    cv2.imwrite("uploaded_image.jpg", image)

    result = extract_features(image)

    if result is None:
        return {
            "success": False,
            "message": "No hand detected"
        }
    features, quality = result

    label, confidence = predict(features)

    feedback = generate_feedback(confidence)

    processing_time = round((time.time() - start_time) * 1000, 2)

    record = {
    "prediction": label,
    "confidence": round(confidence, 4),
    "confidence_level": feedback["confidence_level"],
    "status": feedback["status"],
    "gesture_quality": quality["gesture_quality"],
    "processing_time_ms": processing_time
    }

    add_prediction(record)


    return {
        "success": True,
        "prediction": label,
        "confidence": round(confidence, 4),
        "confidence_level": feedback["confidence_level"],
        "status": feedback["status"],
        "feedback": feedback["feedback"],
        "processing_time_ms": processing_time,
        "hand_position": quality["hand_position"],
        "hand_distance": quality["hand_distance"],
        "gesture_quality": quality["gesture_quality"],
        "suggestion": quality["suggestion"]
    }


# ==================================================
# Prediction History API
# ==================================================

@app.get("/history")
def history():
    return {
        "total_predictions": len(get_history()),
        "history": get_history()
    }


# ==================================================
# Clear Prediction History API
# ==================================================

@app.delete("/history")
def delete_history():
    clear_history()
    return {
        "message": "Prediction history cleared successfully."
    }

@app.get("/analytics")
def analytics():
    return get_analytics()

# ==================================================
# Dashboard API
# ==================================================

@app.get("/dashboard")
def dashboard():

    return get_dashboard()