import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))

load_dotenv(Path(__file__).parent.parent.parent / ".env")

from db.mongo import documents_collection

embedder = SentenceTransformer("all-MiniLM-L6-v2")

def cosine_similarity(vec1: list, vec2: list) -> float:
    """
    measures how similar two vectors are.
    returns number b/w 0 (unrelated) and 1 (identicl meaning)
    """
    a = np.array(vec1)
    b = np.array(vec2)
    return float(np.dot(a, b) / np.linalg.norm(a) * np.linalg.norm(b))

def retrieve_relevant_chunks(query: str, top_k: int = 5) -> list[dict]:
    """
    finds top k most relevnt pdf chunks when user asks query
    embed query into a vector -> load all stored chunks on mongodb -> score chunks using cosine simi -> return top k
    """

    query_embedding = embedder.encode(query).tolist()
    all_docs = list(documents_collection.find({}, {
        "text": 1, "company": 1, "source": 1, "embedding": 1
    }))

    if not all_docs:
        return []
    
    scored = []
    for doc in all_docs:
        score = cosine_similarity(query_embedding, doc["embedding"])
        scored.append({
            "text": doc["text"], "company": doc["company"], "source": doc["source"], "score": score
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]

def format_context(chunks: list[dict]) -> str:
    """
    Formats retrieved chunks into a clean string
    that gets passed to the LLM as context.
    """
    if not chunks:
        return "No relevant documents found."

    context = ""
    for i, chunk in enumerate(chunks, 1):
        context += f"\n[Source {i}: {chunk['company']} — {chunk['source']}]\n"
        context += chunk["text"] + "\n"
        context += "-" * 50 + "\n"
    return context