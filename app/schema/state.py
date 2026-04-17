from typing import TypedDict, Literal, List
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field
from langgraph.graph.state import CompiledStateGraph
import asyncpg
class AppState(TypedDict):
    graph : CompiledStateGraph
    db_pool : asyncpg.Pool

