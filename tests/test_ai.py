import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.ai import (
    ClaudeSession,
    _parse_json,
    curate_feed,
    generate_persona_profile,
)


def _result_line(text: str) -> str:
    return json.dumps({"type": "result", "subtype": "success", "is_error": False, "result": text}) + "\n"


def _fake_proc(stdout_lines: list[str]) -> MagicMock:
    proc = MagicMock()
    proc.poll.return_value = None
    proc.stdout.readline.side_effect = stdout_lines
    return proc


def test_session_request_response():
    proc = _fake_proc([_result_line("PONG")])
    with (
        patch("backend.services.ai._CLAUDE_BIN", "claude"),
        patch("backend.services.ai.subprocess.Popen", return_value=proc) as popen,
    ):
        session = ClaudeSession()
        assert session.request("ping") == "PONG"
    popen.assert_called_once()
    written = proc.stdin.write.call_args[0][0]
    assert json.loads(written)["message"]["content"][0]["text"] == "ping"


def test_session_restart_after_n():
    proc1 = _fake_proc([_result_line("one")])
    proc2 = _fake_proc([_result_line("two")])
    with (
        patch("backend.services.ai._CLAUDE_BIN", "claude"),
        patch("backend.services.ai.subprocess.Popen", side_effect=[proc1, proc2]) as popen,
        patch.object(ClaudeSession, "MAX_REQUESTS", 1),
    ):
        session = ClaudeSession()
        assert session.request("a") == "one"
        assert session.request("b") == "two"
    assert popen.call_count == 2
    proc1.kill.assert_called()  # старый процесс убит при рестарте


def test_session_respawn_on_death():
    dead_proc = _fake_proc([""])  # EOF — процесс умер
    dead_proc.poll.return_value = 1
    alive_proc = _fake_proc([_result_line("OK")])
    with (
        patch("backend.services.ai._CLAUDE_BIN", "claude"),
        patch("backend.services.ai.subprocess.Popen", side_effect=[dead_proc, alive_proc]),
    ):
        session = ClaudeSession()
        with pytest.raises(RuntimeError):
            session.request("first")
        # процесс мёртв → следующий запрос спаунит новый и работает
        assert session.request("second") == "OK"


@pytest.mark.asyncio
async def test_call_claude_retries_on_failure():
    from backend.services import ai as ai_module

    with patch(
        "backend.services.ai._call_claude_sync",
        side_effect=[RuntimeError("pipe broke"), "recovered"],
    ):
        result = await ai_module._call_claude("prompt")
    assert result == "recovered"


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
