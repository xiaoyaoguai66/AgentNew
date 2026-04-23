from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News


async def add_history_list(
    news_id: int,
    db: AsyncSession,
    user_id: int,
):
    query = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(query)
    existing_history = result.scalars().first()
    if existing_history:
        existing_history.view_time = datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history

    history = History(news_id=news_id, user_id=user_id)
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history


async def get_history_list_total(
    user_id: int,
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
):
    count_query = select(func.count()).select_from(History).where(History.user_id == user_id)
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
    user_id: int,
    db: AsyncSession,
    history_id: int,
):
    stmt = delete(History).where(History.id == history_id, History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def clear_history(
    user_id: int,
    db: AsyncSession,
):
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0
