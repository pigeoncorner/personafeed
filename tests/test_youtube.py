from unittest.mock import MagicMock, patch

from backend.services.youtube import search_videos


def _make_item(video_id: str, title: str, channel: str) -> dict:
    return {
        "id": {"videoId": video_id},
        "snippet": {
            "title": title,
            "channelTitle": channel,
            "thumbnails": {"medium": {"url": f"https://img/{video_id}.jpg"}},
        },
    }


def _mock_yt(items_per_call: list[list[dict]]):
    mock_client = MagicMock()
    search_mock = mock_client.search.return_value.list.return_value.execute
    search_mock.side_effect = [{"items": items} for items in items_per_call]
    return mock_client


def test_search_videos_returns_results():
    items = [_make_item("v1", "Title 1", "Chan A")]
    with patch("backend.services.youtube._client", return_value=_mock_yt([items])):
        results = search_videos(["query"])
    assert len(results) == 1
    assert results[0]["video_id"] == "v1"
    assert results[0]["url"] == "https://www.youtube.com/watch?v=v1"


def test_search_videos_deduplication():
    dup = _make_item("v1", "Title 1", "Chan A")
    with patch("backend.services.youtube._client", return_value=_mock_yt([[dup], [dup]])):
        results = search_videos(["query1", "query2"])
    assert len(results) == 1


def test_search_videos_empty_response():
    with patch("backend.services.youtube._client", return_value=_mock_yt([[]])):
        results = search_videos(["query"])
    assert results == []
