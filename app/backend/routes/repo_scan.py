import os
import httpx
import re
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
        
async def get_all_files(client, owner, repo, path="", headers=None):
    all_files = []
    
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = await client.get(url, headers=headers)
    
    contents = response.json()
    
    for item in contents:
        if item["type"] == "file":
            all_files.append(item)
        elif item["type"] == "dir":
            subdir_files = await get_all_files(client, owner, repo, item["path"], headers)
            all_files.extend(subdir_files)
    return all_files
    
@router.post("/scan/repo")
async def scan_repository(repo_name: str, current_user: User = Depends(get_current_user)):
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {current_user.access_token}", 
                   "Accept": "application/vnd.github+json",
                   "User-Agent": "secureakey"
        }
        
        owner = current_user.github_username
        
        all_files = await get_all_files(client, owner, repo_name, "", headers)

        return {"files": all_files}

#TODO: Scan all repositories at once   
@router.post("/scan/user")
async def scan_all_repos(db: Session = Depends(get_db)):
    pass
