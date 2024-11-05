from functools import wraps
from flask import request, jsonify
from firebase_admin import auth
from flask_jwt_extended import get_jwt_identity, jwt_required

def firebase_token_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                token = request.headers['Authorization'].split(" ")[1]
            if not token:
                return jsonify({'message': 'Token is missing!'}), 401
            try:
                decoded_token = auth.verify_id_token(token)
                # You can access user info like this:
                # user_id = decoded_token['uid']
            except:
                return jsonify({'message': 'Token is invalid!'}), 401
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def admin_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            current_user = get_jwt_identity()
            if not isinstance(current_user, dict) or current_user.get('type') != 'admin':
                return jsonify({"error": "Admin access required"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper