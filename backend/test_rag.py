from rag.retriever import retrieve_relevant_chunks, format_context

query = "What is Apple's revenue risk given current stock performance?"
chunks = retrieve_relevant_chunks(query, top_k=3)
print(format_context(chunks))