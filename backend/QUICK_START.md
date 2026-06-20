# Quick Start Guide: RAG + LLM API

## Prerequisites

1. Backend dependencies installed: `pip install -r requirements.txt`
2. Environment variables configured in `.env`:
   ```bash
   OPENAI_API_KEY=your_api_key
   OPENAI_BASE_URL=https://llm.aibricks.io/v1  # or leave empty for standard OpenAI
   ```
3. RAG system initialized with documents

## Step 1: Start the Backend Server

```bash
cd /home/coder/lous/backend
python3 main.py
```

The server will start on `http://localhost:8000`

## Step 2: Initialize RAG System (if not already done)

```bash
curl -X POST "http://localhost:8000/api/rag-init" \
  -H "Content-Type: application/json" \
  -d '{
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "persist_directory": "./chroma_db",
    "collection_name": "loan_documents"
  }'
```

This will:
- Load PDF documents from `./policies` directory
- Create embeddings
- Store vectors in ChromaDB

## Step 3: Test the RAG + LLM Endpoint

### Option A: Using the Test Script

```bash
python3 test_streaming_endpoint.py "What is the minimum credit score requirement?"
```

### Option B: Using curl

```bash
curl -N -X POST "http://localhost:8000/api/rag-llm-search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the loan approval requirements?",
    "k": 4,
    "temperature": 0.7,
    "include_sources": true
  }'
```

Note: The `-N` flag disables buffering to see streaming in real-time.

### Option C: Using the Web Interface

Navigate to `http://localhost:8000/docs` to access the FastAPI interactive documentation and test the endpoint directly.

## Example Response

You'll see a streaming response like:

```
data: {"type": "sources", "data": [{"page_content": "...", "metadata": {...}, "score": 0.234}]}

data: {"type": "chunk", "content": "According"}
data: {"type": "chunk", "content": " to"}
data: {"type": "chunk", "content": " the"}
data: {"type": "chunk", "content": " policy"}
...
data: {"type": "done"}
```

## Frontend Integration Example

```javascript
const response = await fetch('http://localhost:8000/api/rag-llm-search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'What is the minimum credit score?',
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
      
      if (data.type === 'chunk') {
        // Append chunk to UI
        displayChunk(data.content);
      } else if (data.type === 'sources') {
        // Display source documents
        displaySources(data.data);
      } else if (data.type === 'done') {
        // Mark completion
        markComplete();
      }
    }
  }
}
```

## Troubleshooting

### Issue: "RAG system not initialized"
```bash
# Check status
curl http://localhost:8000/api/rag-status

# Initialize if needed
curl -X POST http://localhost:8000/api/rag-init -H "Content-Type: application/json" -d '{}'
```

### Issue: "Failed to initialize LLM"
Check that `OPENAI_API_KEY` is set:
```bash
echo $OPENAI_API_KEY
```

### Issue: "Invalid model name"
List available models:
```bash
curl https://llm.aibricks.io/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/rag-status` | GET | Check RAG system status |
| `/api/rag-init` | POST | Initialize RAG system |
| `/api/rag-search` | POST | RAG similarity search |
| `/api/rag-llm-search` | POST | **RAG + LLM streaming** |

## Configuration Options

### Request Parameters

```json
{
  "query": "Your question here",        // Required
  "k": 4,                               // Number of docs to retrieve (1-20)
  "temperature": 0.7,                   // LLM creativity (0.0-2.0)
  "max_tokens": 1500,                   // Max response length (100-4000)
  "system_prompt": "Custom prompt",     // Optional system message
  "include_sources": true               // Include source docs in response
}
```

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_api_key_here

# Optional (for custom endpoints)
OPENAI_BASE_URL=https://custom-api.com/v1

# RAG Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

## Next Steps

1. **Test with your own queries**: Experiment with different questions
2. **Adjust parameters**: Try different `k`, `temperature`, and `max_tokens` values
3. **Integrate with frontend**: Use the JavaScript example above
4. **Monitor performance**: Check response times and token usage
5. **Review documentation**: Read `RAG_LLM_API.md` for detailed information

## Resources

- **Full Documentation**: `RAG_LLM_API.md`
- **Implementation Details**: `IMPLEMENTATION_SUMMARY.md`
- **Test Scripts**: `test_llm_integration.py`, `test_streaming_endpoint.py`
- **API Docs**: http://localhost:8000/docs (when server is running)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages in the console
3. Check server logs: `python3 main.py` output
4. Verify environment variables are set correctly
