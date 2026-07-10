from pydantic import BaseModel


class GridFilters(BaseModel):
    period_days: int | None = None
    views_min: int | None = None
    views_max: int | None = None
    comments_min: int | None = None
    engagement_min: float | None = None
    duration_min: int | None = None
    duration_max: int | None = None
    exclude_shorts: bool = False
    subscribers_min: int | None = None
    subscribers_max: int | None = None
    channel_age_max_days: int | None = None
    viral_ratio_min: float | None = None


class GridRequest(BaseModel):
    categories: list[str]
    limit: int = 40
    source: str = "youtube"
    filters: GridFilters | None = None
    sort: str = "random"


class VideoItem(BaseModel):
    video_id: str = ""
    title: str
    channel: str
    url: str
    thumbnail: str
    duration: int = 0
    views: int = 0
    likes: int = 0
    comments: int = 0
    published_at: str = ""
    channel_id: str = ""
    channel_subscribers: int = 0
    channel_published_at: str = ""
    why_relevant: str = ""
    category_id: str = ""
    category_label: str = ""
    source: str = "youtube"
    embed_url: str = ""


class GridResponse(BaseModel):
    items: list[VideoItem]
