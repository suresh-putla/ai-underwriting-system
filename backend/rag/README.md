# RAG Setup Module

This module provides a comprehensive RAG (Retrieval Augmented Generation) setup for the LOUS loan origination system.

## Features

- ✅ PDF document loading (single file or directory)
- ✅ Customizable text chunking with configurable chunk size and overlap
- ✅ OpenAI embeddings generation
- ✅ ChromaDB vector storage with persistence
- ✅ Similarity search with scores
- ✅ Add documents to existing vector stores
- ✅ Retriever interface for LangChain chains

## Installation

Install the required dependencies:

```bash
cd backend
pip install -r requirements.txt
```

## Environment Setup

### Option 1: Automatic Setup (Recommended)

Run the setup helper script:

```bash
cd backend/rag
python setup_env.py
```

This will guide you through setting up your `.env` file with your OpenAI API key.

### Option 2: Manual Setup

1. Copy the example file:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. Edit `.env` and add your OpenAI API key:
   ```bash
   OPENAI_API_KEY=sk-your_actual_openai_api_key_here
   ```

### Check Environment Status

```bash
python setup_env.py --check
```

**Note:** The RAG module automatically loads the `.env` file using `python-dotenv`.

## Usage

### Basic Setup

```python
from rag.rag_setup import RAGSetup

# Initialize with custom parameters
rag = RAGSetup(
    chunk_size=1000,        # Size of text chunks
    chunk_overlap=200,      # Overlap between chunks
    persist_directory="./chroma_db",
    collection_name="loan_documents"
)
```

### Process a Single PDF

```python
# Complete setup from a single PDF
vectorstore = rag.setup_from_pdf("path/to/document.pdf")

# Perform similarity search
results = rag.similarity_search("What are the loan requirements?", k=3)
for doc in results:
    print(doc.page_content)
```

### Process a Directory of PDFs

```python
# Process all PDFs in a directory
vectorstore = rag.setup_from_directory("./data/loan_documents")

# Search with relevance scores
results = rag.similarity_search_with_score("underwriting criteria", k=5)
for doc, score in results:
    print(f"Score: {score}")
    print(doc.page_content)
```

### Load Existing Vector Store

```python
# Load previously created vector store
vectorstore = rag.load_existing_vectorstore()

# Continue searching
results = rag.similarity_search("credit score requirements")
```

### Add Documents to Existing Store

```python
# Load existing store
rag.load_existing_vectorstore()

# Load and process new documents
new_docs = rag.load_pdf("path/to/new_document.pdf")
new_chunks = rag.chunk_documents(new_docs)

# Add to existing store
rag.add_documents_to_vectorstore(new_chunks)
```

### Get Retriever for LangChain

```python
# Get retriever interface
retriever = rag.get_retriever(
    search_type="similarity",  # or "mmr", "similarity_score_threshold"
    search_kwargs={"k": 4}
)

# Use with LangChain chains
docs = retriever.get_relevant_documents("query text")
```

## Parameters

### Initialization Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `chunk_size` | int | 1000 | Size of text chunks in characters |
| `chunk_overlap` | int | 200 | Number of overlapping characters between chunks |
| `persist_directory` | str | "./chroma_db" | Directory to persist ChromaDB data |
| `collection_name` | str | "loan_documents" | Name of the ChromaDB collection |
| `openai_api_key` | str | None | OpenAI API key (reads from env if not provided) |

### Chunk Size Guidelines

- **Small chunks (500-800)**: Better for precise matching, more chunks to search
- **Medium chunks (1000-1500)**: Balanced approach, good for most use cases
- **Large chunks (2000+)**: More context per chunk, fewer chunks to search

### Chunk Overlap Guidelines

- **10-20% of chunk size**: Standard recommendation
- **Larger overlap**: Better continuity but more redundancy
- **Smaller overlap**: Less redundancy but potential information loss at boundaries

## Class Methods

### Document Loading
- `load_pdf(pdf_path)` - Load a single PDF file
- `load_pdfs_from_directory(directory_path)` - Load all PDFs from a directory

### Document Processing
- `chunk_documents(documents)` - Split documents into chunks

### Vector Store Operations
- `create_vectorstore(chunks)` - Create new vector store from chunks
- `load_existing_vectorstore()` - Load existing vector store
- `add_documents_to_vectorstore(chunks)` - Add chunks to existing store
- `delete_collection()` - Delete the collection

### Search Operations
- `similarity_search(query, k)` - Search for similar documents
- `similarity_search_with_score(query, k)` - Search with relevance scores
- `get_retriever(search_type, search_kwargs)` - Get LangChain retriever

### Complete Setup
- `setup_from_pdf(pdf_path)` - One-step setup from single PDF
- `setup_from_directory(directory_path)` - One-step setup from directory

## Example Workflow

```python
# 1. Initial setup with loan policy documents
rag = RAGSetup(chunk_size=1200, chunk_overlap=250)
rag.setup_from_directory("./data/loan_policies")

# 2. Search for relevant information
results = rag.similarity_search_with_score(
    "What are the minimum credit score requirements?",
    k=5
)

# 3. Later, add new documents
rag.load_existing_vectorstore()
new_docs = rag.load_pdf("./data/new_policy.pdf")
chunks = rag.chunk_documents(new_docs)
rag.add_documents_to_vectorstore(chunks)

# 4. Use with LangChain for RAG pipeline
retriever = rag.get_retriever(search_kwargs={"k": 4})
# Pass retriever to your LangChain QA chain
```

## Notes

- ChromaDB data is persisted to disk for reuse across sessions
- Embeddings are generated using OpenAI's embedding model
- The vector store automatically handles document metadata
- Use `delete_collection()` carefully as it permanently removes all data

## Troubleshooting

**Issue**: `ValueError: OpenAI API key must be provided`
- **Solution**: Set `OPENAI_API_KEY` in your environment or `.env` file

**Issue**: `FileNotFoundError: PDF file not found`
- **Solution**: Verify the file path is correct and the file exists

**Issue**: Out of memory with large PDFs
- **Solution**: Reduce `chunk_size` or process PDFs one at a time

## Integration with LOUS

This RAG module can be integrated with the LOUS loan origination system to:
- Retrieve relevant loan policies during underwriting
- Answer questions about loan requirements
- Provide context for AI agents making loan decisions
- Support document-based loan application processing
