import sys 
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))

load_dotenv(Path(__file__).parent.parent.parent / ".env")

from db.mongo import conversations_collection

from langchain_core.messages import HumanMessage, AIMessage

def save_message(session_id: str, role: str, content: str):
    """
    saves a single msg to mongodb
    session id groups msgs into one convo
    role is either human or ai
    """
    conversations_collection.insert_one({"session_id": session_id, 
                                         "role": role, 
                                         "content": content, 
                                         "timestamp": datetime.now(tz=None)})
    
def load_chat_history(session_id: str) -> list:
    """
    loads previous msgs for a session from mongodb
    then converts them into lnagchain msg objects 
    """
    messages = conversations_collection.find({"session_id": session_id}, sort=[("timestamp", 1)])

    history = []
    for msg in messages:
        if msg["role"] == "human":
            history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "ai":
            history.append(AIMessage(content=msg["content"]))

    return history

def clear_session(session_id: str):
    """deletes all msgs for givn session id"""
    conversations_collection.delete_many({"session_id": session_id})