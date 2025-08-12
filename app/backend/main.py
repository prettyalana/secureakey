from fastapi import FastAPI
from routes import router
from routes.repo_scan import router as repo_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(router)
app.include_router(repo_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def main():
    return {"message": "Welcome to SecureaKey 🔐"}
