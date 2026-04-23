from pydantic import BaseModel, ConfigDict, Field

from schemas.base import NewsItemBase


class NewsListPageResponse(BaseModel):
    list: list[NewsItemBase]
    total: int
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class NewsDetailResponse(NewsItemBase):
    content: str
    related_news: list[NewsItemBase] = Field(default_factory=list, alias="relatedNews")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
