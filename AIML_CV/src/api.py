from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import cv2
import mediapipe as mp
import numpy as np
import joblib
import os
import time
import uuid

from .feedback import generate_feedback
from .quality import analyze_hand_quality
from .history import add_prediction, get_history, clear_history
from .analytics import get_analytics
from .dashboard import get_dashboard
from .dynamic.dynamic_inference import predict_video


# ==================================================
# FastAPI App
# ==================================================

app = FastAPI(
    title="Sign Language Prediction API",
    description="AI/ML API for ASL alphabet gesture recognition",
    version="1.0.0"
)


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://ai-signlanguage-frontend.onrender.com",
    "https://ai-signlanguage-business-logic.onrender.com",
    "https://ai-signlanguage-business-logic.onrender.com",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ==================================================
# Paths
# ==================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

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


# ==================================================
# Load Model
# ==================================================

try:

    model = joblib.load(
        MODEL_PATH
    )

    label_encoder = joblib.load(
        ENCODER_PATH
    )

    print("Model Loaded Successfully!")

except Exception as e:

    print(
        "Model loading failed:",
        str(e)
    )

    raise


# ==================================================
# MediaPipe
# ==================================================

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.3,
    min_tracking_confidence=0.3
)


# ==================================================
# Home API
# ==================================================

@app.get("/")
def home():

    return {
        "success": True,
        "message": "Sign Language Prediction API is Running"
    }


# ==================================================
# Health API
# ==================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "classes": len(
            label_encoder.classes_
        )
    }


# ==================================================
# Feature Extraction
# ==================================================

def extract_features(image):

    # --------------------------------------------------
    # Convert BGR → RGB
    # --------------------------------------------------

    rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    # --------------------------------------------------
    # MediaPipe hand detection
    # --------------------------------------------------

    results = hands.process(
        rgb
    )

    # --------------------------------------------------
    # No hand detected
    # --------------------------------------------------

    if not results.multi_hand_landmarks:

        return None

    # --------------------------------------------------
    # Get first detected hand
    # --------------------------------------------------

    hand = results.multi_hand_landmarks[0]

    # --------------------------------------------------
    # Analyze hand quality
    # --------------------------------------------------

    quality = analyze_hand_quality(
        hand
    )

    # --------------------------------------------------
    # Extract 21 landmarks
    #
    # Each landmark:
    # x, y, z
    #
    # 21 × 3 = 63 features
    # --------------------------------------------------

    features = []

    for landmark in hand.landmark:

        features.extend([
            landmark.x,
            landmark.y,
            landmark.z
        ])

    return features, quality


# ==================================================
# Prediction
# ==================================================

def predict(features):

    # --------------------------------------------------
    # Convert features to numpy array
    # --------------------------------------------------

    features = np.asarray(
        features,
        dtype=np.float32
    ).reshape(1, -1)

    # --------------------------------------------------
    # Predict class
    # --------------------------------------------------

    prediction = model.predict(
        features
    )[0]

    # --------------------------------------------------
    # Get prediction probabilities
    # --------------------------------------------------

    probabilities = model.predict_proba(
        features
    )[0]

    # --------------------------------------------------
    # Highest probability
    # --------------------------------------------------

    confidence = float(
        np.max(probabilities)
    )

    # --------------------------------------------------
    # Convert encoded value to letter
    # --------------------------------------------------

    label = label_encoder.inverse_transform(
        [prediction]
    )[0]

    return label, confidence
# ==================================================
# Dynamic Word Prediction API
# ==================================================

@app.post("/predict-word")
async def predict_dynamic_word(
    file: UploadFile = File(...)
):

    start_time = time.perf_counter()

    # ==================================================
    # Validate video file
    # ==================================================

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No video file provided."
        )

    if not file.content_type:
        raise HTTPException(
            status_code=400,
            detail="File type could not be determined."
        )

    if not (
        file.content_type.startswith("video/")
        or file.filename.lower().endswith(
            (".avi", ".mp4", ".mov", ".mkv")
        )
    ):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid video file."
        )

    # ==================================================
    # Read uploaded video
    # ==================================================

    video_bytes = await file.read()

    if not video_bytes:

        raise HTTPException(
            status_code=400,
            detail="Uploaded video is empty."
        )

    # ==================================================
    # Temporary directory
    # ==================================================

    temp_dir = os.path.join(
        BASE_DIR,
        "..",
        "temp"
    )

    os.makedirs(
        temp_dir,
        exist_ok=True
    )

    # ==================================================
    # Create unique temporary filename
    # ==================================================

    extension = os.path.splitext(
        file.filename
    )[1]

    if not extension:
        extension = ".avi"

    temp_filename = (
        f"dynamic_{uuid.uuid4().hex}{extension}"
    )

    temp_path = os.path.join(
        temp_dir,
        temp_filename
    )

    # ==================================================
    # Save uploaded video
    # ==================================================

    try:

        with open(
            temp_path,
            "wb"
        ) as video_file:

            video_file.write(
                video_bytes
            )

        # ==================================================
        # Dynamic model prediction
        # ==================================================

        result = predict_video(
            temp_path
        )

        # ==================================================
        # Processing time
        # ==================================================

        processing_time = round(
            (
                time.perf_counter()
                - start_time
            ) * 1000,
            2
        )

        # ==================================================
        # Response
        # ==================================================

        return {
            "success": True,

            "prediction":
                result["prediction"],

            "confidence":
                result["confidence"],

            "sequence_shape":
                result["sequence_shape"],

            "processing_time_ms":
                processing_time
        }

    except Exception as e:

        processing_time = round(
            (
                time.perf_counter()
                - start_time
            ) * 1000,
            2
        )

        return {
            "success": False,

            "prediction": None,

            "confidence": 0.0,

            "message": str(e),

            "processing_time_ms":
                processing_time
        }

    finally:

        # ==================================================
        # Delete temporary video
        # ==================================================

        if os.path.exists(
            temp_path
        ):

            try:
                os.remove(
                    temp_path
                )

            except Exception:
                pass

# ==================================================
# Predict API
# ==================================================

@app.post("/predict")
async def predict_sign(
    file: UploadFile = File(...)
):

    # ==================================================
    # Start timer
    # ==================================================

    start_time = time.perf_counter()

    # ==================================================
    # Validate file type
    # ==================================================

    if not file.content_type:

        raise HTTPException(
            status_code=400,
            detail="File type could not be determined."
        )

    if not file.content_type.startswith(
        "image/"
    ):

        raise HTTPException(
            status_code=400,
            detail="Please upload a valid image file."
        )

    # ==================================================
    # Read uploaded file
    # ==================================================

    image_bytes = await file.read()

    if not image_bytes:

        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty."
        )

    # ==================================================
    # Convert image bytes to numpy
    # ==================================================

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    # ==================================================
    # Decode image
    # ==================================================

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    # IMPORTANT:
    # Check image BEFORE resize
    # ==================================================

    if image is None:

        raise HTTPException(
            status_code=400,
            detail="Invalid or unsupported image."
        )

    # ==================================================
    # Resize image
    # ==================================================

    image = cv2.resize(
        image,
        (640, 640),
        interpolation=cv2.INTER_AREA
    )

    # ==================================================
    # Improve brightness slightly
    # ==================================================

    image = cv2.convertScaleAbs(
        image,
        alpha=1.2,
        beta=25
    )

    # ==================================================
    # Extract hand features
    # ==================================================

    result = extract_features(
        image
    )

    # ==================================================
    # No hand detected
    # ==================================================

    if result is None:

        processing_time = round(
            (
                time.perf_counter()
                - start_time
            ) * 1000,
            2
        )

        return {

            "success": False,

            "prediction": None,

            "confidence": 0.0,

            "confidence_level": "LOW",

            "status": "NO_HAND",

            "feedback": "No hand detected.",

            "possible_issue":
                "The hand is not visible to the camera.",

            "recommendation":
                "Please show your hand clearly inside the camera frame.",

            "processing_time_ms":
                processing_time
        }

    # ==================================================
    # Get features and quality
    # ==================================================

    features, quality = result

    # ==================================================
    # Predict gesture
    # ==================================================

    label, confidence = predict(
        features
    )

    # ==================================================
    # Generate confidence feedback
    # ==================================================

    feedback = generate_feedback(
        confidence
    )

    # ==================================================
    # Calculate processing time
    # ==================================================

    processing_time = round(
        (
            time.perf_counter()
            - start_time
        ) * 1000,
        2
    )

    # ==================================================
    # Get hand recommendation
    # ==================================================

    recommendation = quality.get(
        "suggestion"
    )

    # ==================================================
    # Save prediction history
    # ==================================================

    record = {

        "prediction": label,

        "confidence": round(
            confidence,
            4
        ),

        "confidence_level":
            feedback["confidence_level"],

        "status":
            feedback["status"],

        "gesture_quality":
            quality["gesture_quality"],

        "processing_time_ms":
            processing_time
    }

    add_prediction(
        record
    )

    # ==================================================
    # Final API response
    # ==================================================

    return {

        "success": True,

        # ------------------------------
        # Prediction
        # ------------------------------

        "prediction": label,

        # ------------------------------
        # Confidence
        # ------------------------------

        "confidence": round(
            confidence * 100,
            2
        ),

        "confidence_level":
            feedback["confidence_level"],

        # ------------------------------
        # Model feedback
        # ------------------------------

        "status":
            feedback["status"],

        "feedback":
            feedback["feedback"],

        "possible_issue":
            feedback["possible_issue"],

        # ------------------------------
        # Hand guidance
        # ------------------------------

        "recommendation":
            recommendation,

        "suggestion":
            recommendation,

        "hand_position":
            quality["hand_position"],

        "vertical_position":
            quality["vertical_position"],

        "hand_distance":
            quality["hand_distance"],

        "gesture_quality":
            quality["gesture_quality"],

        # ------------------------------
        # Performance
        # ------------------------------

        "processing_time_ms":
            processing_time
    }


# ==================================================
# Prediction History API
# ==================================================

@app.get("/history")
def history():

    history_data = get_history()

    return {

        "total_predictions":
            len(history_data),

        "history":
            history_data
    }


# ==================================================
# Clear Prediction History API
# ==================================================

@app.delete("/history")
def delete_history():

    clear_history()

    return {

        "success": True,

        "message":
            "Prediction history cleared successfully."
    }


# ==================================================
# Analytics API
# ==================================================

@app.get("/analytics")
def analytics():

    return get_analytics()


# ==================================================
# Dashboard API
# ==================================================

@app.get("/dashboard")
def dashboard():

    return get_dashboard()

# from fastapi import FastAPI, UploadFile, File
# import cv2
# import mediapipe as mp
# import numpy as np
# import joblib
# import os
# import time

# from .feedback import generate_feedback
# from .quality import analyze_hand_quality
# from .history import add_prediction, get_history, clear_history
# from .analytics import get_analytics
# from .dashboard import get_dashboard
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI(title="Sign Language Prediction API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:5173",
#         "http://127.0.0.1:5173",
#         "http://localhost:3000",
#         "http://127.0.0.1:3000",
    "https://ai-signlanguage-frontend.onrender.com",
    "https://ai-signlanguage-business-logic.onrender.com",
    "https://ai-signlanguage-business-logic.onrender.com",
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "xgboost_landmark.pkl")
# ENCODER_PATH = os.path.join(BASE_DIR, "..", "models", "label_encoder.pkl")

# model = joblib.load(MODEL_PATH)
# label_encoder = joblib.load(ENCODER_PATH)
# print("Model Loaded Successfully!")

# mp_hands = mp.solutions.hands
# mp_draw = mp.solutions.drawing_utils

# # static_image_mode=False → tracking mode, much faster for repeated captures
# hands = mp_hands.Hands(
#     static_image_mode=False,
#     max_num_hands=1,
#     min_detection_confidence=0.5,
#     min_tracking_confidence=0.5,
# )

# DEBUG_SAVE_IMAGES = False  # set True only for local debugging


# @app.get("/")
# def home():
#     return {"message": "Sign Language Prediction API is Running"}


# @app.get("/health")
# def health():
#     """Health check — confirms the service and model are up."""
#     return {
#         "status": "ok",
#         "service": "ai-prediction",
#         "model_loaded": model is not None,
#     }


# def extract_features(image):
#     rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     results = hands.process(rgb)

#     if not results.multi_hand_landmarks:
#         return None

#     hand = results.multi_hand_landmarks[0]
#     quality = analyze_hand_quality(hand)

#     if DEBUG_SAVE_IMAGES:
#         debug = image.copy()
#         mp_draw.draw_landmarks(debug, hand, mp_hands.HAND_CONNECTIONS)
#         cv2.imwrite("detected_hand.jpg", debug)

#     features = []
#     for lm in hand.landmark:
#         features.extend([lm.x, lm.y, lm.z])

#     return features, quality


# def predict(features):
#     features = np.array(features).reshape(1, -1)
#     prediction = model.predict(features)[0]
#     confidence = float(model.predict_proba(features).max())
#     label = label_encoder.inverse_transform([prediction])[0]
#     return label, confidence


# @app.post("/predict")
# async def predict_sign(file: UploadFile = File(...)):
#     start_time = time.time()

#     if not file.filename and file.size == 0:
#         return {"success": False, "message": "Empty file uploaded"}

#     image_bytes = await file.read()
#     if not image_bytes:
#         return {"success": False, "message": "No image data received"}

#     image_array = np.frombuffer(image_bytes, np.uint8)
#     image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

#     if image is None:
#         return {"success": False, "message": "Invalid image format"}

#     # 320×320 is sufficient for MediaPipe landmark detection
#     image = cv2.resize(image, (320, 320))
#     image = cv2.convertScaleAbs(image, alpha=1.2, beta=25)

#     if DEBUG_SAVE_IMAGES:
#         cv2.imwrite("uploaded_image.jpg", image)

#     result = extract_features(image)

#     if result is None:
#         return {"success": False, "message": "No hand detected"}

#     features, quality = result
#     label, confidence = predict(features)
#     feedback = generate_feedback(confidence)

#     processing_time = round((time.time() - start_time) * 1000, 2)

#     record = {
#         "prediction": label,
#         "confidence": round(confidence, 4),
#         "confidence_level": feedback["confidence_level"],
#         "status": feedback["status"],
#         "gesture_quality": quality["gesture_quality"],
#         "processing_time_ms": processing_time,
#     }
#     add_prediction(record)

#     return {
#         "success": True,
#         "prediction": label,
#         "confidence": round(confidence * 100, 2),
#         "confidence_level": feedback["confidence_level"],
#         "status": feedback["status"],
#         "feedback": feedback["feedback"],
#         "possible_issue": feedback["possible_issue"],
#         "processing_time_ms": processing_time,
#         "hand_position": quality["hand_position"],
#         "hand_distance": quality["hand_distance"],
#         "gesture_quality": quality["gesture_quality"],
#         "suggestion": quality["suggestion"],
#     }


# @app.get("/history")
# def history():
#     return {"total_predictions": len(get_history()), "history": get_history()}


# @app.delete("/history")
# def delete_history():
#     clear_history()
#     return {"message": "Prediction history cleared successfully."}


# @app.get("/analytics")
# def analytics():
#     return get_analytics()


# @app.get("/dashboard")
# def dashboard():
#     return get_dashboard()