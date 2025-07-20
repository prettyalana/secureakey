from fastapi import FastAPI
from app.backend.routes import router

app = FastAPI()
app.include_router(router)

@app.get("/")
def main():
    return {"message": "Welcome to SecureaKey 🔐"}
