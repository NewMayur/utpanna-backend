from flask import Blueprint, request, jsonify
from utils.auth_utils import firebase_token_required
from models.models import Deal, db
from flask_jwt_extended import jwt_required, get_jwt_identity

deal = Blueprint('deal', __name__)

@deal.route('/deals', methods=['GET'])
@firebase_token_required()
def get_deals():
    deals = Deal.query.all()
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
    deals = Deal.query.all()
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
    new_deal = Deal(
        title=data['title'],
        description=data['description'],
        price=data['price'],
        min_participants=data['min_participants']
    )
    db.session.add(new_deal)
    db.session.commit()
    return jsonify({"message": "Deal created successfully"}), 201

@deal.route('/deals/<int:deal_id>', methods=['GET'])
@firebase_token_required()
def get_deal(deal_id):
    deal = Deal.query.get(deal_id)
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
    deal = Deal.query.get(deal_id)
    if deal:
        data = request.get_json()
        deal.title = data.get('title', deal.title)
        deal.description = data.get('description', deal.description)
        deal.price = data.get('price', deal.price)
        deal.min_participants = data.get('min_participants', deal.min_participants)
        db.session.commit()
        return jsonify({"message": "Deal updated successfully"}), 200
    return jsonify({"message": "Deal not found"}), 404

@deal.route('/deals/<int:deal_id>', methods=['DELETE'])
@jwt_required()
def delete_deal(deal_id):
    deal = Deal.query.get(deal_id)
    if deal:
        db.session.delete(deal)
        db.session.commit()
        return jsonify({"message": "Deal deleted successfully"}), 200
    return jsonify({"message": "Deal not found"}), 404

@deal.route('/search', methods=['GET'])
@firebase_token_required()
def search_deals():
    query = request.args.get('query', '')
    # TODO: Implement search logic
    # This could involve querying the database for deals matching the search query
    return jsonify({"message": "Search functionality not yet implemented", "query": query}), 501