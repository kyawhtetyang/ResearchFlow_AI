from __future__ import annotations


def generate_report(query: str, plan: list[str], findings: list[str], sources: list[dict]) -> str:
    lines = [
        f"# Research Report: {query}",
        "",
        "## Executive Summary",
        "ResearchFlow AI is a standalone agentic research workflow platform. It extends the prior RAG project by adding planning, evidence collection, analysis, reporting, and stored workflow traces.",
        "",
        "## Research Plan",
    ]

    for idx, item in enumerate(plan, start=1):
        lines.append(f"{idx}. {item}")

    lines.extend(["", "## Key Findings"])
    for item in findings:
        lines.append(f"- {item}")

    lines.extend(["", "## Recommended Build Direction"])
    lines.extend(
        [
            "- Build v1 with a custom orchestrator before adopting a framework.",
            "- Use FastAPI, PostgreSQL, Docker, SQLAlchemy, and Alembic as the production foundation.",
            "- Store jobs, steps, sources, and reports so the workflow is auditable.",
            "- Add framework upgrades later: OpenAI Agents SDK, LangGraph, LangChain, and LlamaIndex.",
            "- Connect AI/ML Portfolio Ask only after the standalone ResearchFlow API is stable.",
        ]
    )

    lines.extend(["", "## Recruiter-Facing Proof"])
    lines.extend(
        [
            "- Backend system design: job lifecycle, source storage, report storage, and API contracts.",
            "- AI workflow design: visible planner, search, analysis, and report steps.",
            "- Reliability mindset: deterministic fallback mode, source quality scores, and first-boot verification.",
            "- Upgrade path: OpenAI Agents SDK, LangGraph, LangChain, LlamaIndex, and portfolio integration.",
        ]
    )

    lines.extend(["", "## Sources"])
    for idx, source in enumerate(sources, start=1):
        lines.append(f"{idx}. [{source['title']}]({source['url']}) - quality {source.get('quality_score', source.get('score', 0)):.2f}")

    return "\n".join(lines)
