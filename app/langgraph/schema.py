from typing import TypedDict, Literal, List
from pydantic import BaseModel,Field
from langchain_core.messages import BaseMessage
from app.services.db_service import DBService
from app.services.llm_service import LLMService
from typing import Annotated
from langgraph.graph.message import add_messages
class AgentState(TypedDict):
    relevance: Literal["relevant","irrelevant"]
    db: DBService
    llm: LLMService
    messages: Annotated[List[BaseMessage], add_messages]
    tables: List[str]
    columns: list[str]
    sql_query: str 
    is_safe: bool 
    safety_reason: str
    final_response: str


class RelevanceCheckOutput(BaseModel):
    relevance: Literal["relevant","irrelevant"]

class AIResponse(BaseModel):
    response:str = Field(description="Response for the user")

class TableIdentifierOutput(BaseModel):
    tables: list[str] = Field(description="Tables to be used or belongs to the user's question")

class SQLGeneratorOutput(BaseModel):
    sql_query: str= Field(description="SQL query to answer the user's question")

class SafetyCheckOutput(BaseModel):
    is_safe: bool = Field(description="Whether the SQL query is safe to execute")
    reason: str = Field(description="Reason why the query is unsafe, if applicable")