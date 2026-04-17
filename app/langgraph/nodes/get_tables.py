from app.langgraph.schema import AgentState
from langchain_core.runnables import RunnableConfig
from langchain_core.output_parsers import JsonOutputParser
from app.langgraph.schema import TableIdentifierOutput
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage
from app.langgraph.constants.prompts import GET_TABLES_PROMPT
from app.langgraph.utils.history import get_last_human_message
from app.core.logging import logger



async def get_tables(state:AgentState,config:RunnableConfig):
    logger.info("Calling Get Tables Node")
    try:
        user_msg = get_last_human_message(state["messages"])
        db = config["configurable"]["db"]
        llm_service = config["configurable"]["llm"]
        
        tables = await db.get_tables_async() or []
        
        formatted_tables = "\n".join(tables)
        llm_runnable = llm_service.get_llm(structured=True,output_schema=TableIdentifierOutput)
        get_tables_prompt = GET_TABLES_PROMPT.format(formatted_tables=formatted_tables)
        
        res, msg = await llm_service.ainvoke(
            llm_runnable, 
            [SystemMessage(content=get_tables_prompt), HumanMessage(content=user_msg)], 
            output_schema=TableIdentifierOutput,
            config=config
        )
        
        usage = getattr(msg, "usage_metadata", None)
        clean_msg = AIMessage(content="", usage_metadata=usage)
        
        return {"tables": res.tables, "messages": [clean_msg]}
    except Exception as e:
        logger.error(f"Error in get_tables: {e}")
        return {"tables": [], "error": str(e)}
    