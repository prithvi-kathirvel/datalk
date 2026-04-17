import os
from pydantic_settings import BaseSettings,SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    VERSION_PREFIX: str 
    VERSION : str 
    ENVIRONMENT: str = "development"
    HOST: str 
    PORT: int 
    USER_NAME: str
    DATABASE: str
    PASSWORD: str
    SECRET_KEY: str 
    ALGORITHM : str 
    LLAMA_MODEL_NAME: str
    LLAMA_API_KEY: str
    LLAMA_BASE_URL: str 
    GOOGLE_MODEL_NAME: str
    GOOGLE_API_KEY: str
    MAX_RETRY_ATTEMPTS: int
    RETRY_DELAYS: int
    DEFAULT_TEMPERATURE : float
    DIALECT: str
    DEFAULT_LLM_MODEL:str
    CHECKPOINTER_TYPE: str
    REDIS_URI: str
    POSTGRES_URI: str
    LANGSMITH_TRACING: str
    LANGSMITH_ENDPOINT: str
    LANGSMITH_API_KEY: str
    LANGSMITH_PROJECT: str
    OPENROUTER_API_KEY: str
    GROQ_API_KEY: str

@lru_cache
def get_settings():
    try:
        settings = Settings()
        os.environ["LANGSMITH_TRACING"] = settings.LANGSMITH_TRACING
        os.environ["LANGSMITH_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
        os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
        os.environ["LANGSMITH_PROJECT"] = settings.LANGSMITH_PROJECT
        return settings
    except Exception as e:
        raise Exception(f"Error loading settings: {e}")

    
