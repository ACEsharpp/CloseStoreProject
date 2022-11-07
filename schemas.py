from pydantic import BaseModel

class Customer(BaseModel):
    user_id: int
    role: str
    address: str
    username: str
    password: str

    class Config:
        orm_mode = True