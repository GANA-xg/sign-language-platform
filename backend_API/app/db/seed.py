"""Run: python -m app.db.seed"""
from app.database.session import SessionLocal
from app.models.role import Role
from app.models.sign_language import SignLanguage
from app.models.module import Module
from app.models.lesson import Lesson

def seed():
    db = SessionLocal()
    try:
        # 1. Roles
        for role_name in ["learner", "instructor", "trainer", "admin"]:
            if not db.query(Role).filter(Role.role_name == role_name).first():
                db.add(Role(role_name=role_name))
        db.commit()

        # 2. Sign language
        asl = db.query(SignLanguage).filter(SignLanguage.code == "ASL").first()
        if not asl:
            asl = SignLanguage(code="ASL", name="American Sign Language", is_active=True)
            db.add(asl)
            db.commit()
            db.refresh(asl)

        # 3. Module
        module = db.query(Module).filter(
            Module.sign_language_id == asl.sign_language_id,
            Module.title == "Alphabet",
        ).first()
        if not module:
            module = Module(
                sign_language_id=asl.sign_language_id,
                title="Alphabet",
                description="Learn the ASL alphabet A-Z",
                difficulty_level="beginner",
                sequence_order=1,
                is_published=True,
            )
            db.add(module)
            db.commit()
            db.refresh(module)

        # 4. Lessons A-Z
        for i, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ", start=1):
            exists = db.query(Lesson).filter(
                Lesson.module_id == module.module_id,
                Lesson.title == f"Letter {letter}",
            ).first()
            if not exists:
                db.add(Lesson(
                    module_id=module.module_id,
                    title=f"Letter {letter}",
                    description=f"Learn to sign the letter {letter}",
                    sequence_order=i,
                    difficulty_level="beginner",
                    is_published=True,
                ))
        db.commit()
        print("Seed complete: roles + ASL Alphabet module + 26 lessons")
    finally:
        db.close()

if __name__ == "__main__":
    seed()