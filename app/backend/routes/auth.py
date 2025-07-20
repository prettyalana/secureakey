import os
import httpx
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from fastapi import Request
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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
async def get_code(code: str, state: str | None = None):
    data = {"client_id": github_client_id, "client_secret": github_client_secret, "redirect_uri": redirect_url, "code": code}
    async with httpx.AsyncClient() as client:
        headers = {
            "Accept": "application/json"
        }
        post_exchange_token = await client.post(token_exchange_url, data=data, headers=headers)
    github_code = post_exchange_token.json()
    print(github_code)
    return {
        "code": github_code.get('access_token')
    }