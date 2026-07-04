import json
import time
from unittest.mock import patch

import pytest

from backend.services import pool as pool_service

_CATEGORIES_MAP = {
    "science": {"id": "science", "label": "Наука", "queries": ["science q1", "q2", "q3", "q4"]},
    "history": {"id": "history", "label": "История", "queries": ["history q1", "q2", "q3", "q4"]},
    "art": {"id": "art", "label": "Искусство", "queries": ["art q1", "q2", "q3", "q4"]},
}


def _make_videos(prefix: str, count: int) -> list[dict]:
    return [
        {"video_id": f"{prefix}{i}", "title": f"{prefix} video {i}", "channel": "Ch",
         "url": f"https://yt.com/{prefix}{i}", "thumbnail": "", "duration": 60,
         "views": i * 100, "published_at": "2026-06-01T00:00:00Z"}
        for i in range(count)
    ]


@pytest.fixture(autouse=True)
def reset_pools():
    """Clear in-memory pools before each test."""
    pool_service._pools.clear()
    yield
    pool_service._pools.clear()


# ---------- sample() ----------

def test_sample_interleave():
    pool_service._pools["science"] = {"fetched_at": time.time(), "videos": _make_videos("s", 5)}
    pool_service._pools["history"] = {"fetched_at": time.time(), "videos": _make_videos("h", 5)}

    result = pool_service.sample(["science", "history"], _CATEGORIES_MAP, limit=6)

    cat_ids = [v["category_id"] for v in result]
    # both categories must be present
    assert "science" in cat_ids
    assert "history" in cat_ids


def test_sample_respects_limit():
    pool_service._pools["science"] = {"fetched_at": time.time(), "videos": _make_videos("s", 20)}
    pool_service._pools["history"] = {"fetched_at": time.time(), "videos": _make_videos("h", 20)}

    result = pool_service.sample(["science", "history"], _CATEGORIES_MAP, limit=10)
    assert len(result) <= 10


def test_sample_no_duplicates():
    pool_service._pools["science"] = {"fetched_at": time.time(), "videos": _make_videos("s", 10)}
    pool_service._pools["history"] = {"fetched_at": time.time(), "videos": _make_videos("h", 10)}

    result = pool_service.sample(["science", "history"], _CATEGORIES_MAP, limit=40)
    ids = [v["video_id"] for v in result]
    assert len(ids) == len(set(ids))


def test_sample_tags_category():
    pool_service._pools["science"] = {"fetched_at": time.time(), "videos": _make_videos("s", 3)}

    result = pool_service.sample(["science"], _CATEGORIES_MAP, limit=10)
    assert all(v["category_id"] == "science" for v in result)
    assert all(v["category_label"] == "Наука" for v in result)


def test_sample_skips_unknown_category():
    pool_service._pools["science"] = {"fetched_at": time.time(), "videos": _make_videos("s", 3)}

    result = pool_service.sample(["science", "nonexistent"], _CATEGORIES_MAP, limit=10)
    assert all(v["category_id"] == "science" for v in result)


# ---------- get_pool() / TTL ----------

def test_pool_fresh_no_fetch():
    pool_service._pools["science"] = {"fetched_at": time.time(), "videos": _make_videos("s", 5)}

    with patch("backend.services.pool.youtube.search_videos") as mock_yt:
        result = pool_service.get_pool("science", _CATEGORIES_MAP["science"]["queries"])

    mock_yt.assert_not_called()
    assert len(result) == 5


def test_pool_expired_refetch():
    pool_service._pools["science"] = {
        "fetched_at": time.time() - pool_service._TTL - 1,
        "videos": _make_videos("s", 3),
    }
    fresh = _make_videos("s_new", 7)

    with patch("backend.services.pool.youtube.search_videos", return_value=fresh) as mock_yt:
        result = pool_service.get_pool("science", _CATEGORIES_MAP["science"]["queries"])

    mock_yt.assert_called_once()
    assert result == fresh


def test_pool_missing_fetches():
    fresh = _make_videos("s", 4)
    with patch("backend.services.pool.youtube.search_videos", return_value=fresh) as mock_yt:
        result = pool_service.get_pool("science", _CATEGORIES_MAP["science"]["queries"])

    mock_yt.assert_called_once()
    assert result == fresh


# ---------- persistence ----------

def test_pool_persistence(tmp_path, monkeypatch):
    monkeypatch.setattr(pool_service, "_POOLS_FILE", tmp_path / "pools.json")

    videos = _make_videos("p", 5)
    pool_service._pools["science"] = {"fetched_at": time.time(), "videos": videos}
    pool_service._save_to_disk()

    pool_service._pools.clear()
    pool_service.load_from_disk()

    assert "science" in pool_service._pools
    assert len(pool_service._pools["science"]["videos"]) == 5


# ---------- refresh_stale() ----------

def test_refresh_stale_skips_fresh():
    pool_service._pools["science"] = {"fetched_at": time.time(), "videos": _make_videos("s", 3)}

    with patch("backend.services.pool.youtube.search_videos") as mock_yt:
        pool_service.refresh_stale([_CATEGORIES_MAP["science"]])

    mock_yt.assert_not_called()


def test_refresh_stale_refetches_expired():
    pool_service._pools["science"] = {
        "fetched_at": time.time() - pool_service._TTL - 1,
        "videos": _make_videos("s", 2),
    }
    fresh = _make_videos("s_new", 8)

    with patch("backend.services.pool.youtube.search_videos", return_value=fresh) as mock_yt:
        pool_service.refresh_stale([_CATEGORIES_MAP["science"]])

    mock_yt.assert_called_once()
    assert pool_service._pools["science"]["videos"] == fresh
