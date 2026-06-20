"""
Test script for RAG Setup
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from rag_setup import RAGSetup

# Load environment variables from .env file
load_dotenv()


def test_initialization():
    """Test RAG initialization with different parameters"""
    print("Testing initialization...")

    # Test with default parameters
    try:
        rag1 = RAGSetup()
        print("✓ Default initialization successful")
    except ValueError as e:
        print(f"✗ Default initialization failed (expected if OPENAI_API_KEY not set): {e}")

    # Test with custom parameters
    try:
        rag2 = RAGSetup(
            chunk_size=1500,
            chunk_overlap=300,
            persist_directory="./test_chroma_db",
            collection_name="test_collection",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        print("✓ Custom initialization successful")
        print(f"  - Chunk size: {rag2.chunk_size}")
        print(f"  - Chunk overlap: {rag2.chunk_overlap}")
        print(f"  - Persist directory: {rag2.persist_directory}")
        print(f"  - Collection name: {rag2.collection_name}")
    except ValueError as e:
        print(f"✗ Custom initialization failed: {e}")


def test_text_splitting():
    """Test text chunking functionality"""
    print("\nTesting text splitting...")

    try:
        from langchain_core.documents import Document

        rag = RAGSetup(
            chunk_size=100,
            chunk_overlap=20,
            openai_api_key=os.getenv("OPENAI_API_KEY", "dummy_key_for_test")
        )

        # Create sample document
        sample_text = """
        This is a test document for the loan origination system.
        It contains multiple paragraphs to test the chunking functionality.

        Loan requirements include credit score, income verification, and debt-to-income ratio.
        The underwriting process involves multiple steps including document collection,
        verification, and final approval.

        This text is long enough to be split into multiple chunks based on our chunk size settings.
        """

        sample_doc = Document(page_content=sample_text, metadata={"source": "test"})

        # Test chunking
        chunks = rag.chunk_documents([sample_doc])
        print(f"✓ Text splitting successful")
        print(f"  - Original document length: {len(sample_text)} characters")
        print(f"  - Number of chunks created: {len(chunks)}")
        print(f"  - Average chunk size: {sum(len(c.page_content) for c in chunks) / len(chunks):.0f} characters")

    except Exception as e:
        print(f"✗ Text splitting failed: {e}")


def test_directory_structure():
    """Test that required directories can be created"""
    print("\nTesting directory structure...")

    test_persist_dir = "./test_rag_db"

    try:
        os.makedirs(test_persist_dir, exist_ok=True)
        print(f"✓ Directory creation successful: {test_persist_dir}")

        # Cleanup
        if os.path.exists(test_persist_dir) and not os.listdir(test_persist_dir):
            os.rmdir(test_persist_dir)
            print("✓ Cleanup successful")

    except Exception as e:
        print(f"✗ Directory test failed: {e}")


def test_retrieve_chunks_by_query():
    """Test retrieving chunks based on a query with a mock vector store"""
    print("\nTesting chunk retrieval by query...")

    try:
        from langchain_core.documents import Document
        import shutil

        # Create test directory
        test_persist_dir = "./test_query_retrieval_db"

        # Check if we should use local embeddings
        openai_key = os.getenv("OPENAI_API_KEY")
        use_local = False

        # Try to use OpenAI, fall back to local if it fails
        try:
            # Test if OpenAI embeddings work
            print("  - Attempting to use OpenAI embeddings...")
            rag = RAGSetup(
                chunk_size=200,
                chunk_overlap=50,
                persist_directory=test_persist_dir,
                collection_name="test_query_collection",
                openai_api_key=openai_key,
                use_local_embeddings=False
            )
            # Try a small embedding test using our wrapper class
            from rag_setup import OpenAIEmbeddings
            test_embed = OpenAIEmbeddings(api_key=openai_key)
            test_embed.embed_query("test")
            print("  ✓ OpenAI embeddings available")
        except Exception as e:
            print(f"  - OpenAI embeddings not available: {str(e)[:100]}")
            print("  - Falling back to local embeddings...")
            use_local = True
            rag = RAGSetup(
                chunk_size=200,
                chunk_overlap=50,
                persist_directory=test_persist_dir,
                collection_name="test_query_collection",
                use_local_embeddings=True
            )

        # Create sample loan documents
        sample_docs = [
            Document(
                page_content="""
                Loan Requirements for Personal Loans:
                - Minimum credit score: 650
                - Maximum debt-to-income ratio: 43%
                - Proof of income required
                - Valid government-issued ID
                """,
                metadata={"source": "personal_loans.pdf", "page": 1}
            ),
            Document(
                page_content="""
                Mortgage Underwriting Criteria:
                - Credit score minimum: 620 for conventional loans
                - Down payment: 5-20% depending on loan type
                - Employment history: 2 years minimum
                - Property appraisal required
                """,
                metadata={"source": "mortgage_guidelines.pdf", "page": 1}
            ),
            Document(
                page_content="""
                Business Loan Application Process:
                - Business plan submission
                - Financial statements for last 3 years
                - Credit check on business and owner
                - Collateral evaluation
                - Cash flow analysis
                """,
                metadata={"source": "business_loans.pdf", "page": 1}
            ),
            Document(
                page_content="""
                Auto Loan Requirements:
                - Credit score: 580 minimum
                - Down payment: 10% recommended
                - Vehicle inspection may be required
                - Proof of insurance
                - Income verification
                """,
                metadata={"source": "auto_loans.pdf", "page": 1}
            )
        ]

        print("  - Creating sample documents...")

        # Chunk the documents
        chunks = rag.chunk_documents(sample_docs)
        print(f"  - Created {len(chunks)} chunks from {len(sample_docs)} documents")

        # Create vector store
        print("  - Creating vector store and generating embeddings...")
        vectorstore = rag.create_vectorstore(chunks)
        print("  ✓ Vector store created successfully")

        # Test Query 1: Credit score requirements
        print("\n  Test Query 1: 'What is the minimum credit score required?'")
        results_1 = rag.similarity_search("What is the minimum credit score required?", k=3)
        print(f"  - Retrieved {len(results_1)} chunks")
        for i, doc in enumerate(results_1, 1):
            print(f"\n  Result {i}:")
            print(f"    Source: {doc.metadata.get('source', 'unknown')}")
            print(f"    Content preview: {doc.page_content[:150].strip()}...")

        # Test Query 2: With scores
        print("\n  Test Query 2: 'business loan requirements' (with scores)")
        results_2 = rag.similarity_search_with_score("business loan requirements", k=3)
        print(f"  - Retrieved {len(results_2)} chunks with scores")
        for i, (doc, score) in enumerate(results_2, 1):
            print(f"\n  Result {i} (Relevance Score: {score:.4f}):")
            print(f"    Source: {doc.metadata.get('source', 'unknown')}")
            print(f"    Content preview: {doc.page_content[:150].strip()}...")

        # Test Query 3: Using retriever interface
        print("\n  Test Query 3: Using retriever interface for 'down payment'")
        retriever = rag.get_retriever(
            search_type="similarity",
            search_kwargs={"k": 2}
        )
        results_3 = retriever.get_relevant_documents("down payment")
        print(f"  - Retrieved {len(results_3)} chunks via retriever")
        for i, doc in enumerate(results_3, 1):
            print(f"\n  Result {i}:")
            print(f"    Source: {doc.metadata.get('source', 'unknown')}")
            print(f"    Content preview: {doc.page_content[:150].strip()}...")

        print("\n✓ Query retrieval test successful!")

        # Cleanup
        print("\n  - Cleaning up test database...")
        if os.path.exists(test_persist_dir):
            shutil.rmtree(test_persist_dir)
            print("  ✓ Cleanup complete")

    except ValueError as e:
        print(f"✗ Query retrieval test skipped: {e}")
        print("  Note: Set OPENAI_API_KEY environment variable to run this test")
    except Exception as e:
        print(f"✗ Query retrieval test failed: {e}")
        import traceback
        traceback.print_exc()

        # Cleanup on error
        if 'test_persist_dir' in locals() and os.path.exists(test_persist_dir):
            import shutil
            shutil.rmtree(test_persist_dir)
            print("  - Cleanup completed after error")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("RAG Setup Test Suite")
    print("=" * 60)

    test_initialization()
    test_text_splitting()
    test_directory_structure()
    test_retrieve_chunks_by_query()

    print("\n" + "=" * 60)
    print("Test suite complete!")
    print("=" * 60)
    print("\nNote: For full functionality testing, you need:")
    print("1. OPENAI_API_KEY environment variable set")
    print("2. PDF files to process")
    print("3. Sufficient disk space for ChromaDB")


def test_query_on_existing_store(persist_directory: str, query: str, k: int = 5):
    """
    Test method to retrieve chunks from an existing vector store based on a query.

    Args:
        persist_directory: Path to existing ChromaDB directory
        query: Search query string
        k: Number of results to retrieve (default: 5)

    Example:
        test_query_on_existing_store("./chroma_db", "What are the loan requirements?", k=3)
    """
    print("\n" + "=" * 60)
    print(f"Query Retrieval Test")
    print("=" * 60)
    print(f"Query: '{query}'")
    print(f"Top-k: {k}")
    print(f"Vector Store: {persist_directory}")
    print("=" * 60)

    try:
        # Initialize RAG
        rag = RAGSetup(
            persist_directory=persist_directory,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        # Load existing vector store
        print("\nLoading vector store...")
        rag.load_existing_vectorstore()
        print("✓ Vector store loaded successfully")

        # Perform similarity search with scores
        print(f"\nSearching for: '{query}'")
        results = rag.similarity_search_with_score(query, k=k)

        print(f"\n✓ Retrieved {len(results)} results:\n")

        # Display results
        for i, (doc, score) in enumerate(results, 1):
            print(f"{'='*60}")
            print(f"Result #{i} - Relevance Score: {score:.4f}")
            print(f"{'='*60}")
            print(f"Source: {doc.metadata.get('source', 'N/A')}")
            if 'page' in doc.metadata:
                print(f"Page: {doc.metadata['page']}")
            print(f"\nContent:\n{doc.page_content}\n")

        return results

    except FileNotFoundError:
        print(f"\n✗ Error: Vector store not found at {persist_directory}")
        print("  Please create a vector store first or provide the correct path.")
        return None
    except ValueError as e:
        print(f"\n✗ Error: {e}")
        print("  Make sure OPENAI_API_KEY is set in your environment.")
        return None
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    import sys

    # Check if running in query mode
    if len(sys.argv) > 1 and sys.argv[1] == "--query":
        # Example: python test_rag.py --query "./chroma_db" "What are loan requirements?" 3
        if len(sys.argv) < 4:
            print("Usage: python test_rag.py --query <persist_directory> <query> [k]")
            print("Example: python test_rag.py --query ./chroma_db 'loan requirements' 5")
            sys.exit(1)

        persist_dir = sys.argv[2]
        query = sys.argv[3]
        k = int(sys.argv[4]) if len(sys.argv) > 4 else 5

        test_query_on_existing_store(persist_dir, query, k)
    else:
        # Run full test suite
        run_all_tests()
