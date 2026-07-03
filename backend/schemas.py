from pydantic import BaseModel


class FeedRequest(BaseModel):
    category: str
    language: str = "ru"


class SurpriseRequest(BaseModel):
    categories: list[str]
    language: str = "ru"


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


class NewsItem(BaseModel):
    title: str
    source: str
    url: str
    published_at: str
    why_relevant: str = ""


class FeedResponse(BaseModel):
    category_id: str
    category_label: str
    topic: str
    intro: str
    youtube: list[VideoItem]
    news: list[NewsItem]
    searches: list[str]
    cached: bool
