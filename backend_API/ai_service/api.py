from fastapi import FastAPI, UploadFile, File
import cv2
import mediapipe as mp
import numpy as np
import joblib
import os

# ==================================================
# FastAPI App
# ==================================================

app = FastAPI(title="Sign Language Prediction API")

# ==================================================
# Paths
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "..",
    "models",
    "xgboost_landmark.pkl"
)

ENCODER_PATH = os.path.join(
    BASE_DIR,
    "..",
    "models",
    "label_encoder.pkl"
)

print("Model Path :", MODEL_PATH)
print("Encoder Path :", ENCODER_PATH)

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

    if not results.multi_hand_landmarks:
        return None

    hand = results.multi_hand_landmarks[0]

    features = []

    for point in hand.landmark:
        features.extend([
            point.x,
            point.y,
            point.z
        ])

    return features

# ==================================================
# Prediction Function
# ==================================================

def predict(features):

    features = np.array(features).reshape(1, -1)

    prediction = model.predict(features)[0]

    confidence = float(model.predict_proba(features).max())

    label = label_encoder.inverse_transform([prediction])[0]

    return label, confidence

# ==================================================
# Prediction API
# ==================================================

@app.post("/predict")
async def predict_sign(file: UploadFile = File(...)):

    image_bytes = await file.read()

    image = np.frombuffer(image_bytes, np.uint8)

    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    if image is None:
        return {
            "success": False,
            "message": "Invalid image"
        }

    features = extract_features(image)

    if features is None:
        return {
            "success": False,
            "message": "No hand detected"
        }

    label, confidence = predict(features)

    return {
        "success": True,
        "prediction": label,
        "confidence": round(confidence, 4)
    }

# ==================================================
# Run API
# ==================================================

# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(
#         "api:app",
#         host="127.0.0.1",
#         port=8000,
#         reload=True
#     )