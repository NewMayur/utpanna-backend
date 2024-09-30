from flask import Flask, send_from_directory, jsonify
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from flask_cors import CORS
from datetime import timedelta
from models.models import db

import firebase_admin
from firebase_admin import credentials
import os
# from dotenv import load_dotenv

# load_dotenv()

# Initialize Firebase
cred_path = os.getenv('FIREBASE_ADMINSDK_PATH')
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

app = Flask(__name__, static_folder='templates/web', static_url_path='')

CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = os.getenv('JWT_ACCESS_TOKEN_EXPIRES')
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'

jwt = JWTManager(app)
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
# app.register_blueprint(auth)
app.register_blueprint(deal)

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Server is reachable"}), 200

# Serve Flutter web build files
# @app.route('/')
# @app.route('/web/')
# def serve_index():
#     return send_from_directory(app.static_folder, 'index.html')

# @app.route('/<path:path>')
# def serve_static(path):
#     if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
#         return send_from_directory(app.static_folder, path)
#     else:
#         return send_from_directory(app.static_folder, 'index.html')
with app.app_context():
        db.create_all()
        
if __name__ == '__main__':
    
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
