from fastapi import FastAPI

from app.api.router import api_router
from app.db.init_db import init_db

app = FastAPI(
    title="DigiEmp API",
    description="Autonomous Digital Employee Platform",
    version="1.0.0",
)


@app.on_event("startup")
def startup():
    init_db()


app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "project": "DigiEmp",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }