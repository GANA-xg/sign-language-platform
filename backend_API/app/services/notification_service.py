import uuid
from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(
    db: Session,
    user_id: uuid.UUID,
    notification_type: str,
    title: str,
    message: str,
    related_entity_type: str = None,
    related_entity_id: str = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def notify_badge_earned(db: Session, user_id: uuid.UUID, badge_id: int, badge_name: str):
    return create_notification(
        db=db, user_id=user_id, notification_type="badge_earned",
        title="New Badge Earned! 🏅",
        message=f"You just earned the '{badge_name}' badge. Keep it up!",
        related_entity_type="badge", related_entity_id=str(badge_id),
    )


def notify_streak_milestone(db: Session, user_id: uuid.UUID, streak_days: int):
    return create_notification(
        db=db, user_id=user_id, notification_type="streak_milestone",
        title=f"{streak_days}-Day Streak! 🔥",
        message=f"You've practiced {streak_days} days in a row. Don't break the chain!",
    )


def notify_certificate_ready(db: Session, user_id: uuid.UUID, certificate_id: uuid.UUID):
    return create_notification(
        db=db, user_id=user_id, notification_type="certificate_ready",
        title="Certificate Ready! 🎓",
        message="Your certificate is ready to download.",
        related_entity_type="certificate", related_entity_id=str(certificate_id),
    )


def notify_new_recommendation(db: Session, user_id: uuid.UUID, lesson_id: int, lesson_name: str):
    return create_notification(
        db=db, user_id=user_id, notification_type="new_recommendation",
        title="New Lesson Recommended",
        message=f"Based on your progress, we recommend practicing '{lesson_name}' next.",
        related_entity_type="lesson", related_entity_id=str(lesson_id),
    )