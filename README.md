# ResearchFlow AI

Agentic research workflow platform:

```text
Plan -> Search -> Analyze -> Report -> Store
```

This project is the upgrade path after `RAG Knowledge Assistant`. The RAG project proves retrieval QA. ResearchFlow AI proves multi-step research orchestration with stored jobs, sources, steps, and reports.

## Setup
```bash
cp .env.example .env
docker compose up -d --build
open http://127.0.0.1:8000/
open http://127.0.0.1:8000/docs
```

## Verify
```bash
docker compose exec -T -e PYTHONPATH=/app api pytest -q
python3 backend/scripts/first_boot_verify.py http://127.0.0.1:8000
```

## API
- `GET /health`
- `POST /api/research/`
- `GET /api/research/{job_id}`
- `GET /api/research/{job_id}/summary`
- `GET /api/jobs/`
- `GET /api/reports/{job_id}`
- `POST /api/eval/run`

## Current Release
- `v1`: standalone custom orchestrator with readiness score, eval summary, frontend demo, tests, and verifier.

## Version Roadmap
- `v1.5`: evaluation and observability.
- `v2`: OpenAI Agents SDK.
- `v2.5`: LangGraph, LangChain, and LlamaIndex comparison.
- `v3`: AI/ML Portfolio Ask integration.
