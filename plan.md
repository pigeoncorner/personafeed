# План v2: переключатель источников YouTube ↔ VK/RuTube

## Задача

Источники **не смешиваются**. В топбаре — переключатель:
положение 1 — YouTube, положение 2 — VK/RuTube. Переключатель меняет источник пула.

Второй источник: RuTube (открытый API без авторизации, работает сразу) + VK опционально
при наличии `VK_ACCESS_TOKEN` в `.env`.

**Состояние кода на старте:**
- `config.py`: `vk_access_token: str = ""` — уже добавлено.
- `categories.py`: TypedDict содержит `queries_vk: list[str]`, но поле не заполнено ни в одной категории.
- 36 тестов зелёные. `vkvideo.py`, `rutube.py` — не существуют.

## Ключевые решения дизайна

- `POST /grid {categories, limit, source}`, source ∈ `"youtube" | "ru"`, default `"youtube"`.
- Ключ пула: `f"{category_id}:{source}"` — источники раздельны. Старый `data/pools.json` удалить.
- `queries_vk` → переименовать в `queries_ru` (общее для VK и RuTube).
- Плеер: есть `embed_url` → iframe с ним; нет → YouTube-embed из `video_id`.

## Шаги реализации

Правила исполнителю:
- Файлы с большим числом правок перезаписывать целиком одним Write, не серией Edit.
- Коммит после каждого шага. `ai.py` и `news.py` не трогать.

### 1. categories.py — queries_ru
Перезаписать файл целиком. В TypedDict: заменить `queries_vk` → `queries_ru`.
Каждой категории добавить `queries_ru`:

- science: ["научпоп физика объяснение", "математика красивое доказательство", "астрономия открытия космос"]
- history: ["история древних цивилизаций документальный", "археологические находки", "неизвестные страницы истории"]
- art: ["история живописи разбор картины", "процесс художника таймлапс", "дизайн разбор"]
- tech: ["как это устроено инженерия", "как делают на заводе производство", "разбор техники железо"]
- software: ["программирование разбор архитектуры", "история создания программы", "веб-разработка практика"]
- nature: ["дикая природа документальный", "удивительные животные", "экспедиция природа"]
- philosophy: ["философия просто о сложном", "стоицизм практика жизни", "мысленный эксперимент философия"]
- food: ["кухни мира уличная еда", "наука кулинарии техника", "рецепт от шефа разбор"]
- games: ["разбор геймдизайна", "история видеоигр", "инди разработка игр"]
- music: ["теория музыки объяснение", "история музыкального жанра", "как устроен звук саунд-дизайн"]
- health: ["научный подход тренировки", "психология исследования", "как работает организм человека"]
- business: ["история бизнеса разбор", "экономика простыми словами", "предприниматель история провала"]
- culture: ["традиции народов мира документальный", "путешествие отдалённые места", "социология эксперименты"]
- education: ["как учиться эффективно наука", "методики преподавания", "как работает память обучение"]
- literature: ["разбор книги анализ", "писательское мастерство", "забытые писатели история литературы"]
- movies: ["разбор фильма кинематография", "история кино", "как снимают кино закулисье"]
- sports: ["спортивная наука биомеханика", "история спорта великие моменты", "тренировки профессиональных атлетов"]
- home: ["ремонт своими руками до и после", "дизайн интерьера разбор", "сад огород советы"]
- fun: ["странные эксперименты", "абсурдные факты истории", "смешные изобретения"]

Verify: `python -c "from backend.categories import CATEGORIES; assert all(len(c['queries_ru'])==3 for c in CATEGORIES.values())"`.

### 2. backend/services/rutube.py (новый)
`search_videos(queries, max_per_query=10, freshness_days=30) -> list[dict]`

- Эндпоинт: `GET https://rutube.ru/api/search/video/?query={q}&format=json`
- HTTP через `urllib.request` с **timeout=15** (обязательно).
- Перед маппингом сделать один живой тестовый запрос и проверить реальные поля JSON.
  Ожидаемые: `results[]` → `id`, `title`, `thumbnail_url`, `duration` (сек), `hits` (просмотры),
  `publication_ts` / `created_ts` (unix или ISO), `author.name`, `video_url`.
- Маппинг: `video_id=str(id)`, `url=video_url`, `thumbnail=thumbnail_url`,
  `embed_url=f"https://rutube.ru/play/embed/{id}"`, `source="rutube"`.
- Фильтр свежести 30 дней по дате; если после фильтра пусто — без фильтра. Дедупликация.

### 3. backend/services/vkvideo.py (новый)
Тот же контракт. `GET https://api.vk.com/method/video.search`,
параметры: `q`, `count=max_per_query*2`, `sort=2`, `adult=0`, `extended=1`, `v=5.199`,
`access_token=settings.vk_access_token`. urllib с timeout=15.

- Поле `error` в JSON → RuntimeError.
- Маппинг: `video_id=f"{owner_id}_{id}"`, `url=https://vk.com/video{owner_id}_{id}`,
  `thumbnail` — из `image[]` ближайший к width 320 (fallback первый),
  `published_at` из `date` (unix → ISO UTC), `embed_url` из `player`, `source="vk"`.
  `channel` — имя из `groups`/`profiles` по owner_id, fallback "".
- Фильтр свежести 30 дней, fallback 180. Дедупликация.

### 4. backend/services/pool.py — раздельные пулы
- Ключ: `f"{category_id}:{source}"`.
- `_fetch(cat, source)`:
  - `"youtube"` → `youtube.search_videos(cat["queries"])`, добавить `source="youtube"` каждому.
  - `"ru"` → `rutube.search_videos(cat["queries_ru"])` всегда; если `settings.vk_access_token` непустой →
    `vkvideo.search_videos(cat["queries_ru"])` тоже. Каждый вызов в отдельном try/except.
- `get_pool(cat, source)`, `sample(category_ids, categories_map, limit, source)`.
- `refresh_stale(categories)` — оба источника.
- Удалить `data/pools.json`.

### 5. Схема и роутер
- `schemas.py`: `GridRequest` + `source: str = "youtube"`; `VideoItem` + `source: str = "youtube"`,
  `embed_url: str = ""`.
- `routers/feed.py`: `source not in ("youtube", "ru")` → 422; передать `source` в `sample`;
  прокинуть `source`, `embed_url` в VideoItem.

### 6. Фронтенд
- `index.html`: topbar-center — сегмент-переключатель, две кнопки `▶ YouTube` / `VK · RuTube`,
  id `src-youtube`, `src-ru`, контейнер `id="source-toggle"`, по умолчанию `hidden`.
- `app.js`: `currentSource = localStorage.getItem("pf_source") || "youtube"`;
  клик → сохранить, подсветить, вызвать `loadGrid`; `loadGrid` шлёт `source: currentSource`;
  `openPlayer`: если `item.embed_url` → `iframe.src = item.embed_url`, иначе YouTube-embed.
  Бейдж источника на карточке.
- `style.css`: `#source-toggle` по образцу `.chip`, `.source-badge` по образцу `.cat-badge`.

### 7. .env.example
`YOUTUBE_API_KEY=`, `NEWS_API_KEY=`, `VK_ACCESS_TOKEN=` (опционально, с комментарием).

## Unit-тесты

Новые: `tests/test_rutube.py`, `tests/test_vkvideo.py`.
Обновить: `test_pool.py`, `test_feed.py` под новые сигнатуры (`sample` с `source`, ключи пулов).
Все 36 существующих должны остаться зелёными.

- [ ] rutube: маппинг полей (video_id, url, thumbnail, duration, views, embed_url, source="rutube")
- [ ] rutube: дедупликация id
- [ ] vk: маппинг полей, embed_url из player, video_id = owner_id_id
- [ ] vk: `error` в ответе → RuntimeError
- [ ] vk: фильтр свежести 30 дней / fallback 180
- [ ] pool: ключи пулов содержат source, youtube и ru не пересекаются
- [ ] pool: source="ru" без токена → только rutube вызван
- [ ] pool: source="ru" с токеном → оба вызваны; падение vk не роняет rutube
- [ ] grid: source="ru" отдаёт только ru-элементы
- [ ] grid: неизвестный source → 422
- [ ] grid: default source = "youtube"

## Verification

1. `python -m pytest` — всё зелёное.
2. Удалить `data/pools.json`, запустить сервер.
   `POST /grid {"categories":["science"],"source":"ru"}` → видео RuTube.
3. Браузер: переключатель меняет сетку; RuTube-карточка открывается в iframe `rutube.ru/play/embed/…`;
   выбор источника переживает F5.
4. С VK-токеном: в ru-сетке появляются `source:"vk"`.

## Риски

- Поля JSON RuTube могут отличаться → шаг 2 требует живого запроса перед маппингом.
- RuTube API неофициальный → при rate limit добавить паузу 0.5 с между запросами.
- VK-токен не обязателен: «ru» работает на одном RuTube.
