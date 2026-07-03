from unittest.mock import MagicMock, patch

from backend.services.youtube import parse_duration, search_videos


def _make_item(video_id: str, title: str, channel: str) -> dict:
    return {
        "id": {"videoId": video_id},
        "snippet": {
            "title": title,
            "channelTitle": channel,
            "thumbnails": {"medium": {"url": f"https://img/{video_id}.jpg"}},
            "publishedAt": "2026-06-01T00:00:00Z",
        },
    }


def _make_details(video_id: str, duration: str = "PT10M", views: str = "1000") -> dict:
    return {
        "id": video_id,
        "contentDetails": {"duration": duration},
        "statistics": {"viewCount": views},
    }


def _mock_yt(items_per_call: list[list[dict]], details: list[dict] | None = None):
    mock_client = MagicMock()
    search_mock = mock_client.search.return_value.list.return_value.execute
    search_mock.side_effect = [{"items": items} for items in items_per_call]
    videos_mock = mock_client.videos.return_value.list.return_value.execute
    videos_mock.return_value = {"items": details or []}
    return mock_client


def test_parse_duration():
    assert parse_duration("PT1H2M3S") == 3723
    assert parse_duration("PT45S") == 45
    assert parse_duration("PT10M") == 600
    assert parse_duration("") == 0
    assert parse_duration("invalid") == 0


def test_search_videos_returns_results():
    items = [_make_item("v1", "Title 1", "Chan A")]
    details = [_make_details("v1")]
    with patch("backend.services.youtube._client", return_value=_mock_yt([items], details)):
        results = search_videos(["query"])
    assert len(results) == 1
    assert results[0]["video_id"] == "v1"
    assert results[0]["url"] == "https://www.youtube.com/watch?v=v1"


def test_search_videos_enriched():
    items = [_make_item("v1", "Title 1", "Chan A")]
    details = [_make_details("v1", duration="PT1H2M3S", views="123456")]
    with patch("backend.services.youtube._client", return_value=_mock_yt([items], details)):
        results = search_videos(["query"])
    assert results[0]["duration"] == 3723
    assert results[0]["views"] == 123456
    assert results[0]["published_at"] == "2026-06-01T00:00:00Z"


def test_search_videos_enrich_missing_details():
    items = [_make_item("v1", "Title 1", "Chan A")]
    with patch("backend.services.youtube._client", return_value=_mock_yt([items], [])):
        results = search_videos(["query"])
    assert results[0]["duration"] == 0
    assert results[0]["views"] == 0


def test_search_videos_deduplication():
    dup = _make_item("v1", "Title 1", "Chan A")
    details = [_make_details("v1")]
    with patch("backend.services.youtube._client", return_value=_mock_yt([[dup], [dup]], details)):
        results = search_videos(["query1", "query2"])
    assert len(results) == 1


def test_search_passes_published_after():
    items = [_make_item("v1", "Title 1", "Chan A")]
    mock = _mock_yt([items, items], [_make_details("v1")])
    with patch("backend.services.youtube._client", return_value=mock):
        search_videos(["query1", "query2"], freshness_days=30)

    calls = mock.search.return_value.list.call_args_list
    assert len(calls) == 2
    for call in calls:
        assert "publishedAfter" in call.kwargs
        assert call.kwargs["publishedAfter"].endswith("Z")
    # последний запрос — по дате, остальные — по релевантности
    assert calls[0].kwargs["order"] == "relevance"
    assert calls[1].kwargs["order"] == "date"


def test_search_videos_empty_response():
    with patch("backend.services.youtube._client", return_value=_mock_yt([[]])):
        results = search_videos(["query"])
    assert results == []
