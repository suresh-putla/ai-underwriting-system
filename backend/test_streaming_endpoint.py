"""
Test script for the RAG + LLM streaming endpoint
Demonstrates how to call the /api/rag-llm-search endpoint and handle streaming responses
"""

import asyncio
import json
import httpx
import sys


async def test_streaming_endpoint(query: str, include_sources: bool = True):
    """
    Test the RAG + LLM streaming endpoint

    Args:
        query: The search query
        include_sources: Whether to include source documents
    """
    url = "http://localhost:8000/api/rag-llm-search"

    payload = {
        "query": query,
        "k": 4,
        "temperature": 0.7,
        "max_tokens": 1500,
        "include_sources": include_sources
    }

    print(f"Query: {query}")
    print("=" * 80)
    print()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream('POST', url, json=payload) as response:
                if response.status_code != 200:
                    print(f"Error: HTTP {response.status_code}")
                    error_text = await response.aread()
                    print(error_text.decode())
                    return

                print("Streaming response:")
                print("-" * 80)

                sources_printed = False
                async for line in response.aiter_lines():
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])

                            if data['type'] == 'sources':
                                if not sources_printed:
                                    print("\nSource Documents:")
                                    for i, doc in enumerate(data['data'], 1):
                                        metadata = doc.get('metadata', {})
                                        source = metadata.get('source', 'Unknown')
                                        page = metadata.get('page', 'N/A')
                                        score = doc.get('score', 0)
                                        content_preview = doc['page_content'][:100]
                                        print(f"\n{i}. {source} (Page {page}) - Score: {score:.3f}")
                                        print(f"   Preview: {content_preview}...")
                                    print("\n" + "=" * 80)
                                    print("LLM Response:")
                                    print("-" * 80)
                                    sources_printed = True

                            elif data['type'] == 'chunk':
                                print(data['content'], end='', flush=True)

                            elif data['type'] == 'done':
                                print("\n" + "-" * 80)
                                print("✓ Stream complete")

                            elif data['type'] == 'error':
                                print(f"\n✗ Error: {data['message']}")

                        except json.JSONDecodeError as e:
                            print(f"\nWarning: Failed to parse JSON: {line}")
                            continue

    except httpx.ConnectError:
        print("✗ Error: Could not connect to the server.")
        print("   Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_multiple_queries():
    """Test multiple queries to demonstrate different scenarios"""

    test_queries = [
        "What is the minimum credit score requirement?",
        "What are the debt-to-income ratio requirements?",
        "Explain the loan approval process",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"Test {i}/{len(test_queries)}")
        print(f"{'=' * 80}\n")

        await test_streaming_endpoint(query, include_sources=True)

        if i < len(test_queries):
            print("\nWaiting 2 seconds before next query...\n")
            await asyncio.sleep(2)


async def main():
    """Main test function"""
    print("=" * 80)
    print("RAG + LLM Streaming Endpoint Test")
    print("=" * 80)

    # Check if server is accessible
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/health", timeout=5.0)
            if response.status_code == 200:
                print("✓ Server is running")
            else:
                print(f"⚠ Server responded with status {response.status_code}")
    except httpx.ConnectError:
        print("✗ Error: Server is not running on http://localhost:8000")
        print("  Start the server with: cd backend && python3 main.py")
        return
    except Exception as e:
        print(f"⚠ Warning: Could not check server status: {e}")

    # Check if RAG system is initialized
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/rag-status", timeout=5.0)
            if response.status_code == 200:
                status = response.json()
                if status['initialized'] and status['vectorstore_loaded']:
                    print("✓ RAG system is initialized and ready")
                else:
                    print("⚠ RAG system needs initialization")
                    print("  Call POST /api/rag-init to initialize the vector store")
                    return
    except Exception as e:
        print(f"⚠ Warning: Could not check RAG status: {e}")

    print()

    # Run tests
    if len(sys.argv) > 1:
        # Single query from command line
        query = " ".join(sys.argv[1:])
        await test_streaming_endpoint(query)
    else:
        # Run multiple test queries
        await test_multiple_queries()

    print("\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
