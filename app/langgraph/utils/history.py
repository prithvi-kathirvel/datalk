from typing import List, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, trim_messages
from app.core.logging import logger

def get_wise_history(messages: List[BaseMessage], max_tokens: int = 3000, last_n: int = 10) -> List[BaseMessage]:
    """
    Returns a 'wise' subset of history:
    1. Keeps the system message (if any).
    2. Keeps the last 'n' messages.
    3. Trims based on token count as a safety measure.
    """
    if not messages:
        return []

    valid_messages = [
        m for m in messages 
        if not (isinstance(m, AIMessage) and not m.content.strip())
    ]

    system_msg = [m for m in valid_messages if isinstance(m, SystemMessage)]
    other_msgs = [m for m in valid_messages if not isinstance(m, SystemMessage)]

    selected_msgs = other_msgs[-last_n:] if len(other_msgs) > last_n else other_msgs

    final_msgs = system_msg + selected_msgs
    
    return final_msgs

def format_history_for_prompt(messages: List[BaseMessage]) -> str:
    """Formats history into a string for LLMs that don't take message lists directly."""
    formatted = []
    for m in messages:
        role = "User" if isinstance(m, HumanMessage) else "Assistant"
        if m.content.strip():
            formatted.append(f"{role}: {m.content}")
    return "\n".join(formatted)

def get_last_human_message(messages: List[BaseMessage]) -> str:
    """Extracts the most recent user message from the message history."""
    for m in reversed(messages):
        if isinstance(m, HumanMessage):
            return m.content
    return ""
