from fastapi import APIRouter
from uuid import UUID
from app.schemas.recommendation import RecommendationOut
from app.services.recommendation_service import get_recommendations

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{user_id}", response_model=RecommendationOut)
def get_user_recommendations(user_id: UUID):
    return get_recommendations(user_id)