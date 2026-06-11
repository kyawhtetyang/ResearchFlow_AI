from __future__ import annotations


def summarize_findings(query: str, sources: list[dict]) -> list[str]:
    findings = [
        "The next portfolio step should move from retrieval QA into multi-step research workflow orchestration.",
        "The project should visibly store intermediate agent steps so reviewers can inspect how the answer was produced.",
        "A recruiter-friendly AI Engineer demo needs backend reliability, citations, evaluation, and deployment proof.",
        "The first release should run without a paid API key, then later versions can add OpenAI Agents SDK and ecosystem comparisons.",
    ]

    if sources:
        top_titles = ", ".join(source["title"] for source in sources[:2])
        findings.append(f"The strongest supporting evidence comes from: {top_titles}.")

    if "portfolio" in (query or "").lower() or "ask" in (query or "").lower():
        findings.append("Portfolio Ask should be an integration surface after ResearchFlow AI is stable, not the main engineering lab.")

    return findings
