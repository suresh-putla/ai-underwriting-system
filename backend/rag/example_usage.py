"""
Example usage of RAG Setup
"""

import os
from dotenv import load_dotenv
from rag_setup import RAGSetup

# Load environment variables from .env file
load_dotenv()


def example_single_pdf():
    """Example: Process a single PDF file"""
    # Initialize RAG setup with custom chunk parameters
    rag = RAGSetup(
        chunk_size=1000,
        chunk_overlap=200,
        persist_directory="./chroma_db",
        collection_name="loan_documents"
    )

    # Setup from a single PDF
    vectorstore = rag.setup_from_pdf("path/to/your/document.pdf")

    # Perform a search
    results = rag.similarity_search("What are the loan requirements?", k=3)
    for i, doc in enumerate(results):
        print(f"\nResult {i+1}:")
        print(doc.page_content[:200])


def example_directory():
    """Example: Process all PDFs in a directory"""
    rag = RAGSetup(
        chunk_size=1500,
        chunk_overlap=300,
        persist_directory="./chroma_db_loans",
        collection_name="all_loan_docs"
    )

    # Setup from directory
    vectorstore = rag.setup_from_directory("./data/loan_documents")

    # Search with scores
    results = rag.similarity_search_with_score("underwriting criteria", k=5)
    for i, (doc, score) in enumerate(results):
        print(f"\nResult {i+1} (Score: {score}):")
        print(doc.page_content[:200])


def example_load_existing():
    """Example: Load existing vector store"""
    rag = RAGSetup(
        chunk_size=1000,
        chunk_overlap=200,
        persist_directory="./chroma_db",
        collection_name="loan_documents"
    )

    # Load existing vector store
    vectorstore = rag.load_existing_vectorstore()

    # Get retriever for use with LangChain chains
    retriever = rag.get_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    # Use retriever
    docs = retriever.get_relevant_documents("credit score requirements")
    print(f"Found {len(docs)} relevant documents")


def example_add_more_documents():
    """Example: Add documents to existing vector store"""
    rag = RAGSetup(
        chunk_size=1000,
        chunk_overlap=200,
        persist_directory="./chroma_db",
        collection_name="loan_documents"
    )

    # Load existing vector store
    rag.load_existing_vectorstore()

    # Load and chunk new documents
    new_docs = rag.load_pdf("path/to/new_document.pdf")
    new_chunks = rag.chunk_documents(new_docs)

    # Add to existing store
    rag.add_documents_to_vectorstore(new_chunks)


if __name__ == "__main__":
    # Run examples (uncomment the one you want to try)

    # example_single_pdf()
    # example_directory()
    # example_load_existing()
    # example_add_more_documents()

    print("Example usage script ready!")
