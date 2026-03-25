import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))


def test_stock_tool_bad_ticker():
    """Stock tool should handle unknown tickers gracefully"""
    from agent.tools import get_stock_data
    with patch("agent.tools.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"Global Quote": {}}
        result = get_stock_data.invoke({"ticker": "INVALIDTICKER"})
        assert "No data found" in result or "no data" in result.lower()


def test_rag_tool_no_results():
    """RAG tool should handle empty DB gracefully"""
    from agent.tools import search_financial_documents
    with patch("agent.tools.retrieve_relevant_chunks") as mock_retrieve:
        mock_retrieve.return_value = []
        result = search_financial_documents.invoke({"query": "test query"})
        assert "no relevant documents" in result