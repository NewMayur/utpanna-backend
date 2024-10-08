from flask.cli import FlaskGroup
from app import app
from extensions import init_db, init_migrations, apply_migrations
from models.models import Base, User, Deal, Group, Order

cli = FlaskGroup(app)

@cli.command("init_db")
def init_db_command():
    """Initialize the database."""
    init_db(app)
    print("Initialized the database.")

@cli.command("init_migrations")
def init_migrations_command():
    """Initialize migrations."""
    init_migrations(app)
    print("Initialized migrations.")

@cli.command("apply_migrations")
def apply_migrations_command():
    """Apply migrations."""
    apply_migrations()
    print("Applied migrations.")

if __name__ == "__main__":
    cli()