from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.config import settings
from app.services.errors import ConfigurationError, NoSourcesFoundError, SearchProviderError


def _search_tavily(query: str) -> list[dict]:
    if not settings.tavily_api_key.strip():
        raise ConfigurationError("TAVILY_API_KEY is missing for live web search.")

    payload = {
        "api_key": settings.tavily_api_key,
        "query": query,
        "search_depth": settings.tavily_search_depth,
        "topic": "general",
        "max_results": settings.search_max_results,
        "include_answer": False,
        "include_raw_content": True,
    }
    request = Request(
        "https://api.tavily.com/search",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=settings.provider_timeout_seconds) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise SearchProviderError(
            "Search provider rejected the request.",
            detail or str(exc),
        ) from exc
    except URLError as exc:
        raise SearchProviderError(
            "Search provider request failed to reach Tavily.",
            str(exc),
        ) from exc
    except Exception as exc:
        raise SearchProviderError(
            "Unexpected search provider failure while contacting Tavily.",
            str(exc),
        ) from exc

    results = []
    seen_urls: set[str] = set()
    for item in body.get("results", []):
        url = str(item.get("url") or "").strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        content = str(item.get("raw_content") or item.get("content") or "").strip()
        snippet = str(item.get("content") or item.get("snippet") or "").strip()
        results.append(
            {
                "title": str(item.get("title") or "Untitled source").strip(),
                "url": url,
                "snippet": snippet[:500],
                "content": (content or snippet)[:6000],
                "score": float(item.get("score") or 0.0),
            }
        )

    if not results:
        raise NoSourcesFoundError()

    return results


def search_web(query: str) -> list[dict]:
    provider = settings.search_provider.strip().lower()
    if provider == "tavily":
        return _search_tavily(query)
    raise ConfigurationError(f"Unsupported SEARCH_PROVIDER: {settings.search_provider}")
