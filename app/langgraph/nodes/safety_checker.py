import re
from app.langgraph.schema import AgentState, SafetyCheckOutput
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from app.core.logging import logger
from langchain_core.runnables import RunnableConfig
from app.langgraph.constants.prompts import SAFETY_CHECK_PROMPT

async def safety_checker(state: AgentState, config: RunnableConfig):
    """Safety Check for the SQL Query using Regex and LLM."""
    logger.info("Calling Safety Checker")
    
    sql_query = state.get("sql_query", "")
    if not sql_query:
        return {"is_safe": False, "safety_reason": "No SQL query generated."}

    forbidden_patterns = [
        r"\bDROP\b", r"\bDELETE\b", r"\bUPDATE\b", r"\bINSERT\b", r"\bTRUNCATE\b",
        r"\bALTER\b", r"\bCREATE\b", r"\bGRANT\b", r"\bREVOKE\b"
    ]
    
    for pattern in forbidden_patterns:
        if re.search(pattern, sql_query, re.IGNORECASE):
            logger.warning(f"Safety Check Failed (Regex): Forbidden keyword found in query: {sql_query}")
            return {"is_safe": False, "safety_reason": f"Forbidden keyword detected by regex."}

    trimmed_query = sql_query.strip()
    if trimmed_query.count(";") > 1 or (trimmed_query.count(";") == 1 and not trimmed_query.endswith(";")):
        logger.warning(f"Safety Check Failed (Regex): Multiple statements or mid-query semicolon detected: {sql_query}")
        return {"is_safe": False, "safety_reason": "Multiple SQL statements are not allowed."}
    try:
        llm_service = config["configurable"]["llm"]
        safety_runnable = llm_service.get_llm(structured=True, output_schema=SafetyCheckOutput)
        
        prompt = SAFETY_CHECK_PROMPT.format(sql_query=sql_query)
         
        res, msg = await llm_service.ainvoke(safety_runnable, [HumanMessage(content=prompt)], config=config)
        
        usage = getattr(msg, "usage_metadata", None)
        clean_msg = AIMessage(content="", usage_metadata=usage)

        if not res.is_safe:
            logger.warning(f"Safety Check Failed (LLM): {res.reason}")
        
        return {
            "is_safe": res.is_safe, 
            "safety_reason": res.reason if not res.is_safe else "",
            "messages": [clean_msg]
        }

    except Exception as e:
        logger.error(f"Error in Safety Checker LLM check: {e}")
        return {"is_safe": False, "safety_reason": "Safety validation system error."}
    