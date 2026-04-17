from langgraph.graph import StateGraph,START,END 
from app.langgraph.schema import AgentState
from app.langgraph.nodes import relevance_check,general_chat,get_tables,decision_router,sql_generator,safety_checker,response_generator
from langchain.messages import HumanMessage
from app.services.llm_service import LLMService
from app.services.db_service import DBService
from app.schema.model import ChatInputSchema,DatabaseConfigurationSchema
from app.core.config import get_settings
import uuid
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langgraph.graph.state import CompiledStateGraph
import asyncpg
from app.services.session_service import SessionService


settings = get_settings()


async def build_graph(checkpointer) -> CompiledStateGraph:

        graph = StateGraph(state_schema=AgentState)
        graph.add_node("relevance_check", relevance_check)
        graph.add_node("general_chat",general_chat)
        graph.add_node("get_tables",get_tables)
        graph.add_node("sql_generator",sql_generator)
        graph.add_node("safety_checker",safety_checker)
        graph.add_node("response_generator",response_generator)
        graph.add_edge(START,"relevance_check")
        graph.add_conditional_edges("relevance_check",decision_router,{"get_tables":"get_tables","general_chat":"general_chat"})
        graph.add_edge("general_chat",END)
        graph.add_edge("get_tables","sql_generator")
        graph.add_edge("sql_generator","safety_checker")
        graph.add_edge("safety_checker","response_generator")
        graph.add_edge("response_generator",END)

        graph = graph.compile(checkpointer=checkpointer)
        return graph

async def execute_graph(user_input:ChatInputSchema,db_details:DatabaseConfigurationSchema,graph:CompiledStateGraph,db_pool:asyncpg.Pool, session_service: SessionService):
    """Execute the Langgraph and manage history."""

    db_service = DBService(**db_details.model_dump())
    llm_service = LLMService(user_input.model_name or settings.DEFAULT_LLM_MODEL)
    thread_id = user_input.thread_id or str(uuid.uuid4())
    session_id = user_input.session_id or str(uuid.uuid4())
    user_id = user_input.user_id if hasattr(user_input, "user_id") else "default_user"

    await session_service.create_or_update_session(user_id, thread_id, session_id, title=user_input.message[:50])
    
    await session_service.add_message(session_id, "user", user_input.message)

    config = {"configurable":{"thread_id":thread_id,"session_id":session_id,"db":db_service,"llm":llm_service}}

    initial_state = {
        "messages": [HumanMessage(content=user_input.message)]        
    }
    result = await graph.ainvoke(initial_state,config=config)

    messages = result.get("messages", [])
    
  
    last_human_idx = -1
    for i in range(len(messages) - 1, -1, -1):
        if isinstance(messages[i], HumanMessage):
            last_human_idx = i
            break
            
    turn_input_tokens = 0
    turn_output_tokens = 0
    turn_total_tokens = 0
    
    if last_human_idx != -1:
        for msg in messages[last_human_idx + 1:]:
            usage = getattr(msg, "usage_metadata", None)
            if usage:
                turn_input_tokens += usage.get("input_tokens", 0)
                turn_output_tokens += usage.get("output_tokens", 0)
                turn_total_tokens += usage.get("total_tokens", 0)

    aggregated_usage = {
        "input_tokens": turn_input_tokens,
        "output_tokens": turn_output_tokens,
        "total_tokens": turn_total_tokens
    }

    if "final_response" in result:
        await session_service.add_message(
            session_id, 
            "assistant", 
            result["final_response"],
            kwargs={"usage": aggregated_usage}  
        )

    return {
        "thread_id":thread_id,
        "session_id":session_id,
        "token_usage": aggregated_usage,
        **result
    }
