from app.langgraph.schema import AgentState
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage
from app.core.logging import logger
from langchain_core.runnables import RunnableConfig
from app.langgraph.schema import AIResponse
from app.langgraph.constants.prompts import RESPONSE_GENERATOR_PROMPT

from app.langgraph.utils.history import get_wise_history

async def response_generator(state:AgentState,config:RunnableConfig):
    try:
        logger.info("Calling Response Generator")
        
        # 1. Check if the query was flagged as unsafe
        if not state.get("is_safe", True):
            reason = state.get("safety_reason", "Potential security risk detected.")
            response = f"I cannot execute this request. Reason: {reason}"
            return {"final_response": response, "messages": [AIMessage(content=response)]}

        sql_query = state.get("sql_query", "")
        if not sql_query:
            return {"final_response": "I couldn't generate a valid query for your request.", "messages": []}

        db = config["configurable"]["db"]
        llm_wrapper = config["configurable"]["llm"]
        
        # 2. FIX: Use async execution
        query_result = await db.execute_async(sql_query)
        
        history = get_wise_history(state["messages"], last_n=5)
        
        llm = llm_wrapper.get_llm(structured=True,output_schema=AIResponse)
        system_prompt = RESPONSE_GENERATOR_PROMPT.format(query_result=query_result)
        
        messages = [SystemMessage(content=system_prompt)] + history + [
            HumanMessage(content=f"SQL executed: {sql_query}\nResult: {query_result}")
        ]
        
        # 3. FIX: Pass config for tracing
        res, msg = await llm_wrapper.ainvoke(llm, messages, output_schema=AIResponse, config=config)
        
        usage = getattr(msg, "usage_metadata", None)
        clean_msg = AIMessage(content=res.response, usage_metadata=usage)
        
        return {
            "final_response": res.response, 
            "messages": [clean_msg],
            "query_results": query_result # Optionally store results in state
        }

    except Exception as e:
        logger.error(f"Error in Response Generator: {e}")
        return {"final_response":"I encountered an error while processing the database results.","messages":state["messages"]}