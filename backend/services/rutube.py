"""RuTube video search via public API (no auth required).

RuTube API endpoint: GET https://rutube.ru/api/search/video/?query=...&format=json
Response structure: {"count": N, "results": [...video objects...]}

Video object fields (as of 2025):
  id             — string UUID
  title          — string
  duration       — int (seconds)
  hits           — int (view count)
  publication_ts — ISO datetime string (e.g. "2026-01-15T10:30:00")
  thumbnail_url  — string URL
  video_url      — string URL (canonical page URL)
  author         — {"name": "..."}
"""

import json
import logging
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

_BASE_URL = "https://rutube.ru/api/search/video/"
_HTTP_TIMEOUT = 15
_REQUEST_DELAY = 0.5  # seconds between queries to avoid rate limiting


def search_videos(
    queries: list[str], max_per_query: int = 10, freshness_days: int = 30
) -> list[dict]:
    seen: set[str] = set()
    results: list[dict] = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=freshness_days)
    fetched_count = 0  # total items received from API (before date filter)

    for i, query in enumerate(queries):
        if i > 0:
            time.sleep(_REQUEST_DELAY)
        try:
            items = _fetch_query(query, count=max_per_query * 2)
        except Exception as exc:
            logger.warning("RuTube search failed for query '%s': %s", query, exc)
            continue

        fetched_count += len(items)
        for item in items:
            video_id = str(item.get("id", ""))
            if not video_id or video_id in seen:
                continue

            pub = _parse_date(item.get("publication_ts") or item.get("created_ts"))
            if pub and pub < cutoff:
                continue

            seen.add(video_id)
            results.append({
                "video_id": video_id,
                "title": item.get("title", ""),
                "channel": (item.get("author") or {}).get("name", ""),
                "url": item.get("video_url", f"https://rutube.ru/video/{video_id}/"),
                "thumbnail": item.get("thumbnail_url", ""),
                "duration": int(item.get("duration") or 0),
                "views": int(item.get("hits") or 0),
                "published_at": pub.isoformat() if pub else "",
                "embed_url": f"https://rutube.ru/play/embed/{video_id}",
                "source": "rutube",
            })

            if len(results) >= max_per_query * len(queries):
                break

    # If API returned items but date filter removed all of them, retry without cutoff
    if not results and fetched_count > 0 and freshness_days < 3650:
        logger.info("RuTube: %d items fetched but all filtered by date, retrying without cutoff", fetched_count)
        return search_videos(queries, max_per_query=max_per_query, freshness_days=3650)

    return results


def _fetch_query(query: str, count: int) -> list[dict]:
    params = urllib.parse.urlencode({"query": query, "format": "json", "perPage": count})
    url = f"{_BASE_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as resp:
        data = json.loads(resp.read())
    return data.get("results", [])


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, AttributeError):
        return None
