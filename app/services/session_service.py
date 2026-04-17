import json
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict
from app.core.logging import logger

class SessionService:
    def __init__(self, db_pool):
        self.db_pool = db_pool
    
    async def setup(self):
        """Initialize the chat_session and chat_messages tables."""
        query = """
        CREATE TABLE IF NOT EXISTS chat_session (
            session_id UUID PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            thread_id UUID NOT NULL,
            title TEXT,
            metadata JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS chat_messages (
            id SERIAL PRIMARY KEY,
            session_id UUID REFERENCES chat_session(session_id) ON DELETE CASCADE,
            role VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            additional_kwargs JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        async with self.db_pool.acquire() as conn:
            await conn.execute(query)
            logger.info("Chat history tables checked/created.")

    async def execute(self, query, *args):
        async with self.db_pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query, *args):
        async with self.db_pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def create_or_update_session(self, user_id: str, thread_id: str, session_id: str, title: str = "New Chat"):
        """Ensures a session exists in the chat_session table."""
        query = """
        INSERT INTO chat_session (session_id, user_id, thread_id, title)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (session_id) DO UPDATE 
        SET updated_at = CURRENT_TIMESTAMP, title = EXCLUDED.title
        """
        await self.execute(query, session_id, user_id, thread_id, title)
    
    async def add_message(self, session_id: str, role: str, content: str, kwargs: dict = None):
        """Store a single message in the chat_messages table."""
        await self.execute(
            "INSERT INTO chat_messages (session_id, role, content, additional_kwargs) VALUES ($1, $2, $3, $4)",
            session_id, role, content, json.dumps(kwargs or {})
        )
    
    async def get_clean_history(self, session_id: str, limit: int = 20):
        """Retrieve clean history for UI/display."""
        return await self.fetch(
            "SELECT role, content, created_at FROM chat_messages WHERE session_id = $1 ORDER BY created_at ASC LIMIT $2",
            session_id, limit
        )

    async def delete_session(self, session_id: str):
        await self.execute("DELETE FROM chat_session WHERE session_id = $1", session_id)