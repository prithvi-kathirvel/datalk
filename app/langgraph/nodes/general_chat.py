from app.langgraph.schema import AgentState
from langchain_core.runnables import RunnableConfig
from langchain.messages import HumanMessage, AIMessage
from app.core.logging import logger
from app.langgraph.schema import AIResponse
from langchain_core.output_parsers import JsonOutputParser

from app.langgraph.utils.history import get_wise_history

async def general_chat(state:AgentState,config:RunnableConfig):
    """General Chat to handle chit-chat and general queries"""
    logger.info("Calling General Chat Node")
    try:
        llm_service = config["configurable"]["llm"]
        llm_runnable = llm_service.get_llm(structured=True, output_schema=AIResponse)
        
        history = get_wise_history(state["messages"], last_n=10)
        
        parser = JsonOutputParser(pydantic_object=AIResponse)
        format_instructions = parser.get_format_instructions()
        
        messages = history[:-1] + [HumanMessage(content=history[-1].content + "\n" + format_instructions)]
        
        res, msg = await llm_service.ainvoke(llm_runnable, messages, output_schema=AIResponse, config=config)

        usage = getattr(msg, "usage_metadata", None)
        clean_msg = AIMessage(content=res.response, usage_metadata=usage)

        return {"final_response": res.response, "messages": [clean_msg]}

    except Exception as e:
        logger.error(f"Error in General Chat Node: {e}")
        return {"final_response":"Unable to Process your request buddy!!"}
        
    
    