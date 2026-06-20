"""
Test script to verify RAG initialization with absolute paths
This tests that the readonly database error is fixed
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from rag.rag_setup import RAGSetup

def test_rag_init():
    """Test RAG initialization with absolute paths"""
    print("=" * 60)
    print("Testing RAG Initialization with Absolute Paths")
    print("=" * 60)

    # Use absolute paths
    backend_dir = Path(__file__).parent.resolve()
    persist_dir = backend_dir / "chroma_db_test"
    policies_dir = backend_dir / "policies"

    print(f"\nPaths:")
    print(f"  Backend dir: {backend_dir}")
    print(f"  Persist dir: {persist_dir}")
    print(f"  Policies dir: {policies_dir}")
    print(f"  Policies exist: {policies_dir.exists()}")

    try:
        # Initialize RAG with local embeddings for testing
        print("\n[1/4] Initializing RAG setup...")
        rag_setup = RAGSetup(
            chunk_size=1000,
            chunk_overlap=200,
            persist_directory=str(persist_dir),
            collection_name="test_loan_documents",
            use_local_embeddings=True  # Use local embeddings to avoid API key requirement
        )
        print("✓ RAG setup initialized")

        # Recreate vector store
        print("\n[2/4] Recreating vector store...")
        rag_setup.recreate_vectorstore()
        print(f"✓ Vector store recreated at {persist_dir}")

        # Load documents
        print("\n[3/4] Loading documents from policies directory...")
        rag_setup.setup_from_directory(str(policies_dir))
        print("✓ Documents loaded successfully")

        # Test search
        print("\n[4/4] Testing similarity search...")
        results = rag_setup.similarity_search("What is the minimum credit score?", k=2)
        print(f"✓ Search returned {len(results)} results")

        if results:
            print("\nSample result:")
            print(f"  Content: {results[0].page_content[:100]}...")
            print(f"  Metadata: {results[0].metadata}")

        print("\n" + "=" * 60)
        print("✓ All tests passed! RAG system working correctly.")
        print("=" * 60)

        # Cleanup test database
        import shutil
        if persist_dir.exists():
            shutil.rmtree(persist_dir)
            print(f"\n✓ Cleaned up test database at {persist_dir}")

        return True

    except Exception as e:
        print(f"\n✗ Error during RAG initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_rag_init()
    sys.exit(0 if success else 1)
