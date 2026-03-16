from fastapi import APIRouter
from api.worker.auth import auth_router


worker_router = APIRouter()

worker_router.include_router(auth_router, prefix="/auth")