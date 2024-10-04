from flask import Flask, jsonify
from flask_caching import Cache
from flask_cors import CORS
from models.models import db
from flask_jwt_extended import JWTManager
import firebase_admin
from firebase_admin import credentials
import os, json

from utils.secrets import access_secret_version

# Initialize Firebase
project_id = os.getenv('PROJECT_ID') 
secret_id = os.getenv('SECRET_ID') 
cred_json = access_secret_version(project_id, secret_id)
cred = credentials.Certificate(json.loads(cred_json))
firebase_admin.initialize_app(cred)

# Retrieve JWT secret key
jwt_secret_id = os.getenv('JWT_SECRET_ID')

app = Flask(__name__)
jwt = JWTManager(app)

CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('MYSQL_DATABASE_URI')
app.config['JWT_SECRET_KEY'] = access_secret_version(project_id, jwt_secret_id)
print(app.config['JWT_SECRET_KEY'])
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'

db.init_app(app)

try:
    cache = Cache(app)
except ModuleNotFoundError:
    print("Redis module not found. Please install it using 'pip install redis'.")
    # Fallback to a simple in-memory cache
    app.config['CACHE_TYPE'] = 'simple'
    cache = Cache(app)

# Import and register blueprints
from routes.auth_routes import auth_bp
from routes.deal_routes import deal

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(deal)

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Server is reachable"}), 200

with app.app_context():
    db.create_all()
        
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
