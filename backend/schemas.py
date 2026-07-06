from pydantic import BaseModel


class GridRequest(BaseModel):
    categories: list[str]
    limit: int = 40
    source: str = "youtube"


class VideoItem(BaseModel):
    video_id: str = ""
    title: str
    channel: str
    url: str
    thumbnail: str
    duration: int = 0
    views: int = 0
    published_at: str = ""
    why_relevant: str = ""
    category_id: str = ""
    category_label: str = ""
    source: str = "youtube"
    embed_url: str = ""


class GridResponse(BaseModel):
    items: list[VideoItem]
