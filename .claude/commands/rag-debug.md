---
description: Re-index underwriting policies and test RAG retrieval with a sample query
---

Debug the RAG pipeline end to end:

1. Run `backend/rag/rag_setup.py` to (re)build the ChromaDB index from `backend/policies/underwriting_policies.pdf`.
2. Run `backend/rag/demo_query_retrieval.py` (or `example_usage.py` if that's missing) with a sample underwriting question, e.g. "What is the minimum credit score for conventional loan approval?"
3. Print the retrieved chunks and similarity scores.
4. Flag anything that looks wrong: empty results, low similarity scores across the board, or the index directory (`CHROMA_PERSIST_DIRECTORY` from `.env`) not being created.

If `OPENAI_API_KEY` is missing from `backend/.env`, stop and tell the user to set it — embeddings require it.
