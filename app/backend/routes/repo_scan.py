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
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware

API_KEY_PATTERNS = {
    # More keys coming soon
    "OpenAI": r"sk-[a-zA-Z0-9]{20,}",
    "GitHub": r"gh[ops]_[A-Za-z0-9_]{36,255}",
    "AWS": r"AKIA[0-9A-Z]{16}",
    "Stripe": r"sk_(test_|live_)[0-9a-zA-Z]{24,}",
    "Google": r"AIza[0-9A-Za-z\-_]{35}",
    "Slack": r"xox[baprs]-[0-9a-zA-Z\-]{10,72}",
}

router = APIRouter()


class ScanRepoRequest(BaseModel):
    repo_name: str


@router.get("/repos")
async def get_my_repos(current_user: User = Depends(get_current_user)):
    repos = []
    page = 1
    per_page = 100

    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {current_user.access_token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "secureakey",
        }

        while True:
            url = f"https://api.github.com/user/repos?type=owner&page={page}&per_page={per_page}"
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                break

            batch = response.json()
            if not batch:
                break

            repos.extend(batch)
            page += 1

    return {"repositories": [repo["name"] for repo in repos]}


async def get_all_files(client, owner, repo, path="", headers=None):
    all_files = []

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = await client.get(url, headers=headers)

    contents = response.json()

    if isinstance(contents, dict):
        if contents.get("type") == "file":
            all_files.append(contents)
        return all_files

    if isinstance(contents, list):
        for item in contents:
            if item["type"] == "file":
                all_files.append(item)
            elif item["type"] == "dir":
                subdir_files = await get_all_files(
                    client, owner, repo, item["path"], headers
                )
                all_files.extend(subdir_files)

    return all_files


async def scan_file_content(client, file_info):

    findings = []

    try:
        response = await client.get(file_info["download_url"])
        if response.status_code == 200:
            content = response.text

        lines = content.split("\n")
        for line_num, line in enumerate(lines, 1):
            for key_type, pattern in API_KEY_PATTERNS.items():
                if re.search(pattern, line):
                    findings.append(
                        {
                            "file_path": file_info["path"],
                            "line_number": line_num,
                            "key_type": key_type,
                            "line_content": line.strip()[:100],
                        }
                    )
    except Exception as e:
        pass

    return findings


@router.post("/scan/repo")
async def scan_repository(
    payload: ScanRepoRequest,
    current_user: User = Depends(get_current_user),
):
    repo_name = payload.repo_name
    owner = current_user.github_username

    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {current_user.access_token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "secureakey",
        }

        owner = current_user.github_username

        all_files = await get_all_files(client, owner, repo_name, "", headers)

        all_findings = []
        for file_info in all_files:
            file_findings = await scan_file_content(client, file_info)
            all_findings.extend(file_findings)

        if len(all_findings) > 1:
            return {
                "status": "keys_detected",
                "message": f"⚠️ Found {len(all_findings)} potential API keys!",
                "repository": repo_name,
                "total_files_scanned": len(all_files),
                "findings": all_findings,
            }
        elif len(all_findings) == 1:
            return {
                "status": "keys_detected",
                "message": f"⚠️ Found {len(all_findings)} potential API key!",
                "repository": repo_name,
                "total_files_scanned": len(all_files),
                "findings": all_findings,
            }
        else:
            return {
                "status": "clean",
                "message": "✅ No API keys detected",
                "repository": repo_name,
                "total_files_scanned": len(all_files),
            }

# TODO: Scan all repositories at once
@router.post("/scan/user")
async def scan_all_repos(db: Session = Depends(get_db)):
    pass
