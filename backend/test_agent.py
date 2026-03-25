import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from agent.agent import create_agent
from agent.memory import save_message, load_chat_history

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

def chat(session_id: str, user_input: str):
    history = load_chat_history(session_id)
    agent = create_agent()
    
    print(f"\nYou : {user_input}")

    response = agent.invoke({"input": user_input, "chat_history": history})

    answer = extract_text(response["output"])

    save_message(session_id, "human", user_input)
    save_message(session_id, "ai", answer)

    print(f"\nAgent : {answer}")
    return answer

if __name__ == "__main__":
    import time
    from agent.memory import clear_session
    session_id = "test-session-2"
    clear_session(session_id)

    chat(session_id, "What are Apple's main business risks according to their 10-K?")
    time.sleep(15)
    chat(session_id, "What is Apple's current stock price?")
    time.sleep(15)
    chat(session_id, "Given that stock price and those risks, how would you assess Apple's current risk profile?")