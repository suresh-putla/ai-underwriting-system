"""
Test script for LLM integration
Tests the LLM class and verifies OpenAI connection
"""

import asyncio
import os
from dotenv import load_dotenv
from llm import LLM

# Load environment variables
load_dotenv()


async def test_llm_basic():
    """Test basic LLM functionality"""
    print("=== Testing LLM Basic Chat ===")

    try:
        llm = LLM(model="claude-haiku-4-5", temperature=0.7, max_tokens=100)
        print(f"✓ LLM initialized successfully")
        print(f"  Model: {llm.model}")
        print(f"  Base URL: {llm.base_url or 'default'}")

        # Test non-streaming chat
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in 5 words or less."}
        ]

        print("\nTesting non-streaming response...")
        response = await llm.chat(messages, max_tokens=50)
        print(f"✓ Response: {response}")

        await llm.close()
        print("\n✓ All basic tests passed!")

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_llm_streaming():
    """Test streaming LLM functionality"""
    print("\n=== Testing LLM Streaming ===")

    try:
        llm = LLM(model="claude-haiku-4-5", temperature=0.7, max_tokens=100)

        messages = [
            {"role": "user", "content": "Count from 1 to 5, one number per line."}
        ]

        print("Testing streaming response...")
        stream = await llm.chat(messages, max_tokens=50, stream=True)

        print("Response chunks: ", end="", flush=True)
        async for chunk in stream:
            print(chunk, end="", flush=True)

        print("\n✓ Streaming test passed!")

        await llm.close()

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_llm_with_context():
    """Test LLM with RAG context"""
    print("\n=== Testing LLM with RAG Context ===")

    try:
        llm = LLM(model="claude-haiku-4-5", temperature=0.7, max_tokens=200)

        # Mock RAG documents
        mock_documents = [
            {
                "page_content": "The minimum credit score for loan approval is 680.",
                "metadata": {"source": "policy.pdf", "page": 1}
            },
            {
                "page_content": "Applicants must have a debt-to-income ratio below 43%.",
                "metadata": {"source": "policy.pdf", "page": 2}
            }
        ]

        query = "What is the minimum credit score requirement?"

        print(f"Query: {query}")
        print("Testing non-streaming context response...")
        response = await llm.chat_with_context(
            query=query,
            context_documents=mock_documents,
            stream=False
        )
        print(f"✓ Response: {response[:200]}...")

        print("\nTesting streaming context response...")
        stream = await llm.chat_with_context(
            query=query,
            context_documents=mock_documents,
            stream=True
        )

        print("Response chunks: ", end="", flush=True)
        async for chunk in stream:
            print(chunk, end="", flush=True)

        print("\n✓ Context tests passed!")

        await llm.close()

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests"""
    print("=" * 60)
    print("LLM Integration Test Suite")
    print("=" * 60)

    # Check environment
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    print(f"\nEnvironment:")
    print(f"  OPENAI_API_KEY: {'✓ Set' if api_key else '✗ Not set'}")
    print(f"  OPENAI_BASE_URL: {base_url or 'default'}")
    print()

    if not api_key:
        print("✗ Error: OPENAI_API_KEY not set in environment")
        return

    # Run tests
    await test_llm_basic()
    await test_llm_streaming()
    await test_llm_with_context()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
