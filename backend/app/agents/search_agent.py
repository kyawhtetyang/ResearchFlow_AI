from __future__ import annotations


def search_sources(query: str) -> list[dict]:
    topic = (query or "AI engineering research").strip()
    normalized = topic.lower()

    base_sources = [
        {
            "title": "Production RAG and retrieval systems",
            "url": "internal://researchflow/rag-knowledge-assistant",
            "snippet": "Existing RAG Knowledge Assistant proves FastAPI, Postgres/pgvector, hybrid retrieval, citations, evals, Docker, and VPS delivery.",
            "content": (
                "A strong AI Engineer portfolio should show retrieval architecture, chunking, embeddings, hybrid search, "
                "citations, background ingestion, evaluation, and deployment. The prior RAG Knowledge Assistant already "
                "covers this baseline, so the next project should move into workflow orchestration and source-backed reports."
            ),
            "score": 0.92,
        },
        {
            "title": "Agentic workflow architecture",
            "url": "internal://researchflow/agentic-workflows",
            "snippet": "Agent systems should expose planning, tool calls, state transitions, intermediate steps, and final artifacts.",
            "content": (
                "ResearchFlow AI should demonstrate planner, search/retrieval, analysis, report generation, stored steps, "
                "source quality scoring, and repeatable verification. This proves agent engineering beyond a chatbot."
            ),
            "score": 0.88,
        },
        {
            "title": "AI Engineer project requirements",
            "url": "internal://researchflow/ai-engineer-role",
            "snippet": "Recruiter-friendly AI Engineer projects combine backend reliability, LLM workflows, evaluation, and deployment.",
            "content": (
                "Important skills include Python, FastAPI, PostgreSQL, Docker, vector search, RAG, LLM orchestration, "
                "evaluation, observability, and clean frontend demos. The strongest story is a product that stores jobs, "
                "sources, reports, and quality signals."
            ),
            "score": 0.86,
        },
        {
            "title": "OpenAI Agents SDK upgrade path",
            "url": "internal://researchflow/openai-agents-sdk",
            "snippet": "Later versions can add tools, handoffs, guardrails, sessions, and tracing through the OpenAI Agents SDK.",
            "content": (
                "The v1 release should keep a custom orchestrator. The v2 release should introduce the OpenAI Agents SDK "
                "to demonstrate tool calling, handoffs, guardrails, sessions, human review points, and traces without "
                "hiding the core backend architecture."
            ),
            "score": 0.83,
        },
        {
            "title": "Evaluation and observability layer",
            "url": "internal://researchflow/eval-observability",
            "snippet": "AI Engineer projects should include repeatable checks, quality scoring, and visible traces or stored workflow steps.",
            "content": (
                "ResearchFlow AI should include first-boot verification, source quality scoring, stored agent steps, "
                "readiness summaries, and later regression evals. This makes the demo more production-oriented than a "
                "one-off LLM interaction."
            ),
            "score": 0.81,
        },
    ]

    if "langchain" in normalized or "langgraph" in normalized or "llamaindex" in normalized:
        base_sources.append(
            {
                "title": "Framework comparison path",
                "url": "internal://researchflow/framework-comparison",
                "snippet": "Build custom v1 first, then compare OpenAI Agents SDK, LangGraph, LangChain, and LlamaIndex in later versions.",
                "content": (
                    "Frameworks are useful, but the first release should show first-principles architecture. Later versions "
                    "can add OpenAI Agents SDK for tools/handoffs/guardrails, LangGraph for stateful workflows, LangChain "
                    "for common chains/retrievers, and LlamaIndex for document indexing."
                ),
                "score": 0.84,
            }
        )

    return base_sources
