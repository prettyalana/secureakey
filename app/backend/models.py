from datetime import datetime
from database import engine
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    github_id = Column(Integer, primary_key=True)
    github_username = Column(String(255), unique=True)
    access_token = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    


Base.metadata.create_all(engine)