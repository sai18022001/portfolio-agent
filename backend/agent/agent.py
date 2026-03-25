import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

sys.path.append(str(Path(__file__).parent.parent))

from agent.tools import get_stock_data, search_financial_documents

# load_dotenv(Path(__file__).parent.parent.parent / ".env")


# system prompt define
SYSTEM_PROMPT = """You are an expert AI financial research assistant with access to:
1. Real-time stock market data
2. A library of financial documents including 10-K annual reports and earnings reports

Your job is to help users understand their portfolio, analyze company financials, 
and assess risks based on both live market data and official financial documents.

Guidelines:
- Always use search_financial_documents when asked about fundamentals, risks, or strategies
- Always use get_stock_data when asked about current price or market performance
- For complex questions, use BOTH tools and synthesize the information
- Be specific and cite which documents or data you're drawing from
- Format responses clearly with sections when answering complex questions
"""

# gemini
def get_llm():
    """creates and resturns gemini llm instance"""
    return ChatGoogleGenerativeAI(model="gemini-3-flash-preview", api_key=os.getenv("GEMINI_API_KEY"), temperature=0.3)

# Groq
# def get_llm():
#     """creates and returns Groq Llama 3 instance"""
#     return ChatGroq(
#         model="llama-3.3-70b-versatile", 
#         api_key=os.getenv("GROQ_API_KEY"), 
#         temperature=0.3
#     )

def get_prompt():
    """
    prompt template using ChatPromptTemplate and MessagePlaceholder
    gets filled with chat_history and agent_scratchpad   
    """
    return ChatPromptTemplate.from_messages([("system", SYSTEM_PROMPT), 
                                             MessagesPlaceholder(variable_name="chat_history"), 
                                             ("human", "{input}"),
                                             MessagesPlaceholder(variable_name="agent_scratchpad")
                                             ])

# agent creation
def create_agent():
    """
    get all pieces together to run agent
    LLM : Gemini
    Tools : stock data n RAG search
    prompt : system instructions 
    AgentExecutor : manages tool calls in a loop
    """
    llm = get_llm()
    tools = [get_stock_data, search_financial_documents]
    prompt = get_prompt()

    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=8, max_execution_time=60, handle_parsing_errors=True, return_only_outputs=True, early_stopping_method="generate")
    return executor