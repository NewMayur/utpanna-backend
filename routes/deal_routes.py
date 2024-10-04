from flask import Blueprint, request, jsonify
from utils.auth_utils import firebase_token_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import DatabaseManager

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
            'created_at': deal.created_at,
            'updated_at': deal.updated_at
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
            'created_at': deal.created_at,
            'updated_at': deal.updated_at
        })
    return jsonify(deal_data), 200

@deal.route('/deals', methods=['POST'])
@jwt_required()
def create_deal():
    data = request.get_json()
    user_id = get_jwt_identity()
    new_deal = DatabaseManager.add_deal(
        title=data['title'],
        description=data['description'],
        price=data['price'],
        location=data.get('location', ''),
        user_id=user_id
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
            'created_at': deal.created_at,
            'updated_at': deal.updated_at
        }
        return jsonify(deal_data), 200
    return jsonify({"message": "Deal not found"}), 404

@deal.route('/deals/<int:deal_id>', methods=['PUT'])
@jwt_required()
def update_deal(deal_id):
    data = request.get_json()
    updated_deal = DatabaseManager.update_deal(
        deal_id=deal_id,
        title=data.get('title'),
        description=data.get('description'),
        price=data.get('price'),
        location=data.get('location')
    )
    if updated_deal:
        return jsonify({"message": "Deal updated successfully"}), 200
    return jsonify({"message": "Deal not found"}), 404

@deal.route('/deals/<int:deal_id>', methods=['DELETE'])
@jwt_required()
def delete_deal(deal_id):
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