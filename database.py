from models.models import db, User, Deal, DealImage
from sqlalchemy.exc import SQLAlchemyError

class DatabaseManager:
    @staticmethod
    def add_user(username, email, password):
        try:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def add_deal(title, description, price, location, user_id):
        try:
            new_deal = Deal(title=title, description=description, price=price, location=location, user_id=user_id)
            db.session.add(new_deal)
            db.session.commit()
            return new_deal
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_deal(deal_id):
        return Deal.query.get(deal_id)

    @staticmethod
    def get_all_deals():
        return Deal.query.all()

    @staticmethod
    def update_deal(deal_id, title, description, price, location):
        try:
            deal = Deal.query.get(deal_id)
            if deal:
                deal.title = title
                deal.description = description
                deal.price = price
                deal.location = location
                db.session.commit()
                return deal
            return None
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_deal(deal_id):
        try:
            deal = Deal.query.get(deal_id)
            if deal:
                db.session.delete(deal)
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def add_deal_image(deal_id, image_url):
        try:
            new_image = DealImage(deal_id=deal_id, image_url=image_url)
            db.session.add(new_image)
            db.session.commit()
            return new_image
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_deal_images(deal_id):
        return DealImage.query.filter_by(deal_id=deal_id).all()

    @staticmethod
    def delete_deal_image(image_id):
        try:
            image = DealImage.query.get(image_id)
            if image:
                db.session.delete(image)
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e