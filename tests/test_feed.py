import json
from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _fake_topic():
    return {
        "topic": "Археология звука",
        "intro": "Учёные реконструируют голоса прошлого.",
        "queries": ["acoustic archaeology", "ancient sound reconstruction", "archaeoacoustics"],
        "news_topics": ["archaeoacoustics research"],
    }


def _fake_curate_response():
    return {
        "youtube": [
            {"video_id": "v1", "title": "Sound of the Past", "channel": "SciShow", "why_relevant": "Ключевое видео"}
        ],
        "news": [
            {"url": "https://nature.com/1", "title": "New Study", "source": "Nature", "why_relevant": "Важно"}
        ],
        "top_searches": ["archaeoacoustics 2026"],
    }


def _fake_youtube_raw():
    return [{"video_id": "v1", "title": "Sound of the Past", "channel": "SciShow",
             "url": "https://www.youtube.com/watch?v=v1", "thumbnail": "https://img/v1.jpg",
             "duration": 3723, "views": 123456, "published_at": "2026-06-01T00:00:00Z"}]


def _fake_news_raw():
    return [{"url": "https://nature.com/1", "title": "New Study",
             "source": "Nature", "published_at": "2026-06-15T00:00:00Z"}]


def _patches(topic_mock=None):
    return (
        patch("backend.routers.feed.ai.generate_topic",
              new=topic_mock or AsyncMock(return_value=_fake_topic())),
        patch("backend.services.youtube.search_videos", return_value=_fake_youtube_raw()),
        patch("backend.services.news.search_news", new=AsyncMock(return_value=_fake_news_raw())),
        patch("backend.routers.feed.ai.curate_feed",
              new=AsyncMock(return_value=_fake_curate_response())),
    )


@pytest.fixture(autouse=True)
def clear_cache():
    from backend.routers.feed import _cache
    _cache._store.clear()
    yield
    _cache._store.clear()


def test_get_categories():
    response = client.get("/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 15
    assert all("id" in c and "emoji" in c and "label" in c and "hint" in c for c in data)


def test_feed_returns_valid_response():
    p1, p2, p3, p4 = _patches()
    with p1, p2, p3, p4:
        response = client.post("/feed", json={"category": "history", "language": "ru"})

    assert response.status_code == 200
    data = response.json()
    assert data["category_id"] == "history"
    assert data["category_label"] == "История"
    assert data["topic"] == "Археология звука"
    assert data["intro"]
    assert len(data["youtube"]) == 1
    assert data["youtube"][0]["why_relevant"] == "Ключевое видео"
    assert data["cached"] is False


def test_feed_response_fields():
    p1, p2, p3, p4 = _patches()
    with p1, p2, p3, p4:
        response = client.post("/feed", json={"category": "history", "language": "ru"})

    video = response.json()["youtube"][0]
    assert video["video_id"] == "v1"
    assert video["duration"] == 3723
    assert video["views"] == 123456
    assert video["published_at"] == "2026-06-01T00:00:00Z"


def test_feed_cache_key_has_date():
    p1, p2, p3, p4 = _patches()
    with p1, p2, p3, p4:
        client.post("/feed", json={"category": "history", "language": "ru"})

    from backend.routers.feed import _cache
    keys = list(_cache._store.keys())
    assert len(keys) == 1
    assert date.today().isoformat() in keys[0]


def test_feed_cached_on_second_request():
    p1, p2, p3, p4 = _patches()
    with p1, p2, p3, p4:
        client.post("/feed", json={"category": "history", "language": "ru"})
        response = client.post("/feed", json={"category": "history", "language": "ru"})

    assert response.json()["cached"] is True


def test_feed_custom_topic():
    p1, p2, p3, p4 = _patches()
    with p1, p2, p3, p4:
        response = client.post("/feed", json={"category": "пчеловодство", "language": "ru"})

    assert response.status_code == 200
    assert response.json()["category_id"] == "пчеловодство"


def test_surprise_picks_from_list():
    p1, p2, p3, p4 = _patches()
    with p1, p2, p3, p4:
        response = client.post("/surprise", json={"categories": ["history"], "language": "ru"})

    assert response.status_code == 200
    data = response.json()
    assert data["category_id"] == "history"
    assert data["topic"] == "Археология звука"
    assert data["intro"]


def test_surprise_not_cached():
    topic_mock = AsyncMock(return_value=_fake_topic())
    p1, p2, p3, p4 = _patches(topic_mock)
    with p1, p2, p3, p4:
        client.post("/surprise", json={"categories": ["history"], "language": "ru"})
        client.post("/surprise", json={"categories": ["history"], "language": "ru"})

    assert topic_mock.call_count == 2  # каждый клик — новая генерация темы


def test_surprise_empty_categories():
    response = client.post("/surprise", json={"categories": [], "language": "ru"})
    assert response.status_code == 422


def test_surprise_unknown_category():
    response = client.post("/surprise", json={"categories": ["nonexistent"], "language": "ru"})
    assert response.status_code == 422


def test_feed_degradation_curate_fails():
    p1 = patch("backend.routers.feed.ai.generate_topic", new=AsyncMock(return_value=_fake_topic()))
    p2 = patch("backend.services.youtube.search_videos", return_value=_fake_youtube_raw())
    p3 = patch("backend.services.news.search_news", new=AsyncMock(return_value=_fake_news_raw()))
    p4 = patch("backend.routers.feed.ai.curate_feed", new=AsyncMock(side_effect=RuntimeError("Claude down")))
    with p1, p2, p3, p4:
        response = client.post("/feed", json={"category": "history", "language": "ru"})

    assert response.status_code == 200
    data = response.json()
    assert len(data["youtube"]) == 1
    assert data["youtube"][0]["why_relevant"] == ""  # сырые результаты без аннотаций
