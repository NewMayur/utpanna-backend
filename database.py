from models.models import User, Deal, DealImage
from sqlalchemy.exc import SQLAlchemyError
from extensions import Session

class DatabaseManager:
    @staticmethod
    def add_user(username, email, password, firebase_uid=None, phone_number=None):
        try:
            new_user = User(username=username, email=email, firebase_uid=firebase_uid, phone_number=phone_number)
            if password:
                new_user.set_password(password)
            Session.add(new_user)
            Session.commit()
            return new_user
        except SQLAlchemyError as e:
            Session.rollback()
            raise e

    @staticmethod
    def get_user_by_username(username):
        return Session.query(User).filter_by(username=username).first()

    @staticmethod
    def get_user_by_email(email):
        return Session.query(User).filter_by(email=email).first()

    @staticmethod
    def get_user_by_firebase_uid(firebase_uid):
        return Session.query(User).filter_by(firebase_uid=firebase_uid).first()

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