from fastapi import APIRouter
from api.frontend.auth import auth_router
from api.frontend.project import project_router
from api.frontend.worker import worker_router
from api.frontend.user import user_router
from api.frontend.chat import chat_router


frontend_router = APIRouter()

frontend_router.include_router(auth_router, prefix="/auth")
frontend_router.include_router(project_router, prefix="/project")
frontend_router.include_router(worker_router, prefix="/worker")
frontend_router.include_router(user_router, prefix="/user")
frontend_router.include_router(chat_router, prefix="/chat")