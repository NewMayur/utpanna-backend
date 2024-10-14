import os
import pymysql
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes
from utils.secrets import access_secret_version
import logging

logger = logging.getLogger(__name__)

def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    try:
        instance_connection_name = os.getenv('INSTANCE_CONNECTION_NAME')
        db_user = os.getenv('DB_USER')
        project_id = os.getenv('PROJECT_ID')
        db_pass_id = os.getenv('DB_PASS_ID')
        db_pass = access_secret_version(project_id, db_pass_id)
        db_name = os.getenv('DB_NAME')

        if not all([instance_connection_name, db_user, project_id, db_pass, db_name]):
            raise ValueError("Missing required environment variables for database connection")

        logger.info(f"Connecting to: {instance_connection_name}")
        logger.info(f"DB User: {db_user}")
        logger.info(f"DB Name: {db_name}")

        ip_type = IPTypes.PRIVATE if os.getenv("PRIVATE_IP") else IPTypes.PUBLIC
        connector = Connector(ip_type=ip_type)

        def getconn() -> pymysql.connections.Connection:
            conn: pymysql.connections.Connection = connector.connect(
                instance_connection_name,
                "pymysql",
                user=db_user,
                password=db_pass,
                db=db_name,
            )
            return conn

        engine = sqlalchemy.create_engine(
            "mysql+pymysql://",
            creator=getconn,
        )

        # Test the connection
        with engine.connect() as connection:
            connection.execute(sqlalchemy.text("SELECT 1"))
            logger.info("Database connection successful")

        return engine

    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise