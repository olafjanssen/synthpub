from typing import Optional, List
from sqlalchemy import text
from .db import db, db_session

class DatabaseManager:
    @staticmethod
    def check_connection() -> bool:
        """Check if database connection is working."""
        try:
            db.session.execute(text('SELECT 1'))
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False

    @staticmethod
    def get_table_names() -> List[str]:
        """Get all table names in the database."""
        return db.engine.table_names()

    @staticmethod
    def get_table_count(table_name: str) -> Optional[int]:
        """Get the number of rows in a table."""
        try:
            result = db.session.execute(
                text(f'SELECT COUNT(*) FROM {table_name}')
            )
            return result.scalar()
        except Exception as e:
            print(f"Error counting rows in {table_name}: {e}")
            return None

    @staticmethod
    def vacuum_database() -> bool:
        """
        Cleanup and optimize the database.
        Note: Only works with SQLite
        """
        try:
            with db_session() as session:
                session.execute(text('VACUUM'))
            return True
        except Exception as e:
            print(f"Database vacuum failed: {e}")
            return False 