"""Database configuration and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path

# Create database directory if it doesn't exist
DB_DIR = Path(__file__).parent / "data"
DB_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_DIR / 'app.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """Dependency for getting database session in routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables and apply any missing column migrations."""
    from sqlalchemy import text, inspect
    Base.metadata.create_all(bind=engine)

    # Migrate: add exam_time column to registrations if it doesn't exist
    with engine.connect() as conn:
        inspector = inspect(engine)
        existing_cols = [c["name"] for c in inspector.get_columns("registrations")]
        if "exam_time" not in existing_cols:
            conn.execute(text("ALTER TABLE registrations ADD COLUMN exam_time VARCHAR DEFAULT ''"))
            conn.commit()
        if "admit_card_sent" not in existing_cols:
            conn.execute(text("ALTER TABLE registrations ADD COLUMN admit_card_sent BOOLEAN DEFAULT 0 NOT NULL"))
            conn.commit()

    otp_cols = [c["name"] for c in inspector.get_columns("otp_codes")]
    with engine.connect() as conn:
        if "failed_attempts" not in otp_cols:
            conn.execute(text("ALTER TABLE otp_codes ADD COLUMN failed_attempts INTEGER DEFAULT 0 NOT NULL"))
            conn.commit()
