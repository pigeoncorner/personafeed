# StumbleFeed

**Discover videos you'd never think to search for.**

StumbleFeed is a serendipity engine for YouTube content — inspired by StumbleUpon. You pick topics you care about, and StumbleFeed surfaces non-obvious, high-quality videos from those areas. No algorithm optimizing for addiction. No endless scroll. Just one curated feed, refreshed on demand.

🌐 **Live demo:** [stumblefeed.me](https://stumblefeed.me)  
📦 **Repo:** [github.com/pigeoncorner/personafeed](https://github.com/pigeoncorner/personafeed)

---

## The Problem

YouTube's recommendation algorithm is great at keeping you watching — but terrible at helping you discover things you didn't know you wanted to find. Searching requires you to already know what to look for. Trending feeds surface the same viral content for everyone.

StumbleFeed flips this: you define your interests once, and the feed finds surprising, non-obvious content within those areas.

---

## How It Works

1. **Select categories** — 20 topics from Science to Philosophy to Film
2. **Apply a preset** — Default, Top Rising, Top Bloggers, Top Commented, Viral Videos
3. **Hit Stumble** — get a curated grid of videos you'd never have found yourself
4. **Watch in-page** — embedded player, no redirect to YouTube

The backend pre-fetches a pool of videos per category via YouTube Data API v3 and persists it locally (7-day TTL). Requests are served from the pool instantly. An AI layer (Claude CLI) generates surprising topic angles and curates results for relevance.

---

## Screenshots

> _Coming soon — site live at [stumblefeed.me](https://stumblefeed.me)_

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vanilla JS, CSS Grid — no frameworks |
| Backend | Python 3, FastAPI, uvicorn |
| Video source | YouTube Data API v3 |
| Russian sources | VK Video API, RuTube |
| AI curation | Claude (via Claude Code CLI, stream-json mode) |
| Deployment | Cloudflare Pages (frontend) + VPS + Caddy (backend) |
| HTTP client | httpx |
| Config | pydantic-settings, `.env` |

---

## Project Structure

```
personafeed/
├── backend/
│   ├── main.py              # FastAPI app, lifespan, CORS
│   ├── config.py            # pydantic-settings (env vars)
│   ├── categories.py        # 20 categories with search queries
│   ├── schemas.py           # Request / response models
│   ├── routers/
│   │   └── feed.py          # GET /categories, POST /grid
│   └── services/
│       ├── pool.py          # Pre-fetch pool, 7-day TTL, disk persistence
│       ├── youtube.py       # YouTube Data API v3 client
│       ├── ai.py            # Claude CLI warm subprocess session
│       ├── vkvideo.py       # VK Video API client
│       └── news.py          # News API client
├── frontend/
│   ├── index.html
│   ├── app.js               # Category picker, filter panel, grid render
│   └── style.css
├── deploy/
│   ├── setup.sh             # VPS one-command setup script
│   ├── stumblefeed.service  # systemd unit file
│   └── Caddyfile            # Caddy reverse proxy config
├── tests/
│   └── test_pool.py
└── requirements.txt
```

---

## Running Locally

### Prerequisites

- Python 3.11+
- YouTube Data API v3 key — [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → YouTube Data API v3
- News API key — [newsapi.org](https://newsapi.org/)

### Setup

```bash
git clone https://github.com/pigeoncorner/personafeed.git
cd personafeed

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env`:

```env
YOUTUBE_API_KEY=your_youtube_key
NEWS_API_KEY=your_newsapi_key
VK_ACCESS_TOKEN=          # optional — VK Video support
```

### Run

```bash
uvicorn backend.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000)

### Tests

```bash
pytest tests/
```

---

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/categories` | List all 20 categories |
| `POST` | `/grid` | Get curated video grid |
| `GET` | `/health` | Health check |

### POST /grid — request body

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

## AI Integration

StumbleFeed uses **Claude** (via [Claude Code](https://claude.ai/code) CLI) in a warm subprocess mode — a persistent `claude` process is kept alive between requests to avoid the 10–20 s cold-start overhead of spawning Node.js each time.

The AI layer does two things:

1. **Topic generation** — given a category and a random "angle" (hidden history, economics, cross-cultural connections, etc.), Claude invents a surprising narrow topic the user would never think to search for themselves
2. **Content curation** — given raw YouTube results, Claude ranks and filters for relevance, adding a one-sentence `why_relevant` explanation per video

The entire development of StumbleFeed was carried out using **Kodik IDE** (Claude Code).

---

## Deployment

### Frontend → Cloudflare Pages

Connect the `main` branch to Cloudflare Pages. No build step required — output directory: `frontend/`.

Automatic deploys on every push to `main`.

### Backend → VPS (Ubuntu)

```bash
git clone -b main https://github.com/pigeoncorner/personafeed.git /tmp/personafeed
bash /tmp/personafeed/deploy/setup.sh

nano /opt/stumblefeed/.env   # fill in API keys
systemctl start stumblefeed
systemctl status stumblefeed
```

Caddy handles reverse proxy and SSL (Let's Encrypt) automatically.

---

## Categories

| | | | |
|---|---|---|---|
| 🔬 Science & Math | 🏛️ History | 🎨 Art & Design | ⚙️ Technology |
| 💻 Software | 🌿 Nature | 🧠 Philosophy | 🍜 Food |
| 🎮 Games | 🎵 Music | 🩺 Health | 💼 Business |
| 🌍 Culture | 📚 Education | 📖 Literature | 🎬 Film & Series |
| ⚽ Sports | 🏡 Home & Garden | 🤪 Entertainment | ✈️ Travel |

---

## License

MIT
