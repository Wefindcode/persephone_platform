from __future__ import annotations

from contextlib import contextmanager

from sqlmodel import Session, SQLModel, create_engine

from .models import run as run_model  # noqa: F401
from .models import user as user_model  # noqa: F401
from .repositories.users import UserRepository
from .settings import settings

engine = create_engine(settings.db_url, echo=False)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    from .services.security import hash_password  # Imported lazily to avoid cycles

    with Session(engine) as session:
        repo = UserRepository(session)
        if repo.get_by_email("admin@persephone.local") is None:
            repo.create(
                email="admin@persephone.local",
                password_hash=hash_password("admin"),
            )


@contextmanager
def session_scope() -> Session:
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


def get_session() -> Session:
    with session_scope() as session:
        yield session
