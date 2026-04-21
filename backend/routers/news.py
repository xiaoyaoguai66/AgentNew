from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import true, null
from sqlalchemy.ext.asyncio import AsyncSession

from crud import news
from crud import news_cache

from config.db_conf import get_db

#创建APIRouter实例，设置前缀和标签
router = APIRouter(prefix="/api/news", tags=["news"])

@router.get("/categories")
async def get_categories(skip: int = 0, limit: int = 100,db:AsyncSession=Depends(get_db)):
    categories = await news_cache.get_categories(db, skip, limit)
    return {
        "code":200,
        "msg":"获取分类成功",
        "data":categories
    }

@router.get("/list")
async def get_news(
        category_id:int = Query(...,alias="categoryId") ,
        db:AsyncSession=Depends(get_db),
        page: int = 1,
        page_size: int = Query(10, le=100, alias="pageSize"),
):
    #分析规则，查询新闻列表 计算总量，计算是否还有更多
    skip = (page - 1) * page_size
    total =await news.get_news_count(db,category_id)
    news_list = await news_cache.get_news_list(db,category_id, skip, page_size)
    han_more = (skip+page_size)<total
    return {
        "code":200,
        "message":"success",
        "data":{
            "list":news_list,
            "total": total,
            "hanMore": han_more
        },

    }


@router.get("/detail")
async def get_news_detail(db:AsyncSession = Depends(get_db),news_id:int = Query(...,alias="id")):
    news_detail = await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404,detail="新闻不存在")
    views_res = await news.increase_news_view(db, news_detail.id)
    if not views_res:
        raise HTTPException(status_code=404,detail="新闻不存在")
    related_news = await news.get_related_news(db, news_detail.category_id,news_detail.id)
    return {
        "code":200,
        "message":"success",
        "data":{
            "id":news_detail.id,
            "title":  news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publish_time": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news,
        }
    }