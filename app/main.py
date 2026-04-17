from fastapi import FastAPI,Depends 
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from app.api.v1.api import router
from app.core.config import get_settings,Settings
from app.core.logging import setup_logging,logger,logging_middleware
from app.core.middleware import get_current_user
from app.langgraph.graph import build_graph 
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import asyncpg

settings = get_settings()
setup_logging(environment=settings.ENVIRONMENT)

from app.services.session_service import SessionService

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application Started")
    try:
        logger.info("Creating Database Pool")
        db_pool = await asyncpg.create_pool(dsn=settings.POSTGRES_URI,min_size=2,max_size=10)
        logger.info("Database Pool Created")
        
        session_service = SessionService(db_pool)
        await session_service.setup()
        app.state.session_service = session_service

    except Exception as e:
        logger.error(f"Error creating Database pool or setting up sessions: {e}")
        raise Exception(f"Error creating Database pool: {e}")
    async with AsyncPostgresSaver.from_conn_string(settings.POSTGRES_URI) as checkpointer:
        await checkpointer.setup()
        app.state.db_pool = db_pool
        app.state.graph = await build_graph(checkpointer)
        logger.info("Graph compiled and checkpointer ready")
        yield

    logger.info("Application Shutting Down")


app = FastAPI(lifespan=lifespan)
logging_middleware(app)
app.include_router(router,prefix=settings.VERSION_PREFIX)