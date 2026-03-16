from api.frontend.router import frontend_router
from fastapi import APIRouter


api_router = APIRouter()

api_router.include_router(frontend_router, prefix="/frontend")
