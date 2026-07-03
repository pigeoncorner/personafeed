from googleapiclient.discovery import build

from backend.config import settings

_yt = None


def _client():
    global _yt
    if _yt is None:
        _yt = build("youtube", "v3", developerKey=settings.youtube_api_key)
    return _yt


def search_videos(queries: list[str], max_per_query: int = 5) -> list[dict]:
    seen: set[str] = set()
    results: list[dict] = []

    for query in queries:
        response = (
            _client()
            .search()
            .list(
                q=query,
                part="snippet",
                type="video",
                maxResults=max_per_query,
                relevanceLanguage="en",
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
                }
            )

    return results
