import bcrypt
import jwt
from datetime import datetime, timezone
from database import engine
from pydantic import EmailStr
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    github_id = Column(Integer, primary_key=True)
    github_username = Column(String(255), unique=True)
    access_token = Column(String(255))
    # email = Column(String(255), unique=True)
    # hashed_password = Column(String(255), unique=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime)
    
    # @staticmethod
    # def hash_password(password: str) -> str:
    #     hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    #     return hashed.decode()
    
    


Base.metadata.create_all(engine)