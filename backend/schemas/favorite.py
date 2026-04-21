from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from schemas.base import NewsItemBase


class FavoriteCheck(BaseModel):
    # 检查收藏状态响应 - isFavorite 布尔
    is_favorite: bool = Field(..., alias="isFavorite")



class FavoriteAddRequest(BaseModel):
    # 添加收藏请求 - 传入 newsId
    news_id: int = Field(..., alias="newsId")

#规划两个类，新闻模型类+收藏的模型类
class FavoriteNewsItemResponse(NewsItemBase):
    # 收藏列表项 - 包含 favoriteId 与 favoriteTime
    favorite_id: int = Field(..., alias="favoriteId")
    favorite_time: datetime= Field(..., alias="favoriteTime")
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


#收藏列表
class FavoritelistRequest(BaseModel):
    list:list[FavoriteNewsItemResponse]
    total: int
    has_more: bool = Field(..., alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
