import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)


def test_health_check():
    """API should return running status"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_chat_requires_message():
    """Chat endpoint should reject empty requests"""
    response = client.post("/chat", json={})
    assert response.status_code == 422


def test_session_history_empty():
    """New session should return empty history"""
    response = client.get("/session/nonexistent-session-123/history")
    assert response.status_code == 200
    assert response.json()["messages"] == []


def test_delete_session():
    """Delete session should return success"""
    response = client.delete("/session/test-session-abc")
    assert response.status_code == 200


@patch("main.create_agent")
@patch("main.load_chat_history")
@patch("main.save_message")
def test_chat_endpoint(mock_save, mock_history, mock_agent):
    """Chat endpoint should return answer and session_id"""

    mock_history.return_value = []
    mock_executor = MagicMock()
    mock_executor.invoke.return_value = {"output": "Apple's main risks are..."}
    mock_agent.return_value = mock_executor

    response = client.post("/chat", json={
        "message": "What are Apple's risks?",
        "session_id": "ci-test-session"
    })

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "session_id" in data
    assert data["answer"] == "Apple's main risks are..."
    assert data["session_id"] == "ci-test-session"