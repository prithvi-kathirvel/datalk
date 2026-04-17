from app.core.config import get_settings
from app.utils.models import llm_models
from langchain_core.language_models import BaseChatModel
from app.core.logging import logger
from tenacity import retry,stop_after_attempt,wait_fixed,retry_if_exception_type,before_sleep_log 
from app.core.logging import llm_retry_logger
from app.core.config import get_settings
from openai import (
    APIError,
    APITimeoutError,
    OpenAIError,
    RateLimitError,
)
from langchain_core.output_parsers import JsonOutputParser

settings = get_settings()
class LLMRegistryService:
    LLMS = llm_models
    @classmethod
    def get(cls, model_name: str) -> BaseChatModel:
        model_entry = None
        for entry in cls.LLMS:
            if entry["name"] == model_name:
                model_entry = entry
                break

        if not model_entry:
            available_models = [entry["name"] for entry in cls.LLMS]
            raise ValueError(
                f"model '{model_name}' not found in registry. available models: {', '.join(available_models)}"
            )

        logger.debug("using_default_llm_instance", model_name=model_name)
        return model_entry["llm"] 
    
    @classmethod
    def get_available_models(cls):
        return [{"name":entry["name"],"provider":entry["provider"]} for entry in cls.LLMS] 



class LLMService:
    def __init__(self,model_name:str):
        self.model_name = model_name
        self.llm = LLMRegistryService.get(model_name)

    def get_llm(self, structured: bool = False, output_schema=None):
        if self.model_name == "meta/llama-3.3-70b-instruct":
            parser = JsonOutputParser(pydantic_object=output_schema)
            def inject_instructions(input_vars):
                return f"{input_vars}\n\n{parser.get_format_instructions()}"

            return inject_instructions | self.llm | parser
        if structured:
            return self.llm.with_structured_output(output_schema, include_raw=True)
        return self.llm

    @retry(
        stop=stop_after_attempt(settings.MAX_RETRY_ATTEMPTS),
        wait=wait_fixed(settings.RETRY_DELAYS),
        retry=retry_if_exception_type((RateLimitError, APITimeoutError, APIError)),
        before_sleep=llm_retry_logger,
        reraise=True
    )
    async def ainvoke(self, llm_runnable, messages, output_schema=None, config=None):
        """Invoke LLM and return both the parsed result and the original message."""
        response = await llm_runnable.ainvoke(messages, config=config)
        
        if isinstance(response, dict) and "raw" in response:
            return response["parsed"], response["raw"]
        
        if isinstance(response, dict) and output_schema:
            try:
                parsed_obj = output_schema(**response)
                from langchain_core.messages import AIMessage
                import json
                msg = AIMessage(content=json.dumps(response))
                return parsed_obj, msg
            except Exception:
                return response, response

        return response, response

    @retry(
        stop=stop_after_attempt(settings.MAX_RETRY_ATTEMPTS),
        wait=wait_fixed(settings.RETRY_DELAYS),
        retry=retry_if_exception_type((RateLimitError, APITimeoutError, APIError)),
        before_sleep=llm_retry_logger
    )    
    def invoke(self,messages:list):
        if not isinstance(messages,list):
            messages = [HumanMessage(content=messages)]
        
        return  self.llm.invoke(messages)
