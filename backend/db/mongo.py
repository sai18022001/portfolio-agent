from pymongo import MongoClient
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(Path(__file__).parent.parent.parent / ".env")

client = MongoClient(os.getenv("MONGODB_URI"))

db = client[os.getenv("DB_NAME")]

# - 'documents' stores the embedded PDF chunks
# - 'conversations' stores chat history
documents_collection = db["documents"]
conversations_collection = db["conversations"]

def get_db():
    """Returns the database instance - used by other files"""
    return db