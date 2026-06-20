# RAG + LLM API Documentation

## Overview

This document describes the RAG + LLM integration that combines vector similarity search with large language model (LLM) responses to provide intelligent, context-aware answers to user queries.

## Architecture

### Components

1. **LLM Module** (`backend/llm.py`): Handles OpenAI-compatible chat API integration
2. **RAG API** (`backend/api/api.py`): Exposes REST endpoints for RAG search and LLM responses
3. **RAG Setup** (`backend/rag/rag_setup.py`): Manages document ingestion and vector storage

### Flow

1. User sends a query to `/api/rag-llm-search`
2. Backend performs similarity search on vector store (ChromaDB)
3. Retrieved documents are formatted as context
4. LLM generates a response using the context
5. Response is streamed back to the client in real-time

## API Endpoints

### POST `/api/rag-llm-search`

Performs RAG similarity search and generates a streaming LLM response.

#### Request Body

```json
{
  "query": "What is the minimum credit score requirement?",
  "k": 4,
  "temperature": 0.7,
  "max_tokens": 1500,
  "system_prompt": "Optional custom system prompt",
  "include_sources": true
}
```

#### Parameters

- `query` (string, required): The search query text
- `k` (integer, optional, default=4): Number of RAG results to retrieve (1-20)
- `temperature` (float, optional, default=0.7): LLM sampling temperature (0.0-2.0)
- `max_tokens` (integer, optional, default=1500): Maximum tokens in LLM response (100-4000)
- `system_prompt` (string, optional): Custom system prompt for the LLM
- `include_sources` (boolean, optional, default=true): Include source documents in response

#### Response Format

The response is streamed as Server-Sent Events (SSE) in JSON format:

**Source Documents** (if `include_sources=true`):
```json
data: {
  "type": "sources",
  "data": [
    {
      "page_content": "The minimum credit score for loan approval is 680.",
      "metadata": {"source": "policy.pdf", "page": 1},
      "score": 0.234
    }
  ]
}
```

**Response Chunks** (streamed as LLM generates):
```json
data: {"type": "chunk", "content": "According"}
data: {"type": "chunk", "content": " to"}
data: {"type": "chunk", "content": " the"}
```

**Completion**:
```json
data: {"type": "done"}
```

**Error** (if something goes wrong):
```json
data: {"type": "error", "message": "Error description"}
```

## LLM Class

The `LLM` class in `backend/llm.py` provides the core functionality for interacting with language models.

### Initialization

```python
from llm import LLM

llm = LLM(
    model="claude-haiku-4-5",  # or "gpt-4o-mini", etc.
    temperature=0.7,
    max_tokens=1000
)
```

### Methods

#### `chat(messages, temperature, max_tokens, stream)`

Send a chat completion request.

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
]

# Non-streaming
response = await llm.chat(messages)

# Streaming
stream = await llm.chat(messages, stream=True)
async for chunk in stream:
    print(chunk, end="")
```

#### `chat_with_context(query, context_documents, system_prompt, temperature, max_tokens, stream)`

Generate a response using RAG context documents.

```python
context_docs = [
    {
        "page_content": "The minimum credit score is 680.",
        "metadata": {"source": "policy.pdf", "page": 1}
    }
]

response = await llm.chat_with_context(
    query="What's the minimum credit score?",
    context_documents=context_docs,
    stream=False
)
```

## Configuration

### Environment Variables

Set these in your `.env` file:

```bash
# OpenAI API key (or compatible API key)
OPENAI_API_KEY=your_api_key_here

# Optional: Custom base URL for OpenAI-compatible APIs (e.g., Claude via proxy)
OPENAI_BASE_URL=https://llm.aibricks.io/v1
```

### Supported Models

When using the standard OpenAI API:
- `gpt-4o`
- `gpt-4o-mini`
- `gpt-4-turbo`
- `gpt-3.5-turbo`

When using the AIBricks proxy (custom OPENAI_BASE_URL):
- `claude-sonnet-4-5-20250929`
- `claude-haiku-4-5`
- `claude-opus-4-7`

## Usage Examples

### Example 1: Basic RAG + LLM Search

```bash
curl -X POST "http://localhost:8000/api/rag-llm-search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the income requirements for loan approval?",
    "k": 4,
    "temperature": 0.7,
    "include_sources": true
  }'
```

### Example 2: Custom System Prompt

```bash
curl -X POST "http://localhost:8000/api/rag-llm-search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the debt-to-income ratio requirement",
    "k": 3,
    "system_prompt": "You are a loan officer explaining policies to applicants. Be clear and concise.",
    "temperature": 0.5
  }'
```

### Example 3: JavaScript/TypeScript Client

```javascript
async function ragLLMSearch(query) {
  const response = await fetch('http://localhost:8000/api/rag-llm-search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      k: 4,
      temperature: 0.7,
      include_sources: true
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));

        switch (data.type) {
          case 'sources':
            console.log('Source documents:', data.data);
            break;
          case 'chunk':
            process.stdout.write(data.content);
            break;
          case 'done':
            console.log('\nStream complete');
            break;
          case 'error':
            console.error('Error:', data.message);
            break;
        }
      }
    }
  }
}

// Usage
ragLLMSearch('What is the minimum credit score?');
```

### Example 4: Python Client

```python
import httpx
import json

async def rag_llm_search(query: str):
    async with httpx.AsyncClient() as client:
        async with client.stream(
            'POST',
            'http://localhost:8000/api/rag-llm-search',
            json={
                'query': query,
                'k': 4,
                'temperature': 0.7,
                'include_sources': True
            },
            timeout=30.0
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith('data: '):
                    data = json.loads(line[6:])

                    if data['type'] == 'sources':
                        print(f"Found {len(data['data'])} source documents")
                    elif data['type'] == 'chunk':
                        print(data['content'], end='', flush=True)
                    elif data['type'] == 'done':
                        print('\nComplete!')
                    elif data['type'] == 'error':
                        print(f'\nError: {data["message"]}')

# Usage
import asyncio
asyncio.run(rag_llm_search('What is the minimum credit score?'))
```

## Testing

Run the test suite to verify the integration:

```bash
cd backend
python3 test_llm_integration.py
```

This will test:
1. Basic LLM chat functionality
2. Streaming responses
3. RAG context integration

## Error Handling

The API handles several error scenarios:

1. **RAG system not initialized** (503): Call `/api/rag-init` first
2. **Vector store not loaded** (503): Ensure documents are ingested
3. **LLM initialization failure** (500): Check API key and model name
4. **Invalid model name** (400): Verify the model is supported by your API endpoint
5. **Streaming errors**: Sent as error messages in the stream

## Performance Considerations

1. **Streaming**: Responses are streamed to reduce time-to-first-token
2. **Chunking**: RAG documents are chunked for efficient retrieval
3. **Caching**: LLM and RAG instances are initialized once and reused
4. **Token limits**: Adjust `max_tokens` based on expected response length

## Security

1. **API Key**: Store in `.env` file, never commit to version control
2. **Input validation**: All inputs are validated using Pydantic models
3. **Rate limiting**: Consider implementing rate limiting for production
4. **CORS**: Configure appropriate CORS settings for your frontend domain

## Troubleshooting

### Issue: "RAG system not initialized"
**Solution**: Call `/api/rag-init` endpoint first to initialize the vector store

### Issue: "Failed to initialize LLM"
**Solution**: Check that `OPENAI_API_KEY` is set in your environment

### Issue: "Invalid model name"
**Solution**: Verify the model name matches what's available at your API endpoint. Run:
```bash
curl https://your-api-url/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Issue: Slow responses
**Solution**: 
- Reduce `k` (number of retrieved documents)
- Use a faster model (e.g., claude-haiku instead of opus)
- Reduce `max_tokens`

## Future Enhancements

Potential improvements:
1. Add conversation history support for multi-turn dialogs
2. Implement caching of RAG results for common queries
3. Add support for multiple vector stores
4. Implement hybrid search (keyword + semantic)
5. Add relevance score filtering
6. Support for images and multimodal documents
