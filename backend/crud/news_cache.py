from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from cache.news_cache import get_cached_categories, set_cached_categories, get_cached_news_list, set_cache_news_list
from models.news import Category, News
from schemas.base import NewsItemBase


#获取分类 - 分页查询 Category 表并返回列表
async def get_categories(db: AsyncSession,skip: int = 0, limit: int = 100, ):
    #先从缓存中获取数据- 写入缓存 - 返回数据
    cache_categories = await get_cached_categories()
    if cache_categories:
        return cache_categories

    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()
    if categories: #先把ORM格式转为字典，ORM转为Pydantic，再转为字典,by_alias,不使用别名
        categories = [NewsItemBase.model_validate(item)
                      .model_dump(mode="json",by_alias=False) for item in categories]
        await set_cached_categories(categories)

    return categories

#获取新闻列表 - 按 category_id 分页查询 News
async def get_news_list(db: AsyncSession,category_id:int, skip: int = 0, limit: int = 10, ):
    #从缓存获取新闻列表
    cache_categories_list = await get_cached_news_list(category_id, skip//limit + 1, limit)
    if cache_categories_list: #返回ORM格式
        return [News(**item)for item in cache_categories_list]

    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    cache_categories_list= result.scalars().all()
    if cache_categories_list:
        cache_categories_list = jsonable_encoder(cache_categories_list)
        await set_cache_news_list(category_id,skip//limit + 1,limit, cache_categories_list)
    return cache_categories_list

#获取新闻总数 - 统计指定分类下的新闻数量
async def get_news_count(db: AsyncSession,category_id:int ):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()

#获取新闻详情 - 按 id 查询单条新闻或返回 None
async def get_news_detail(db: AsyncSession, news_id:int):
    stmt = select(News).where( News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

#增加新闻阅读量 - 执行 update 并返回是否命中行
async def increase_news_view(db: AsyncSession, news_id:int):
    stmt = update(News).where(News.id == news_id).values(views=News.views+ 1)
    result = await db.execute(stmt)
    await db.commit()
    #数据库更新操作 检查数据库是否命中了数据 命中返回True
    return result.rowcount > 0

#获取相关推荐 - 同分类排除自身，按 views/publish_time 排序返回简化信息
async def get_related_news(db: AsyncSession, category_id:int, news_id:int,limit: int = 5):
    #order_by排序
    stmt = select(News).where(
        News.category_id==category_id,
        News.id!=news_id
    ).order_by(
        News.views.desc(), #默认降序，desc表示降序
        News.publish_time.desc()
    ).limit(limit)
    result = await db.execute(stmt)
    # return result.scalars().all()
    related_news = result.scalars().all()
    #列表推导式 ,推导列表核心数据，在return
    return  [{"id":news_detail.id,
            "title":  news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publish_time": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,}for news_detail in related_news]



