from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.routers import feed

app = FastAPI(title="PersonaFeed")

app.include_router(feed.router)

# StaticFiles регистрируется после роутеров — иначе перекроет /feed и /personas
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


@app.get("/health")
async def health():
    return {"status": "ok"}
