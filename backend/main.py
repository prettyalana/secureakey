from fastapi import FastAPI
from auth import router

app = FastAPI()
app.include_router(router)

@app.get("/")
def main():
    return {"message": "Welcome to SecureaKey 🔐"}
