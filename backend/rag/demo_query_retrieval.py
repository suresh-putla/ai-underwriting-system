"""
Demo: Query-based Chunk Retrieval
This script demonstrates how to retrieve relevant chunks using different query methods.
"""

import os
from dotenv import load_dotenv
from rag_setup import RAGSetup
from langchain_core.documents import Document

# Load environment variables from .env file
load_dotenv()


def demo_query_retrieval():
    """
    Demonstrates three ways to retrieve chunks based on queries:
    1. Simple similarity search
    2. Similarity search with scores
    3. Using retriever interface
    """

    print("=" * 70)
    print("RAG Query Retrieval Demo")
    print("=" * 70)

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  OPENAI_API_KEY not set. Set it to run this demo:")
        print("   export OPENAI_API_KEY='your-api-key'")
        return

    # Initialize RAG
    print("\n1. Initializing RAG Setup...")
    rag = RAGSetup(
        chunk_size=500,
        chunk_overlap=100,
        persist_directory="./demo_chroma_db",
        collection_name="demo_loan_docs"
    )
    print("   ✓ RAG initialized with chunk_size=500, chunk_overlap=100")

    # Create sample documents
    print("\n2. Creating sample loan policy documents...")
    sample_documents = [
        Document(
            page_content="""
            CONVENTIONAL LOAN REQUIREMENTS

            Credit Score Requirements:
            - Minimum credit score: 620
            - Recommended credit score: 700 or higher
            - Credit history: 2+ years

            Down Payment:
            - Minimum: 5% for credit scores 700+
            - Minimum: 10% for credit scores 620-699
            - 20% down payment avoids PMI

            Income Requirements:
            - Debt-to-income ratio: Maximum 43%
            - Employment history: 2 years minimum
            - Income documentation: W-2s, pay stubs, tax returns
            """,
            metadata={"source": "conventional_loans.pdf", "page": 1, "loan_type": "conventional"}
        ),
        Document(
            page_content="""
            FHA LOAN REQUIREMENTS

            Credit Score Requirements:
            - Minimum credit score: 580 for 3.5% down payment
            - Minimum credit score: 500 for 10% down payment
            - Credit history: More lenient than conventional

            Down Payment:
            - As low as 3.5% with 580+ credit score
            - 10% minimum with 500-579 credit score

            Income Requirements:
            - Debt-to-income ratio: Maximum 43% (some flexibility to 50%)
            - Employment history: 2 years preferred
            - All income sources considered
            """,
            metadata={"source": "fha_loans.pdf", "page": 1, "loan_type": "fha"}
        ),
        Document(
            page_content="""
            VA LOAN REQUIREMENTS

            Eligibility:
            - Active duty service members
            - Veterans with honorable discharge
            - Certain surviving spouses
            - Certificate of Eligibility (COE) required

            Credit Score Requirements:
            - No official minimum, but most lenders require 620
            - Competitive rates with credit score 660+

            Down Payment:
            - 0% down payment available
            - No PMI required
            - Funding fee applies (waived for disabled veterans)

            Income Requirements:
            - Debt-to-income ratio: Maximum 41% (flexible)
            - Residual income requirements must be met
            """,
            metadata={"source": "va_loans.pdf", "page": 1, "loan_type": "va"}
        ),
        Document(
            page_content="""
            UNDERWRITING APPROVAL PROCESS

            Stage 1: Pre-Qualification (Day 1-2)
            - Initial credit check
            - Income verification
            - Basic eligibility assessment

            Stage 2: Application (Day 3-5)
            - Complete loan application
            - Submit documentation
            - Lock interest rate (optional)

            Stage 3: Processing (Day 6-15)
            - Verify employment
            - Order appraisal
            - Review title report
            - Check credit again

            Stage 4: Underwriting (Day 16-25)
            - Detailed file review
            - Automated underwriting decision
            - Manual underwriter review if needed
            - Conditions issued

            Stage 5: Clear to Close (Day 26-30)
            - All conditions met
            - Final approval
            - Schedule closing
            """,
            metadata={"source": "underwriting_process.pdf", "page": 1, "doc_type": "process"}
        ),
    ]

    print(f"   ✓ Created {len(sample_documents)} sample documents")

    # Chunk documents
    print("\n3. Chunking documents...")
    chunks = rag.chunk_documents(sample_documents)
    print(f"   ✓ Created {len(chunks)} chunks")

    # Create vector store
    print("\n4. Creating vector store and generating embeddings...")
    print("   (This may take a few seconds...)")
    vectorstore = rag.create_vectorstore(chunks)
    print("   ✓ Vector store created and persisted")

    # Query demonstrations
    print("\n" + "=" * 70)
    print("QUERY DEMONSTRATIONS")
    print("=" * 70)

    # Demo 1: Simple similarity search
    print("\n📝 DEMO 1: Simple Similarity Search")
    print("-" * 70)
    query_1 = "What is the minimum credit score for FHA loans?"
    print(f"Query: '{query_1}'")
    print(f"Retrieving top 2 results...\n")

    results_1 = rag.similarity_search(query_1, k=2)
    for i, doc in enumerate(results_1, 1):
        print(f"Result {i}:")
        print(f"  Source: {doc.metadata.get('source', 'N/A')}")
        print(f"  Loan Type: {doc.metadata.get('loan_type', 'N/A')}")
        print(f"  Content:\n{doc.page_content[:250].strip()}...\n")

    # Demo 2: Similarity search with scores
    print("\n📊 DEMO 2: Similarity Search with Relevance Scores")
    print("-" * 70)
    query_2 = "Tell me about down payment requirements"
    print(f"Query: '{query_2}'")
    print(f"Retrieving top 3 results with scores...\n")

    results_2 = rag.similarity_search_with_score(query_2, k=3)
    for i, (doc, score) in enumerate(results_2, 1):
        print(f"Result {i} - Relevance Score: {score:.4f}")
        print(f"  Source: {doc.metadata.get('source', 'N/A')}")
        print(f"  Loan Type: {doc.metadata.get('loan_type', 'N/A')}")
        print(f"  Content:\n{doc.page_content[:200].strip()}...\n")

    # Demo 3: Using retriever interface
    print("\n🔍 DEMO 3: Using Retriever Interface (for LangChain integration)")
    print("-" * 70)
    query_3 = "What are the underwriting stages?"
    print(f"Query: '{query_3}'")
    print(f"Using retriever with k=2...\n")

    retriever = rag.get_retriever(
        search_type="similarity",
        search_kwargs={"k": 2}
    )
    results_3 = retriever.get_relevant_documents(query_3)
    for i, doc in enumerate(results_3, 1):
        print(f"Result {i}:")
        print(f"  Source: {doc.metadata.get('source', 'N/A')}")
        print(f"  Document Type: {doc.metadata.get('doc_type', 'N/A')}")
        print(f"  Content:\n{doc.page_content[:300].strip()}...\n")

    # Demo 4: Different query types
    print("\n🎯 DEMO 4: Testing Different Query Types")
    print("-" * 70)

    test_queries = [
        "maximum debt to income ratio",
        "VA loan eligibility",
        "employment history requirements",
        "PMI requirements"
    ]

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = rag.similarity_search_with_score(query, k=1)
        if results:
            doc, score = results[0]
            print(f"  Best Match (Score: {score:.4f}): {doc.metadata.get('source', 'N/A')}")
            print(f"  Preview: {doc.page_content[:150].strip()}...")

    # Cleanup
    print("\n" + "=" * 70)
    print("CLEANUP")
    print("=" * 70)

    cleanup = input("\nDelete demo database? (y/n): ").strip().lower()
    if cleanup == 'y':
        import shutil
        if os.path.exists("./demo_chroma_db"):
            shutil.rmtree("./demo_chroma_db")
            print("✓ Demo database deleted")
    else:
        print("Demo database kept at: ./demo_chroma_db")
        print("You can reuse it by loading with rag.load_existing_vectorstore()")

    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        demo_query_retrieval()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
