from sqlalchemy import create_engine, inspect
from sqlalchemy_utils import database_exists, create_database
from models.models import Base
from utils.mysql_connector import connect_with_connector
import os
from dotenv import load_dotenv
import logging

load_dotenv()

def check_db_exists():
    # Add logging to check environment variables
    logging.info(f"DB_USER: {os.getenv('DB_USER')}")
    logging.info(f"DB_HOST: {os.getenv('DB_HOST')}")
    logging.info(f"DB_NAME: {os.getenv('DB_NAME')}")
    logging.info(f"INSTANCE_CONNECTION_NAME: {os.getenv('INSTANCE_CONNECTION_NAME')}")

    engine = connect_with_connector()
    
    # Log the engine URL to check if it's correctly configured
    logging.info(f"Engine URL: {engine.url}")

    try:
        if not database_exists(engine.url):
            create_database(engine.url)
            print(f"Database '{engine.url.database}' created.")
        else:
            print(f"Database '{engine.url.database}' already exists.")
    except Exception as e:
        logging.error(f"Error checking/creating database: {str(e)}")
        raise

    return engine

def create_tables(engine):
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if not existing_tables:
        Base.metadata.create_all(engine)
        print("Tables created successfully.")
    else:
        print("Tables already exist.")

def initialize_database():
    engine = check_db_exists()
    create_tables(engine)
    print("Database initialized and tables created.")