import logging
from app.langgraph.schema import AgentState
from app.langgraph.constants.prompts import RELEVANCE_PROMPT
from app.langgraph.schema import RelevanceCheckOutput
from langchain_core.runnables import RunnableConfig
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import SystemMessage, AIMessage
from app.core.logging import logger

from app.langgraph.utils.history import get_wise_history, get_last_human_message

async def relevance_check(state: AgentState, config: RunnableConfig):
    """Classifies if the query is SQL-related or general chat."""
    logger.info("Calling Relevance_check")
    try:
        llm_service = config["configurable"]["llm"] 
        llm_runnable = llm_service.get_llm(structured=True, output_schema=RelevanceCheckOutput)
        
        history = get_wise_history(state["messages"], last_n=5)
        user_msg = get_last_human_message(state["messages"])

        parser = JsonOutputParser(pydantic_object=RelevanceCheckOutput)
        format_instructions = parser.get_format_instructions()

        prompt_content = RELEVANCE_PROMPT.format(user_msg=user_msg, format_instructions=format_instructions)
        messages = [SystemMessage(content=prompt_content)] + history
        
        res, msg = await llm_service.ainvoke(llm_runnable, messages, output_schema=RelevanceCheckOutput, config=config)
        
        usage = getattr(msg, "usage_metadata", None)
        clean_msg = AIMessage(content="", usage_metadata=usage)
        
        return {"relevance": res.relevance, "messages": [clean_msg]}

        
    except Exception as e:
        logger.error(f"Error in relevance_check: {e}")
        return {"relevance": "irrelevant"} 
