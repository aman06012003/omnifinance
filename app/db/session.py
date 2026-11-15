"""Database session and initialization."""
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

# SQLite connection args for thread safety
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
engine = create_engine(settings.DATABASE_URL, echo=False, connect_args=connect_args)

def init_db() -> None:
    """Create tables if they don't exist."""
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """Dependency for yielding database sessions."""
    with Session(engine) as session:
        yield session
