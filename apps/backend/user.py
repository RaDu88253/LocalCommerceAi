from sqlalchemy import Column, Integer, String
from .database import Base 

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True)
    first_name = Column(String(255), index=True)
    last_name = Column(String(255), index=True)
    hashed_password = Column(String(255), nullable=False)
    phone_number = Column(String(50), unique=True, index=True)

    def __repr__(self):
        return f"<User(username='{self.username}', name='{self.first_name} {self.last_name}')>"
