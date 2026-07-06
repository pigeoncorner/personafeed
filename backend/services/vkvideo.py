"""VK Video search via VK API v5.199.

Requires a user access_token with `video` scope in settings.vk_access_token.
Without the token this module is never called.
"""

import json
import logging
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

from backend.config import settings

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.vk.com/method/video.search"
_HTTP_TIMEOUT = 15


def search_videos(
    queries: list[str], max_per_query: int = 10, freshness_days: int = 30
) -> list[dict]:
    seen: set[str] = set()
    results: list[dict] = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=freshness_days)

    for query in queries:
        items, groups, profiles = _fetch_query(query, count=max_per_query * 2)
        owner_names = _build_owner_map(groups, profiles)

        for item in items:
            owner_id = item.get("owner_id", 0)
            item_id = item.get("id", 0)
            video_id = f"{owner_id}_{item_id}"

            if video_id in seen:
                continue

            pub = _unix_to_dt(item.get("date"))
            if pub and pub < cutoff:
                continue

            seen.add(video_id)
            results.append({
                "video_id": video_id,
                "title": item.get("title", ""),
                "channel": owner_names.get(owner_id, ""),
                "url": f"https://vk.com/video{owner_id}_{item_id}",
                "thumbnail": _pick_thumbnail(item.get("image", [])),
                "duration": int(item.get("duration") or 0),
                "views": int(item.get("views") or 0),
                "published_at": pub.isoformat() if pub else "",
                "embed_url": item.get("player", ""),
                "source": "vk",
            })

            if len(results) >= max_per_query * len(queries):
                break

    # Fallback: relax freshness to 180 days if nothing found
    if not results and freshness_days < 180:
        logger.info("VK: no results within %d days, retrying with 180 days", freshness_days)
        return search_videos(queries, max_per_query=max_per_query, freshness_days=180)

    return results


def _fetch_query(query: str, count: int) -> tuple[list[dict], list[dict], list[dict]]:
    params = urllib.parse.urlencode({
        "q": query,
        "count": count,
        "sort": 2,        # by relevance
        "adult": 0,
        "extended": 1,    # include groups/profiles for channel names
        "v": "5.199",
        "access_token": settings.vk_access_token,
    })
    url = f"{_BASE_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as resp:
        data = json.loads(resp.read())

    if "error" in data:
        raise RuntimeError(
            f"VK API error {data['error'].get('error_code')}: "
            f"{data['error'].get('error_msg', 'unknown')}"
        )

    resp_body = data.get("response", {})
    return (
        resp_body.get("items", []),
        resp_body.get("groups", []),
        resp_body.get("profiles", []),
    )


def _build_owner_map(groups: list[dict], profiles: list[dict]) -> dict[int, str]:
    names: dict[int, str] = {}
    for g in groups:
        names[-g["id"]] = g.get("name", "")
    for p in profiles:
        names[p["id"]] = f"{p.get('first_name', '')} {p.get('last_name', '')}".strip()
    return names


def _pick_thumbnail(images: list[dict]) -> str:
    if not images:
        return ""
    target = 320
    best = min(images, key=lambda img: abs(img.get("width", 0) - target))
    return best.get("url", "")


def _unix_to_dt(ts: int | None) -> datetime | None:
    if not ts:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc)
