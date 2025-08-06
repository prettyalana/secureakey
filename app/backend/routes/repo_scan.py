import os
import httpx
from auth import get_current_user
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
    pass


@router.post("/scan/repo")
async def scan_repository(repo_name: str, db: Session = Depends(get_db)):
    pass


@router.post("/scan/user")
async def scan_all_repos(db: Session = Depends(get_db)):
    pass
