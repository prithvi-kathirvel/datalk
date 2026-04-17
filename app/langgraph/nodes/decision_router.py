from app.langgraph.schema import AgentState
from langchain_core.runnables import RunnableConfig
from app.core.logging import logger

async def decision_router(state:AgentState,config:RunnableConfig):
    logger.info("Calling Decision Router Node")
    try:
        if state["relevance"] == "relevant":
            return "get_tables"
        else:
            return "general_chat"
    except Exception as e:
        logger.error(f"Error in decision_router: {e}")
        return "general_chat"


    
