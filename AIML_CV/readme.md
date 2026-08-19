# AI Sign Language Recognition System

## Overview

This project implements an AI-powered Sign Language Recognition system that detects hand gestures using MediaPipe and predicts sign language alphabets using an XGBoost Machine Learning model. The prediction service is exposed through FastAPI APIs for easy integration with the frontend.

---

## Features

- Real-time hand detection using MediaPipe
- 21 hand landmark extraction (63 features)
- XGBoost-based gesture classification
- FastAPI REST APIs
- Prediction confidence score
- Confidence level and feedback
- Prediction history
- Analytics dashboard
- Performance monitoring

---

## Technology Stack

- Python
- OpenCV
- MediaPipe
- NumPy
- Pandas
- Scikit-Learn
- XGBoost
- FastAPI
- Joblib

---

## Project Pipeline

1. Capture image/frame from webcam or uploaded image.
2. Detect hand using MediaPipe Hands.
3. Extract 21 hand landmarks.
4. Convert landmarks into a 63-dimensional feature vector.
5. Load the trained XGBoost model.
6. Predict the sign language gesture.
7. Generate confidence score and feedback.
8. Return the result through FastAPI.
9. Store prediction history and analytics.

---

## API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/predict` | Predict sign language gesture |
| GET | `/history` | View prediction history |
| DELETE | `/history` | Clear prediction history |
| GET | `/analytics` | View prediction analytics |
| GET | `/dashboard` | Dashboard summary |

---

## Project Structure

```
AIML_CV/
│
├── dataset/
├── models/
│   ├── xgboost_landmark.pkl
│   └── label_encoder.pkl
│
├── src/
│   ├── api.py
│   ├── detector.py
│   ├── feature_extractor.py
│   ├── predict.py
│   ├── feedback.py
│   ├── quality.py
│   └── test_model.py
│
├── requirements.txt
└── README.md
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Run the API

```bash
uvicorn src.api:app --reload --port 8001
```

---

## Model

- Algorithm: XGBoost Classifier
- Feature Extraction: MediaPipe Hands
- Input: 63 hand landmark features
- Output: Sign language gesture

---

## Current Status

- ✅ Feature extraction completed
- ✅ Model training completed
- ✅ FastAPI backend completed
- ✅ Prediction API completed
- ✅ Analytics module completed
- ✅ Testing completed
- 🔄 Frontend integration in progress