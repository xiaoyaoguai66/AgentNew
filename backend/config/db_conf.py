from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession

ASYNC_DATABASE_URL = "mysql+aiomysql://root:LJBljb0221@localhost:3306/news_app?charset=utf8"
#创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20,
)
#创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession)

#依赖项
async def get_db():
    #数据库会话依赖 - 提供 AsyncSession 并在请求结束时提交/回滚
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
