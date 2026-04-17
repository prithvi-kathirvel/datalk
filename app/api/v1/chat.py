from fastapi import APIRouter,Depends,Request
from app.core.middleware import get_current_user
from app.services import user_service
from app.services.user_service import fetch_database_details_by_user_id
from app.schema.model import ChatInputSchema
from app.langgraph.graph import execute_graph
from app.api.v1.deps import get_graph,get_db_pool,get_session_service

chat_router = APIRouter(dependencies=[Depends(get_current_user)])

@chat_router.post("/chat")
async def chat(user_input:ChatInputSchema ,user=Depends(get_current_user),graph=Depends(get_graph),db_pool=Depends(get_db_pool), session_service=Depends(get_session_service)):
    
    db_details = await fetch_database_details_by_user_id(user)
    if len(db_details)==0:
        return {"message":"No Database Configuration was registered for this User"}
    
    result = await execute_graph(user_input,db_details[0],graph,db_pool, session_service)
    return {"message":"Hi Chat","user":user,"db_details":db_details,"table":result}


@chat_router.get("/history")
async def get_clean_history(session_id:str, session_service=Depends(get_session_service)):
    """Retrieves history from the dedicated chat_messages table."""
    return await session_service.get_clean_history(session_id)



