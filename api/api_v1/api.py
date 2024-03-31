from fastapi import APIRouter
from api.api_v1.endpoints import start
from api.api_v1.endpoints import registration
from api.api_v1.endpoints import crpt


api_router = APIRouter()
api_router.include_router(start.router, tags=["Настройки системы"])
api_router.include_router(registration.router,tags=["Система регистрации участников мероприятия"])
api_router.include_router(crpt.router,tags=["Печать КМ"])

