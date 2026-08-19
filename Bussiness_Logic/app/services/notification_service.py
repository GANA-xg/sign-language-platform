import uuid
from uuid import UUID
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.schemas.notification import NotificationOut, NotificationListOut, NotificationType
from app.services.gamification_service import compute_gamification
from app.services.certificate_service import check_eligibility
from app.services.recommendation_service import get_recommendations

# Toggle to True once Intern 2's Notification API is live
USE_REAL_NOTIFICATION_API = False
INTERN2_NOTIFICATION_URL = "http://127.0.0.1:8000/notifications"

# In-memory store: user_id -> list of notifications
_notification_store: Dict[UUID, List[NotificationOut]] = {}


def _create_notification(
    user_id: UUID,
    notification_type: NotificationType,
    title: str,
    message: str,
) -> NotificationOut:
    notification = NotificationOut(
        notification_id=str(uuid.uuid4())[:8].upper(),
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        is_read=False,
        created_at=datetime.now(timezone.utc),
    )

    if USE_REAL_NOTIFICATION_API:
        # Forward to Intern 2's API when ready
        try:
            import httpx
            httpx.post(INTERN2_NOTIFICATION_URL, json={
                "user_id": str(user_id),
                "type": notification_type.value,
                "title": title,
                "message": message,
            }, timeout=5.0)
        except Exception:
            pass  # don't crash if her API is down — store locally as fallback

    # Always store locally too
    _notification_store.setdefault(user_id, []).append(notification)
    return notification


def _already_notified(user_id: UUID, notification_type: NotificationType, title: str) -> bool:
    """Avoid duplicate notifications for the same event."""
    existing = _notification_store.get(user_id, [])
    return any(
        n.notification_type == notification_type and n.title == title
        for n in existing
    )


def trigger_notifications(user_id: UUID) -> List[NotificationOut]:
    """
    Checks all key events for a user and creates notifications
    for any that haven't been notified yet.
    Call this after a practice session ends or an attempt is recorded.
    """
    created = []

    # ── 1. Badge earned notifications ────────────────────────────────
    gamification = compute_gamification(user_id)
    for badge in gamification.badges:
        if badge.earned:
            title = f"Badge Earned: {badge.name}"
            if not _already_notified(user_id, NotificationType.badge_earned, title):
                n = _create_notification(
                    user_id=user_id,
                    notification_type=NotificationType.badge_earned,
                    title=title,
                    message=f"Congratulations! You've earned the '{badge.name}' badge. {badge.description}",
                )
                created.append(n)

    # ── 2. Certificate eligible notification ─────────────────────────
    eligibility = check_eligibility(user_id)
    if eligibility.eligible:
        title = "Certificate Ready! 🎓"
        if not _already_notified(user_id, NotificationType.certificate_ready, title):
            n = _create_notification(
                user_id=user_id,
                notification_type=NotificationType.certificate_ready,
                title=title,
                message="You've met all the requirements! Go to the Reports page to download your certificate.",
            )
            created.append(n)

    # ── 3. New recommendation notification ───────────────────────────
    recs = get_recommendations(user_id)
    if recs.total_recommended > 0:
        title = "New Practice Recommendation"
        if not _already_notified(user_id, NotificationType.new_recommendation, title):
            signs = ", ".join(r.sign for r in recs.recommendations[:3])
            n = _create_notification(
                user_id=user_id,
                notification_type=NotificationType.new_recommendation,
                title=title,
                message=f"Based on your recent practice, we recommend focusing on: {signs}.",
            )
            created.append(n)

    return created


def get_notifications(user_id: UUID) -> NotificationListOut:
    notifications = _notification_store.get(user_id, [])
    unread = sum(1 for n in notifications if not n.is_read)
    return NotificationListOut(
        user_id=user_id,
        notifications=sorted(notifications, key=lambda n: n.created_at, reverse=True),
        unread_count=unread,
        total=len(notifications),
    )


def mark_all_read(user_id: UUID) -> NotificationListOut:
    notifications = _notification_store.get(user_id, [])
    for n in notifications:
        n.is_read = True
    return get_notifications(user_id)