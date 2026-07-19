# StumbleFeed

**Видео, которые вы никогда бы не нашли сами.**

StumbleFeed — сервис случайных находок на YouTube, вдохновлённый StumbleUpon. Вы выбираете интересные темы, а StumbleFeed показывает неочевидные качественные видео из этих областей. Никакого алгоритма, оптимизирующего залипание. Никакого бесконечного скролла. Одна лента, обновляется по кнопке.

🌐 **Демо:** [stumblefeed.me](https://stumblefeed.me)
📦 **Репозиторий:** [github.com/pigeoncorner/personafeed](https://github.com/pigeoncorner/personafeed)

---

## Проблема

Рекомендательный алгоритм YouTube отлично удерживает у экрана — но плохо помогает находить то, о чём вы не знали. Поиск требует заранее знать, что искать. Тренды показывают всем одно и то же вирусное.

StumbleFeed переворачивает это: вы один раз задаёте интересы, а лента находит неожиданный контент внутри них.

---

## Как пользоваться

1. **Выберите категории** — 20 тем от науки до философии и кино. Выбор сохраняется в браузере, при следующем визите онбординг не показывается.
2. **Выберите пресет** — Default, Top Rising (набирающие обороты), Top Bloggers, Top Commented, Viral Videos. Плюс фильтры: свежесть видео, количество просмотров, возраст канала.
3. **Переключите источник** при желании — ▶ YouTube или VK · RuTube.
4. **Нажмите Stumble** — получите сетку видео, которые сами бы не нашли. Кнопка 🎲 перезагружает ленту с новой выборкой.
5. **Смотрите на странице** — встроенный плеер в модальном окне, без перехода на YouTube.

Чипы категорий вверху страницы фильтруют ленту по одной теме («Все» — все выбранные).

Бэкенд заранее собирает пул видео по каждой категории через YouTube Data API v3 и хранит его на диске (TTL 24 часа) — запросы пользователей обслуживаются из пула мгновенно, без расхода квоты API. AI-слой (Claude CLI) генерирует неожиданные темы и фильтрует результаты.

---

## Стек

| Слой | Технология |
|------|-----------|
| Фронтенд | Vanilla JS, CSS Grid, сборка Vite — без фреймворков |
| Бэкенд | Python 3, FastAPI, uvicorn |
| Источник видео | YouTube Data API v3 |
| Российские источники | VK Video API, RuTube |
| AI-курация | Claude (через Claude Code CLI, режим stream-json) |
| Деплой | Cloudflare Pages (фронтенд) + VPS + Caddy (бэкенд) |
| HTTP-клиент | httpx |
| Конфигурация | pydantic-settings, `.env` |

---

## Структура проекта

```
personafeed/
├── backend/
│   ├── main.py              # FastAPI-приложение, lifespan, CORS
│   ├── config.py            # pydantic-settings (переменные окружения)
│   ├── categories.py        # 20 категорий с поисковыми запросами
│   ├── schemas.py           # Модели запросов / ответов
│   ├── routers/
│   │   └── feed.py          # GET /categories, POST /grid
│   └── services/
│       ├── pool.py          # Пул с предзагрузкой, TTL 24 ч, персист на диск
│       ├── youtube.py       # Клиент YouTube Data API v3
│       ├── ai.py            # Персистентная сессия Claude CLI
│       ├── vkvideo.py       # Клиент VK Video API
│       ├── rutube.py        # Клиент RuTube
│       └── news.py          # Клиент News API
├── frontend/
│   ├── index.html
│   ├── app.js               # Выбор категорий, панель фильтров, рендер сетки
│   └── style.css
├── deploy/
│   ├── setup.sh             # Скрипт настройки VPS одной командой
│   ├── stumblefeed.service  # systemd-юнит
│   └── Caddyfile            # Конфиг реверс-прокси Caddy
├── tests/
│   └── test_pool.py
├── vite.config.js           # Сборка фронтенда + dev-прокси к API
└── requirements.txt
```

---

## Запуск локально

### Требования

- Python 3.11+
- Node.js 18+ (для Vite)
- Ключ YouTube Data API v3 — [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → YouTube Data API v3
- Ключ News API — [newsapi.org](https://newsapi.org/)

### Установка

```bash
git clone https://github.com/pigeoncorner/personafeed.git
cd personafeed

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

npm install
```

Создайте `.env`:

```env
YOUTUBE_API_KEY=your_youtube_key
NEWS_API_KEY=your_newsapi_key
VK_ACCESS_TOKEN=          # опционально — поддержка VK Video
```

### Запуск (dev-режим)

Два терминала:

```bash
# 1. Бэкенд
python -m uvicorn backend.main:app --port 8002 --reload

# 2. Фронтенд (Vite dev-сервер, проксирует API на бэкенд)
npm run dev
```

Открыть [http://localhost:5173](http://localhost:5173).

### Сборка фронтенда

```bash
npm run build     # результат в dist/
```

### Тесты

```bash
pytest tests/
```

---

## API

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/categories` | Список всех 20 категорий |
| `POST` | `/grid` | Курируемая сетка видео |
| `GET` | `/health` | Проверка живости |

### POST /grid — тело запроса

```json
{
  "categories": ["science", "history"],
  "source": "youtube",
  "limit": 20,
  "sort": "velocity",
  "filters": {
    "period": "30",
    "views": "lt10k",
    "channel": "young"
  }
}
```

---

## AI-интеграция

StumbleFeed использует **Claude** через [Claude Code](https://claude.ai/code) CLI вместо AI API — для небольшого проекта это уместно: работает по подписке, не требует отдельного ключа. Персистентный процесс `claude` живёт между запросами (режим stream-json), что убирает холодный старт в 10–20 секунд на каждый вызов.

AI-слой делает две вещи:

1. **Генерация тем** — для категории и случайного «угла» (скрытая история, экономика явления, кросс-культурные связи и т.д.) Claude придумывает узкую неожиданную тему, которую пользователь сам не стал бы искать
2. **Курация контента** — сырую выдачу YouTube Claude ранжирует и фильтрует по релевантности

Проект полностью разработан в **Kodik IDE** (Claude Code).

---

## Деплой

### Фронтенд → Cloudflare Pages

Подключите ветку `main` к Cloudflare Pages. Команда сборки: `npm run build`, директория вывода: `dist`.

Автодеплой при каждом пуше в `main`.

### Бэкенд → VPS (Ubuntu)

```bash
git clone -b main https://github.com/pigeoncorner/personafeed.git /tmp/personafeed
bash /tmp/personafeed/deploy/setup.sh

nano /opt/stumblefeed/.env   # заполнить ключи API
systemctl start stumblefeed
systemctl status stumblefeed
```

Caddy автоматически поднимает реверс-прокси и SSL (Let's Encrypt).

---

## Категории

| | | | |
|---|---|---|---|
| 🔬 Наука и математика | 🏛️ История | 🎨 Искусство и дизайн | ⚙️ Технологии и железо |
| 💻 Интернет и софт | 🌿 Природа и животные | 🧠 Философия и жизнь | 🍜 Еда и кулинария |
| 🎮 Игры | 🎵 Музыка и звук | 🩺 Здоровье | 💼 Бизнес и экономика |
| 🌍 Культура и общество | 📚 Образование | 📖 Литература | 🎬 Кино и сериалы |
| ⚽ Спорт | 🏡 Дом и сад | 🤪 Развлечения | ✈️ Путешествия |

---

## Лицензия

MIT
