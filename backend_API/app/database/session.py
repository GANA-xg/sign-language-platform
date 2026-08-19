"""
Engine + session factory for the whole team to import.

Usage as a FastAPI dependency:

    from fastapi import Depends
    from app.database.session import get_db

    @router.get("/lessons")
    def list_lessons(db: Session = Depends(get_db)):
        return db.query(Lesson).all()
"""
import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:divya16@localhost:5432/sign_language_learning",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()