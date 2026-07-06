from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from backend.services import rutube


def _make_api_response(items: list[dict]) -> dict:
    return {"count": len(items), "results": items}


def _make_item(i: int, days_ago: int = 5) -> dict:
    from datetime import timedelta
    pub = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
    return {
        "id": f"id{i}",
        "title": f"Video {i}",
        "duration": 120 + i * 10,
        "hits": 1000 * i,
        "publication_ts": pub,
        "thumbnail_url": f"https://img.rutube.ru/{i}.jpg",
        "video_url": f"https://rutube.ru/video/id{i}/",
        "author": {"name": f"Channel {i}"},
    }


def _mock_fetch(items):
    def inner(query, count):
        return items
    return inner


def test_rutube_maps_fields():
    items = [_make_item(1)]
    with patch.object(rutube, "_fetch_query", side_effect=_mock_fetch(items)):
        results = rutube.search_videos(["тест"])

    assert len(results) == 1
    v = results[0]
    assert v["video_id"] == "id1"
    assert v["title"] == "Video 1"
    assert v["channel"] == "Channel 1"
    assert v["url"] == "https://rutube.ru/video/id1/"
    assert v["thumbnail"] == "https://img.rutube.ru/1.jpg"
    assert v["duration"] == 130
    assert v["views"] == 1000
    assert v["embed_url"] == "https://rutube.ru/play/embed/id1"
    assert v["source"] == "rutube"
    assert v["published_at"]


def test_rutube_deduplication():
    items = [_make_item(1), _make_item(1)]  # same id
    with patch.object(rutube, "_fetch_query", side_effect=_mock_fetch(items)):
        results = rutube.search_videos(["тест"])

    ids = [v["video_id"] for v in results]
    assert len(ids) == len(set(ids))


def test_rutube_filters_old_videos():
    fresh = _make_item(1, days_ago=5)
    old = _make_item(2, days_ago=60)
    with patch.object(rutube, "_fetch_query", side_effect=_mock_fetch([fresh, old])):
        results = rutube.search_videos(["тест"], freshness_days=30)

    assert len(results) == 1
    assert results[0]["video_id"] == "id1"


def test_rutube_fallback_when_all_old():
    old_items = [_make_item(i, days_ago=60) for i in range(3)]
    call_count = [0]

    def mock_fetch(query, count):
        call_count[0] += 1
        return old_items

    with patch.object(rutube, "_fetch_query", side_effect=mock_fetch):
        # First call with 30 days returns nothing → recursive retry with 10 years
        results = rutube.search_videos(["тест"], freshness_days=30)

    # Got results on retry (no date cutoff on 10-year window)
    assert len(results) > 0


def test_rutube_query_failure_continues():
    def mock_fetch(query, count):
        raise ConnectionError("Network error")

    with patch.object(rutube, "_fetch_query", side_effect=mock_fetch):
        results = rutube.search_videos(["q1", "q2"])

    assert results == []


def test_rutube_multiple_queries_dedup():
    item = _make_item(1)
    with patch.object(rutube, "_fetch_query", side_effect=_mock_fetch([item])):
        results = rutube.search_videos(["q1", "q2"])

    ids = [v["video_id"] for v in results]
    assert ids.count("id1") == 1
