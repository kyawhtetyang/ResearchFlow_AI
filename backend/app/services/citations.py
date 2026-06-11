from __future__ import annotations


def score_source_quality(source: dict) -> float:
    score = float(source.get("score") or 0.5)
    url = str(source.get("url") or "")
    content = str(source.get("content") or "")

    if url.startswith("internal://"):
        score += 0.05
    if len(content) > 180:
        score += 0.05
    if "deployment" in content.lower() or "evaluation" in content.lower():
        score += 0.05

    return min(score, 1.0)
