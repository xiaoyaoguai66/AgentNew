from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import Category, News


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 100):
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10):
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_news_count(db: AsyncSession, category_id: int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()


async def get_news_detail(db: AsyncSession, news_id: int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def increase_news_view(db: AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def batch_increase_news_views(db: AsyncSession, view_deltas: dict[int, int]) -> int:
    updated_count = 0
    for news_id, delta in view_deltas.items():
        stmt = update(News).where(News.id == news_id).values(views=News.views + delta)
        result = await db.execute(stmt)
        updated_count += result.rowcount or 0
    return updated_count


async def get_related_news(db: AsyncSession, category_id: int, news_id: int, limit: int = 5):
    stmt = (
        select(News)
        .where(News.category_id == category_id, News.id != news_id)
        .order_by(News.views.desc(), News.publish_time.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_hot_news(
    db: AsyncSession,
    category_id: int | None = None,
    limit: int = 10,
):
    stmt = select(News)
    if category_id is not None:
        stmt = stmt.where(News.category_id == category_id)
    stmt = stmt.order_by(News.views.desc(), News.publish_time.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_news_by_ids(db: AsyncSession, news_ids: list[int]):
    if not news_ids:
        return []

    stmt = select(News).where(News.id.in_(news_ids))
    result = await db.execute(stmt)
    news_items = result.scalars().all()
    order_map = {news_id: index for index, news_id in enumerate(news_ids)}
    return sorted(news_items, key=lambda item: order_map.get(item.id, len(news_ids)))


async def get_news_candidates(
    db: AsyncSession,
    category_ids: list[int] | None = None,
    published_after: datetime | None = None,
    limit: int = 120,
):
    stmt = select(News)
    if category_ids:
        stmt = stmt.where(News.category_id.in_(category_ids))
    if published_after is not None:
        stmt = stmt.where(News.publish_time >= published_after)
    stmt = stmt.order_by(News.publish_time.desc(), News.views.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_news_for_indexing(
    db: AsyncSession,
    news_ids: list[int] | None = None,
    limit: int = 20,
):
    stmt = select(News)
    if news_ids:
        stmt = stmt.where(News.id.in_(news_ids))
    stmt = stmt.order_by(News.publish_time.desc(), News.id.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
