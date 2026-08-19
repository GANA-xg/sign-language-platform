import httpx
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.security import HTTPAuthorizationCredentials
from app.core.security import oauth2_scheme, decode_token

router = APIRouter(prefix="/predict", tags=["Prediction"])

AI_SERVICE_URL = "http://127.0.0.1:8001/predict"


@router.post("/")
async def predict(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
):
    payload = decode_token(credentials.credentials)

    file_bytes = await file.read()
    files = {"file": (file.filename, file_bytes, file.content_type)}

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.post(AI_SERVICE_URL, files=files)
            response.raise_for_status()
            result = response.json()
        except httpx.HTTPError:
            return {
                "status": "error",
                "message": "AI prediction service unavailable"
            }

    if not result.get("success"):
        return {
            "status": "no_prediction",
            "user": payload["sub"],
            "message": result.get("message", "Prediction failed")
        }

    return {
        "status": "success",
        "user": payload["sub"],
        "prediction": result["prediction"],
        "confidence": result["confidence"]
    }