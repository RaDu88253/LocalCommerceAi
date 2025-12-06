from pydantic import BaseModel, EmailStr
import datetime
from typing import Optional

# Schema pentru datele primite la crearea unui utilizator
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone_number: str

# Schema pentru datele returnate de API (fără parolă)
class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: str
    created_at: datetime.datetime

    # Această configurație permite Pydantic să citească datele
    # direct dintr-un model SQLAlchemy.
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str