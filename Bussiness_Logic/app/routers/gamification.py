from fastapi import APIRouter
from uuid import UUID
from app.schemas.gamification import GamificationOut
from app.services.gamification_service import compute_gamification

router = APIRouter(prefix="/gamification", tags=["gamification"])


@router.get("/{user_id}", response_model=GamificationOut)
def get_gamification(user_id: UUID):
    return compute_gamification(user_id)