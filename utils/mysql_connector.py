import os
import pymysql
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes
from utils.secrets import access_secret_version
import logging

logger = logging.getLogger(__name__)

def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    instance_connection_name = os.getenv('INSTANCE_CONNECTION_NAME')
    db_user = os.getenv('DB_USER')
    project_id = os.getenv('PROJECT_ID')  # Make sure to add this to your .env file
    db_pass = access_secret_version(project_id, 'DB_PASS')
    db_name = os.getenv('DB_NAME')

    logger.info(f"Connecting to: {instance_connection_name}")
    logger.info(f"DB User: {db_user}")
    logger.info(f"DB Name: {db_name}")

    ip_type = IPTypes.PRIVATE if os.getenv("PRIVATE_IP") else IPTypes.PUBLIC
    connector = Connector(ip_type="public")

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        return conn

    return sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )