from fastapi import APIRouter
from api.frontend.auth import auth_router


frontend_router = APIRouter()

frontend_router.include_router(auth_router, prefix="/auth")