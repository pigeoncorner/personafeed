# PersonaFeed — серендипити по категориям (пивот от персонажей)

## Задача

Отказаться от персонажей. Модель cloudhiker.net: пользователь выбирает категории →
система выдаёт неожиданный свежий контент из них. Плюс ускорение AI-вызовов
(warm CLI-сессия) и свежесть ленты (publishedAfter + дата в ключе кеша).

YouTube-клон UI сохраняется, меняется наполнение.

## Шаги реализации

1. **Warm CLI-сессия** (`ai.py`): долгоживущий процесс `claude -p --input-format stream-json
   --output-format stream-json`, класс `ClaudeSession` (lazy start, asyncio.Lock,
   рестарт каждые ~15 запросов и при падении). Сигнатура `_call_claude()` не меняется.
   → verify: smoke-тест CLI + unit-тесты с mock Popen.
2. **Категории** (`categories.py` вместо `personas.py`, ~18 шт. по образцу cloudhiker):
   `GET /categories`, `POST /feed {category}` (кеш с датой в ключе),
   `POST /surprise {categories[]}` (random категория → Claude придумывает niche-тему,
   без кеша топика). Промпт `_TOPIC_PROMPT` вместо `_PROFILE_PROMPT`.
   `FeedResponse`: `{category_id, category_label, topic, intro, youtube[], news[], searches[], cached}`.
   → verify: unit-тесты endpoint'ов.
3. **Свежесть** (`youtube.py`): `publishedAfter` = now−30d, микс order relevance/date.
   → verify: unit-тест параметров вызова.
4. **Фронтенд**: онбординг «Выбери категории» (localStorage), chips = выбранные категории + «⚙»,
   кнопка «🎲 Удиви меня» в топбаре, баннер с темой/intro, поиск = «своя тема».
   → verify: визуально в браузере.
5. Все тесты зелёные → коммит → пуш.

## Unit-тесты

- [x] `test_ai.py::test_session_request_response` — warm-сессия: запрос/ответ JSONL (mock Popen).
- [x] `test_ai.py::test_session_restart_after_n` — рестарт процесса после N запросов.
- [x] `test_ai.py::test_session_respawn_on_death` — respawn при падении процесса + retry.
- [x] `test_feed.py::test_get_categories` — GET /categories отдаёт список.
- [x] `test_feed.py::test_feed_cache_key_has_date` — ключ кеша содержит дату.
- [x] `test_feed.py::test_surprise_picks_from_list` — категория выбрана из переданных, есть topic/intro.
- [x] `test_feed.py::test_surprise_not_cached` — повторный surprise генерирует новый топик.
- [x] `test_youtube.py::test_search_passes_published_after` — publishedAfter передаётся в API.

Все 28 тестов зелёные (04.07.2026).

## Риски

- YouTube-квота: surprise ≈ 300–400 units → ~25 кликов/день. Смягчение: 3 запроса, кеш 30 мин на повторные seed-запросы.
- Формат stream-json проверить smoke-тестом до реализации.
