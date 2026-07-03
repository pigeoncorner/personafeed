import asyncio
import json
import re
import shutil
import subprocess

from backend.personas import PersonaProfile, get_static_profile

_CLAUDE_BIN = shutil.which("claude")


def _call_claude_sync(prompt: str, timeout: int = 120) -> str:
    if _CLAUDE_BIN is None:
        raise RuntimeError("claude CLI not found in PATH")
    result = subprocess.run(
        [_CLAUDE_BIN, "-p", "--model", "haiku"],
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI error: {result.stderr[:200]}")
    return result.stdout.strip()


async def _call_claude(prompt: str) -> str:
    return await asyncio.to_thread(_call_claude_sync, prompt)


def _parse_json(raw: str) -> dict:
    """Извлекает JSON из ответа, игнорируя markdown-обёртки и лишний текст."""
    match = re.search(r"```(?:json)?\s*([\s\S]+?)```", raw)
    if match:
        raw = match.group(1)
    raw = raw.strip()
    start = raw.find("{")
    if start != -1:
        raw = raw[start:]
    return json.loads(raw)


_PROFILE_PROMPT = """\
You are a persona profiling assistant. Return ONLY valid JSON, no markdown, no explanation.

Generate an internet persona profile for: {persona}{specialty_hint}
Response language for name/context fields: {language}
Search queries must always be in English.

Required JSON structure:
{{
  "name": "localized persona name",
  "context": "2-3 sentence description of this persona's information diet (in {language})",
  "topics": ["topic1", "topic2", "topic3", "topic4", "topic5"],
  "seed_queries": ["english query 1", "english query 2", "english query 3", "english query 4"],
  "preferred_channels": ["Channel1", "Channel2", "Channel3"],
  "preferred_publications": ["Publication1", "Publication2", "Publication3"]
}}
"""

_CURATION_PROMPT = """\
You are a content curation assistant. Return ONLY valid JSON, no markdown, no explanation.

Persona: {persona_name}
Context: {persona_context}

Raw YouTube results:
{youtube_raw}

Raw News results:
{news_raw}

Select and rank the most relevant items for this persona. Add a brief why_relevant explanation \
(1 sentence, in {language}) for each item. Keep up to 10 YouTube items and 8 news items.

Required JSON structure:
{{
  "youtube": [
    {{"video_id": "...", "title": "...", "channel": "...", "why_relevant": "..."}}
  ],
  "news": [
    {{"url": "...", "title": "...", "source": "...", "why_relevant": "..."}}
  ],
  "top_searches": ["query 1", "query 2", "query 3"]
}}
"""


async def generate_persona_profile(
    persona: str, language: str = "ru", specialty: str | None = None
) -> PersonaProfile:
    static = get_static_profile(persona)
    if static:
        return static

    specialty_hint = f" (specialty: {specialty})" if specialty else ""
    prompt = _PROFILE_PROMPT.format(
        persona=persona,
        specialty_hint=specialty_hint,
        language=language,
    )
    raw = await _call_claude(prompt)
    data = _parse_json(raw)
    return {
        "id": persona,
        "name": data["name"],
        "context": data["context"],
        "topics": data["topics"],
        "seed_queries": data["seed_queries"],
        "preferred_channels": data.get("preferred_channels", []),
        "preferred_publications": data.get("preferred_publications", []),
    }


async def curate_feed(
    profile: PersonaProfile,
    youtube_raw: list[dict],
    news_raw: list[dict],
    language: str = "ru",
) -> dict:
    prompt = _CURATION_PROMPT.format(
        persona_name=profile["name"],
        persona_context=profile["context"],
        youtube_raw=json.dumps(youtube_raw, ensure_ascii=False),
        news_raw=json.dumps(news_raw, ensure_ascii=False),
        language=language,
    )
    raw = await _call_claude(prompt)
    return _parse_json(raw)
