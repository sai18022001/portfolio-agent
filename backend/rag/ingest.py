import os
import sys
from pathlib import Path
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))
from db.mongo import documents_collection

load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Load the embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# extract text from pdf
def extract_text_from_pdf(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    return full_text

# split text into chunks.
def split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    splits a long text into smaller overlapping chunks
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
    return chunks

# embed chunks then store in mongodb
def ingest_pdf(pdf_path: str, company_name: str):
    """
    for one pdf : extract text -> split into chunks -> embed each chunks -> save to mongodb
    """

    text = extract_text_from_pdf(pdf_path)
    chunks = split_into_chunks(text)

    stored = 0
    for i, chunk in enumerate(chunks):
        # text to vector
        embedding = embedder.encode(chunk).tolist()

        doc = {
            "company": company_name,
            "source": os.path.basename(pdf_path),
            "chunk_index": i,
            "text": chunk,
            "embedding": embedding
        }

        exists = documents_collection.find_one({"source": doc["source"], "chunk_index": i})

        if not exists:
            documents_collection.insert_one(doc)
            stored += 1

    print(f"stored {stored} new chunks for {company_name}")

def ingest_all_pdfs():
    """scans the pdfs/data folder then ingest every pdf found """
    pdf_dir = Path(__file__).parent.parent / "data" / "pdfs"
    print(f"looking for pdfs in {pdf_dir}")
    print(f"folder exists: {pdf_dir.exists()}")
    if not pdf_dir.exists():
        print(f"pdf folder not found : {pdf_dir}")
        return
    
    pdf_files = list(pdf_dir.glob("*pdf"))
    if not pdf_files:
        print("No PDFs found in data/pdfs/")
        return 
    print(f"found {len(pdf_files)} pdfs to ingest")

    for pdf_path in pdf_files:
        company_name = pdf_path.stem
        ingest_pdf(str(pdf_path), company_name)

    print("\nall pdfs ingested")
    print(f"total chunks in db: {documents_collection.count_documents({})}")

if __name__ == "__main__":
        ingest_all_pdfs()