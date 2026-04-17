from pydantic import BaseModel, Field 
from typing import Optional
class ChatInputSchema(BaseModel):
    message: str 
    model_name : str 
    temperature: float
    session_id: Optional[str] = None 
    thread_id: Optional[str] = None

class DatabaseConfigurationSchema(BaseModel):
    dialect: str 
    host: str 
    port: int 
    user: str 
    password: str 
    database: str
    # kwargs: Optional[dict] 