---
description: Run all backend tests and report results
---

Run the backend's standalone test scripts and summarize pass/fail for each:

```bash
cd backend
python test_rag_init.py
python test_llm_integration.py
python test_streaming_endpoint.py
python rag/test_rag.py
```

For each script: report whether it succeeded or failed, and if it failed, show the relevant error and propose a fix. Do not modify code unless the user asks — just run, observe, and report. If `requirements.txt` dependencies are missing, install them first with `pip install -r requirements.txt`.
