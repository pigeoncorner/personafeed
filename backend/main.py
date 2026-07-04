import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.categories import CATEGORIES
from backend.routers import feed
from backend.services import pool as pool_service

logger = logging.getLogger(__name__)

_REFRESH_INTERVAL = 3600  # check every hour


async def _background_refresher():
    categories = list(CATEGORIES.values())
    while True:
        try:
            await asyncio.to_thread(pool_service.refresh_stale, categories)
        except Exception as exc:
            logger.warning("Background pool refresh error: %s", exc)
        await asyncio.sleep(_REFRESH_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool_service.load_from_disk()
    task = asyncio.create_task(_background_refresher())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="PersonaFeed", lifespan=lifespan)

app.include_router(feed.router)

# StaticFiles регистрируется после роутеров — иначе перекроет /grid и /categories
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


@app.get("/health")
async def health():
    return {"status": "ok"}
