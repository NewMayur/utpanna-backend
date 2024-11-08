from models.models import Admin, DealParticipant, User, Deal, DealImage
from sqlalchemy.exc import SQLAlchemyError
from extensions import Session

class DatabaseManager:
    @staticmethod
    def add_user(firebase_uid, phone_number=None, name=None, address=None):
        try:
            new_user = User(
                firebase_uid=firebase_uid,
                phone_number=phone_number,
                name=name,
                address=address
            )
            Session.add(new_user)
            Session.commit()
            return new_user
        except SQLAlchemyError as e:
            Session.rollback()
            raise e

    @staticmethod
    def add_admin(username, email, password):
        try:
            new_admin = Admin(username=username, email=email)
            new_admin.set_password(password)
            Session.add(new_admin)
            Session.commit()
            return new_admin
        except SQLAlchemyError as e:
            Session.rollback()
            raise e

    @staticmethod
    def get_admin_by_username(username):
        return Session.query(Admin).filter_by(username=username).first()

    @staticmethod
    def get_admin_by_email(email):
        return Session.query(Admin).filter_by(email=email).first()

    @staticmethod
    def get_user_by_firebase_uid(firebase_uid):
        return Session.query(User).filter_by(firebase_uid=firebase_uid).first()
    
    @staticmethod
    def update_user_details(firebase_uid, name, address):
        try:
            user = Session.query(User).filter_by(firebase_uid=firebase_uid).first()
            if user:
                user.name = name
                user.address = address
                Session.commit()
                return user
            return None
        except SQLAlchemyError as e:
            Session.rollback()
            raise e

    @staticmethod
    def add_participant(deal_id, firebase_uid):
        try:
            user = Session.query(User).filter_by(firebase_uid=firebase_uid).first()
            deal = Session.query(Deal).get(deal_id)
            
            if not user or not deal:
                return None, "User or deal not found"
                
            # Check if already participated
            existing = Session.query(DealParticipant).filter_by(
                deal_id=deal_id,
                user_id=user.id
            ).first()
            
            if existing:
                return None, "Already participated"
                
            participant = DealParticipant(deal_id=deal_id, user_id=user.id)
            Session.add(participant)
            
            # Update deal status
            deal.current_participants += 1
            if deal.current_participants >= deal.min_participants:
                deal.status = 'closed'
                
            Session.commit()
            return participant, None
        except SQLAlchemyError as e:
            Session.rollback()
            raise e

    @staticmethod
    def add_deal(title, description, price, user_id, min_participants):
        try:
            new_deal = Deal(title=title, description=description, price=price, user_id=user_id, min_participants=min_participants)
            Session.add(new_deal)
            Session.commit()
            return new_deal
        except SQLAlchemyError as e:
            Session.rollback()
            raise e

    @staticmethod
    def get_deal(deal_id):
        return Session.query(Deal).get(deal_id)

    @staticmethod
    def get_all_deals():
        return Session.query(Deal).all()

    @staticmethod
    def update_deal(deal_id, title, description, price):
        try:
            deal = Session.query(Deal).get(deal_id)
            if deal:
                deal.title = title
                deal.description = description
                deal.price = price
                Session.commit()
                return deal
            return None
        except SQLAlchemyError as e:
            Session.rollback()
            raise e

    @staticmethod
    def delete_deal(deal_id):
        try:
            deal = Session.query(Deal).get(deal_id)
            if deal:
                Session.delete(deal)
                Session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            Session.rollback()
            raise e

    @staticmethod
    def add_deal_image(deal_id, image_url):
        try:
            # Check if deal exists
            deal = Session.query(Deal).get(deal_id)
            if not deal:
                raise ValueError("Deal not found")
                
            # Check number of existing images
            existing_images = Session.query(DealImage).filter_by(deal_id=deal_id).count()
            if existing_images >= 3:
                raise ValueError("Maximum number of images reached")
                
            new_image = DealImage(deal_id=deal_id, image_url=image_url)
            Session.add(new_image)
            Session.commit()
            return new_image
        except SQLAlchemyError as e:
            Session.rollback()
            raise e

    @staticmethod
    def get_deal_images(deal_id):
        return Session.query(DealImage).filter_by(deal_id=deal_id).all()

    @staticmethod
    def delete_deal_image(image_id):
        try:
            image = Session.query(DealImage).get(image_id)
            if image:
                Session.delete(image)
                Session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            Session.rollback()
            raise e