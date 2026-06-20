"""
RAG Setup Module for LOUS
Handles document ingestion, chunking, embedding, and vector storage using LangChain and ChromaDB
"""

import os
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.schema import Document

# Load environment variables from .env file
load_dotenv()


class OpenAIEmbeddings:
    """OpenAI embeddings wrapper for production use"""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        """
        Initialize OpenAI embeddings.

        Args:
            api_key: OpenAI API key
            model: Embedding model to use (default: text-embedding-3-small)
                  Options: text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002
        """
        try:
            from langchain_openai import OpenAIEmbeddings as LangChainOpenAIEmbeddings
            self.embeddings = LangChainOpenAIEmbeddings(
                openai_api_key=api_key,
                model=model
            )
        except ImportError:
            raise ImportError(
                "langchain-openai not installed. Install with: pip install langchain-openai"
            )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        return self.embeddings.embed_query(text)


class LocalEmbeddings:
    """Local embeddings using sentence-transformers for testing/offline use"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize local embeddings.

        Args:
            model_name: Sentence transformer model (default: all-MiniLM-L6-v2)
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. Install with: pip install sentence-transformers"
            )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        embedding = self.model.encode([text], convert_to_numpy=True)
        return embedding[0].tolist()


class RAGSetup:
    """
    RAG Setup class for managing document processing and vector storage.

    Handles:
    - PDF document loading
    - Document chunking with customizable parameters
    - Embedding generation using OpenAI
    - Vector storage in ChromaDB
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        persist_directory: str = "./chroma_db",
        collection_name: str = "loan_documents",
        openai_api_key: Optional[str] = None,
        embedding_model: str = "text-embedding-3-small",
        use_local_embeddings: bool = False
    ):
        """
        Initialize RAG Setup.

        Args:
            chunk_size: Size of text chunks (default: 1000)
            chunk_overlap: Overlap between chunks (default: 200)
            persist_directory: Directory to persist ChromaDB (default: ./chroma_db)
            collection_name: Name of the ChromaDB collection (default: loan_documents)
            openai_api_key: OpenAI API key (if None, reads from environment)
            embedding_model: OpenAI embedding model (default: text-embedding-3-small)
                           Options: text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002
            use_local_embeddings: Use local sentence-transformers instead of OpenAI (default: False)
                                For testing or when OpenAI API is not available
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.use_local_embeddings = use_local_embeddings

        # Initialize embeddings
        if use_local_embeddings:
            print("Using local embeddings (sentence-transformers)")
            self.embeddings = LocalEmbeddings()
            self.openai_api_key = None
        else:
            # Set up OpenAI API key
            self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
            if not self.openai_api_key:
                raise ValueError(
                    "OpenAI API key must be provided or set in OPENAI_API_KEY environment variable. "
                    "Alternatively, set use_local_embeddings=True to use local embeddings for testing."
                )

            # Initialize OpenAI embeddings using our wrapper class
            try:
                print(f"Using OpenAI embeddings (model: {self.embedding_model})")
                self.embeddings = OpenAIEmbeddings(
                    api_key=self.openai_api_key,
                    model=self.embedding_model
                )
            except Exception as e:
                # If using non-standard API endpoint, provide helpful error
                raise ValueError(
                    f"Failed to initialize embeddings with model '{self.embedding_model}'. "
                    f"Error: {str(e)}. "
                    f"If using a non-OpenAI compatible API, try setting use_local_embeddings=True for testing."
                )

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        # Vector store (initialized when loading documents)
        self.vectorstore = None

    def load_pdf(self, pdf_path: str) -> List[Document]:
        """
        Load a single PDF document.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of Document objects
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        print(f"Loaded {len(documents)} pages from {pdf_path}")
        return documents

    def load_pdfs_from_directory(self, directory_path: str) -> List[Document]:
        """
        Load all PDF documents from a directory.

        Args:
            directory_path: Path to directory containing PDFs

        Returns:
            List of Document objects
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        loader = DirectoryLoader(
            directory_path,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True
        )
        documents = loader.load()
        print(f"Loaded {len(documents)} pages from {directory_path}")
        return documents

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks.

        Args:
            documents: List of Document objects to chunk

        Returns:
            List of chunked Document objects
        """
        chunks = self.text_splitter.split_documents(documents)
        print(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks

    def create_vectorstore(self, chunks: List[Document]) -> Chroma:
        """
        Create a ChromaDB vector store from document chunks.

        Args:
            chunks: List of chunked Document objects

        Returns:
            Chroma vector store instance
        """
        # Create persist directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)

        print(f"Creating vector store with {len(chunks)} chunks...")
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=self.collection_name
        )

        print(f"Vector store created and persisted to {self.persist_directory}")
        return self.vectorstore

    def load_existing_vectorstore(self) -> Chroma:
        """
        Load an existing ChromaDB vector store.

        Returns:
            Chroma vector store instance
        """
        if not os.path.exists(self.persist_directory):
            raise FileNotFoundError(f"Vector store not found at {self.persist_directory}")

        print(f"Loading existing vector store from {self.persist_directory}")
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=self.collection_name
        )

        return self.vectorstore

    def add_documents_to_vectorstore(self, chunks: List[Document]) -> None:
        """
        Add new document chunks to existing vector store.

        Args:
            chunks: List of chunked Document objects to add
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call create_vectorstore or load_existing_vectorstore first.")

        print(f"Adding {len(chunks)} chunks to existing vector store...")
        self.vectorstore.add_documents(chunks)
        print("Documents added successfully")

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Perform similarity search on the vector store.

        Args:
            query: Search query
            k: Number of results to return (default: 4)

        Returns:
            List of most similar Document objects
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call create_vectorstore or load_existing_vectorstore first.")

        results = self.vectorstore.similarity_search(query, k=k)
        return results

    def similarity_search_with_score(self, query: str, k: int = 4) -> List[tuple]:
        """
        Perform similarity search with relevance scores.

        Args:
            query: Search query
            k: Number of results to return (default: 4)

        Returns:
            List of tuples (Document, score)
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call create_vectorstore or load_existing_vectorstore first.")

        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return results

    def setup_from_pdf(self, pdf_path: str) -> Chroma:
        """
        Complete RAG setup from a single PDF file.
        Loads, chunks, embeds, and stores the document.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Chroma vector store instance
        """
        print(f"\n=== Starting RAG Setup for {pdf_path} ===")

        # Load document
        documents = self.load_pdf(pdf_path)

        # Chunk documents
        chunks = self.chunk_documents(documents)

        # Create vector store
        vectorstore = self.create_vectorstore(chunks)

        print("=== RAG Setup Complete ===\n")
        return vectorstore

    def setup_from_directory(self, directory_path: str) -> Chroma:
        """
        Complete RAG setup from a directory of PDF files.
        Loads, chunks, embeds, and stores all documents.

        Args:
            directory_path: Path to directory containing PDFs

        Returns:
            Chroma vector store instance
        """
        print(f"\n=== Starting RAG Setup for directory {directory_path} ===")

        # Load documents
        documents = self.load_pdfs_from_directory(directory_path)

        # Chunk documents
        chunks = self.chunk_documents(documents)

        # Create vector store
        vectorstore = self.create_vectorstore(chunks)

        print("=== RAG Setup Complete ===\n")
        return vectorstore

    def get_retriever(self, search_type: str = "similarity", search_kwargs: Optional[dict] = None):
        """
        Get a retriever interface for the vector store.

        Args:
            search_type: Type of search ("similarity", "mmr", "similarity_score_threshold")
            search_kwargs: Additional search parameters (e.g., {"k": 4})

        Returns:
            VectorStoreRetriever instance
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call create_vectorstore or load_existing_vectorstore first.")

        search_kwargs = search_kwargs or {"k": 4}
        return self.vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs=search_kwargs
        )

    def create_collection(self, documents: Optional[List[Document]] = None) -> Chroma:
        """
        Create a ChromaDB collection.

        This method always creates a fresh collection. If a collection with the same name
        already exists, it will be deleted first (collection only, not the directory).

        Args:
            documents: Optional list of documents to initialize the collection with.
                      If None, creates an empty collection.

        Returns:
            Chroma vector store instance
        """
        import chromadb
        import logging

        logger = logging.getLogger(__name__)

        # Create persist directory if it doesn't exist
        os.makedirs(self.persist_directory, exist_ok=True)

        # Connect to ChromaDB client and check if collection exists
        try:
            client = chromadb.PersistentClient(path=self.persist_directory)
            collections = client.list_collections()

            # Check if collection with this name exists
            if any(col.name == self.collection_name for col in collections):
                # Delete only the collection, not the directory
                print(f"Collection '{self.collection_name}' already exists. Deleting...")
                client.delete_collection(name=self.collection_name)
                logger.info(f"Deleted existing collection: {self.collection_name}")
                print(f"Collection '{self.collection_name}' deleted successfully")

        except Exception as e:
            # If we can't check/delete, log warning but continue to try creating
            logger.warning(f"Could not check/delete existing collection: {str(e)}")
            print(f"Warning: Could not check for existing collection: {str(e)}")

        # Create new collection
        if documents and len(documents) > 0:
            print(f"Creating collection '{self.collection_name}' with {len(documents)} documents...")
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory,
                collection_name=self.collection_name
            )
            print(f"Collection created with {len(documents)} documents")
        else:
            # Create empty collection by initializing without documents
            print(f"Creating empty collection '{self.collection_name}'...")
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name=self.collection_name
            )
            print("Empty collection created")

        print(f"Collection persisted to {self.persist_directory}")
        return self.vectorstore

    def delete_collection(self) -> None:
        """
        Delete the ChromaDB collection.
        Warning: This will permanently remove all stored embeddings.
        """
        if self.vectorstore is None:
            print("No active vector store to delete")
            return

        print(f"Deleting collection: {self.collection_name}")
        self.vectorstore.delete_collection()
        self.vectorstore = None
        print("Collection deleted successfully")

    def recreate_vectorstore(self) -> None:
        """
        Recreate the vector store by deleting existing data and preparing for fresh ingestion.
        Properly deletes the ChromaDB collection using the client API, then removes the directory.
        Warning: This will permanently remove all stored embeddings and require re-ingestion.
        """
        import shutil
        import chromadb

        # First, try to delete the collection using ChromaDB client API
        if os.path.exists(self.persist_directory):
            try:
                print(f"Connecting to ChromaDB at {self.persist_directory}")
                # Create a persistent ChromaDB client
                client = chromadb.PersistentClient(path=self.persist_directory)

                # Get list of existing collections
                collections = client.list_collections()
                collection_names = [col.name for col in collections]

                # Delete the collection if it exists
                if self.collection_name in collection_names:
                    print(f"Deleting existing collection: {self.collection_name}")
                    client.delete_collection(name=self.collection_name)
                    print(f"Collection '{self.collection_name}' deleted successfully")
                else:
                    print(f"Collection '{self.collection_name}' not found, skipping deletion")

            except Exception as e:
                print(f"Warning: Could not delete collection via ChromaDB API: {str(e)}")
                print("Proceeding with directory deletion...")

            # Delete the entire persist directory
            try:
                print(f"Deleting vector store directory at {self.persist_directory}")
                shutil.rmtree(self.persist_directory)
                print("Vector store directory deleted")
            except Exception as e:
                print(f"Warning: Could not delete directory: {str(e)}")

        # Create fresh persist directory
        os.makedirs(self.persist_directory, exist_ok=True)
        print(f"Created fresh vector store directory at {self.persist_directory}")

        # Reset vectorstore instance
        self.vectorstore = None
        print("Vector store recreated and ready for document ingestion")
