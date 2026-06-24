from __future__ import annotations


def score_source_quality(source: dict) -> float:
    score = float(source.get("score") or 0.5)
    url = str(source.get("url") or "")
    content = str(source.get("content") or "")
    title = str(source.get("title") or "")

    if url.startswith("https://"):
        score += 0.05
    if any(marker in url for marker in (".gov", ".edu", ".org")):
        score += 0.05
    if len(content) > 300:
        score += 0.05
    if len(title) > 12:
        score += 0.03
    if "analysis" in content.lower() or "survey" in content.lower() or "report" in content.lower():
        score += 0.05

    return min(score, 1.0)

###### memory.py
