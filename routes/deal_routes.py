from flask import Blueprint, request, jsonify, current_app
from utils.auth_utils import firebase_token_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import DatabaseManager
from firebase_admin import auth
from werkzeug.utils import secure_filename
import uuid
from extensions import Session

deal = Blueprint('deal', __name__)

@deal.route('/deals', methods=['GET'])
@firebase_token_required()
def get_deals():
    deals = DatabaseManager.get_all_deals()
    deal_data = []
    for deal in deals:
        images = DatabaseManager.get_deal_images(deal.id)
        image_urls = [image.image_url for image in images]
        deal_data.append({
            'id': deal.id,
            'title': deal.title,
            'description': deal.description,
            'price': deal.price,
            'min_participants': deal.min_participants,
            'current_participants': deal.current_participants,
            'status': deal.status,
            'images': image_urls,
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
            'updated_at': str(deal.updated_at),
            'progress_percentage': (deal.current_participants / deal.min_participants) * 100
        })
    return jsonify(deal_data), 200

@deal.route('/deals', methods=['POST'])
@jwt_required()
def create_deal():
    current_user = get_jwt_identity()
    # Verify it's an admin
    if not isinstance(current_user, dict) or current_user.get('type') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
        
    try:
        # Get deal data and images from form
        data = request.form
        images = request.files.getlist('images') if 'images' in request.files else []
        
        # First create the deal
        new_deal = DatabaseManager.add_deal(
            title=data['title'],
            description=data['description'],
            price=float(data['price']),
            user_id=current_user['id'],
            min_participants=int(data['min_participants'])
        )
        
        # If deal creation successful, handle images
        uploaded_images = []
        if images:
            # Call the existing add_deal_image function
            response = add_deal_image(new_deal.id)
            if response[1] == 201:  # If images uploaded successfully
                uploaded_images = response[0].get_json()['images']
        
        return jsonify({
            "message": "Deal created successfully", 
            "deal_id": new_deal.id,
            "images": uploaded_images
        }), 201
        
    except Exception as e:
        Session.rollback()
        return jsonify({"error": str(e)}), 500

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
    current_user = get_jwt_identity()
    # Verify it's an admin
    if not isinstance(current_user, dict) or current_user.get('type') != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
        
    if 'images' not in request.files:
        return jsonify({"error": "No images provided"}), 400
        
    images = request.files.getlist('images')
    
    if len(images) > 3:
        return jsonify({"error": "Maximum 3 images allowed"}), 400
        
    storage_client = current_app.storage_client
    bucket = storage_client.bucket(current_app.config['BUCKET_NAME'])
    
    uploaded_images = []
    
    try:
        for image in images:
            if image and allowed_file(image.filename):
                # Generate unique filename
                filename = secure_filename(image.filename)
                unique_filename = f"deals/{deal_id}/{str(uuid.uuid4())}_{filename}"
                
                # Upload to Cloud Storage
                blob = bucket.blob(unique_filename)
                blob.upload_from_string(
                    image.read(),
                    content_type=image.content_type
                )
                
                # Make the blob publicly readable
                blob.make_public()
                
                # Store image URL in database
                image_url = blob.public_url
                new_image = DatabaseManager.add_deal_image(deal_id, image_url)
                uploaded_images.append({
                    "id": new_image.id,
                    "url": image_url
                })
                
        return jsonify({
            "message": "Images uploaded successfully",
            "images": uploaded_images
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@deal.route('/deals/<int:deal_id>/images', methods=['GET'])
@firebase_token_required()
def get_deal_images(deal_id):
    try:
        images = DatabaseManager.get_deal_images(deal_id)
        image_data = [{
            "id": image.id,
            "url": image.image_url
        } for image in images]
        return jsonify(image_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        firebase_uid = decoded_token['user_id']
        
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
            
        # Check if user exists
        user = DatabaseManager.get_user_by_firebase_uid(decoded_token['user_id'])
        
        if user:
            # Update existing user
            user = DatabaseManager.update_user_details(
                firebase_uid=decoded_token['user_id'],
                name=data['name'],
                address=data['address']
            )
        else:
            # Create new user
            user = DatabaseManager.add_user(
                firebase_uid=decoded_token['user_id'],
                phone_number=decoded_token.get('phone_number'),
                name=data['name'],
                address=data['address']
            )
        
        return jsonify({
            "message": "Details updated successfully",
            "user": {
                "name": user.name,
                "address": user.address
            }
        }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@deal.route('/deals/<int:deal_id>/participants', methods=['GET'])
@jwt_required()
def get_deal_participants(deal_id):
    deal = DatabaseManager.get_deal(deal_id)
    if not deal:
        return jsonify({"error": "Deal not found"}), 404
        
    participants = []
    for participant in deal.participants:
        user = participant.user
        participants.append({
            'id': user.id,
            'name': user.name,
            'phone_number': user.phone_number,
            'address': user.address,
            'joined_at': str(participant.created_at)
        })
    
    return jsonify(participants), 200


@deal.route('/view-deal/<int:deal_id>', methods=['GET'])
@jwt_required()
def view_deal(deal_id):
    deal = DatabaseManager.get_deal(deal_id)
    if not deal:
        return jsonify({"message": "Deal not found"}), 404

    # Get participants
    participants = []
    for participant in deal.participants:
        user = participant.user
        participants.append({
            'id': user.id,
            'name': user.name,
            'phone_number': user.phone_number,
            'address': user.address,
            'joined_at': str(participant.created_at)
        })

    # Get images
    images = []
    for image in deal.images:
        images.append({
            'id': image.id,
            'image_url': image.image_url,
            'created_at': str(image.created_at)
        })

    deal_data = {
        'id': deal.id,
        'title': deal.title,
        'description': deal.description,
        'price': deal.price,
        'min_participants': deal.min_participants,
        'current_participants': deal.current_participants,
        'status': deal.status,
        'created_at': str(deal.created_at),
        'updated_at': str(deal.updated_at),
        'progress_percentage': (deal.current_participants / deal.min_participants) * 100,
        'participants': participants,
        'images': images
    }
    return jsonify(deal_data), 200