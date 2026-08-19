"""
Accessibility Trainer Dashboard — Pydantic Schemas (updated post Day 3)

AssignLearnerRequest and TrainerAssignmentOut removed — assignment is
now owned by Intern 2's service. Only analytics-facing schemas remain.
"""

from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional


class LearnerAnalyticsOut(BaseModel):
    learner_id: UUID
    sessions_this_week: int
    engagement_level: str            # "High" | "Medium" | "Low"
    avg_assessment_score: float
    skill_development_trend: Optional[float] = None
    certification_status: str        # "Certified" | "In Progress" | "Not Started"
    highest_certified_level: Optional[str] = None


class TrainerDashboardOut(BaseModel):
    trainer_id: UUID
    assigned_learners_count: int
    avg_sessions_per_week: float
    avg_assessment_score: float
    certified_count: int
    low_engagement_count: int
    learners: List[LearnerAnalyticsOut]