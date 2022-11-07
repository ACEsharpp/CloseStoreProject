from sqlalchemy import or_
from sqlalchemy.orm import Session
import models, schemas


def add_customer(db: Session, customer: schemas.Customer) -> models.Customer:
    new_customer = models.Customer(username=customer.username, role=customer.role, password=customer.password)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


def delete_customer(db: Session, customer_username) -> bool:
    user = get_customer(db, customer_username)
    db.delete(user)
    db.commit()
    return user


def get_customer(db: Session, customer_username) -> models.Customer:
    return db.query(models.Customer).filter_by(username=customer_username).first()


def updateUser(db: Session, customer: schemas.Customer):
    db.query(models.Customer).filter_by(username=customer.username).update({"password": customer.password})
    db.commit()
    db.refresh(customer)

def updateAddress(db: Session, customer: schemas.Customer):
    db.query(models.Customer).filter_by(username=customer.username).update({"address": customer.address})
    db.commit()
    db.refresh(customer)

def get_clothes_for_welcome_page(db: Session):
    return db.query(models.Product).all()


def add_product(db: Session, product: schemas.Product) -> models.Product:
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def update_product(db: Session, product: schemas.Product) -> models.Product:
    db.query(models.Product).filter_by(product_id=product.product_id).update({"photo": product.photo})
    db.commit()
    db.refresh(product)
    return product

def get_products_of_seller(db: Session, owner_id):
    return db.query(models.Product).filter_by(owner_id=owner_id).all()

def searchProduct(db: Session, text: str):
    type_one = "%"+text.upper()+"%"
    type_two ="%"+text.lower()+"%"
    return db.query(models.Product).filter(or_(models.Product.name.like(type_one), models.Product.name.like(type_two),
                                           models.Product.color.like(type_one), models.Product.color.like(type_two) ,
                                           models.Product.type.like(type_one) , models.Product.type.like(type_two) ,
                                           models.Product.model.like(type_one) , models.Product.model.like(type_two))).all()

def clear_customer_card(db: Session, customer_id):
    db.query(models.Card).filter_by(customer_id=customer_id).delete()
    db.commit()


def clear_customer_favs(db: Session, customer_id):
    db.query(models.Favorites).filter_by(customer_id=customer_id).delete()
    db.commit()

def get_customer_favorites(db: Session, customer_id):
    return db.query(models.Product).join(models.Favorites).join(models.Customer).filter_by(user_id=customer_id).all()


def get_customer_card(db: Session, customer_id):
    return db.query(models.Product).join(models.Card).join(models.Customer).filter_by(user_id=customer_id).all()

def get_product(db: Session, product_id):
    return db.query(models.Product).filter_by(product_id=product_id).first()

def get_user_card_product(db: Session, product_id, user_id):
    return db.query(models.Card).filter_by(product_id=product_id, customer_id=user_id).first()
def get_user_favs_product(db: Session, product_id, user_id):
    return db.query(models.Favorites).filter_by(product_id=product_id, customer_id=user_id).first()


def add_product_to_user_card(db: Session, card: models.Card):
    db.add(card)
    db.commit()
    db.refresh(card)

def add_product_to_user_favs(db: Session, favs: models.Favorites):
    db.add(favs)
    db.commit()
    db.refresh(favs)

def delete_product_from_user_card(db: Session, card: models.Card):
    db.delete(card)
    db.commit()

def delete_product_from_user_favs(db: Session, favs: models.Favorites):
    db.delete(favs)
    db.commit()

