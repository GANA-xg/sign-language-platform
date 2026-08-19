from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.instructor_student import InstructorStudent
from app.models.user import User
from app.core.security import get_current_user, get_user_roles


router = APIRouter(
    prefix="/trainer",
    tags=["Trainer"],
)


def verify_trainer_access(
    trainer_id: UUID,
    current_user: User,
) -> None:
    """
    Trainer or instructor can access their own learners.
    Admin can access any trainer.
    """

    roles = get_user_roles(current_user)

    if "admin" in roles:
        return

    if "trainer" not in roles and "instructor" not in roles:
        raise HTTPException(
            status_code=403,
            detail="Only trainers, instructors, or admins can access trainer data",
        )

    if current_user.user_id != trainer_id:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own trainer data",
        )


@router.get("/{trainer_id}/learners")
def get_trainer_learners(
    trainer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return learner IDs assigned to this trainer.

    The existing instructor_students table is reused because it already
    stores the relationship:

        instructor_id -> learner_id

    For trainer accounts, instructor_id contains the trainer's user_id.
    """

    verify_trainer_access(
        trainer_id,
        current_user,
    )

    assignments = (
        db.query(InstructorStudent)
        .filter(
            InstructorStudent.instructor_id == trainer_id,
            InstructorStudent.status == "active",
        )
        .all()
    )

    return [
        str(assignment.learner_id)
        for assignment in assignments
    ]


@router.get("/{trainer_id}/learners/details")
def get_trainer_learner_details(
    trainer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return full learner information for the trainer dashboard.
    """

    verify_trainer_access(
        trainer_id,
        current_user,
    )

    learner_ids = (
        db.query(InstructorStudent.learner_id)
        .filter(
            InstructorStudent.instructor_id == trainer_id,
            InstructorStudent.status == "active",
        )
        .all()
    )

    ids = [
        row[0]
        for row in learner_ids
    ]

    if not ids:
        return []

    learners = (
        db.query(User)
        .filter(
            User.user_id.in_(ids),
            User.is_active.is_(True),
        )
        .all()
    )

    return [
        {
            "user_id": str(learner.user_id),
            "full_name": learner.full_name,
            "email": learner.email,
        }
        for learner in learners
    ]


@router.post("/assign-student/{learner_id}")
def assign_student_to_trainer(
    learner_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Assign a learner to the currently logged-in trainer.
    """

    roles = get_user_roles(current_user)

    if "trainer" not in roles and "admin" not in roles:
        raise HTTPException(
            status_code=403,
            detail="Only trainers or admins can assign learners",
        )

    learner = (
        db.query(User)
        .filter(
            User.user_id == learner_id,
            User.is_active.is_(True),
        )
        .first()
    )

    if not learner:
        raise HTTPException(
            status_code=404,
            detail="Learner not found",
        )

    existing = (
        db.query(InstructorStudent)
        .filter(
            InstructorStudent.instructor_id
            == current_user.user_id,
            InstructorStudent.learner_id
            == learner_id,
        )
        .first()
    )

    if existing:
        if existing.status != "active":
            existing.status = "active"
            db.commit()

        return {
            "message": "Student assigned",
            "trainer_id": str(
                current_user.user_id
            ),
            "learner_id": str(
                learner_id
            ),
        }

    assignment = InstructorStudent(
        instructor_id=current_user.user_id,
        learner_id=learner_id,
        status="active",
    )

    db.add(assignment)
    db.commit()

    return {
        "message": "Student assigned",
        "trainer_id": str(
            current_user.user_id
        ),
        "learner_id": str(
            learner_id
        ),
    }


@router.delete(
    "/{trainer_id}/learners/{learner_id}"
)
def remove_student_from_trainer(
    trainer_id: UUID,
    learner_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Remove a learner from a trainer.
    """

    verify_trainer_access(
        trainer_id,
        current_user,
    )

    assignment = (
        db.query(InstructorStudent)
        .filter(
            InstructorStudent.instructor_id
            == trainer_id,
            InstructorStudent.learner_id
            == learner_id,
            InstructorStudent.status == "active",
        )
        .first()
    )

    if not assignment:
        raise HTTPException(
            status_code=404,
            detail="Learner is not assigned to this trainer",
        )

    assignment.status = "inactive"

    db.commit()

    return {
        "message": "Student removed",
        "trainer_id": str(trainer_id),
        "learner_id": str(learner_id),
    }