from fastapi import APIRouter, Query
from app.schemas.leaderboard import LeaderboardOut, RankBy
from app.services.leaderboard_service import compute_leaderboard

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("", response_model=LeaderboardOut)
def get_leaderboard(rank_by: RankBy = Query(default=RankBy.accuracy)):
    return compute_leaderboard(rank_by)