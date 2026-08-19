from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.lesson import Lesson
from app.schemas.course import LessonCreate, LessonResponse
from app.core.security import require_role

router = APIRouter(prefix="/courses", tags=["Courses"])


class CourseSummary(BaseModel):
    id: int
    title: str
    description: str | None = None
    difficulty: str
    category: str
    lessons: int = 0


@router.get("", response_model=list[CourseSummary])
def list_courses(db: Session = Depends(get_db)):
    """Group published lessons by module_id into course-like summaries."""
    lessons = (
        db.query(Lesson)
        .filter(Lesson.is_published.is_(True))
        .order_by(Lesson.module_id, Lesson.sequence_order)
        .all()
    )

    modules: dict[int, list[Lesson]] = {}
    for l in lessons:
        modules.setdefault(l.module_id, []).append(l)

    courses = []
    for module_id, module_lessons in sorted(modules.items()):
        first = module_lessons[0]
        courses.append(
            CourseSummary(
                id=module_id,
                title=f"Module {module_id}",
                description=first.description,
                difficulty=first.difficulty_level,
                category=first.category,
                lessons=len(module_lessons),
            )
        )
    return courses


@router.get(
    "/{course_id}",
    response_model=CourseSummary,
    summary="Get a course (module) by ID",
)
def get_course(course_id: int, db: Session = Depends(get_db)):
    lessons = (
        db.query(Lesson)
        .filter(Lesson.module_id == course_id, Lesson.is_published.is_(True))
        .order_by(Lesson.sequence_order)
        .all()
    )
    if not lessons:
        raise HTTPException(status_code=404, detail="Course not found")
    first = lessons[0]
    return CourseSummary(
        id=course_id,
        title=f"Module {course_id}",
        description=first.description,
        difficulty=first.difficulty_level,
        category=first.category,
        lessons=len(lessons),
    )


@router.get("/lessons", response_model=list[LessonResponse])
def list_lessons(
    module_id: int | None = None,
    category: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    query = db.query(Lesson).filter(Lesson.is_published.is_(True))
    if module_id:
        query = query.filter(Lesson.module_id == module_id)
    if category:
        query = query.filter(Lesson.category == category)
    if search:
        query = query.filter(Lesson.title.ilike(f"%{search}%"))
    offset = (page - 1) * page_size
    return query.order_by(Lesson.sequence_order).offset(offset).limit(page_size).all()


@router.get(
    "/lessons/{lesson_id}",
    response_model=LessonResponse,
    summary="Get a single lesson by ID",
)
def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.post(
    "/lessons",
    response_model=LessonResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new lesson (admin/instructor only)",
)
def create_lesson(
    payload: LessonCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("admin", "instructor")),
):
    lesson = Lesson(**payload.model_dump())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


@router.delete(
    "/lessons/{lesson_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a lesson (admin only)",
)
def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("admin")),
):
    lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    db.delete(lesson)
    db.commit()

@router.put(
    "/lessons/{lesson_id}",
    response_model=LessonResponse,
    summary="Update a lesson (admin/instructor only)",
)
def update_lesson(
    lesson_id: int,
    payload: LessonCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_role("admin", "instructor")),
):
    lesson = db.query(Lesson).filter(Lesson.lesson_id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    for field, value in payload.model_dump().items():
        setattr(lesson, field, value)

    db.commit()
    db.refresh(lesson)
    return lesson