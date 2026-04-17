from app.langgraph.schema import AgentState
from app.langgraph.schema import SQLGeneratorOutput
from app.langgraph.constants.prompts import SQL_GENERATOR_PROMPT
from app.langgraph.schema import SQLGeneratorOutput
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage
from app.core.logging import logger
from langchain_core.runnables import RunnableConfig


from app.langgraph.utils.history import get_wise_history

async def sql_generator(state:AgentState,config:RunnableConfig):
   logger.info("Calling SQL Generator Node")
   try:
      history = get_wise_history(state["messages"], last_n=10)
      
      relevant_tables = state["tables"]
      db = config["configurable"]["db"]
      llm_wrapper = config["configurable"]["llm"]
      
      schema = await db.get_schemas_async(relevant_tables)
      
      llm_runnable = llm_wrapper.get_llm(structured=True,output_schema=SQLGeneratorOutput)
      system_prompt = SQL_GENERATOR_PROMPT.format(schema=schema)
      
      messages = [SystemMessage(content=system_prompt)] + history
      
      res, msg = await llm_wrapper.ainvoke(llm_runnable, messages, output_schema=SQLGeneratorOutput, config=config)
      
      usage = getattr(msg, "usage_metadata", None)
      clean_msg = AIMessage(content="", usage_metadata=usage)
      
      return {"sql_query": res.sql_query, "messages": [clean_msg]}

   except Exception as e:
      logger.error(f"Error in Sql Generator: {e}")
      return {"sql_query":""}
