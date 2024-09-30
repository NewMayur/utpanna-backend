from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from firebase_admin import auth
from models.models import User, db

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
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # In a real application, you might want to blacklist the token here
    return jsonify({"message": "Successfully logged out"}), 200

@auth_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        return jsonify({
            "id": user.id,
            "phone_number": user.phone_number
        }), 200
    return jsonify({"error": "User not found"}), 404