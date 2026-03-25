import requests
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain.tools import tool

# load_dotenv(Path(__file__).parent.parent.parent / ".env")
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

sys.path.append(str(Path(__file__).parent.parent))

from rag.retriever import retrieve_relevant_chunks, format_context

# tool -> realtime stock data
@tool
def get_stock_data(ticker: str) -> str:
    """
    finds out realtime stock data for given ticker symbol.
    use this when user asks about current stock price, performance, or market data for a specific company.
    Arguments : 
                ticker : stock ticker symbol e.g. AAPL, MSFT, TSLA
    Returns :
                current price, change, volume and other market data
    """
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return "error : alpha vantage api key not found"
    
    # api endpoinnt for alpha vantage
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        quote = data.get("Global Quote", {})

        if not quote:
            return f"no data found for {ticker}."
        
        result = f"""
            Stock Data for {ticker}:
            - Price:          ${quote.get('05. price', 'N/A')}
            - Change:         {quote.get('09. change', 'N/A')} ({quote.get('10. change percent', 'N/A')})
            - Open:           ${quote.get('02. open', 'N/A')}
            - High:           ${quote.get('03. high', 'N/A')}
            - Low:            ${quote.get('04. low', 'N/A')}
            - Volume:         {quote.get('06. volume', 'N/A')}
            - Latest Trading: {quote.get('07. latest trading day', 'N/A')}
                    """
        return result.strip()
    
    except requests.exceptions.Timeout:
        return "error: req timed out. try again"
    except Exception as e:
        return f"error fetching data : {str(e)}"


# tool : RAG searcch over pdfs
@tool
def search_financial_documents(query: str) -> str:
    """
    Searches through ingested financial pdf documents (10-Ks, earnings reports) to find relevant information.
    Use this when the user asks about : 
    - company financials, revenue, profit, expenses
    - business risks, strategies, or outlook
    - any question that requires information from annual reports

    Arguments :
                query : question or topic to search for in the documnets
    Returns :
                relevant excerpts from financial documents
    """
    chunks = retrieve_relevant_chunks(query, top_k=4)
    if not chunks:
        return "no relevant documents found. make sure pdfs have been ingested."
    return format_context(chunks)