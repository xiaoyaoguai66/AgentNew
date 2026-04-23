from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from services import news_service
from utils.response import success_response


router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/categories")
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    categories = await news_service.get_categories(db, skip, limit)
    return success_response(message="获取分类成功", data=categories)


@router.get("/list")
async def get_news(
    category_id: int = Query(..., alias="categoryId"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
    db: AsyncSession = Depends(get_db),
):
    news_page = await news_service.get_news_list(db, category_id, page, page_size)
    return success_response(message="获取新闻列表成功", data=news_page)


@router.get("/detail")
async def get_news_detail(
    news_id: int = Query(..., alias="id"),
    db: AsyncSession = Depends(get_db),
):
    news_detail = await news_service.get_news_detail(db, news_id)
    return success_response(message="获取新闻详情成功", data=news_detail)


@router.get("/hot")
async def get_hot_news(
    category_id: int | None = Query(None, alias="categoryId"),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    hot_news = await news_service.get_hot_news(db, category_id, limit)
    return success_response(message="获取热门新闻成功", data=hot_news)
