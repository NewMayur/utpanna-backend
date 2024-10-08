from flask import Flask, jsonify
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import firebase_admin
from firebase_admin import credentials
import os
import json
from utils.secrets import access_secret_version
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import logging
from extensions import engine, Session
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Firebase
project_id = os.getenv('PROJECT_ID')
cred_json = access_secret_version(project_id, 'FIREBASE_ADMINSDK_PATH')
cred = credentials.Certificate(json.loads(cred_json))

GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

app = Flask(__name__)
jwt = JWTManager(app)

app.config['JWT_SECRET_KEY'] = access_secret_version(project_id, 'JWT_SECRET_KEY')
app.config['CACHE_TYPE'] = 'simple'

# Use the engine created by connect_with_connector()
app.config['SQLALCHEMY_DATABASE_URI'] = engine.url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    return jsonify({"message": "Server is reachable"}), 200

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

def test_db_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info(f"Initial database connection test successful: {result.fetchone()[0]}")
    except SQLAlchemyError as e:
        logger.error(f"Initial database connection test failed: {str(e)}")
        raise

if __name__ == '__main__':
    logger.info("Starting the application...")
    test_db_connection()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))