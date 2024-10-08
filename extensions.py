import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from alembic.config import Config
from alembic import command
from utils.mysql_connector import connect_with_connector
import logging

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
engine = connect_with_connector()

# Create a scoped session
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def init_db(app):
    # Import all models here to ensure they are known to SQLAlchemy
    from models.models import Base

    # Create all tables
    with app.app_context():
        Base.metadata.create_all(bind=engine)

def init_migrations(app):
    # Set up Alembic configuration
    alembic_cfg = Config("migrations/alembic.ini")
    alembic_cfg.set_main_option("script_location", "migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", str(engine.url))

    # Check if the migrations directory exists
    if not os.path.exists("migrations"):
        logger.info("Creating migrations directory...")
        # Create the migrations directory if it doesn't exist
        command.init(alembic_cfg, "migrations")
    else:
        logger.info("Migrations directory already exists. Skipping creation.")

    try:
        # Generate an initial migration
        command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
    except Exception as e:
        logger.warning(f"Error generating initial migration: {str(e)}. This may be normal if migrations already exist.")

    try:
        # Apply the migration
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        logger.error(f"Error applying migration: {str(e)}")
        raise

def apply_migrations():
    alembic_cfg = Config("migrations/alembic.ini")
    command.upgrade(alembic_cfg, "head")