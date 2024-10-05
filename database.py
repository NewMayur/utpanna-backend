from models.models import User, Deal, DealImage
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from utils.mysql_connector import connect_with_connector

engine = connect_with_connector()
Session = sessionmaker(bind=engine)

class DatabaseManager:
    @staticmethod
    def add_user(username, email, password, firebase_uid=None, phone_number=None):
        session = Session()
        try:
            new_user = User(username=username, email=email, firebase_uid=firebase_uid, phone_number=phone_number)
            if password:
                new_user.set_password(password)
            session.add(new_user)
            session.commit()
            return new_user
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def get_user_by_username(username):
        session = Session()
        try:
            return session.query(User).filter_by(username=username).first()
        finally:
            session.close()

    @staticmethod
    def get_user_by_email(email):
        session = Session()
        try:
            return session.query(User).filter_by(email=email).first()
        finally:
            session.close()

    @staticmethod
    def get_user_by_firebase_uid(firebase_uid):
        session = Session()
        try:
            return session.query(User).filter_by(firebase_uid=firebase_uid).first()
        finally:
            session.close()

    @staticmethod
    def add_deal(title, description, price, user_id, min_participants):
        session = Session()
        try:
            new_deal = Deal(title=title, description=description, price=price, user_id=user_id, min_participants=min_participants)
            session.add(new_deal)
            session.commit()
            return new_deal
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def get_deal(deal_id):
        session = Session()
        try:
            return session.query(Deal).get(deal_id)
        finally:
            session.close()

    @staticmethod
    def get_all_deals():
        session = Session()
        try:
            return session.query(Deal).all()
        finally:
            session.close()

    @staticmethod
    def update_deal(deal_id, title, description, price):
        session = Session()
        try:
            deal = session.query(Deal).get(deal_id)
            if deal:
                deal.title = title
                deal.description = description
                deal.price = price
                session.commit()
                return deal
            return None
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def delete_deal(deal_id):
        session = Session()
        try:
            deal = session.query(Deal).get(deal_id)
            if deal:
                session.delete(deal)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def add_deal_image(deal_id, image_url):
        session = Session()
        try:
            new_image = DealImage(deal_id=deal_id, image_url=image_url)
            session.add(new_image)
            session.commit()
            return new_image
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def get_deal_images(deal_id):
        session = Session()
        try:
            return session.query(DealImage).filter_by(deal_id=deal_id).all()
        finally:
            session.close()

    @staticmethod
    def delete_deal_image(image_id):
        session = Session()
        try:
            image = session.query(DealImage).get(image_id)
            if image:
                session.delete(image)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()