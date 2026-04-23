from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud import history
from models.users import User
from schemas.history import HistoryAddRequest, HistoryListResponse, HistoryNewsItemResponse
from utils.auth import get_current_user
from utils.response import success_response


router = APIRouter(prefix="/api/history", tags=["history"])


@router.post("/add")
async def add_history(
    data: HistoryAddRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await history.add_history_list(data.news_id, db, user.id)
    return success_response(
        message="添加历史成功",
        data={
            "id": result.id,
            "newsId": result.news_id,
            "viewTime": result.view_time,
        },
    )


@router.get("/list")
async def get_history_list(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"),
):
    rows, total = await history.get_history_list_total(user.id, db, page, page_size)
    history_list = [
        HistoryNewsItemResponse.model_validate(
            {
                **news_item.__dict__,
                "viewTime": view_time,
                "history_id": history_id,
            }
        )
        for news_item, view_time, history_id in rows
    ]
    has_more = total > page * page_size
    data = HistoryListResponse(list=history_list, total=total, hasMore=has_more)
    return success_response(message="获取历史列表成功", data=data)


@router.delete("/delete/{history_id}")
async def delete_history(
    history_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await history.delete_history(user.id, db, history_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="历史记录不存在")
    return success_response(message="删除成功")


@router.delete("/clear")
async def clear_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await history.clear_history(user.id, db)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="没有历史记录可清空")
    return success_response(message="清空历史成功")
