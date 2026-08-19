"""
Shared declarative base for every ORM model in the project.

All model modules import `Base` from here and register themselves on
`Base.metadata`. `app/models/__init__.py` imports every model module so
that Alembic's `--autogenerate` (and `Base.metadata.create_all`) can see
the full set of tables in one place.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass