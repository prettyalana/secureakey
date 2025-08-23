import os
import httpx
import re
import base64
from .auth import get_current_user
from fastapi import APIRouter, Depends, Request, HTTPException
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


async def scan_file_content(client, file_info, headers, owner, repo):

    findings = []
    
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_info['path']}"

    try:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            content = base64.b64decode(data["content"]).decode('utf-8')

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

@router.get("/file/{repo_name}/{file_path:path}")
async def get_file_content(repo_name: str, file_path: str, current_user: User = Depends(get_current_user)):
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {current_user.access_token}"}
        url = f"https://api.github.com/repos/{current_user.github_username}/{repo_name}/contents/{file_path}"
        response = await client.get(url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="File not found")
            
        data = response.json()
        content = base64.b64decode(data["content"]).decode('utf-8')
        return {"content": content, "sha": data["sha"]}

class FileUpdateRequest(BaseModel):
    new_content: str
    sha: str

@router.put("/file/{repo_name}/{file_path:path}")
async def update_file(repo_name: str, file_path: str, payload: FileUpdateRequest, current_user: User = Depends(get_current_user)):
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {current_user.access_token}"}
        url = f"https://api.github.com/repos/{current_user.github_username}/{repo_name}/contents/{file_path}"
        
        encoded_content = base64.b64encode(payload.new_content.encode('utf-8')).decode('utf-8')
        data = {"message": f"Fixed API key in {file_path}", "content": encoded_content, "sha": payload.sha}
        
        response = await client.put(url, headers=headers, json=data)
        return {"status": "success" if response.status_code == 200 else "error"}