import asyncio
import logging

from fastapi import APIRouter, HTTPException

from backend.categories import CATEGORIES, list_categories
from backend.schemas import GridRequest, GridResponse, VideoItem
from backend.services import pool as pool_service

router = APIRouter()
logger = logging.getLogger(__name__)

_VALID_SOURCES = {"youtube", "ru"}


@router.get("/categories")
async def get_categories():
    return list_categories()


@router.post("/grid", response_model=GridResponse)
async def get_grid(req: GridRequest):
    if not req.categories:
        raise HTTPException(status_code=422, detail="Нужна хотя бы одна категория")

    if req.source not in _VALID_SOURCES:
        raise HTTPException(
            status_code=422,
            detail=f"Неизвестный источник '{req.source}'. Допустимые: {sorted(_VALID_SOURCES)}"
        )

    valid_ids = [c for c in req.categories if c in CATEGORIES]
    unknown = [c for c in req.categories if c not in CATEGORIES]
    if unknown:
        logger.warning("Unknown categories ignored: %s", unknown)
    if not valid_ids:
        raise HTTPException(status_code=422, detail="Нет известных категорий")

    raw = await asyncio.to_thread(
        pool_service.sample, valid_ids, CATEGORIES, req.limit, req.source
    )

    items = [
        VideoItem(
            video_id=v.get("video_id", ""),
            title=v.get("title", ""),
            channel=v.get("channel", ""),
            url=v.get("url", ""),
            thumbnail=v.get("thumbnail", ""),
            duration=v.get("duration", 0),
            views=v.get("views", 0),
            published_at=v.get("published_at", ""),
            why_relevant=v.get("why_relevant", ""),
            category_id=v.get("category_id", ""),
            category_label=v.get("category_label", ""),
            source=v.get("source", req.source),
            embed_url=v.get("embed_url", ""),
        )
        for v in raw
    ]

    return GridResponse(items=items)
