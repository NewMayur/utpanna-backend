from flask import Blueprint, request, jsonify
from firebase_admin import auth
from requests import Session
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
        user_id = decoded_token['user_id']
        user = DatabaseManager.get_user_by_firebase_uid(user_id)
        if not user:
            # Create new user with just firebase_uid and phone_number
            user = DatabaseManager.add_user(
                firebase_uid=user_id,
                phone_number=decoded_token['phone_number']
            )
        return jsonify({
            "message": "Successfully authenticated",}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# @auth_bp.route('/user/details', methods=['GET'])
# @firebase_token_required()
# def get_user_details():
#     try:
#         token = request.headers['Authorization'].split(" ")[1]
#         decoded_token = auth.verify_id_token(token)
#         user = DatabaseManager.get_user_by_firebase_uid(decoded_token['uid'])
#         if user:
#             return jsonify({
#                 "name": user.name,
#                 "address": user.address,
#                 "phone_number": user.phone_number
#             }), 200
#         return jsonify({"error": "User not found"}), 404
#     except Exception as e:
#         return jsonify({"error": str(e)}), 401

# @auth_bp.route('/user/details', methods=['POST'])
# @firebase_token_required()
# def update_user_details():
#     try:
#         data = request.get_json()
#         token = request.headers['Authorization'].split(" ")[1]
#         decoded_token = auth.verify_id_token(token)
        
#         user = DatabaseManager.get_user_by_firebase_uid(decoded_token['uid'])
#         if user:
#             user.name = data.get('name')
#             user.address = data.get('address')
#             Session.commit()
#             return jsonify({
#                 "message": "Details updated successfully",
#                 "user": {
#                     "name": user.name,
#                     "address": user.address
#                 }
#             }), 200
#         return jsonify({"error": "User not found"}), 404
#     except Exception as e:
#         Session.rollback()
#         return jsonify({"error": str(e)}), 400

@auth_bp.route('/admin/register', methods=['POST'])
def admin_register():
    data = request.get_json()
    try:
        new_admin = DatabaseManager.add_admin(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        return jsonify({"message": "Admin created successfully", "admin_id": new_admin.id}), 201
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    try:
        admin = DatabaseManager.get_admin_by_username(data['username'])
        if admin and admin.check_password(data['password']):
            access_token = create_access_token(identity={'id': admin.id, 'type': 'admin'})
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

@auth_bp.route('/user/details', methods=['GET'])
@firebase_token_required()
def get_user_details():
    try:
        token = request.headers['Authorization'].split(" ")[1]
        decoded_token = auth.verify_id_token(token)
        user = DatabaseManager.get_user_by_firebase_uid(decoded_token['uid'])
        if user:
            return jsonify({
                "name": user.name,
                "address": user.address
            }), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 401

# @auth_bp.route('/user/details', methods=['POST'])
# @firebase_token_required()
# def update_user_details():
#     try:
#         data = request.get_json()
#         token = request.headers['Authorization'].split(" ")[1]
#         decoded_token = auth.verify_id_token(token)
        
#         if not data.get('name') or not data.get('address'):
#             return jsonify({"error": "Name and address are required"}), 400
            
#         user = DatabaseManager.get_user_by_firebase_uid(decoded_token['uid'])
#         if user:
#             user.name = data['name']
#             user.address = data['address']
#             Session.commit()
#             return jsonify({
#                 "message": "Details updated successfully",
#                 "user": {
#                     "name": user.name,
#                     "address": user.address
#                 }
#             }), 200
#         return jsonify({"error": "User not found"}), 404
#     except Exception as e:
#         Session.rollback()
#         return jsonify({"error": str(e)}), 400