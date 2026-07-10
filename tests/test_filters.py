import time
from datetime import datetime, timedelta, timezone

import pytest

from backend.services import pool as pool_service
from backend.services.pool import _apply_filters, _SORT_KEYS


def _iso(days_ago: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()


def _video(**overrides) -> dict:
    base = {
        "video_id": "v1", "title": "t", "channel": "c", "url": "u", "thumbnail": "",
        "duration": 600, "views": 5000, "likes": 100, "comments": 20,
        "published_at": _iso(10), "channel_id": "ch1",
        "channel_subscribers": 50000, "channel_published_at": _iso(1000),
        "source": "youtube", "embed_url": "",
    }
    base.update(overrides)
    return base


@pytest.fixture(autouse=True)
def reset_pools():
    pool_service._pools.clear()
    yield
    pool_service._pools.clear()


# ---------- _apply_filters ----------

def test_no_filters_returns_all():
    videos = [_video(video_id="a"), _video(video_id="b")]
    assert _apply_filters(videos, None) == videos
    assert _apply_filters(videos, {}) == videos


def test_views_min_max():
    videos = [_video(video_id="low", views=500),
              _video(video_id="mid", views=50_000),
              _video(video_id="high", views=500_000)]
    assert [v["video_id"] for v in _apply_filters(videos, {"views_max": 10_000})] == ["low"]
    assert [v["video_id"] for v in _apply_filters(videos, {"views_min": 100_000})] == ["high"]
    assert [v["video_id"] for v in _apply_filters(
        videos, {"views_min": 10_000, "views_max": 100_000})] == ["mid"]


def test_comments_min():
    videos = [_video(video_id="quiet", comments=5), _video(video_id="hot", comments=500)]
    assert [v["video_id"] for v in _apply_filters(videos, {"comments_min": 100})] == ["hot"]


def test_engagement_min():
    # 1000 просмотров: 200 лайков+комментов = 0.2 vs 2 = 0.002
    videos = [_video(video_id="dead", views=1000, likes=1, comments=1),
              _video(video_id="alive", views=1000, likes=150, comments=50)]
    assert [v["video_id"] for v in _apply_filters(videos, {"engagement_min": 0.05})] == ["alive"]


def test_period_days():
    videos = [_video(video_id="fresh", published_at=_iso(3)),
              _video(video_id="old", published_at=_iso(90)),
              _video(video_id="nodate", published_at="")]
    assert [v["video_id"] for v in _apply_filters(videos, {"period_days": 7})] == ["fresh"]


def test_duration_and_shorts():
    videos = [_video(video_id="short", duration=45),
              _video(video_id="mid", duration=300),
              _video(video_id="long", duration=3600)]
    assert [v["video_id"] for v in _apply_filters(videos, {"exclude_shorts": True})] == ["mid", "long"]
    assert [v["video_id"] for v in _apply_filters(videos, {"duration_max": 240})] == ["short"]
    assert [v["video_id"] for v in _apply_filters(videos, {"duration_min": 1200})] == ["long"]


def test_subscribers_min_max():
    videos = [_video(video_id="small", channel_subscribers=2000),
              _video(video_id="big", channel_subscribers=500_000)]
    assert [v["video_id"] for v in _apply_filters(videos, {"subscribers_min": 100_000})] == ["big"]
    assert [v["video_id"] for v in _apply_filters(videos, {"subscribers_max": 10_000})] == ["small"]


def test_channel_age_max_days():
    videos = [_video(video_id="young", channel_published_at=_iso(100)),
              _video(video_id="veteran", channel_published_at=_iso(2000)),
              _video(video_id="nodate", channel_published_at="")]
    assert [v["video_id"] for v in _apply_filters(
        videos, {"channel_age_max_days": 365})] == ["young"]


def test_viral_ratio():
    videos = [_video(video_id="viral", views=100_000, channel_subscribers=1000),
              _video(video_id="normal", views=1000, channel_subscribers=100_000),
              _video(video_id="unknown_subs", views=100_000, channel_subscribers=0)]
    # неизвестные подписчики (0) не считаются вирусными
    assert [v["video_id"] for v in _apply_filters(videos, {"viral_ratio_min": 2.0})] == ["viral"]


def test_missing_fields_treated_as_zero():
    # видео от ru-источников без likes/comments/subscribers
    bare = {"video_id": "ru1", "views": 5000, "duration": 300, "published_at": _iso(5)}
    assert _apply_filters([bare], {"views_min": 1000}) == [bare]
    assert _apply_filters([bare], {"comments_min": 1}) == []
    assert _apply_filters([bare], {"subscribers_min": 1}) == []


# ---------- sort keys ----------

def test_sort_key_engagement():
    v = _video(views=1000, likes=80, comments=20)
    assert _SORT_KEYS["engagement"](v) == pytest.approx(0.1)


def test_sort_key_engagement_zero_views():
    v = _video(views=0, likes=10, comments=0)
    assert _SORT_KEYS["engagement"](v) == 10  # деление на max(views,1), не падает


def test_sort_key_velocity():
    v = _video(views=10_000, published_at=_iso(10))
    assert _SORT_KEYS["velocity"](v) == pytest.approx(1000, rel=0.05)


def test_sort_key_velocity_no_date_goes_last():
    assert _SORT_KEYS["velocity"](_video(published_at="")) == -1.0


# ---------- sample() with filters/sort ----------

_MAP = {"science": {"id": "science", "label": "Наука", "queries": ["q"], "queries_ru": ["з"]}}


def _fill_pool(videos):
    pool_service._pools["science:youtube"] = {
        "version": pool_service._POOL_VERSION, "fetched_at": time.time(), "videos": videos,
    }


def test_sample_applies_filters():
    _fill_pool([_video(video_id="a", views=500), _video(video_id="b", views=50_000)])
    result = pool_service.sample(["science"], _MAP, limit=10, filters={"views_max": 10_000})
    assert [v["video_id"] for v in result] == ["a"]


def test_sample_sorts_by_views():
    _fill_pool([_video(video_id="a", views=10), _video(video_id="b", views=999),
                _video(video_id="c", views=100)])
    result = pool_service.sample(["science"], _MAP, limit=10, sort="views")
    assert [v["video_id"] for v in result] == ["b", "c", "a"]


def test_sample_sorts_by_date():
    _fill_pool([_video(video_id="old", published_at=_iso(30)),
                _video(video_id="new", published_at=_iso(1))])
    result = pool_service.sample(["science"], _MAP, limit=10, sort="date")
    assert [v["video_id"] for v in result] == ["new", "old"]


def test_sample_sort_respects_limit_and_dedup():
    _fill_pool([_video(video_id=f"v{i}", views=i) for i in range(20)])
    result = pool_service.sample(["science"], _MAP, limit=5, sort="views")
    assert len(result) == 5
    ids = [v["video_id"] for v in result]
    assert len(ids) == len(set(ids))


def test_sample_random_unchanged():
    _fill_pool([_video(video_id=f"v{i}") for i in range(5)])
    result = pool_service.sample(["science"], _MAP, limit=10, sort="random")
    assert len(result) == 5
