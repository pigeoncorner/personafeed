import json
from unittest.mock import AsyncMock, patch

import pytest

from backend.services.ai import _parse_json, curate_feed, generate_persona_profile


def test_parse_json_clean():
    raw = '{"key": "value"}'
    assert _parse_json(raw) == {"key": "value"}


def test_parse_json_markdown_wrapper():
    raw = '```json\n{"key": "value"}\n```'
    assert _parse_json(raw) == {"key": "value"}


def test_parse_json_with_preamble():
    raw = 'Here is the JSON:\n{"key": "value"}'
    assert _parse_json(raw) == {"key": "value"}


def test_parse_json_markdown_no_lang():
    raw = "```\n{\"key\": \"value\"}\n```"
    assert _parse_json(raw) == {"key": "value"}


@pytest.mark.asyncio
async def test_generate_persona_profile_static():
    # Базовые персонажи не вызывают subprocess
    with patch("backend.services.ai._call_claude_sync") as mock:
        profile = await generate_persona_profile("scientist", "ru")
    mock.assert_not_called()
    assert profile["id"] == "scientist"
    assert "topics" in profile
    assert "seed_queries" in profile


@pytest.mark.asyncio
async def test_generate_persona_profile_custom():
    fake_response = json.dumps({
        "name": "Пчеловод",
        "context": "Пчеловод следит за здоровьем пчелиных семей...",
        "topics": ["beekeeping", "apiculture", "honey production"],
        "seed_queries": ["beekeeping techniques 2024", "varroa mite treatment"],
        "preferred_channels": ["Barnyard Bees"],
        "preferred_publications": ["Bee Culture"],
    })
    # Патчим синхронную функцию, чтобы не трогать глобальный asyncio.to_thread
    with patch("backend.services.ai._call_claude_sync", return_value=fake_response):
        profile = await generate_persona_profile("beekeeper", "ru")
    assert profile["name"] == "Пчеловод"
    assert "beekeeping" in profile["topics"]


@pytest.mark.asyncio
async def test_curate_feed():
    fake_response = json.dumps({
        "youtube": [
            {"video_id": "abc123", "title": "Physics Lecture", "channel": "MIT OCW", "why_relevant": "Базовая лекция"}
        ],
        "news": [
            {"url": "https://nature.com/1", "title": "New Findings", "source": "Nature", "why_relevant": "Ключевое исследование"}
        ],
        "top_searches": ["arxiv preprints", "quantum computing 2024"],
    })

    from backend.personas import get_static_profile
    profile = get_static_profile("scientist")

    with patch("backend.services.ai._call_claude_sync", return_value=fake_response):
        result = await curate_feed(profile, [], [], "ru")

    assert result["youtube"][0]["video_id"] == "abc123"
    assert result["news"][0]["source"] == "Nature"
    assert len(result["top_searches"]) == 2
