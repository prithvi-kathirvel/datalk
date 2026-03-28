from fastapi import APIRouter,Depends
from typing import Annotated
from app.core.config import get_settings,Settings

router = APIRouter()

@router.get("/health")
def health_check(settings:Annotated[Settings,Depends(get_settings)]):
    return {"status":"Healthy","version":settings.VERSION}