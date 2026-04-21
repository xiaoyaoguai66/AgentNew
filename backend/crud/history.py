from datetime import datetime

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News
from models.users import User

async def add_history_list(
        news_id: int,
        db : AsyncSession ,
        user_id : int
):
    # 添加或更新浏览历史 - 若存在则更新时间，否则插入新记录并返回
    query  = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(query)
    existing_history = result.scalars().first()
    if existing_history :
        existing_history.view_time = datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    else:
        history = History(news_id=news_id, user_id=user_id)
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history


async def get_history_list_total(
        user_id : int,
        db : AsyncSession,
        page : int = 1,
        page_size: int = 10
):
    # 查询历史总数并联表查询对应新闻 - 返回 rows 与 total
    count_query = select(func.count()).where(History.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()
    query = (
        select(News, History.view_time.label("view_time"), History.id.label("history_id"))
        .join(History, History.news_id == News.id)
        .where(History.user_id == user_id)
        .order_by(History.view_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    rows = result.all()
    return rows, total

async def delete_history(
        user_id : int,
        db : AsyncSession,
        news_id : int
):
    # 删除历史记录 - 根据 history id（注意路由中传入的应为 history id）和 user_id 删除
    stmt = delete(History).where(History.news_id == news_id,
                                 History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0

async def clear_history(
        user_id : int,
        db : AsyncSession,
):
    # 清空某用户的所有历史记录并返回受影响的行数
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()

    return result.rowcount or 0
