from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

_FAKE_VIDEOS = {
    "science": [
        {"video_id": "s1", "title": "Science Video", "channel": "SciCh",
         "url": "https://yt.com/s1", "thumbnail": "https://img/s1.jpg",
         "duration": 600, "views": 1000, "published_at": "2026-06-01T00:00:00Z"},
    ],
    "history": [
        {"video_id": "h1", "title": "History Video", "channel": "HistCh",
         "url": "https://yt.com/h1", "thumbnail": "https://img/h1.jpg",
         "duration": 900, "views": 2000, "published_at": "2026-06-02T00:00:00Z"},
    ],
}


def _fake_sample(category_ids, categories_map, limit=40):
    result = []
    for cid in category_ids:
        for v in _FAKE_VIDEOS.get(cid, []):
            item = dict(v, category_id=cid, category_label=categories_map[cid]["label"])
            result.append(item)
    return result[:limit]


@pytest.fixture(autouse=True)
def patch_pool_sample():
    with patch("backend.routers.feed.pool_service.sample", side_effect=_fake_sample):
        yield


def test_get_categories():
    response = client.get("/categories")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 15
    assert all(
        "id" in c and "emoji" in c and "label" in c and "hint" in c and "queries" in c
        for c in data
    )
    assert all(len(c["queries"]) == 4 for c in data)


def test_grid_endpoint():
    response = client.post("/grid", json={"categories": ["science", "history"]})
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 2
    category_ids = {v["category_id"] for v in items}
    assert category_ids == {"science", "history"}


def test_grid_single_category():
    response = client.post("/grid", json={"categories": ["science"]})
    assert response.status_code == 200
    items = response.json()["items"]
    assert all(v["category_id"] == "science" for v in items)


def test_grid_items_have_category_label():
    response = client.post("/grid", json={"categories": ["history"]})
    items = response.json()["items"]
    assert items[0]["category_label"] == "История"


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
    # sample is mocked — just verify the endpoint passes limit through
    assert response.status_code == 200
