# План: research-фильтры и пресеты в ленте

## Задача

В подборке много мусора: единственный «фильтр качества» — ранжирование relevance от
YouTube. Добавить пользовательские настройки фильтрации и сортировки выборки +
пресеты-комбинации («Восходящие тренды», «Лидеры ниши», «Дискуссии», «Вирусное»).

Ключевые факты:
- `_enrich()` в `youtube.py` уже вызывает `videos.list part="contentDetails,statistics"` —
  `likeCount`/`commentCount` приходят, но не сохраняются → фильтры вовлечённости = 0 доп. квоты.
- Подписчики и возраст канала — батч `channels.list part=statistics,snippet`
  (1 юнит на 50 каналов).
- RuTube/VK отдают только `views`/`duration`/`published_at` → фильтры по
  комментариям/каналам только для source=youtube, UI скрывает их для «ru».
- Пул кеширован в `data/pools.json` (24 ч) без новых полей → версионный сброс пула.

## Шаги реализации

### 1. Обогащение данных — `backend/services/youtube.py`
- `search_videos()`: сохранять `channel_id` из `snippet["channelId"]`.
- `_enrich()`: сохранять `likes` (`likeCount`, нет → 0), `comments` (`commentCount`, скрыт → 0).
- Новая `_enrich_channels(videos)`: уникальные channel_id батчами по 50 →
  `channels().list(part="statistics,snippet")` → `channel_subscribers`
  (hiddenSubscriberCount → 0), `channel_published_at`. Вызов из `search_videos()`.

### 2. Схемы — `backend/schemas.py`
- `GridFilters`: `period_days`, `views_min/max`, `comments_min`, `engagement_min`,
  `duration_min/max`, `exclude_shorts`, `subscribers_min/max`,
  `channel_age_max_days`, `viral_ratio_min` — все опциональные.
- `GridRequest`: + `filters: GridFilters | None`, + `sort: str = "random"`.
- `VideoItem`: + `likes`, `comments`, `channel_id`, `channel_subscribers`,
  `channel_published_at`.

### 3. Фильтрация и сортировка — `backend/services/pool.py`
- `_POOL_VERSION = 2` в записи пула; несовпадение версии → stale (сброс старого кеша).
- `_apply_filters(videos, filters)` — чистая функция, отсутствующие поля = 0.
- `sample(..., filters=None, sort="random")`: фильтр по бакетам до интерливинга;
  `random` — как сейчас; иначе объединить, дедуп, сортировка, `limit`.
  Ключи: `date`, `views`, `comments`, `engagement` ((likes+comments)/max(views,1)),
  `velocity` (views/дней с публикации; без даты — в конец).

### 4. Роутер — `backend/routers/feed.py`
- Валидация `sort` ∈ {random, date, views, comments, engagement, velocity} → иначе 422.
- Прокинуть `filters`/`sort` в `sample`, новые поля в `VideoItem`.

### 5. Frontend — `index.html`, `app.js`, `style.css`
- Кнопка «Фильтры» рядом с переключателем источника → панель:
  пресеты-чипы (🌱 Восходящие: до 10k + 30 дней + канал < года + sort=velocity;
  👑 Лидеры ниши: 100k+ подписчиков + sort=views; 💬 Дискуссии: 100+ комментариев +
  sort=comments; 🎯 Вирусное: views/подписчики ≥ 2 + 30 дней + sort=views; ✖ Сброс),
  период (7/30/90/все), просмотры (до 10k / 10k–100k / 100k+ / все),
  комментарии (10+/100+/1000+/все, YouTube-only), длительность (без Shorts / до 4 /
  4–20 / 20+ / все), каналы (топ/малые/молодые/все, YouTube-only),
  сортировка (случайно/дата/просмотры/комментарии/вовлечённость/динамика).
- Состояние в localStorage `pf_filters`; при source=«ru» YouTube-only контролы
  скрываются и сбрасываются; изменение → `loadGrid()`.

### 6. Документация
- `researchplan.md`: пометить, что research-фильтры (Этап 2) реализованы в хакатонной версии.

## Unit-тесты

- [ ] `_enrich` сохраняет likes/comments; отсутствующие счётчики → 0
- [ ] `_enrich_channels` маппит подписчиков/дату канала, батчит по 50
- [ ] `_apply_filters`: каждый фильтр; отсутствующие поля = 0
- [ ] сортировки velocity/engagement корректны; без published_at при velocity — в конце
- [ ] пул без `version` → stale
- [ ] `/grid`: неизвестный sort → 422; запрос без filters работает как раньше
- [ ] существующие тесты остаются зелёными
