from fastapi import APIRouter

from app.api.users import router as users_router
from app.api.agents import router as agents_router
from app.api.ai import router as ai_router

api_router = APIRouter()

api_router.include_router(users_router)
api_router.include_router(agents_router)
api_router.include_router(ai_router)