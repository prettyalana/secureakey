import os
import httpx
from .auth import get_current_user
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse, JSONResponse
from dotenv import load_dotenv
from pydantic import BaseModel
from database import get_db
from models import User
from datetime import datetime

router = APIRouter()


@router.get("/repos")
async def get_my_repos(current_user: User = Depends(get_current_user)):
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {current_user.access_token}", "Accept": "application/vnd.github+json",
                   "User-Agent": "secureakey"
        }
        
        response = await client.get(
            "https://api.github.com/user/repos", headers=headers
        )
        
        if response.status_code == 200:
            repos = response.json()
            return {"repositories": [repo["name"] for repo in repos]}
        

@router.post("/scan/repo")
async def scan_repository(repo_name: str, current_user: User = Depends(get_current_user)):
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {current_user.access_token}", 
                   "Accept": "application/vnd.github+json",
                   "User-Agent": "secureakey"
        }
        
        owner = current_user.github_username
        response = await client.get(
            "https://api.github.com/user/repos/{owner}/{repo_name}/contents", headers=headers
        )

        if response.status_code == 200:
            contents = response.json()
            return {"items": contents}

@router.post("/scan/user")
async def scan_all_repos(db: Session = Depends(get_db)):
    pass
