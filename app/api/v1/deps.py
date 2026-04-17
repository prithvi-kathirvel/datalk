from fastapi import Request
from langgraph.graph.state import CompiledStateGraph
import asyncpg

def get_graph(request: Request) -> CompiledStateGraph:
    state = getattr(request.app.state, "graph", None)
    if state is None:
        raise RuntimeError("Graph not initialized — app may still be starting")
    return state

def get_db_pool(request: Request) -> asyncpg.Pool:
    state = getattr(request.app.state, "db_pool", None)
    if state is None:
        raise RuntimeError("Database pool not initialized — app may still be starting")
    return state

def get_session_service(request: Request):
    state = getattr(request.app.state, "session_service", None)
    if state is None:
        raise RuntimeError("Session service not initialized — app may still be starting")
    return state