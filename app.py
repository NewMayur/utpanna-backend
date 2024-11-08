from flask import Flask, jsonify
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import firebase_admin
from firebase_admin import credentials
from google.cloud import storage
import os
import json
from utils.secrets_utils import access_secret_version
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import logging
from extensions import engine, Session
from dotenv import load_dotenv
from sqlalchemy import inspect
from models.models import Base

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Firebase
project_id = os.getenv('PROJECT_ID')
cred_json = access_secret_version(project_id, 'FIREBASE_ADMINSDK_PATH')
cred = credentials.Certificate(json.loads(cred_json))
firebase_admin.initialize_app(cred)

storage_client = storage.Client()

app = Flask(__name__)
jwt = JWTManager(app)

app.config['JWT_SECRET_KEY'] = access_secret_version(project_id, 'JWT_SECRET_KEY')
app.config['CACHE_TYPE'] = 'simple'

# Use the engine created by connect_with_connector()
app.config['SQLALCHEMY_DATABASE_URI'] = str(engine.url)
logger.info(f"Database URL: {engine.url}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.storage_client = storage_client
app.config['BUCKET_NAME'] = os.getenv('BUCKET_NAME')

logger.info(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")

cache = Cache(app)
CORS(app)

# Import and register blueprints
from routes.auth_routes import auth_bp
from routes.deal_routes import deal

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(deal)


@app.route('/test', methods=['GET'])
def test():
    env = os.getenv('ENV')
    return jsonify({"message": f"{env} server is reachable"}), 200

@app.route('/db-test', methods=['GET'])
def db_test():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return jsonify({"message": "Database connection successful", "result": result.fetchone()[0]}), 200
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {str(e)}")
        return jsonify({"message": "Database connection failed", "error": str(e)}), 500

@app.before_request
def create_session():
    Session()

@app.teardown_appcontext
def shutdown_session(exception=None):
    Session.remove()

def create_tables(engine):
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if not existing_tables:
        Base.metadata.create_all(engine)
        print("Tables created successfully.")
    else:
        print("Tables already exist.")

if __name__ == '__main__':
    logger.info("Starting the application...")
    create_tables(engine)
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 8080)))