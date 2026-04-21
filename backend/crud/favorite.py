from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News


#检查当前用户是否收藏了新闻 - 查询 Favorite 表判断是否存在
async def is_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    stmt = select(Favorite).where(
        Favorite.user_id == user_id,
         Favorite.news_id == news_id,)
    result = await db.execute(stmt)
    return result.scalars().one_or_none() is not None

#添加收藏 - 插入 Favorite 记录并返回新对象
async def add_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

#删除收藏 - 根据 user_id 和 news_id 删除记录并返回是否删除成功
async def remove_news_favorite(
        news_id: int,
        user_id: int,
        db : AsyncSession
):
    stmt = delete(Favorite).where(
        Favorite.user_id == user_id,
        Favorite.news_id == news_id
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount>0


async def get_favorite_list(
        user_id: int,
        db: AsyncSession,
        page: int = 1 ,
        page_size: int = 10
):
    #总量 + 收藏的新闻列表
    count_query = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalars().all()

    #联表join（字段别名）+收藏时间排序 + 分页

    #新闻对象，收藏时间，收藏id]
    query = (select(News,Favorite.created_at.label("favorite_time"),
                   Favorite.id.label("favorite_id"))
             .join(Favorite,Favorite.news_id== News.id)
             .where(Favorite.user_id == user_id )
             .order_by(Favorite.created_at.desc())
             .offset((page-1)*page_size).limit(page_size))
    result = await db.execute(query)
    rows = result.scalars().all()
    return rows,total

#清空当前用户所有收藏 - 执行 delete 并返回受影响行数
async def clear_favorite_list(user_id: int, db: AsyncSession):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0

