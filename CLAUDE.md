# LOUS — Loan Origination & Underwriting System

AI-powered loan origination/underwriting demo app. RAG-based policy lookup + LLM-driven underwriting assistance.

## Stack

- **Backend**: Python 3.11, FastAPI, SQLite (`backend/db/lous.db`), ChromaDB (vector store for RAG), LangChain, OpenAI/Anthropic via `backend/llm/`
- **Frontend**: React 18, Vite, Tailwind CSS, React Router, Axios

## Project Structure

```
backend/
  main.py            # FastAPI app entry, serves API + built frontend SPA
  api/api.py          # RAG API: similarity search + LLM endpoints
  routers/            # health.py, auth.py
  agents/             # (scaffolded, not yet implemented)
  tools/              # (scaffolded, not yet implemented)
  rag/rag_setup.py    # ChromaDB + embedding pipeline setup
  llm/                # LLM wrapper (Claude/OpenAI)
  db/database.py      # SQLite access
  policies/underwriting_policies.pdf  # source doc for RAG index
frontend/
  src/pages/          # LoginPage.jsx, Dashboard.jsx
  src/api/client.js    # Axios client
  src/components/
```

## Run Commands

Backend (from `backend/`):
```bash
pip install -r requirements.txt
python main.py          # http://localhost:8000
```

Frontend (from `frontend/`):
```bash
npm install
npm run dev              # http://localhost:5173
```

Docker (full stack): `docker-compose up --build` → http://localhost:8000

## Tests

No unified test runner yet — tests are standalone scripts, run individually:
```bash
python backend/rag/test_rag.py
python backend/test_rag_init.py
python backend/test_llm_integration.py
python backend/test_streaming_endpoint.py
```
TODO: consolidate into a `pytest` suite under `backend/tests/`.

## Environment Variables

Backend `.env` (copy from `backend/.env.example`): `API_HOST`, `API_PORT`, `DATABASE_PATH`, `CHROMA_PERSIST_DIRECTORY`, `OPENAI_API_KEY` (required for RAG/embeddings), `ANTHROPIC_API_KEY` (optional, for Claude LLM).

Frontend `.env` (copy from `frontend/.env.example`): `VITE_API_URL` (leave empty for local dev — uses Vite proxy).

## Default Test Logins

`admin` / `admin123`, `loan_officer` / `officer123`, `underwriter` / `under123` — change before production.

## API Endpoints (current)

- `GET /api/health`
- `POST /api/user-auth`
- RAG/LLM endpoints under `/api/` from `backend/api/api.py` (similarity search, streaming chat)

## Conventions & Notes

- API routers are registered before the SPA static-file mount in `main.py`; the catch-all SPA route is always defined **last** — keep it that way when adding routers.
- `backend/agents/` and `backend/tools/` are empty scaffolds — this is where the underwriting AI agent logic is intended to land per the roadmap.
- RAG source-of-truth document is `backend/policies/underwriting_policies.pdf`; re-run `backend/rag/rag_setup.py` indexing after changing it.
- No CI configured yet (no `.github/workflows/`). No linter config committed for backend (no `ruff`/`black` config) or frontend (no `.eslintrc`).
- This is a demo/prototype (single commit history) — expect rapid structural changes; keep this file updated as routers/agents/tools fill in.

## Roadmap (from README, unchecked)

Loan application submission workflow, document upload/management, AI underwriting engine, risk dashboard, compliance checking automation, report generation, credit bureau integration, email notifications, advanced analytics.
