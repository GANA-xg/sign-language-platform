"""
Accessibility Trainer-Learner Assignment — Data Model (STUB)

Standing in for the real trainer-learner mapping table that Intern 5 is
building (per M4 SRS, Intern 5 Day 2). Kept here so Trainer analytics
(this file's consumer, trainer_analytics_service.py) isn't blocked
waiting on the DB team — same "swap for real DB later" pattern as every
other model in this service.

TODO (Intern 5 DB integration): Replace with a real SQLAlchemy model
once the trainer-learner mapping table lands.
"""

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class TrainerAssignment:
    trainer_id: UUID
    learner_id: UUID
    assigned_at: datetime