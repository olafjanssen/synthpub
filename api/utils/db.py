from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from contextlib import contextmanager
from typing import Generator

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def init_db(app) -> None:
    """Initialize database and migrations."""
    db.init_app(app)
    Migrate(app, db)

@contextmanager
def db_session() -> Generator:
    """
    Context manager for database sessions.
    Automatically handles commit/rollback and session cleanup.
    """
    try:
        yield db.session
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    finally:
        db.session.close()

def create_tables(app) -> None:
    """Create all database tables."""
    with app.app_context():
        db.create_all()

def drop_tables(app) -> None:
    """Drop all database tables."""
    with app.app_context():
        db.drop_all()
