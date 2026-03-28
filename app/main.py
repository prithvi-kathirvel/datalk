from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.v1.api import router
from app.core.config import get_settings,Settings
from app.core.logging import setup_logging,logger,logging_middleware

settings = get_settings()
setup_logging(environment=settings.ENVIRONMENT)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application Started")
    yield
    logger.info("Application Shutting Down")


app = FastAPI(lifespan=lifespan)
logging_middleware(app)

app.include_router(router,prefix=settings.VERSION_PREFIX)