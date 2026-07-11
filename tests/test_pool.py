import json
import time
from unittest.mock import patch

import pytest

from backend.services import pool as pool_service

_CATEGORIES_MAP = {
    "science": {
        "id": "science", "label": "Наука",
        "queries": ["science q1", "q2", "q3", "q4"],
        "queries_ru": ["наука q1", "q2", "q3"],
    },
    "history": {
        "id": "history", "label": "История",
        "queries": ["history q1", "q2", "q3", "q4"],
        "queries_ru": ["история q1", "q2", "q3"],
    },
    "art": {
        "id": "art", "label": "Искусство",
        "queries": ["art q1", "q2", "q3", "q4"],
        "queries_ru": ["искусство q1", "q2", "q3"],
    },
}


def _make_videos(prefix: str, count: int, source: str = "youtube") -> list[dict]:
    return [
        {"video_id": f"{prefix}{i}", "title": f"{prefix} video {i}", "channel": "Ch",
         "url": f"https://yt.com/{prefix}{i}", "thumbnail": "", "duration": 60,
         "views": i * 100, "published_at": "2026-06-01T00:00:00Z",
         "source": source, "embed_url": ""}
        for i in range(count)
    ]


@pytest.fixture(autouse=True)
def reset_pools(tmp_path):
    pool_service._pools.clear()
    orig_file = pool_service._POOLS_FILE
    pool_service._POOLS_FILE = tmp_path / "pools.json"
    yield
    pool_service._POOLS_FILE = orig_file
    pool_service._pools.clear()


# ---------- sample() ----------

def test_sample_interleave():
    pool_service._pools["science:youtube"] = {"version": pool_service._POOL_VERSION, "fetched_at": time.time(), "videos": _make_videos("s", 5)}
    pool_service._pools["history:youtube"] = {"version": pool_service._POOL_VERSION, "fetched_at": time.time(), "videos": _make_videos("h", 5)}

    result = pool_service.sample(["science", "history"], _CATEGORIES_MAP, limit=6, source="youtube")
    cat_ids = [v["category_id"] for v in result]
    assert "science" in cat_ids
    assert "history" in cat_ids


def test_sample_respects_limit():
    pool_service._pools["science:youtube"] = {"version": pool_service._POOL_VERSION, "fetched_at": time.time(), "videos": _make_videos("s", 20)}
    pool_service._pools["history:youtube"] = {"version": pool_service._POOL_VERSION, "fetched_at": time.time(), "videos": _make_videos("h", 20)}

    result = pool_service.sample(["science", "history"], _CATEGORIES_MAP, limit=10, source="youtube")
    assert len(result) <= 10


def test_sample_no_duplicates():
    pool_service._pools["science:youtube"] = {"version": pool_service._POOL_VERSION, "fetched_at": time.time(), "videos": _make_videos("s", 10)}
    pool_service._pools["history:youtube"] = {"version": pool_service._POOL_VERSION, "fetched_at": time.time(), "videos": _make_videos("h", 10)}

    result = pool_service.sample(["science", "history"], _CATEGORIES_MAP, limit=40, source="youtube")
    ids = [v["video_id"] for v in result]
    assert len(ids) == len(set(ids))


def test_sample_tags_category():
    pool_service._pools["science:youtube"] = {"version": pool_service._POOL_VERSION, "fetched_at": time.time(), "videos": _make_videos("s", 3)}

    result = pool_service.sample(["science"], _CATEGORIES_MAP, limit=10, source="youtube")
    assert all(v["category_id"] == "science" for v in result)
    assert all(v["category_label"] == "Наука" for v in result)


def test_sample_skips_unknown_category():
    pool_service._pools["science:youtube"] = {"version": pool_service._POOL_VERSION, "fetched_at": time.time(), "videos": _make_videos("s", 3)}

    result = pool_service.sample(["science", "nonexistent"], _CATEGORIES_MAP, limit=10, source="youtube")
    assert all(v["category_id"] == "science" for v in result)


def test_sample_sources_are_separate():
    pool_service._pools["science:youtube"] = {"version": pool_service._POOL_VERSION, "fetched_at": time.time(), "videos": _make_videos("yt", 5, "youtube")}
    pool_service._pools["science:ru"] = {"version": pool_service._POOL_VERSION, "fetched_at": time.time(), "videos": _make_videos("ru", 5, "rutube")}

    yt_result = pool_service.sample(["science"], _CATEGORIES_MAP, limit=10, source="youtube")
    ru_result = pool_service.sample(["science"], _CATEGORIES_MAP, limit=10, source="ru")

    assert all(v["source"] == "youtube" for v in yt_result)
    assert all(v["source"] == "rutube" for v in ru_result)


# ---------- get_pool() / TTL ----------

def test_pool_fresh_no_fetch():
    pool_service._pools["science:youtube"] = {"version": pool_service._POOL_VERSION, "fetched_at": time.time(), "videos": _make_videos("s", 5)}

    with patch("backend.services.pool.youtube.search_videos") as mock_yt:
        result = pool_service.get_pool(_CATEGORIES_MAP["science"], "youtube")

    mock_yt.assert_not_called()
    assert len(result) == 5


def test_pool_expired_refetch():
    pool_service._pools["science:youtube"] = {
        "version": pool_service._POOL_VERSION,
        "fetched_at": time.time() - pool_service._TTL - 1,
        "videos": _make_videos("s", 3),
    }
    fresh = _make_videos("s_new", 7)

    with patch("backend.services.pool.youtube.search_videos", return_value=fresh) as mock_yt:
        result = pool_service.get_pool(_CATEGORIES_MAP["science"], "youtube")

    mock_yt.assert_called_once()
    assert len(result) == 7


def test_pool_old_version_is_stale():
    # запись без поля version (старый формат кеша) перезапрашивается
    pool_service._pools["science:youtube"] = {"fetched_at": time.time(), "videos": _make_videos("s", 3)}
    fresh = _make_videos("s_new", 6)

    with patch("backend.services.pool.youtube.search_videos", return_value=fresh) as mock_yt:
        result = pool_service.get_pool(_CATEGORIES_MAP["science"], "youtube")

    mock_yt.assert_called_once()
    assert len(result) == 6


def test_pool_missing_fetches():
    fresh = _make_videos("s", 4)
    with patch("backend.services.pool.youtube.search_videos", return_value=fresh) as mock_yt:
        result = pool_service.get_pool(_CATEGORIES_MAP["science"], "youtube")

    mock_yt.assert_called_once()
    assert len(result) == 4


def test_pool_ru_without_token():
    fresh_ru = _make_videos("ru", 5, "rutube")
    with patch("backend.services.pool.settings") as mock_settings, \
         patch("backend.services.rutube.search_videos", return_value=fresh_ru) as mock_rt, \
         patch("backend.services.vkvideo.search_videos") as mock_vk:
        mock_settings.vk_access_token = ""
        result = pool_service.get_pool(_CATEGORIES_MAP["science"], "ru")

    mock_rt.assert_called_once()
    mock_vk.assert_not_called()
    assert len(result) == 5


def test_pool_ru_with_token_calls_both():
    fresh_ru = _make_videos("ru", 3, "rutube")
    fresh_vk = _make_videos("vk", 3, "vk")
    with patch("backend.services.pool.settings") as mock_settings, \
         patch("backend.services.rutube.search_videos", return_value=fresh_ru), \
         patch("backend.services.vkvideo.search_videos", return_value=fresh_vk):
        mock_settings.vk_access_token = "token123"
        result = pool_service.get_pool(_CATEGORIES_MAP["science"], "ru")

    assert len(result) == 6


def test_pool_ru_vk_failure_isolated():
    fresh_ru = _make_videos("ru", 5, "rutube")
    with patch("backend.services.pool.settings") as mock_settings, \
         patch("backend.services.rutube.search_videos", return_value=fresh_ru), \
         patch("backend.services.vkvideo.search_videos", side_effect=RuntimeError("VK error")):
        mock_settings.vk_access_token = "token123"
        result = pool_service.get_pool(_CATEGORIES_MAP["science"], "ru")

    assert len(result) == 5
    assert all(v["source"] == "rutube" for v in result)


# ---------- persistence ----------

def test_pool_persistence(tmp_path, monkeypatch):
    monkeypatch.setattr(pool_service, "_POOLS_FILE", tmp_path / "pools.json")

    videos = _make_videos("p", 5)
    pool_service._pools["science:youtube"] = {"version": pool_service._POOL_VERSION, "fetched_at": time.time(), "videos": videos}
    pool_service._save_to_disk()

    pool_service._pools.clear()
    pool_service.load_from_disk()

    assert "science:youtube" in pool_service._pools
    assert len(pool_service._pools["science:youtube"]["videos"]) == 5


# ---------- refresh_stale() ----------

def test_refresh_stale_skips_fresh():
    pool_service._pools["science:youtube"] = {"version": pool_service._POOL_VERSION, "fetched_at": time.time(), "videos": _make_videos("s", 3)}
    pool_service._pools["science:ru"] = {"version": pool_service._POOL_VERSION, "fetched_at": time.time(), "videos": _make_videos("r", 3, "rutube")}

    with patch("backend.services.pool.youtube.search_videos") as mock_yt, \
         patch("backend.services.rutube.search_videos") as mock_rt:
        pool_service.refresh_stale([_CATEGORIES_MAP["science"]])

    mock_yt.assert_not_called()
    mock_rt.assert_not_called()


def test_refresh_stale_refetches_expired():
    pool_service._pools["science:youtube"] = {
        "version": pool_service._POOL_VERSION,
        "fetched_at": time.time() - pool_service._TTL - 1,
        "videos": _make_videos("s", 2),
    }
    pool_service._pools["science:ru"] = {"version": pool_service._POOL_VERSION, "fetched_at": time.time(), "videos": _make_videos("r", 3, "rutube")}
    fresh = _make_videos("s_new", 8)

    with patch("backend.services.pool.youtube.search_videos", return_value=fresh) as mock_yt, \
         patch("backend.services.rutube.search_videos", return_value=[]) as mock_rt:
        pool_service.refresh_stale([_CATEGORIES_MAP["science"]])

    mock_yt.assert_called_once()
    mock_rt.assert_not_called()  # ru pool is fresh
    assert pool_service._pools["science:youtube"]["videos"] == fresh
