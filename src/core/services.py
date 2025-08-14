from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from . import models

def create_user(db: Session, user_data: dict):
    hashed_password = bcrypt.hash(user_data["password"])
    db_user = models.User(
        username=user_data["username"],
        email=user_data["email"],
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_google_id(db: Session, google_id: str):
    return db.query(models.User).filter(models.User.google_id == google_id).first()

def create_user_from_oauth(db: Session, user_data: dict):
    db_user = models.User(
        username=user_data.get("username"),
        email=user_data["email"],
        google_id=user_data["google_id"],
        profile_picture=user_data.get("profile_picture")
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user