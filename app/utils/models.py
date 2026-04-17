from typing import List,Dict
from langchain_openai import ChatOpenAI
from app.core.config import get_settings 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_vertexai import ChatVertexAI
from google.oauth2 import service_account
from langchain_openrouter import ChatOpenRouter 
from langchain_groq import ChatGroq

settings = get_settings()
credentials = service_account.Credentials.from_service_account_file(
    "service_account.json",scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

llm_models : List[Dict] = [
    {
        "name": settings.LLAMA_MODEL_NAME,
        "llm" : ChatOpenAI(
            model=settings.LLAMA_MODEL_NAME,
            api_key=settings.LLAMA_API_KEY,
            base_url=settings.LLAMA_BASE_URL,
            temperature = settings.DEFAULT_TEMPERATURE
        ),
        "provider":"meta"
    },
    {
        "name": "gemini-2.0-flash-lite",
        "llm" : ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            api_key=settings.GOOGLE_API_KEY,
            temperature = settings.DEFAULT_TEMPERATURE
        ),
        "provider":"google"
    },
    {
        "name": "gemini-2.5-flash",
        "llm" : ChatVertexAI(
            model="gemini-2.5-flash",
            credentials=credentials, 
            temperature=settings.DEFAULT_TEMPERATURE,
        ),
        "provider":"google"
    },
    {
        "name": "gemma",
        "llm" : ChatOpenRouter(
            model="google/gemma-4-26b-a4b-it:free",
            api_key=settings.OPENROUTER_API_KEY,
            temperature = settings.DEFAULT_TEMPERATURE,
            timeout=60,      
            max_retries=3 
        ),
        "provider":"openrouter"
    },
    {
        "name": "openai/gpt-oss-120b",
        "llm" : ChatGroq(
            model="openai/gpt-oss-120b",
            api_key=settings.GROQ_API_KEY,
            temperature = settings.DEFAULT_TEMPERATURE,
            timeout=60,
            max_retries=2,
        ),
        "provider":"groq"
    }
]