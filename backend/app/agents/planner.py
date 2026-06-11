from __future__ import annotations


def plan_research(query: str) -> list[str]:
    topic = (query or "").strip()
    if not topic:
        return []

    return [
        f"Clarify the research goal and expected output for: {topic}",
        "Identify the strongest evidence categories: job requirements, technical docs, project examples, and market signals.",
        "Collect candidate sources and rank them by relevance, specificity, and credibility.",
        "Extract repeated requirements, tools, patterns, and implementation signals.",
        "Write a concise report with findings, recommended build direction, and citations.",
    ]
