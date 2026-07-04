"""Video pool per category — pre-fetched, persisted, TTL-refreshed.

Each pool holds ~40 videos fetched via YouTube search using the category's
curated queries. Pools are stored in data/pools.json so restarts don't burn
API quota. TTL is 24 hours; a background refresher calls refresh_stale()
periodically.
"""

import json
import logging
import random
import threading
import time
from pathlib import Path

from backend.services import youtube

logger = logging.getLogger(__name__)

_POOLS_FILE = Path("data/pools.json")
_TTL = 86400  # 24 h
_MAX_PER_QUERY = 10

# {category_id: {"fetched_at": float, "videos": [...]}}
_pools: dict[str, dict] = {}
_lock = threading.Lock()


def load_from_disk() -> None:
    if not _POOLS_FILE.exists():
        return
    try:
        data = json.loads(_POOLS_FILE.read_text(encoding="utf-8"))
        with _lock:
            _pools.update(data)
        logger.info("Loaded pools for %d categories from disk", len(data))
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
    return time.time() - pool.get("fetched_at", 0) > _TTL


def _fetch(category_id: str, queries: list[str]) -> list[dict]:
    logger.info("Fetching pool for category '%s'", category_id)
    videos = youtube.search_videos(queries, max_per_query=_MAX_PER_QUERY)
    logger.info("Fetched %d videos for '%s'", len(videos), category_id)
    return videos


def get_pool(category_id: str, queries: list[str]) -> list[dict]:
    """Return pool for category, fetching synchronously if missing or stale."""
    with _lock:
        pool = _pools.get(category_id)
        if pool and not _is_stale(pool):
            return pool["videos"]

    videos = _fetch(category_id, queries)
    with _lock:
        _pools[category_id] = {"fetched_at": time.time(), "videos": videos}
        _save_to_disk()
    return videos


def refresh_stale(categories: list[dict]) -> None:
    """Refresh all stale pools. Intended for background calls."""
    for cat in categories:
        category_id = cat["id"]
        with _lock:
            pool = _pools.get(category_id)
            stale = pool is None or _is_stale(pool)
        if stale:
            try:
                videos = _fetch(category_id, cat["queries"])
                with _lock:
                    _pools[category_id] = {"fetched_at": time.time(), "videos": videos}
            except Exception as exc:
                logger.warning("Pool refresh failed for '%s': %s", category_id, exc)
    with _lock:
        if _pools:
            _save_to_disk()


def sample(category_ids: list[str], categories_map: dict, limit: int = 40) -> list[dict]:
    """Return up to `limit` videos interleaved across requested categories.

    Uses round-robin over per-category shuffled slices so every category
    is represented even if limit < total pool size.
    """
    # Build per-category pools (lazy-fetch if needed)
    buckets: list[list[dict]] = []
    for cid in category_ids:
        cat = categories_map.get(cid)
        if cat is None:
            continue
        videos = get_pool(cid, cat["queries"])
        if not videos:
            continue
        shuffled = list(videos)
        random.shuffle(shuffled)
        # Tag each video with its category
        for v in shuffled:
            v = dict(v)
            v["category_id"] = cid
            v["category_label"] = cat["label"]
        bucket = []
        for v in shuffled:
            v2 = dict(v)
            v2["category_id"] = cid
            v2["category_label"] = cat["label"]
            bucket.append(v2)
        buckets.append(bucket)

    if not buckets:
        return []

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
