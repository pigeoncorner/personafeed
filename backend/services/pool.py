"""Video pool per category+source — pre-fetched, persisted, TTL-refreshed.

Pool key: f"{category_id}:{source}" where source in ("youtube", "ru").
Stored in data/pools.json. TTL is 24 hours.
"""

import json
import logging
import random
import threading
import time
from datetime import datetime
from pathlib import Path

from backend.config import settings
from backend.services import youtube

logger = logging.getLogger(__name__)

_POOLS_FILE = Path("data/pools.json")
_TTL = 86400 * 7  # 7 days
_MAX_PER_QUERY = 25
# версия формата записи пула: несовпадение → пул перезапрашивается
# (v2 добавила likes/comments/channel_* — старый кеш без них бесполезен для фильтров)
_POOL_VERSION = 2

# {pool_key: {"fetched_at": float, "videos": [...]}}
_pools: dict[str, dict] = {}
_lock = threading.Lock()


def load_from_disk() -> None:
    if not _POOLS_FILE.exists():
        return
    try:
        data = json.loads(_POOLS_FILE.read_text(encoding="utf-8"))
        valid = {k: v for k, v in data.items() if ":" in k}
        with _lock:
            _pools.update(valid)
        logger.info("Loaded pools for %d keys from disk", len(data))
    except Exception as exc:
        logger.warning("Failed to load pools from disk: %s", exc)


def _save_to_disk() -> None:
    try:
        _POOLS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _POOLS_FILE.write_text(
            json.dumps(_pools, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception as exc:
        logger.warning("Failed to save pools to disk: %s", exc)


def _is_stale(pool: dict) -> bool:
    if pool.get("version") != _POOL_VERSION:
        return True
    return time.time() - pool.get("fetched_at", 0) > _TTL


def _fetch(cat: dict, source: str) -> list[dict]:
    category_id = cat["id"]
    logger.info("Fetching pool for '%s' source='%s'", category_id, source)
    videos: list[dict] = []

    if source == "youtube":
        raw = youtube.search_videos(cat["queries"], max_per_query=_MAX_PER_QUERY)
        for v in raw:
            v = dict(v)
            v.setdefault("source", "youtube")
            v.setdefault("embed_url", "")
            videos.append(v)

    elif source == "ru":
        # RuTube — always
        try:
            from backend.services import rutube
            ru_videos = rutube.search_videos(cat["queries_ru"], max_per_query=_MAX_PER_QUERY)
            videos.extend(ru_videos)
        except Exception as exc:
            logger.warning("RuTube fetch failed for '%s': %s", category_id, exc)

        # VK — only if token is configured
        if settings.vk_access_token:
            try:
                from backend.services import vkvideo
                vk_videos = vkvideo.search_videos(cat["queries_ru"], max_per_query=_MAX_PER_QUERY)
                videos.extend(vk_videos)
            except Exception as exc:
                logger.warning("VK fetch failed for '%s': %s", category_id, exc)

    logger.info("Fetched %d videos for '%s' source='%s'", len(videos), category_id, source)
    return videos


def get_pool(cat: dict, source: str) -> list[dict]:
    """Return pool for category+source, fetching synchronously if missing or stale.

    On fetch failure (quota, network, etc.) returns stale videos if available,
    otherwise returns empty list — never raises to callers.
    """
    pool_key = f"{cat['id']}:{source}"
    with _lock:
        pool = _pools.get(pool_key)
        if pool and not _is_stale(pool):
            return pool["videos"]
        fallback = pool["videos"] if pool else []

    try:
        videos = _fetch(cat, source)
    except Exception as exc:
        logger.warning("Failed to fetch pool for '%s' source='%s': %s", cat["id"], source, exc)
        return fallback

    with _lock:
        _pools[pool_key] = {"version": _POOL_VERSION, "fetched_at": time.time(), "videos": videos}
        _save_to_disk()
    return videos


def refresh_stale(categories: list[dict]) -> None:
    """Refresh all stale pools for both sources. Intended for background calls."""
    for cat in categories:
        for source in ("youtube", "ru"):
            pool_key = f"{cat['id']}:{source}"
            with _lock:
                pool = _pools.get(pool_key)
                stale = pool is None or _is_stale(pool)
            if stale:
                try:
                    videos = _fetch(cat, source)
                    with _lock:
                        _pools[pool_key] = {
                            "version": _POOL_VERSION, "fetched_at": time.time(), "videos": videos
                        }
                except Exception as exc:
                    logger.warning(
                        "Pool refresh failed for '%s' source='%s': %s", cat["id"], source, exc
                    )
    with _lock:
        if _pools:
            _save_to_disk()


def _published_ts(value: str) -> float:
    if not value:
        return 0.0
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def _engagement(v: dict) -> float:
    return (v.get("likes", 0) + v.get("comments", 0)) / max(v.get("views", 0), 1)


def _velocity(v: dict) -> float:
    ts = _published_ts(v.get("published_at", ""))
    if not ts:
        return -1.0  # видео без даты — в конец
    days = max((time.time() - ts) / 86400, 1.0)
    return v.get("views", 0) / days


_SORT_KEYS = {
    "date": lambda v: _published_ts(v.get("published_at", "")),
    "views": lambda v: v.get("views", 0),
    "comments": lambda v: v.get("comments", 0),
    "engagement": _engagement,
    "velocity": _velocity,
}

VALID_SORTS = {"random", *_SORT_KEYS}


def _passes_filters(v: dict, f: dict) -> bool:
    views = v.get("views", 0)
    duration = v.get("duration", 0)
    subs = v.get("channel_subscribers", 0)

    if f.get("period_days") is not None:
        ts = _published_ts(v.get("published_at", ""))
        if not ts or ts < time.time() - f["period_days"] * 86400:
            return False
    if f.get("views_min") is not None and views < f["views_min"]:
        return False
    if f.get("views_max") is not None and views > f["views_max"]:
        return False
    if f.get("comments_min") is not None and v.get("comments", 0) < f["comments_min"]:
        return False
    if f.get("engagement_min") is not None and _engagement(v) < f["engagement_min"]:
        return False
    if f.get("duration_min") is not None and duration < f["duration_min"]:
        return False
    if f.get("duration_max") is not None and duration > f["duration_max"]:
        return False
    if f.get("exclude_shorts") and duration < 60:
        return False
    if f.get("subscribers_min") is not None and subs < f["subscribers_min"]:
        return False
    if f.get("subscribers_max") is not None and subs > f["subscribers_max"]:
        return False
    if f.get("channel_age_max_days") is not None:
        ts = _published_ts(v.get("channel_published_at", ""))
        if not ts or ts < time.time() - f["channel_age_max_days"] * 86400:
            return False
    if f.get("viral_ratio_min") is not None:
        if subs <= 0 or views / subs < f["viral_ratio_min"]:
            return False
    return True


def _apply_filters(videos: list[dict], filters: dict | None) -> list[dict]:
    if not filters:
        return videos
    return [v for v in videos if _passes_filters(v, filters)]


def sample(
    category_ids: list[str],
    categories_map: dict,
    limit: int = 40,
    source: str = "youtube",
    filters: dict | None = None,
    sort: str = "random",
) -> list[dict]:
    """Return up to `limit` videos interleaved across requested categories for given source."""
    buckets: list[list[dict]] = []
    for cid in category_ids:
        cat = categories_map.get(cid)
        if cat is None:
            continue
        videos = _apply_filters(get_pool(cat, source), filters)
        if not videos:
            continue
        shuffled = list(videos)
        random.shuffle(shuffled)
        bucket = []
        for v in shuffled:
            v2 = dict(v)
            v2["category_id"] = cid
            v2["category_label"] = cat["label"]
            bucket.append(v2)
        buckets.append(bucket)

    if not buckets:
        return []

    sort_key = _SORT_KEYS.get(sort)
    if sort_key is not None:
        merged: list[dict] = []
        merged_seen: set[str] = set()
        for bucket in buckets:
            for video in bucket:
                vid_id = video.get("video_id", "")
                if vid_id and vid_id in merged_seen:
                    continue
                if vid_id:
                    merged_seen.add(vid_id)
                merged.append(video)
        merged.sort(key=sort_key, reverse=True)
        return merged[:limit]

    # Round-robin interleave
    result: list[dict] = []
    seen: set[str] = set()
    indices = [0] * len(buckets)

    while len(result) < limit:
        added_any = False
        for i, bucket in enumerate(buckets):
            if len(result) >= limit:
                break
            while indices[i] < len(bucket):
                video = bucket[indices[i]]
                indices[i] += 1
                vid_id = video.get("video_id", "")
                if vid_id and vid_id in seen:
                    continue
                if vid_id:
                    seen.add(vid_id)
                result.append(video)
                added_any = True
                break
        if not added_any:
            break

    return result
