from sqlalchemy import (Column, Integer, String, Boolean)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=True) # Make nullable for Google users
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=True) # Make nullable for Google users
    google_id = Column(String, unique=True, nullable=True)
    profile_picture = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"
