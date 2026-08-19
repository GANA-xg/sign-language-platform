import httpx

AI_SERVICE_URL = "http://127.0.0.1:8001/predict"  # confirm exact port with Abhinaya


def predict_sign(image_bytes: bytes, filename: str = "frame.jpg", content_type: str = "image/jpeg") -> dict:
    """
    Calls Abhinaya's real AI prediction service (MediaPipe + XGBoost).

    Input:
        image_bytes -> raw image bytes (webcam frame)
    Output:
        {"prediction": "A", "confidence": 0.97}
        or {"prediction": "No Hand Detected", "confidence": 0.0} if no hand found
        or {"prediction": "Service Unavailable", "confidence": 0.0} if her service is down
    """
    files = {"file": (filename, image_bytes, content_type)}

    try:
        response = httpx.post(AI_SERVICE_URL, files=files, timeout=15.0)
        response.raise_for_status()
        result = response.json()
    except httpx.HTTPError:
        return {"prediction": "Service Unavailable", "confidence": 0.0}

    if not result.get("success"):
        return {"prediction": "No Hand Detected", "confidence": 0.0}

    return {
        "prediction": result["prediction"],
        "confidence": result["confidence"]
    }