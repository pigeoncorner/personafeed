import re
from datetime import datetime, timedelta, timezone

from googleapiclient.discovery import build

from backend.config import settings

_yt = None

_DURATION_RE = re.compile(
    r"PT(?:(?P<h>\d+)H)?(?:(?P<m>\d+)M)?(?:(?P<s>\d+)S)?"
)


def _client():
    global _yt
    if _yt is None:
        _yt = build("youtube", "v3", developerKey=settings.youtube_api_key)
    return _yt


def parse_duration(iso: str) -> int:
    match = _DURATION_RE.fullmatch(iso or "")
    if not match:
        return 0
    h, m, s = (int(match.group(g) or 0) for g in ("h", "m", "s"))
    return h * 3600 + m * 60 + s


def _enrich(videos: list[dict]) -> None:
    ids = [v["video_id"] for v in videos]
    details: dict[str, dict] = {}
    for i in range(0, len(ids), 50):
        response = (
            _client()
            .videos()
            .list(id=",".join(ids[i : i + 50]), part="contentDetails,statistics")
            .execute()
        )
        for item in response.get("items", []):
            details[item["id"]] = item

    for video in videos:
        item = details.get(video["video_id"], {})
        video["duration"] = parse_duration(
            item.get("contentDetails", {}).get("duration", "")
        )
        video["views"] = int(item.get("statistics", {}).get("viewCount", 0))


def search_videos(
    queries: list[str], max_per_query: int = 5, freshness_days: int = 30
) -> list[dict]:
    seen: set[str] = set()
    results: list[dict] = []

    published_after = (
        datetime.now(timezone.utc) - timedelta(days=freshness_days)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    for i, query in enumerate(queries):
        response = (
            _client()
            .search()
            .list(
                q=query,
                part="snippet",
                type="video",
                maxResults=max_per_query,
                relevanceLanguage="en",
                publishedAfter=published_after,
                # последний запрос — по дате: смесь релевантного и самого нового
                order="date" if i == len(queries) - 1 else "relevance",
            )
            .execute()
        )
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            if video_id in seen:
                continue
            seen.add(video_id)
            snippet = item["snippet"]
            results.append(
                {
                    "video_id": video_id,
                    "title": snippet["title"],
                    "channel": snippet["channelTitle"],
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "thumbnail": snippet["thumbnails"]["medium"]["url"],
                    "published_at": snippet.get("publishedAt", ""),
                }
            )

    if results:
        _enrich(results)

    return results
