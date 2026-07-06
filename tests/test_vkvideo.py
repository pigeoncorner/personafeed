from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from backend.services import vkvideo


def _unix(days_ago: int = 5) -> int:
    return int((datetime.now(timezone.utc) - timedelta(days=days_ago)).timestamp())


def _make_item(i: int, days_ago: int = 5) -> dict:
    return {
        "id": i,
        "owner_id": 100 + i,
        "title": f"VK Video {i}",
        "duration": 200 + i * 10,
        "views": 500 * i,
        "date": _unix(days_ago),
        "image": [
            {"url": f"https://img.vk.com/s{i}.jpg", "width": 160},
            {"url": f"https://img.vk.com/m{i}.jpg", "width": 320},
            {"url": f"https://img.vk.com/l{i}.jpg", "width": 640},
        ],
        "player": f"https://vk.com/video_ext.php?oid={100+i}&id={i}&hash=abc",
    }


def _make_api_response(items: list[dict], groups=None, profiles=None, error=None) -> dict:
    if error:
        return {"error": {"error_code": error[0], "error_msg": error[1]}}
    return {
        "response": {
            "count": len(items),
            "items": items,
            "groups": groups or [],
            "profiles": profiles or [],
        }
    }


def _mock_fetch(response):
    import json
    import io
    from unittest.mock import MagicMock

    def inner(query, count):
        import json
        data = json.dumps(response).encode()
        mock_resp = MagicMock()
        mock_resp.read.return_value = data
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return response["response"]["items"], \
               response["response"].get("groups", []), \
               response["response"].get("profiles", [])
    return inner


def _patch_fetch(items, groups=None, profiles=None):
    resp = _make_api_response(items, groups=groups, profiles=profiles)

    def inner(query, count):
        return (
            resp["response"]["items"],
            resp["response"].get("groups", []),
            resp["response"].get("profiles", []),
        )
    return inner


def test_vk_maps_fields():
    items = [_make_item(1)]
    with patch.object(vkvideo, "_fetch_query", side_effect=_patch_fetch(items)):
        results = vkvideo.search_videos(["тест"])

    assert len(results) == 1
    v = results[0]
    assert v["video_id"] == "101_1"
    assert v["title"] == "VK Video 1"
    assert v["url"] == "https://vk.com/video101_1"
    assert v["duration"] == 210
    assert v["views"] == 500
    assert v["embed_url"] == "https://vk.com/video_ext.php?oid=101&id=1&hash=abc"
    assert v["source"] == "vk"
    assert v["published_at"]


def test_vk_thumbnail_picks_closest_320():
    items = [_make_item(1)]
    with patch.object(vkvideo, "_fetch_query", side_effect=_patch_fetch(items)):
        results = vkvideo.search_videos(["тест"])

    # image with width=320 should be picked
    assert "m1.jpg" in results[0]["thumbnail"]


def test_vk_video_id_format():
    item = _make_item(5)
    item["owner_id"] = -200  # group (negative owner_id)
    with patch.object(vkvideo, "_fetch_query", side_effect=_patch_fetch([item])):
        results = vkvideo.search_videos(["тест"])

    assert results[0]["video_id"] == "-200_5"
    assert results[0]["url"] == "https://vk.com/video-200_5"


def test_vk_error_raises():
    def mock_fetch(query, count):
        raise RuntimeError("VK API error 5: User authorization failed")

    with patch.object(vkvideo, "_fetch_query", side_effect=mock_fetch):
        with pytest.raises(RuntimeError, match="VK API error"):
            vkvideo.search_videos(["тест"])


def test_vk_filters_old_30_days():
    fresh = _make_item(1, days_ago=10)
    old = _make_item(2, days_ago=60)
    with patch.object(vkvideo, "_fetch_query", side_effect=_patch_fetch([fresh, old])):
        results = vkvideo.search_videos(["тест"], freshness_days=30)

    assert len(results) == 1
    assert results[0]["video_id"] == "101_1"


def test_vk_fallback_180_days():
    old_items = [_make_item(i, days_ago=60) for i in range(3)]

    def mock_fetch(query, count):
        return old_items, [], []

    with patch.object(vkvideo, "_fetch_query", side_effect=mock_fetch):
        results = vkvideo.search_videos(["тест"], freshness_days=30)

    # fallback to 180 days should return results
    assert len(results) > 0


def test_vk_deduplication():
    item = _make_item(1)
    with patch.object(vkvideo, "_fetch_query", side_effect=_patch_fetch([item])):
        results = vkvideo.search_videos(["q1", "q2"])

    ids = [v["video_id"] for v in results]
    assert ids.count("101_1") == 1


def test_vk_channel_from_groups():
    item = _make_item(1)
    item["owner_id"] = -300
    groups = [{"id": 300, "name": "Cool Group"}]
    with patch.object(vkvideo, "_fetch_query", side_effect=_patch_fetch([item], groups=groups)):
        results = vkvideo.search_videos(["тест"])

    assert results[0]["channel"] == "Cool Group"


def test_vk_channel_from_profiles():
    item = _make_item(1)
    item["owner_id"] = 42
    profiles = [{"id": 42, "first_name": "John", "last_name": "Doe"}]
    with patch.object(vkvideo, "_fetch_query", side_effect=_patch_fetch([item], profiles=profiles)):
        results = vkvideo.search_videos(["тест"])

    assert results[0]["channel"] == "John Doe"
