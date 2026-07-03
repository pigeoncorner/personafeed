import asyncio
import logging
import random
from datetime import date

from fastapi import APIRouter, HTTPException

from backend.cache import TTLCache
from backend.categories import get_category, list_categories
from backend.schemas import (
    FeedRequest,
    FeedResponse,
    NewsItem,
    SurpriseRequest,
    VideoItem,
)
from backend.services import ai, youtube, news as news_service

router = APIRouter()
logger = logging.getLogger(__name__)

_cache = TTLCache()

_TTL_FEED = 6 * 3600  # 6 часов (ключ включает дату — завтра лента другая)


@router.get("/categories")
async def get_categories():
    return list_categories()


@router.post("/feed", response_model=FeedResponse)
async def get_feed(req: FeedRequest):
    category = get_category(req.category)
    if category:
        category_id, label, hint = category["id"], category["label"], category["hint"]
    else:
        # произвольная тема из поиска
        category_id, label, hint = req.category, req.category, ""

    feed_key = f"feed:{category_id}:{req.language}:{date.today().isoformat()}"
    cached = _cache.get(feed_key)
    if cached:
        cached["cached"] = True
        return FeedResponse(**cached)

    payload = await _build_feed(category_id, label, hint, req.language)
    _cache.set(feed_key, payload, _TTL_FEED)
    return FeedResponse(**payload)


@router.post("/surprise", response_model=FeedResponse)
async def get_surprise(req: SurpriseRequest):
    if not req.categories:
        raise HTTPException(status_code=422, detail="Нужна хотя бы одна категория")

    category_id = random.choice(req.categories)
    category = get_category(category_id)
    if category is None:
        raise HTTPException(status_code=422, detail=f"Неизвестная категория: {category_id}")

    # без кеша — каждый клик новая тема
    payload = await _build_feed(
        category["id"], category["label"], category["hint"], req.language
    )
    return FeedResponse(**payload)


async def _build_feed(category_id: str, label: str, hint: str, language: str) -> dict:
    # 1. Неожиданная тема внутри категории
    try:
        topic = await ai.generate_topic(label, hint, language)
    except Exception as exc:
        logger.error("Topic generation failed: %s", exc)
        raise HTTPException(status_code=503, detail="Не удалось сгенерировать тему")

    # 2. Параллельные запросы к YouTube и News
    youtube_raw: list[dict] = []
    news_raw: list[dict] = []

    async def fetch_youtube():
        nonlocal youtube_raw
        try:
            youtube_raw = await asyncio.to_thread(
                youtube.search_videos, topic["queries"]
            )
        except Exception as exc:
            logger.warning("YouTube fetch failed: %s", exc)

    async def fetch_news():
        nonlocal news_raw
        try:
            news_raw = await news_service.search_news(topic["news_topics"])
        except Exception as exc:
            logger.warning("News fetch failed: %s", exc)

    await asyncio.gather(fetch_youtube(), fetch_news())

    # 3. Курирование через Claude
    curated_youtube = []
    curated_news = []
    searches = topic.get("queries", [])[:3]

    try:
        curated = await ai.curate_feed(topic, youtube_raw, news_raw, language)
        searches = curated.get("top_searches", searches)

        id_to_raw = {v["video_id"]: v for v in youtube_raw}
        for item in curated.get("youtube", []):
            raw = id_to_raw.get(item.get("video_id"), {})
            curated_youtube.append(
                VideoItem(
                    video_id=item.get("video_id", ""),
                    title=item.get("title") or raw.get("title", ""),
                    channel=item.get("channel") or raw.get("channel", ""),
                    url=raw.get("url", f"https://www.youtube.com/watch?v={item.get('video_id','')}"),
                    thumbnail=raw.get("thumbnail", ""),
                    duration=raw.get("duration", 0),
                    views=raw.get("views", 0),
                    published_at=raw.get("published_at", ""),
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
                video_id=v["video_id"],
                title=v["title"],
                channel=v["channel"],
                url=v["url"],
                thumbnail=v["thumbnail"],
                duration=v.get("duration", 0),
                views=v.get("views", 0),
                published_at=v.get("published_at", ""),
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

    return {
        "category_id": category_id,
        "category_label": label,
        "topic": topic["topic"],
        "intro": topic.get("intro", ""),
        "youtube": [v.model_dump() for v in curated_youtube],
        "news": [n.model_dump() for n in curated_news],
        "searches": searches,
        "cached": False,
    }
