import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _fake_curate_response():
    return json.dumps({
        "youtube": [
            {"video_id": "v1", "title": "Physics Lecture", "channel": "MIT OCW", "why_relevant": "Ключевая лекция"}
        ],
        "news": [
            {"url": "https://nature.com/1", "title": "New Study", "source": "Nature", "why_relevant": "Важно"}
        ],
        "top_searches": ["arxiv preprints 2024"],
    })


def _fake_youtube_raw():
    return [{"video_id": "v1", "title": "Physics Lecture", "channel": "MIT OCW",
             "url": "https://www.youtube.com/watch?v=v1", "thumbnail": "https://img/v1.jpg"}]


def _fake_news_raw():
    return [{"url": "https://nature.com/1", "title": "New Study",
             "source": "Nature", "published_at": "2024-01-01T00:00:00Z"}]


@pytest.fixture(autouse=True)
def clear_cache():
    from backend.routers.feed import _cache
    _cache._store.clear()
    yield
    _cache._store.clear()


def test_feed_scientist_returns_valid_response():
    curated = json.loads(_fake_curate_response())
    with (
        patch("backend.services.youtube.search_videos", return_value=_fake_youtube_raw()),
        patch("backend.services.news.search_news", new=AsyncMock(return_value=_fake_news_raw())),
        patch("backend.services.ai.curate_feed", new=AsyncMock(return_value=curated)),
    ):
        response = client.post("/feed", json={"persona": "scientist", "language": "ru"})

    assert response.status_code == 200
    data = response.json()
    assert data["persona_id"] == "scientist"
    assert len(data["youtube"]) == 1
    assert data["youtube"][0]["why_relevant"] == "Ключевая лекция"
    assert data["cached"] is False


def test_feed_cached_on_second_request():
    curated = json.loads(_fake_curate_response())
    with (
        patch("backend.services.youtube.search_videos", return_value=_fake_youtube_raw()),
        patch("backend.services.news.search_news", new=AsyncMock(return_value=_fake_news_raw())),
        patch("backend.services.ai.curate_feed", new=AsyncMock(return_value=curated)),
    ):
        client.post("/feed", json={"persona": "scientist", "language": "ru"})
        response = client.post("/feed", json={"persona": "scientist", "language": "ru"})

    assert response.json()["cached"] is True


def test_feed_degradation_curate_fails():
    with (
        patch("backend.services.youtube.search_videos", return_value=_fake_youtube_raw()),
        patch("backend.services.news.search_news", new=AsyncMock(return_value=_fake_news_raw())),
        patch("backend.services.ai.curate_feed", new=AsyncMock(side_effect=RuntimeError("Claude down"))),
    ):
        response = client.post("/feed", json={"persona": "scientist", "language": "ru"})

    assert response.status_code == 200
    data = response.json()
    assert len(data["youtube"]) == 1
    assert data["youtube"][0]["why_relevant"] == ""  # сырые результаты без аннотаций
