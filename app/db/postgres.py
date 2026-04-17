# app/db/postgres.py

from sqlalchemy import create_engine
from app.core.config import get_settings

settings = get_settings()

DATABASE_URI = (
    f"postgresql+psycopg2://{settings.USER_NAME}:"
    f"{settings.PASSWORD}@{settings.HOST}:"
    f"{settings.PORT}/{settings.DATABASE}"
)

engine = create_engine(DATABASE_URI, pool_pre_ping=True)