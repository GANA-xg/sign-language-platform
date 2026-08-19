from fastapi import APIRouter
from uuid import UUID
from app.schemas.analytics import AnalyticsOut, WeeklyAnalyticsOut
from app.services.analytics_service import compute_analytics, compute_weekly_analytics

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/{user_id}/weekly", response_model=WeeklyAnalyticsOut)
def get_weekly_analytics(user_id: UUID):
    return compute_weekly_analytics(user_id)


@router.get("/{user_id}", response_model=AnalyticsOut)
def get_analytics(user_id: UUID):
    return compute_analytics(user_id)
