from sqlalchemy import Column, ForeignKey, Integer, String
from database import Base


class Customer(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, autoincrement=True, unique=True, primary_key=True, nullable=False)
    role = Column(String(255), nullable=False)
    address = Column(String(255))
    username = Column(String(255), unique=True)
    password = Column(String(255), nullable=False)


class Favorites(Base):
    __tablename__ = 'favorites'
    favorite_id = Column(Integer, autoincrement=True, unique=True, primary_key=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('users.user_id'))
    product_id = Column(Integer, ForeignKey('products.product_id'))


class Card(Base):
    __tablename__ = 'card'
    card_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('users.user_id'))
    product_id = Column(Integer, ForeignKey('products.product_id'))

class Product(Base):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.user_id'))
    name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)
    color = Column(String(255), nullable=False)
    photo = Column(String(255), nullable=False)
    type = Column(String(255), nullable=False)
    model = Column(String(255), nullable=False, unique=False)
    country = Column(String(255))