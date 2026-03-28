from pydantic_settings import BaseSettings,SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    VERSION_PREFIX: str 
    VERSION : str 
    ENVIRONMENT: str = "development"


@lru_cache
def get_settings():
    return Settings()
