from fastapi import APIRouter
from backend.api import health, callqa, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(callqa.router, prefix="/api", tags=["callqa"])
api_router.include_router(ui.router, tags=["ui"])
