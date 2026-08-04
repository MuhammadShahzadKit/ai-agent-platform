from fastapi import FastAPI

app = FastAPI(
    title="DigiEmp API",
    description="Autonomous Digital Employee Platform",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "project": "DigiEmp",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }