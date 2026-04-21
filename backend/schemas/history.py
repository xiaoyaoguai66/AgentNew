from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


class HistoryAddRequest(BaseModel):
    # 添加历史请求 - 只需传入 newsId
    news_id: int = Field(..., alias="newsId")


class HistoryNewsItemResponse(NewsItemBase):
    # 浏览历史列表项 - 包含 historyId 与 viewTime
    history_id: int = Field(alias="historyId")
    view_time: datetime = Field(alias="viewTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True)


class HistoryListResponse(BaseModel):
    list: list[HistoryNewsItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )