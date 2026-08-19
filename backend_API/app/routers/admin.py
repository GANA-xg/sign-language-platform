import csv
import io

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.lesson import Lesson
from app.core.security import require_role
from app.schemas.admin_bulk import (
    BulkUserActionRequest, BulkUserActionResponse, BulkLessonUploadResult
)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users")
def list_all_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    users = db.query(User).all()
    return [
        {
            "user_id": u.user_id, "full_name": u.full_name, "email": u.email,
            "is_active": u.is_active,
            "roles": [ur.role.role_name for ur in u.user_roles],
        } for u in users
    ]


@router.patch("/users/{user_id}/status")
def toggle_user_status(
    user_id: str,
    is_active: bool,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = is_active
    db.commit()
    return {"message": f"User {'activated' if is_active else 'deactivated'}"}


@router.patch("/users/{user_id}/role")
def change_user_role(
    user_id: str,
    role_name: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    user = db.query(User).filter(User.user_id == user_id).first()
    role = db.query(Role).filter(Role.role_name == role_name).first()
    if not user or not role:
        raise HTTPException(status_code=404, detail="User or role not found")

    existing = db.query(UserRole).filter_by(user_id=user_id, role_id=role.role_id).first()
    if not existing:
        db.add(UserRole(user_id=user_id, role_id=role.role_id))
        db.commit()
    return {"message": f"Role '{role_name}' added to user"}


# ---------------------------------------------------------------------------
# Milestone 3 - Day 4: Bulk admin operations
# Admin-only (not instructor) — matches gating of other endpoints in this file
# ---------------------------------------------------------------------------

@router.post("/users/bulk-action", response_model=BulkUserActionResponse)
def bulk_user_action(
    payload: BulkUserActionRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    if payload.action not in ("activate", "deactivate"):
        raise HTTPException(status_code=400, detail="action must be 'activate' or 'deactivate'")

    new_status = payload.action == "activate"
    updated_count = 0
    failed_ids = []

    for user_id in payload.user_ids:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            failed_ids.append(user_id)
            continue
        user.is_active = new_status
        updated_count += 1

    db.commit()
    return BulkUserActionResponse(updated_count=updated_count, failed_ids=failed_ids)


@router.post("/lessons/bulk-upload", response_model=BulkLessonUploadResult)
async def bulk_upload_lessons(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    contents = await file.read()
    decoded = contents.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))

    created_count = 0
    failed_rows = []
    required_fields = {"module_id", "title", "sequence_order"}

    for i, row in enumerate(reader, start=1):
        if not required_fields.issubset(row.keys()):
            failed_rows.append({"row": i, "error": "Missing required fields", "data": row})
            continue
        try:
            lesson = Lesson(
                module_id=int(row["module_id"]),
                title=row["title"],
                description=row.get("description") or None,
                sequence_order=int(row["sequence_order"]),
                estimated_duration_minutes=int(row["estimated_duration_minutes"]) if row.get("estimated_duration_minutes") else None,
                difficulty_level=row.get("difficulty_level", "beginner"),
                is_published=row.get("is_published", "false").lower() == "true",
                category=row.get("category", "Alphabet"),
            )
            db.add(lesson)
            created_count += 1
        except Exception as e:
            failed_rows.append({"row": i, "error": str(e), "data": row})

    db.commit()
    return BulkLessonUploadResult(created_count=created_count, failed_rows=failed_rows)