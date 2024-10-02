from flask import Blueprint, request, jsonify
from firebase_admin import auth
from models.models import User, db
from utils.auth_utils import firebase_token_required
from flask_jwt_extended import create_access_token, jwt_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/send_otp', methods=['POST'])
def send_otp():
    phone_number = request.json.get('phone_number')
    try:
        verification_id = auth.create_user()
        
        return jsonify({"verification_id": verification_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    verification_id = request.json.get('verification_id')
    otp = request.json.get('otp')
    try:
        decoded_token = auth.verify_id_token(verification_id)
        user_id = decoded_token['uid']
        user = User.query.filter_by(firebase_uid=user_id).first()
        if not user:
            user = User(firebase_uid=user_id, phone_number=decoded_token['phone_number'])
            db.session.add(user)
            db.session.commit()
        return jsonify({"message": "Successfully authenticated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify({"message": "Invalid username or password"}), 401

@auth_bp.route('/logout', methods=['POST'])
@firebase_token_required()
def logout():
    # Firebase handles token revocation on the client-side
    return jsonify({"message": "Successfully logged out"}), 200

@auth_bp.route('/user', methods=['GET'])
@firebase_token_required()
def get_user():
    # The user's Firebase UID will be available in the decoded token
    # You can access it in the request context if needed
    try:
        token = request.headers['Authorization'].split(" ")[1]
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token['uid']
        user = User.query.filter_by(firebase_uid=user_id).first()
        if user:
            return jsonify({
                "id": user.id,
                "phone_number": user.phone_number
            }), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 401