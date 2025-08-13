import os
import httpx
from jose import jwt, JWTError
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import User
from datetime import datetime, timedelta, timezone

router = APIRouter()
security = HTTPBearer()

load_dotenv()
github_client_id = os.getenv("GITHUB_CLIENT_ID")
github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
redirect_url = os.getenv("GITHUB_REDIRECT_URI")

github_auth_url = f"https://github.com/login/oauth/authorize?client_id={github_client_id}&redirect_uri={redirect_url}&scope=repo,user:email"
token_exchange_url = "https://github.com/login/oauth/access_token"


@router.get("/auth/login")
async def get_auth():
    return RedirectResponse(github_auth_url)


@router.get("/auth/callback")
async def get_code(
    code: str, state: str | None = None, db: Session = Depends(get_db)
):  # give me a database session I can use to save data
    data = {
        "client_id": github_client_id,
        "client_secret": github_client_secret,
        "redirect_uri": redirect_url,
        "code": code,
    }
    async with httpx.AsyncClient() as client:
        headers = {"Accept": "application/json"}
        post_exchange_token = await client.post(
            token_exchange_url, data=data, headers=headers
        )
        github_code = post_exchange_token.json()
        access_token = github_code.get("access_token")
        user_headers = {"Authorization": f"token {access_token}"}
        user_response = await client.get(
            "https://api.github.com/user", headers=user_headers
        )
        user_data = user_response.json()
    existing_user = db.query(User).filter(User.github_id == user_data["id"]).first()

    if existing_user == None:
        new_user = User(
            github_id=user_data["id"],
            github_username=user_data["login"],
            access_token=access_token,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(new_user)
    else:
        existing_user.access_token = access_token
        existing_user.updated_at = datetime.now(timezone.utc)

    jwt_token = jwt.encode(
        {
            "github_id": user_data["id"],
            "exp": datetime.now(timezone.utc) + timedelta(days=30),
        },
        os.getenv("SECRET_KEY"),
        algorithm="HS256",
    )

    db.commit()

    return RedirectResponse(
        url=f"https://secureakey.onrender.com/?token={jwt_token}&username={user_data['login']}"
    )


def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(
            token.credentials, os.getenv("SECRET_KEY"), algorithms=["HS256"]
        )
        github_id = payload.get("github_id")
        user = db.query(User).filter(User.github_id == github_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
