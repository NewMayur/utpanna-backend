from flask import Blueprint, request, jsonify
from firebase_admin import auth
from models.models import User
from utils.auth_utils import firebase_token_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from database import DatabaseManager
from sqlalchemy.exc import SQLAlchemyError

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
        user = DatabaseManager.get_user_by_firebase_uid(user_id)
        if not user:
            user = DatabaseManager.add_user(
                username=None,
                email=None,
                password=None,
                firebase_uid=user_id,
                phone_number=decoded_token['phone_number']
            )
        return jsonify({"message": "Successfully authenticated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        new_user = DatabaseManager.add_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        return jsonify({"message": "User created successfully", "user_id": new_user.id}), 201
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    try:
        user = DatabaseManager.get_user_by_username(data['username'])
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user.id)
            return jsonify(access_token=access_token, token_type="Bearer"), 200
        return jsonify({"message": "Invalid username or password"}), 401
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    return jsonify(logged_in_as=current_user_id), 200

@auth_bp.route('/logout', methods=['POST'])
@firebase_token_required()
def logout():
    # Firebase handles token revocation on the client-side
    return jsonify({"message": "Successfully logged out"}), 200

@auth_bp.route('/user', methods=['GET'])
@firebase_token_required()
def get_user():
    try:
        token = request.headers['Authorization'].split(" ")[1]
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token['uid']
        user = DatabaseManager.get_user_by_firebase_uid(user_id)
        if user:
            return jsonify({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number
            }), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 401