import asyncio
import logging

from fastapi import APIRouter, HTTPException

from backend.cache import TTLCache
from backend.personas import list_personas
from backend.schemas import FeedRequest, FeedResponse, NewsItem, VideoItem
from backend.services import ai, youtube, news as news_service

router = APIRouter()
logger = logging.getLogger(__name__)

_cache = TTLCache()

_TTL_FEED = 6 * 3600   # 6 часов
_TTL_PROFILE = 24 * 3600  # 24 часа


@router.get("/personas")
async def get_personas():
    return list_personas()


@router.post("/feed", response_model=FeedResponse)
async def get_feed(req: FeedRequest):
    feed_key = f"feed:{req.persona}:{req.specialty}:{req.language}"
    cached = _cache.get(feed_key)
    if cached:
        cached["cached"] = True
        return FeedResponse(**cached)

    # 1. Профиль персонажа
    profile_key = f"profile:{req.persona}:{req.specialty}:{req.language}"
    profile = _cache.get(profile_key)
    if profile is None:
        try:
            profile = await ai.generate_persona_profile(
                req.persona, req.language, req.specialty
            )
            _cache.set(profile_key, profile, _TTL_PROFILE)
        except Exception as exc:
            logger.error("Profile generation failed: %s", exc)
            raise HTTPException(status_code=503, detail="Не удалось сгенерировать профиль персонажа")

    # 2. Параллельные запросы к YouTube и News
    youtube_raw: list[dict] = []
    news_raw: list[dict] = []

    async def fetch_youtube():
        nonlocal youtube_raw
        try:
            youtube_raw = await asyncio.to_thread(
                youtube.search_videos, profile["seed_queries"]
            )
        except Exception as exc:
            logger.warning("YouTube fetch failed: %s", exc)

    async def fetch_news():
        nonlocal news_raw
        try:
            news_raw = await news_service.search_news(profile["topics"])
        except Exception as exc:
            logger.warning("News fetch failed: %s", exc)

    await asyncio.gather(fetch_youtube(), fetch_news())

    # 3. Курирование через Claude
    curated_youtube = []
    curated_news = []
    searches = profile.get("seed_queries", [])[:3]

    try:
        curated = await ai.curate_feed(profile, youtube_raw, news_raw, req.language)
        searches = curated.get("top_searches", searches)

        id_to_raw = {v["video_id"]: v for v in youtube_raw}
        for item in curated.get("youtube", []):
            raw = id_to_raw.get(item.get("video_id"), {})
            curated_youtube.append(
                VideoItem(
                    title=item.get("title") or raw.get("title", ""),
                    channel=item.get("channel") or raw.get("channel", ""),
                    url=raw.get("url", f"https://www.youtube.com/watch?v={item.get('video_id','')}"),
                    thumbnail=raw.get("thumbnail", ""),
                    why_relevant=item.get("why_relevant", ""),
                )
            )

        url_to_raw = {n["url"]: n for n in news_raw}
        for item in curated.get("news", []):
            raw = url_to_raw.get(item.get("url", ""), {})
            curated_news.append(
                NewsItem(
                    title=item.get("title") or raw.get("title", ""),
                    source=item.get("source") or raw.get("source", ""),
                    url=item.get("url", ""),
                    published_at=raw.get("published_at", ""),
                    why_relevant=item.get("why_relevant", ""),
                )
            )
    except Exception as exc:
        logger.warning("Curation failed, returning raw results: %s", exc)
        curated_youtube = [
            VideoItem(
                title=v["title"],
                channel=v["channel"],
                url=v["url"],
                thumbnail=v["thumbnail"],
            )
            for v in youtube_raw
        ]
        curated_news = [
            NewsItem(
                title=n["title"],
                source=n["source"],
                url=n["url"],
                published_at=n["published_at"],
            )
            for n in news_raw
        ]

    payload = {
        "persona_id": profile["id"],
        "persona_name": profile["name"],
        "persona_context": profile["context"],
        "youtube": [v.model_dump() for v in curated_youtube],
        "news": [n.model_dump() for n in curated_news],
        "searches": searches,
        "cached": False,
    }
    _cache.set(feed_key, payload, _TTL_FEED)

    return FeedResponse(**payload)
