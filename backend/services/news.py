import httpx

from backend.config import settings

_BASE_URL = "https://newsapi.org/v2/everything"


async def search_news(topics: list[str], max_per_topic: int = 5) -> list[dict]:
    seen: set[str] = set()
    results: list[dict] = []

    async with httpx.AsyncClient(timeout=15) as client:
        for topic in topics[:2]:  # лимит: 2 запроса чтобы не жечь 100 req/day
            response = await client.get(
                _BASE_URL,
                params={
                    "q": topic,
                    "language": "en",
                    "sortBy": "relevancy",
                    "pageSize": max_per_topic,
                    "apiKey": settings.news_api_key,
                },
            )
            response.raise_for_status()
            for article in response.json().get("articles", []):
                url = article.get("url", "")
                if url in seen or not url:
                    continue
                seen.add(url)
                results.append(
                    {
                        "url": url,
                        "title": article.get("title", ""),
                        "source": article.get("source", {}).get("name", ""),
                        "published_at": article.get("publishedAt", ""),
                    }
                )

    return results
