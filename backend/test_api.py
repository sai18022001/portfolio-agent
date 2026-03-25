# backend/test_api.py
import requests

BASE = "http://localhost:8000"
SESSION = "api-test-001"

def chat(message: str):
    response = requests.post(f"{BASE}/chat", json={
        "message": message,
        "session_id": SESSION
    })
    data = response.json()
    print(f"\nYou: {message}")
    print(f"Agent: {data['answer']}")
    print(f"Session: {data['session_id']}")
    return data

# Test 1: Basic question
chat("What are Apple's main business risks?")

# Test 2: Follow-up (tests memory over HTTP)
chat("What is Apple's current stock price?")

# Test 3: Clear session
requests.delete(f"{BASE}/session/{SESSION}")
print(f"\nSession {SESSION} cleared.")

# Test 4: After clearing — agent has no memory
chat("What did we just discuss?")