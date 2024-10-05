from flask import Flask, jsonify
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import firebase_admin
from firebase_admin import credentials
import os
import json
from utils.secrets import access_secret_version
from utils.mysql_connector import connect_with_connector
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging
from dotenv import load_dotenv
frpm 
load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the SQLAlchemy engine
engine = connect_with_connector()

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Initialize Firebase
project_id = os.getenv('PROJECT_ID')
cred_json = access_secret_version(project_id, 'FIREBASE_ADMINSDK_PATH')
cred = credentials.Certificate(json.loads(cred_json))
firebase_admin.initialize_app(cred)

# gac_id = os.getenv('GAC_ID')
GOOGLE_APPLICATION_CREDENTIALS = access_secret_version(project_id, 'GOOGLE_APPLICATION_CREDENTIALS')

app = Flask(__name__)
jwt = JWTManager(app)


app.config['JWT_SECRET_KEY'] = access_secret_version(project_id, 'JWT_SECRET_KEY')
app.config['CACHE_TYPE'] = 'simple'

cache = Cache(app)
CORS(app)

# Import models
from models.models import Base, User, Deal, Group, Order

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
            result = connection.execute("SELECT 1")
            return jsonify({"message": "Database connection successful", "result": result.fetchone()[0]}), 200
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {str(e)}")
        return jsonify({"message": "Database connection failed", "error": str(e)}), 500

# Create all tables
try:
    Base.metadata.create_all(engine)
    logger.info("Database tables created successfully")
except SQLAlchemyError as e:
    logger.error(f"Error creating database tables: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))