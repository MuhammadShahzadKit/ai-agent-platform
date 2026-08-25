from fastapi import APIRouter

from app.api.users import router as users_router
from app.api.agents import router as agents_router
from app.api.chat import router as chat_router
from app.api.memory import router as memory_router
from app.api.missions import router as missions_router
from app.api.rag import router as rag_router
from app.api.conversations import router as conversations_router


api_router = APIRouter()


api_router.include_router(users_router)
api_router.include_router(agents_router)
api_router.include_router(chat_router)
api_router.include_router(memory_router)
api_router.include_router(missions_router)
api_router.include_router(rag_router)
api_router.include_router(conversations_router)