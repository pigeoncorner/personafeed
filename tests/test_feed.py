from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

_FAKE_VIDEOS = {
    "science": [
        {"video_id": "s1", "title": "Science Video", "channel": "SciCh",
         "url": "https://yt.com/s1", "thumbnail": "https://img/s1.jpg",
         "duration": 600, "views": 1000, "published_at": "2026-06-01T00:00:00Z",
         "source": "youtube", "embed_url": ""},
    ],
    "history": [
        {"video_id": "h1", "title": "History Video", "channel": "HistCh",
         "url": "https://yt.com/h1", "thumbnail": "https://img/h1.jpg",
         "duration": 900, "views": 2000, "published_at": "2026-06-02T00:00:00Z",
         "source": "youtube", "embed_url": ""},
    ],
    "science_ru": [
        {"video_id": "rt1", "title": "RuTube Video", "channel": "RTCh",
         "url": "https://rutube.ru/video/rt1/", "thumbnail": "https://img/rt1.jpg",
         "duration": 500, "views": 500, "published_at": "2026-06-03T00:00:00Z",
         "source": "rutube", "embed_url": "https://rutube.ru/play/embed/rt1"},
    ],
}


def _fake_sample_youtube(category_ids, categories_map, limit=40, source="youtube"):
    if source != "youtube":
        return []
    result = []
    for cid in category_ids:
        for v in _FAKE_VIDEOS.get(cid, []):
            result.append(dict(v, category_id=cid, category_label=categories_map[cid]["label"]))
    return result[:limit]


def _fake_sample_ru(category_ids, categories_map, limit=40, source="youtube"):
    if source != "ru":
        return []
    result = []
    for cid in category_ids:
        for v in _FAKE_VIDEOS.get(f"{cid}_ru", []):
            result.append(dict(v, category_id=cid, category_label=categories_map[cid]["label"]))
    return result[:limit]


@pytest.fixture(autouse=True)
def patch_pool_sample():
    with patch("backend.routers.feed.pool_service.sample", side_effect=_fake_sample_youtube):
        yield


def test_get_categories():
    response = client.get("/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 15
    assert all(
        "id" in c and "emoji" in c and "label" in c and "hint" in c
        and "queries" in c and "queries_ru" in c
        for c in data
    )
    assert all(len(c["queries_ru"]) == 3 for c in data)


def test_grid_endpoint():
    response = client.post("/grid", json={"categories": ["science", "history"]})
    assert response.status_code == 200
    items = response.json()["items"]
    category_ids = {v["category_id"] for v in items}
    assert "science" in category_ids
    assert "history" in category_ids


def test_grid_single_category():
    response = client.post("/grid", json={"categories": ["science"]})
    assert response.status_code == 200
    items = response.json()["items"]
    assert all(v["category_id"] == "science" for v in items)


def test_grid_items_have_category_label():
    response = client.post("/grid", json={"categories": ["history"]})
    items = response.json()["items"]
    assert items[0]["category_label"] == "История"


def test_grid_items_have_source_and_embed():
    response = client.post("/grid", json={"categories": ["science"]})
    item = response.json()["items"][0]
    assert "source" in item
    assert "embed_url" in item


def test_grid_default_source_is_youtube():
    response = client.post("/grid", json={"categories": ["science"]})
    assert response.status_code == 200
    items = response.json()["items"]
    assert all(v["source"] == "youtube" for v in items)


def test_grid_ru_source():
    with patch("backend.routers.feed.pool_service.sample", side_effect=_fake_sample_ru):
        response = client.post("/grid", json={"categories": ["science"], "source": "ru"})
    assert response.status_code == 200
    items = response.json()["items"]
    assert all(v["source"] == "rutube" for v in items)


def test_grid_invalid_source():
    response = client.post("/grid", json={"categories": ["science"], "source": "invalid"})
    assert response.status_code == 422


def test_grid_empty_categories():
    response = client.post("/grid", json={"categories": []})
    assert response.status_code == 422


def test_grid_unknown_category_ignored():
    response = client.post("/grid", json={"categories": ["science", "nonexistent"]})
    assert response.status_code == 200
    items = response.json()["items"]
    assert all(v["category_id"] == "science" for v in items)


def test_grid_all_unknown():
    response = client.post("/grid", json={"categories": ["nonexistent"]})
    assert response.status_code == 422


def test_grid_respects_limit():
    response = client.post("/grid", json={"categories": ["science", "history"], "limit": 1})
    assert response.status_code == 200
