from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    firebase_uid = Column(String(128), unique=True, nullable=True)
    phone_number = Column(String(20), unique=True, nullable=True)
    username = Column(String(80), unique=True, nullable=True)
    email = Column(String(120), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)  # Changed from 128 to 255

    groups = relationship('Group', back_populates='creator')
    orders = relationship('Order', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Deal(Base):
    __tablename__ = 'deal'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    min_participants = Column(Integer, nullable=False)
    current_participants = Column(Integer, default=0)
    status = Column(String(20), default='open')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    groups = relationship('Group', back_populates='deal')
    orders = relationship('Order', back_populates='deal')
    images = relationship('DealImage', back_populates='deal')

class DealImage(Base):
    __tablename__ = 'deal_image'
    id = Column(Integer, primary_key=True)
    deal_id = Column(Integer, ForeignKey('deal.id'), nullable=False)
    image_url = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    deal = relationship('Deal', back_populates='images')

class Group(Base):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    creator_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    deal_id = Column(Integer, ForeignKey('deal.id'), nullable=False)

    creator = relationship('User', back_populates='groups')
    deal = relationship('Deal', back_populates='groups')
    orders = relationship('Order', back_populates='group')

class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    deal_id = Column(Integer, ForeignKey('deal.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('group.id'), nullable=False)
    status = Column(String(20), default='pending')

    user = relationship('User', back_populates='orders')
    deal = relationship('Deal', back_populates='orders')
    group = relationship('Group', back_populates='orders')