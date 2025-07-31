import os
import httpx
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from fastapi import Request
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User
from datetime import datetime

router = APIRouter()

load_dotenv()
github_client_id = os.getenv("GITHUB_CLIENT_ID")
github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
redirect_url = os.getenv("GITHUB_REDIRECT_URI")

github_auth_url = f"https://github.com/login/oauth/authorize?client_id={github_client_id}&redirect_uri={redirect_url}&scope=user:email"
token_exchange_url = "https://github.com/login/oauth/access_token"

@router.get("/auth/login")
async def get_auth():
    return {"auth_url": github_auth_url}

@router.get("/auth/callback")
async def get_code(code: str, state: str | None = None, db: Session = Depends(get_db)): #give me a database session I can use to save data
    data = {"client_id": github_client_id, "client_secret": github_client_secret, "redirect_uri": redirect_url, "code": code}
    async with httpx.AsyncClient() as client:
        headers = {
            "Accept": "application/json"
        }
        post_exchange_token = await client.post(token_exchange_url, data=data, headers=headers)
        github_code = post_exchange_token.json()
        access_token = github_code.get('access_token')
        user_headers = {"Authorization": f"Bearer {access_token}"}
        user_response = await client.get("https://api.github.com/user", headers=user_headers)
        user_data = user_response.json()
        print(user_data)
    existing_user = db.query(User).filter(User.github_id == user_data["id"]).first()
    
    if existing_user == None:
        new_user = User(
            github_id = user_data["id"],
            github_username = user_data["login"],
            access_token = access_token,
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        db.add(new_user)
    else:
        existing_user.access_token = access_token
        existing_user.updated_at = datetime.now()
        
    db.commit()
    
    return {
        "message": "User saved successfully",
        "user": {
            "github_id": user_data["id"],
            "github_username": user_data["login"],
            "created_at": user_data["created_at"],
            "updated_at": user_data["updated_at"]
        }
    }