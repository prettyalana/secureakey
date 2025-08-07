import os
import bcrypt
import jwt
from datetime import datetime, timezone
from database import engine
from pydantic import EmailStr
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    github_id = Column(Integer, primary_key=True)
    github_username = Column(String(255), unique=True)
    access_token = Column(String(255))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime)


class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    token = Column(String(500))


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    access_token = Column(String(500))
    token_type = Column(String(50), default="bearer")


def create_access_token(data: dict, expires_delta=None):
    from datetime import timedelta

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm="HS256")

    return encoded_jwt


def is_token_blacklisted(token, session):
    return session.query(BlacklistedToken).filter_by(token=token).first() is not None


Base.metadata.create_all(engine)