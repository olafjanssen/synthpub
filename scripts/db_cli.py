import click
import os
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from api import create_app
from api.utils.db import db, create_tables, drop_tables
from api.utils.db_manager import DatabaseManager

app = create_app()

@click.group()
def cli():
    """Database management commands."""
    pass

@cli.command()
def init():
    """Initialize the database."""
    with app.app_context():
        create_tables(app)
    click.echo("Database initialized successfully!")

@cli.command()
def drop():
    """Drop all database tables."""
    if click.confirm("Are you sure you want to drop all tables?"):
        with app.app_context():
            drop_tables(app)
        click.echo("Database tables dropped successfully!")

@cli.command()
def status():
    """Check database status."""
    with app.app_context():
        manager = DatabaseManager()
        
        # Check connection
        if manager.check_connection():
            click.echo("Database connection: OK")
        else:
            click.echo("Database connection: FAILED")
            return

        # Show tables and their row counts
        tables = manager.get_table_names()
        click.echo("\nDatabase tables:")
        for table in tables:
            count = manager.get_table_count(table)
            click.echo(f"- {table}: {count} rows")

@cli.command()
def optimize():
    """Optimize the database."""
    with app.app_context():
        manager = DatabaseManager()
        if manager.vacuum_database():
            click.echo("Database optimized successfully!")
        else:
            click.echo("Database optimization failed!")

if __name__ == '__main__':
    cli() 