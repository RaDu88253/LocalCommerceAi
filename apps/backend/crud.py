from sqlalchemy.orm import Session

import models, schemas
from security import get_password_hash

def get_user_by_email(db: Session, email: str):
    """Găsește un utilizator după email."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    """Găsește un utilizator după username."""
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Creează un utilizator nou în baza de date."""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user