# LOUS API Endpoints

Complete reference for all REST API endpoints in the LOUS backend.

**Base URL**: `http://localhost:8000`  
**API Prefix**: `/api` (all endpoints below are prefixed with `/api`)

---

## Health

| Method + Path | Description | Request | Response |
|---------------|-------------|---------|----------|
| `GET /api/health` | Health check endpoint | None | `{status: "healthy", timestamp: ISO8601, service: "LOUS API"}` |

---

## Authentication

| Method + Path | Description | Request | Response |
|---------------|-------------|---------|----------|
| `POST /api/user-auth` | Authenticate user against SQLite database | **Body**: `AuthRequest` <br> - `username: str` <br> - `password: str` | **Success**: `AuthResponse` <br> - `success: bool` <br> - `message: str` <br> - `username: str` <br> - `role: str` <br><br> **Error 401**: Invalid credentials <br> **Error 500**: Server error |

---

## Admin Tables

**Note**: These endpoints are currently NOT protected by authentication middleware. They should be restricted to admin role once auth middleware is implemented.

### Table Management

| Method + Path | Description | Request | Response |
|---------------|-------------|---------|----------|
| `GET /api/admin/tables` | List all user tables in database | None | `TableListResponse` <br> - `tables: list[str]` (excludes sqlite_* system tables) |
| `GET /api/admin/tables/{table_name}/schema` | Get schema information for a specific table | **Path**: `table_name: str` | `TableSchemaResponse` <br> - `table_name: str` <br> - `columns: list[ColumnInfo]` <br><br> Each `ColumnInfo`: <br> - `name: str` <br> - `type: str` <br> - `notnull: bool` <br> - `pk: bool` <br> - `default_value: str \| null` <br><br> **Error 404**: Table not found |
| `GET /api/admin/tables/{table_name}/rows` | Get all rows from a specific table | **Path**: `table_name: str` | `RowsResponse` <br> - `table_name: str` <br> - `rows: list[dict]` <br> - `count: int` <br><br> **Error 404**: Table not found |
| `POST /api/admin/tables/{table_name}/rows` | Insert a new row into a table | **Path**: `table_name: str` <br><br> **Body**: `CreateRowRequest` <br> - `data: Dict[str, Any]` (column_name: value pairs) | **Success**: <br> - `success: true` <br> - `message: str` <br> - `row_id: int` <br><br> **Error 400**: Invalid columns or constraint violation <br> **Error 404**: Table not found |
| `DELETE /api/admin/tables/{table_name}/rows` | Delete a row from a table by primary key | **Path**: `table_name: str` <br><br> **Body**: `DeleteRowRequest` <br> - `primary_key: Dict[str, Any]` (pk_column: value pairs) | **Success**: <br> - `success: true/false` <br> - `message: str` <br> - `deleted_count: int` <br><br> **Error 400**: Invalid PK columns or no PK defined <br> **Error 404**: Table not found |

---

## Submitted Documents

| Method + Path | Description | Request | Response |
|---------------|-------------|---------|----------|
| `GET /api/submitted-docs?user_id={user_id}` | Get all submitted loan documents for a specific user | **Query**: `user_id: str` (required) | `SubmittedDocsResponse` <br> - `user_id: str` <br> - `documents: list[dict]` (each with DOC_TYPE and STATUS) <br> - `count: int` <br><br> **Error 400**: Missing user_id |

---

## RAG/LLM

### Initialization & Status

| Method + Path | Description | Request | Response |
|---------------|-------------|---------|----------|
| `POST /api/rag-init` | Initialize RAG system with specified config (recreates collection if exists) | **Body**: `InitializeRequest` <br> - `chunk_size: int` (default: 1000, range: 100-5000) <br> - `chunk_overlap: int` (default: 200, range: 0-1000) <br> - `persist_directory: str \| null` (default: backend/chroma_db) <br> - `collection_name: str` (default: "loan_documents") <br> - `embedding_model: str` (default: "text-embedding-3-small") <br> - `use_local_embeddings: bool` (default: false) | `StatusResponse` <br> - `initialized: bool` <br> - `vectorstore_loaded: bool` <br> - `message: str` <br><br> **Error 500**: Init/loading/collection creation failure |
| `GET /api/rag-status` | Check current status of RAG system | None | `StatusResponse` <br> - `initialized: bool` <br> - `vectorstore_loaded: bool` <br> - `message: str` |

### Similarity Search

| Method + Path | Description | Request | Response |
|---------------|-------------|---------|----------|
| `POST /api/rag-search` | Perform similarity search on vector store | **Body**: `SearchQuery` <br> - `query: str` (min length: 1) <br> - `k: int` (default: 4, range: 1-20) | `SearchResponse` <br> - `query: str` <br> - `results: list[DocumentResult]` <br> - `count: int` <br><br> Each `DocumentResult`: <br> - `page_content: str` <br> - `metadata: dict` <br><br> **Error 503**: RAG not initialized <br> **Error 500**: Search failed |
| `GET /api/rag-search?query={query}&k={k}` | Perform similarity search (GET alternative) | **Query**: <br> - `query: str` (required, min length: 1) <br> - `k: int` (default: 4, range: 1-20) | Same as POST `/api/rag-search` |
| `POST /api/rag-search-with-score` | Perform similarity search with relevance scores (lower = more similar) | **Body**: `SearchQuery` <br> - `query: str` (min length: 1) <br> - `k: int` (default: 4, range: 1-20) | `SearchWithScoreResponse` <br> - `query: str` <br> - `results: list[ScoredDocumentResult]` <br> - `count: int` <br><br> Each `ScoredDocumentResult`: <br> - `page_content: str` <br> - `metadata: dict` <br> - `score: float` <br><br> **Error 503**: RAG not initialized <br> **Error 500**: Search failed |
| `GET /api/rag-search-with-score?query={query}&k={k}` | Perform similarity search with scores (GET alternative) | **Query**: <br> - `query: str` (required, min length: 1) <br> - `k: int` (default: 4, range: 1-20) | Same as POST `/api/rag-search-with-score` |

### RAG + LLM Streaming

| Method + Path | Description | Request | Response |
|---------------|-------------|---------|----------|
| `POST /api/rag-llm-search` | Perform RAG search + generate streaming LLM response | **Body**: `RAGLLMSearchQuery` <br> - `query: str` (min length: 1) <br> - `k: int` (default: 4, range: 1-20) <br> - `temperature: float \| null` (default: 0.7, range: 0.0-2.0) <br> - `max_tokens: int \| null` (default: 1500, range: 100-4000) <br> - `system_prompt: str \| null` (optional custom prompt) <br> - `include_sources: bool` (default: true) | **Streaming Response** (text/event-stream, Server-Sent Events): <br><br> 1. If `include_sources=true`: <br> `{"type": "sources", "data": [{page_content, metadata, score}, ...]}` <br><br> 2. LLM chunks: <br> `{"type": "chunk", "content": "text"}` (multiple) <br><br> 3. Completion: <br> `{"type": "done"}` <br><br> 4. Error (if any): <br> `{"type": "error", "message": "..."}` <br><br> **Error 503**: RAG not initialized <br> **Error 500**: LLM init or search failed |

---

## SPA Routes

| Method + Path | Description |
|---------------|-------------|
| `GET /test` | Serve test.html for Docker verification |
| `GET /{full_path:path}` | Catch-all SPA route — serves frontend/dist/index.html for all non-API routes (defined LAST in routing) |

---

## Security Notes

- **Admin endpoints**: Currently **NOT** protected by authentication middleware. Should be restricted to admin role once auth is implemented.
- **SQL Injection Protection**: All table/column names are validated against the database schema before use. Only VALUES use parameterized queries (? placeholders). SQLite does not support parameterized table/column identifiers.
- **CORS**: Currently allows all origins (`allow_origins=["*"]`) — should be restricted in production.

---

## Request/Response Models

### Authentication
```python
# Request
AuthRequest:
  username: str
  password: str

# Response
AuthResponse:
  success: bool
  message: str
  username: str | None
  role: str | None
```

### Admin Tables
```python
# Table Management
CreateRowRequest:
  data: Dict[str, Any]  # {column_name: value, ...}

DeleteRowRequest:
  primary_key: Dict[str, Any]  # {pk_column: value, ...}

# Schema Info
ColumnInfo:
  name: str
  type: str
  notnull: bool
  pk: bool
  default_value: str | None
```

### RAG/LLM
```python
# Initialization
InitializeRequest:
  chunk_size: int = 1000
  chunk_overlap: int = 200
  persist_directory: str | None = None
  collection_name: str = "loan_documents"
  embedding_model: str = "text-embedding-3-small"
  use_local_embeddings: bool = False

# Search
SearchQuery:
  query: str
  k: int = 4

# RAG + LLM
RAGLLMSearchQuery:
  query: str
  k: int = 4
  temperature: float | None = 0.7
  max_tokens: int | None = 1500
  system_prompt: str | None = None
  include_sources: bool = True

# Results
DocumentResult:
  page_content: str
  metadata: Dict[str, Any]

ScoredDocumentResult:
  page_content: str
  metadata: Dict[str, Any]
  score: float
```

---

## Testing

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Default test credentials:
- Admin: `admin` / `admin123`
- Loan Officer: `loan_officer` / `officer123`
- Underwriter: `underwriter` / `under123`

**⚠️ Change these before production deployment.**
