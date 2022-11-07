from pydantic import BaseModel


class Customer(BaseModel):
    user_id: int
    role: str
    address: str
    username: str
    password: str

    class Config:
        orm_mode = True


class Favorites(BaseModel):
    favorite_id: int
    customer_id: int
    product_id: int

    class Config:
        orm_mode = True

class Card(BaseModel):
    card_id: int
    customer_id: int
    product_id: int

    class Config:
        orm_mode = True


class Product(BaseModel):
    product_id: int
    owner_id: int
    name: str
    price: int
    color: str
    photo: str
    type: str
    model: str
    country: str

    class Config:
        orm_mode = True
