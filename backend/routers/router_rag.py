"""
RAG API Module - REST API for similarity search functionality
Exposes vector similarity search endpoints using FastAPI
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
from pathlib import Path
import json

from rag.rag_setup import RAGSetup
from llm import LLM

# Get absolute paths for directories
BACKEND_DIR = Path(__file__).parent.parent.resolve()
DEFAULT_CHROMA_DIR = BACKEND_DIR / "chroma_db"
DEFAULT_POLICIES_DIR = BACKEND_DIR / "policies"

# Create router
router = APIRouter()

# Global RAG setup instance
rag_setup: Optional[RAGSetup] = None

# Global LLM instance
llm: Optional[LLM] = None


def get_llm() -> LLM:
    """Get or initialize the LLM instance"""
    global llm
    if llm is None:
        try:
            llm = LLM(
                model="claude-sonnet",
                temperature=0.7,
                max_tokens=1500
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize LLM: {str(e)}"
            )
    return llm


class SearchQuery(BaseModel):
    """Request model for similarity search"""
    query: str = Field(..., description="Search query text", min_length=1)
    k: int = Field(default=4, description="Number of results to return", ge=1, le=20)


class DocumentResult(BaseModel):
    """Response model for a document result"""
    page_content: str = Field(..., description="The text content of the document chunk")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata (source, page, etc.)")


class ScoredDocumentResult(BaseModel):
    """Response model for a document result with score"""
    page_content: str = Field(..., description="The text content of the document chunk")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata (source, page, etc.)")
    score: float = Field(..., description="Similarity score (lower is more similar)")


class SearchResponse(BaseModel):
    """Response model for similarity search"""
    query: str
    results: List[DocumentResult]
    count: int


class SearchWithScoreResponse(BaseModel):
    """Response model for similarity search with scores"""
    query: str
    results: List[ScoredDocumentResult]
    count: int


class InitializeRequest(BaseModel):
    """Request model for initializing RAG setup"""
    chunk_size: int = Field(default=1000, description="Size of text chunks", ge=100, le=5000)
    chunk_overlap: int = Field(default=200, description="Overlap between chunks", ge=0, le=1000)
    persist_directory: Optional[str] = Field(default=None, description="Directory to persist ChromaDB (defaults to backend/chroma_db)")
    collection_name: str = Field(default="loan_documents", description="Name of the ChromaDB collection")
    embedding_model: str = Field(default="text-embedding-3-small", description="OpenAI embedding model")
    use_local_embeddings: bool = Field(default=False, description="Use local embeddings instead of OpenAI")


class StatusResponse(BaseModel):
    """Response model for status check"""
    initialized: bool
    vectorstore_loaded: bool
    message: str


class RAGLLMSearchQuery(BaseModel):
    """Request model for RAG + LLM search"""
    query: str = Field(..., description="Search query text", min_length=1)
    k: int = Field(default=4, description="Number of RAG results to retrieve", ge=1, le=20)
    temperature: Optional[float] = Field(default=0.7, description="LLM temperature", ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=1500, description="Maximum tokens in LLM response", ge=100, le=4000)
    system_prompt: Optional[str] = Field(default=None, description="Optional custom system prompt")
    include_sources: bool = Field(default=True, description="Include source documents in response")


def get_rag_setup() -> RAGSetup:
    """Get the RAG setup instance, raise error if not initialized"""
    if rag_setup is None:
        raise HTTPException(
            status_code=503,
            detail="RAG system not initialized. Please call /initialize endpoint first."
        )
    if rag_setup.vectorstore is None:
        raise HTTPException(
            status_code=503,
            detail="Vector store not loaded. Please load or create a vector store first."
        )
    return rag_setup


@router.post("/rag/init", response_model=StatusResponse, summary="Initialize RAG System")
async def initialize(config: InitializeRequest):
    """
    Initialize the RAG system with specified configuration.
    If a collection with the same name exists, it will be deleted and recreated with fresh documents.
    This must be called before using similarity search endpoints.
    """
    global rag_setup

    try:
        # Use absolute path for persist_directory
        persist_dir = config.persist_directory
        if persist_dir is None:
            persist_dir = str(DEFAULT_CHROMA_DIR)
        else:
            # Convert relative paths to absolute paths
            persist_path = Path(persist_dir)
            if not persist_path.is_absolute():
                persist_dir = str(BACKEND_DIR / persist_dir)

        # Use absolute path for policies directory
        policies_dir = str(DEFAULT_POLICIES_DIR)

        # Initialize RAG setup
        rag_setup = RAGSetup(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            persist_directory=persist_dir,
            collection_name=config.collection_name,
            embedding_model=config.embedding_model,
            use_local_embeddings=config.use_local_embeddings
        )

        # Load and chunk documents from policies directory
        try:
            documents = rag_setup.load_pdfs_from_directory(policies_dir)
            chunks = rag_setup.chunk_documents(documents)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load documents from {policies_dir}: {str(e)}"
            )

        # Create collection (deletes existing if present and creates fresh one)
        try:
            rag_setup.create_collection(documents=chunks)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create collection: {str(e)}. This may be due to file permissions or a locked database."
            )

        return StatusResponse(
            initialized=True,
            vectorstore_loaded=True,
            message=f"RAG system initialized successfully. Collection '{config.collection_name}' created at {persist_dir}."
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"Failed to initialize RAG system: {str(e)}")


@router.get("/rag/status", response_model=StatusResponse, summary="Check RAG System Status")
async def get_status():
    """
    Check the current status of the RAG system.
    Returns whether the system is initialized and if a vector store is loaded.
    """
    initialized = rag_setup is not None
    vectorstore_loaded = rag_setup.vectorstore is not None if initialized else False

    if not initialized:
        message = "RAG system not initialized"
    elif not vectorstore_loaded:
        message = "RAG system initialized but vector store not loaded"
    else:
        message = "RAG system ready"

    return StatusResponse(
        initialized=initialized,
        vectorstore_loaded=vectorstore_loaded,
        message=message
    )


@router.post("/rag/search", response_model=SearchResponse, summary="RAG Search")
async def rag_search(search_query: SearchQuery):
    """
    Perform similarity search on the vector store.

    Returns the k most similar document chunks to the query without scores.
    """
    setup = get_rag_setup()

    try:
        results = setup.similarity_search(
            query=search_query.query,
            k=search_query.k
        )

        # Convert Document objects to response model
        document_results = [
            DocumentResult(
                page_content=doc.page_content,
                metadata=doc.metadata
            )
            for doc in results
        ]

        return SearchResponse(
            query=search_query.query,
            results=document_results,
            count=len(document_results)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG search failed: {str(e)}")


@router.post("/rag/search-with-score", response_model=SearchWithScoreResponse, summary="RAG Search with Scores")
async def rag_search_with_score(search_query: SearchQuery):
    """
    Perform similarity search with relevance scores.

    Returns the k most similar document chunks along with their similarity scores.
    Lower scores indicate higher similarity.
    """
    setup = get_rag_setup()

    try:
        results = setup.similarity_search_with_score(
            query=search_query.query,
            k=search_query.k
        )

        # Convert (Document, score) tuples to response model
        scored_results = [
            ScoredDocumentResult(
                page_content=doc.page_content,
                metadata=doc.metadata,
                score=score
            )
            for doc, score in results
        ]

        return SearchWithScoreResponse(
            query=search_query.query,
            results=scored_results,
            count=len(scored_results)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG search with score failed: {str(e)}")


@router.get("/rag/search", response_model=SearchResponse, summary="RAG Search (GET)")
async def rag_search_get(
    query: str = Query(..., description="Search query text", min_length=1),
    k: int = Query(default=4, description="Number of results to return", ge=1, le=20)
):
    """
    Perform similarity search using GET request with query parameters.

    Alternative endpoint for simple queries without POST body.
    """
    search_query = SearchQuery(query=query, k=k)
    return await rag_search(search_query)


@router.get("/rag/search-with-score", response_model=SearchWithScoreResponse, summary="RAG Search with Scores (GET)")
async def rag_search_with_score_get(
    query: str = Query(..., description="Search query text", min_length=1),
    k: int = Query(default=4, description="Number of results to return", ge=1, le=20)
):
    """
    Perform similarity search with scores using GET request with query parameters.

    Alternative endpoint for simple queries without POST body.
    """
    search_query = SearchQuery(query=query, k=k)
    return await rag_search_with_score(search_query)


@router.post("/rag/llm-search", summary="RAG + LLM Streaming Search")
async def rag_llm_search(search_query: RAGLLMSearchQuery):
    """
    Perform RAG similarity search and generate an LLM response with streaming.

    This endpoint:
    1. Retrieves relevant documents using RAG similarity search
    2. Feeds the documents as context to an LLM
    3. Streams the LLM's response back to the client in real-time

    The response is streamed as Server-Sent Events (SSE) in JSON format:
    - Each chunk contains: {"type": "chunk", "content": "text"}
    - Source documents are sent first (if include_sources=True): {"type": "sources", "data": [...]}
    - Final message indicates completion: {"type": "done"}
    """
    # Get RAG and LLM instances
    rag = get_rag_setup()
    llm_instance = get_llm()

    try:
        # Perform RAG search to get context documents
        results = rag.similarity_search_with_score(
            query=search_query.query,
            k=search_query.k
        )

        # Convert results to dict format for LLM
        context_docs = [
            {
                "page_content": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            }
            for doc, score in results
        ]

        # Create streaming response generator
        async def generate_stream():
            """Generator function for streaming response"""
            try:
                # First, send the source documents if requested
                if search_query.include_sources:
                    sources_data = {
                        "type": "sources",
                        "data": [
                            {
                                "page_content": doc["page_content"],
                                "metadata": doc["metadata"],
                                "score": doc["score"]
                            }
                            for doc in context_docs
                        ]
                    }
                    yield f"data: {json.dumps(sources_data)}\n\n"

                # Stream the LLM response
                stream = await llm_instance.chat_with_context(
                    query=search_query.query,
                    context_documents=context_docs,
                    system_prompt=search_query.system_prompt,
                    temperature=search_query.temperature,
                    max_tokens=search_query.max_tokens,
                    stream=True
                )

                # Yield each chunk from the LLM
                async for chunk in stream:
                    chunk_data = {
                        "type": "chunk",
                        "content": chunk
                    }
                    yield f"data: {json.dumps(chunk_data)}\n\n"

                # Send completion message
                done_data = {"type": "done"}
                yield f"data: {json.dumps(done_data)}\n\n"

            except Exception as e:
                # Send error message
                error_data = {
                    "type": "error",
                    "message": str(e)
                }
                yield f"data: {json.dumps(error_data)}\n\n"

        # Return streaming response with SSE headers
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"RAG + LLM search failed: {str(e)}"
        )
