import os
import sys
import uuid
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.append(str(Path(__file__).parent))
from agent.agent import create_agent
from agent.memory import save_message, load_chat_history, clear_session

app = FastAPI(title="Portfolio Research Agent", description="AI agent for financial research using RAG and live market data", version="1.0.0")

app.add_middleware(CORSMiddleware, 
                   allow_origins=["http://localhost:3000", "http://localhost:5173"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],)

class ChatRequest(BaseModel):
    message : str
    session_id : str | None = None

class ChatResponse(BaseModel):
    answer : str
    session_id : str

def extract_text(raw) -> str:
    if isinstance(raw, str):
        return raw
    if isinstance(raw, list):
        parts = []
        for block in raw:
            if isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        return " ".join(parts).strip()
    return str(raw)


# ----- routes -----
@app.get("/")
def root():
    return {"status": "running", "message": "Portfolio Research Agent API"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint

    Accepts : {"message": "What are Apple's risks ?", "session_id" : "465413" }
    Returns : {"answer" : "....", "session_id": "465413" }
    """
    try:
        session_id = request.session_id or str(uuid.uuid4())
        history = load_chat_history(session_id)
        agent = create_agent()
        response = agent.invoke({"input": request.message, "chat_history": history})
        answer = extract_text(response["output"])
        if "agent stopped" in answer.lower() or answer.strip() == "":
            answer = (  "I need more information to answer that fully. "
                        "Could you ask about a specific company or metric? "
                        "For example: 'What did Apple say about AI in their 10-K?'")
        save_message(session_id, "human", request.message)
        save_message(session_id, "ai", answer)
        return ChatResponse(answer=answer, session_id=session_id)
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            raise HTTPException(status_code=429, detail="API rate limit reached for the day.")
        raise HTTPException(status_code=500, detail=error_msg)

@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    """clears convo history for a session
        uused for New Chat button
    """
    clear_session(session_id)
    return {"message" : f"Session {session_id} deleted."}

@app.get("/session/{session_id}/history")
def get_history(session_id: str):
    """returns full chat histiry for a session"""
    from db.mongo import conversations_collection
    messages = list(conversations_collection.find({"session_id":session_id},{"_id":0,"role":1,"content":1,"timestamp":1},sort=[("timestamp",1)]))
    return {"session_id": session_id, "messages":messages}