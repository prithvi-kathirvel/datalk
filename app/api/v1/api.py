from fastapi import APIRouter,Depends
from typing import Annotated
from app.core.config import get_settings,Settings
from app.api.v1.chat import chat_router

router = APIRouter()

router.include_router(chat_router,tags=["Chat"])


@router.get("/health")
def health_check(settings:Annotated[Settings,Depends(get_settings)]):
    return {"status":"Healthy","version":settings.VERSION}