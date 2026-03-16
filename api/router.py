from api.frontend.router import frontend_router
from api.worker.router import worker_router
from fastapi import APIRouter


api_router = APIRouter()

api_router.include_router(frontend_router, prefix="/frontend")
api_router.include_router(worker_router, prefix="/worker")
