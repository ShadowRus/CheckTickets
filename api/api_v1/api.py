from fastapi import APIRouter
from api.api_v1.endpoints import start


api_router = APIRouter()
api_router.include_router(start.router, tags=["Стартовая страница"])

