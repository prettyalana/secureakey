from fastapi import FastAPI
from routes import router
from routes.repo_scan import router as repo_router

app = FastAPI()
app.include_router(router)
app.include_router(repo_router)

@app.get("/")
def main():
    return {"message": "Welcome to SecureaKey 🔐"}
