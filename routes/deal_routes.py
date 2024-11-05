from flask import Blueprint, request, jsonify
from utils.auth_utils import firebase_token_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import DatabaseManager
from firebase_admin import auth

deal = Blueprint('deal', __name__)

@deal.route('/deals', methods=['GET'])
@firebase_token_required()
def get_deals():
    deals = DatabaseManager.get_all_deals()
    deal_data = []
    for deal in deals:
        deal_data.append({
            'id': deal.id,
            'title': deal.title,
            'description': deal.description,
            'price': deal.price,
            'min_participants': deal.min_participants,
            'current_participants': deal.current_participants,
            'status': deal.status,
            'created_at': str(deal.created_at),
            'updated_at': str(deal.updated_at)
        })
    return jsonify(deal_data), 200

@deal.route('/deal-list', methods=['GET'])
@jwt_required()
def get_deal_list():
    deals = DatabaseManager.get_all_deals()
    deal_data = []
    for deal in deals:
        deal_data.append({
            'id': deal.id,
            'title': deal.title,
            'description': deal.description,
            'price': deal.price,
            'min_participants': deal.min_participants,
            'current_participants': deal.current_participants,
            'status': deal.status,
            'created_at': str(deal.created_at),
            'updated_at': str(deal.updated_at)
        })
    return jsonify(deal_data), 200

@deal.route('/deals', methods=['POST'])
@jwt_required()
def create_deal():
    current_user = get_jwt_identity()
    # Verify it's an admin
    if not isinstance(current_user, dict) or current_user.get('type') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
        
    data = request.get_json()
    new_deal = DatabaseManager.add_deal(
        title=data['title'],
        description=data['description'],
        price=data['price'],
        user_id=current_user['id'],
        min_participants=data['min_participants']
    )
    return jsonify({"message": "Deal created successfully", "deal_id": new_deal.id}), 201

@deal.route('/deals/<int:deal_id>', methods=['GET'])
@firebase_token_required()
def get_deal(deal_id):
    deal = DatabaseManager.get_deal(deal_id)
    if deal:
        deal_data = {
            'id': deal.id,
            'title': deal.title,
            'description': deal.description,
            'price': deal.price,
            'min_participants': deal.min_participants,
            'current_participants': deal.current_participants,
            'status': deal.status,
            'created_at': str(deal.created_at),
            'updated_at': str(deal.updated_at)
        }
        return jsonify(deal_data), 200
    return jsonify({"message": "Deal not found"}), 404

@deal.route('/deals/<int:deal_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_deal(deal_id):
    current_user = get_jwt_identity()
    # Verify it's an admin
    if not isinstance(current_user, dict) or current_user.get('type') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    if request.method == 'PUT':
        data = request.get_json()
        updated_deal = DatabaseManager.update_deal(
            deal_id=deal_id,
            title=data.get('title'),
            description=data.get('description'),
            price=data.get('price'),
        )
        if updated_deal:
            return jsonify({"message": "Deal updated successfully"}), 200
        return jsonify({"message": "Deal not found"}), 404
        
    elif request.method == 'DELETE':
        if DatabaseManager.delete_deal(deal_id):
            return jsonify({"message": "Deal deleted successfully"}), 200
        return jsonify({"message": "Deal not found"}), 404

@deal.route('/search', methods=['GET'])
@firebase_token_required()
def search_deals():
    query = request.args.get('query', '')
    # TODO: Implement search logic in DatabaseManager
    # This could involve querying the database for deals matching the search query
    return jsonify({"message": "Search functionality not yet implemented", "query": query}), 501

@deal.route('/deals/<int:deal_id>/images', methods=['POST'])
@jwt_required()
def add_deal_image(deal_id):
    data = request.get_json()
    image_url = data.get('image_url')
    if not image_url:
        return jsonify({"message": "Image URL is required"}), 400
    
    new_image = DatabaseManager.add_deal_image(deal_id, image_url)
    if new_image:
        return jsonify({"message": "Image added successfully", "image_id": new_image.id}), 201
    return jsonify({"message": "Failed to add image"}), 400

@deal.route('/deals/<int:deal_id>/images', methods=['GET'])
@firebase_token_required()
def get_deal_images(deal_id):
    images = DatabaseManager.get_deal_images(deal_id)
    image_data = [{"id": image.id, "image_url": image.image_url} for image in images]
    return jsonify(image_data), 200

@deal.route('/deals/images/<int:image_id>', methods=['DELETE'])
@jwt_required()
def delete_deal_image(image_id):
    if DatabaseManager.delete_deal_image(image_id):
        return jsonify({"message": "Image deleted successfully"}), 200
    return jsonify({"message": "Image not found"}), 404


@deal.route('/deals/<int:deal_id>/participate', methods=['POST'])
@firebase_token_required()
def participate_in_deal(deal_id):
    try:
        token = request.headers['Authorization'].split(" ")[1]
        decoded_token = auth.verify_id_token(token)
        firebase_uid = decoded_token['uid']
        
        user = DatabaseManager.get_user_by_firebase_uid(firebase_uid)
        if not user.name or not user.address:
            return jsonify({
                "error": "User details required",
                "code": "DETAILS_REQUIRED"
            }), 400
            
        participant, error = DatabaseManager.add_participant(deal_id, firebase_uid)
        if error:
            return jsonify({"error": error}), 400
            
        return jsonify({
            "message": "Successfully participated in deal",
            "deal_id": deal_id
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@deal.route('/user/details', methods=['POST'])
@firebase_token_required()
def update_user_details():
    try:
        data = request.get_json()
        token = request.headers['Authorization'].split(" ")[1]
        decoded_token = auth.verify_id_token(token)
        
        if not data.get('name') or not data.get('address'):
            return jsonify({"error": "Name and address are required"}), 400
            
        user = DatabaseManager.update_user_details(
            firebase_uid=decoded_token['user_id'],
            name=data['name'],
            address=data['address']
        )
        
        if user:
            return jsonify({
                "message": "Details updated successfully",
                "user": {
                    "name": user.name,
                    "address": user.address
                }
            }), 200
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400