from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import join
from starlette import status

from config.db_conf import get_db
from crud import history

from models.history import History

from models.users import User

from schemas.history import HistoryAddRequest, HistoryListResponse, HistoryNewsItemResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])

@router.post("/add")
#添加浏览历史 - 验证 token -> 插入或更新 History 记录 -> 返回新增/更新的历史项
async def add_history(
        data : HistoryAddRequest,
        db : AsyncSession = Depends(get_db),
        user : User = Depends(get_current_user)
):
    result = await history.add_history_list(data.news_id, db, user.id)

    return success_response(message="添加历史成功",data=result)


@router.get("/list")
#获取浏览历史列表 - 验证 token -> 分页查询关联新闻和浏览时间 -> 返回列表和总数
async def get_history_list(
        user : User = Depends(get_current_user),
        db : AsyncSession = Depends(get_db),
        page : int = Query(1,ge = 1),
        page_size: int = Query(10,ge = 1,le=100,alias="pageSize")
):
    rows, total = await history.get_history_list_total(user.id, db, page, page_size)
    history_list = [HistoryNewsItemResponse.model_validate({
        **news.__dict__,
        "viewTime": view_time,
        "history_id": history_id
    } )for news, view_time, history_id in rows]
    has_More = total > page * page_size
    data = HistoryListResponse(list=history_list,total=total,hasMore=has_More)
    return success_response(message="获取历史列表成功",data=data)

@router.delete("/delete/{history_id}")
#删除单条历史 - 验证 token -> 按 history id 删除 -> 返回删除结果或 404
async def delete_history(
        history_id: int,
        db : AsyncSession = Depends(get_db),
        user : User = Depends(get_current_user)
):
    result = await history.delete_history(user.id, db, history_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="历史记录不存在")

    return success_response(message="删除成功")

@router.delete("/clear")
#清空用户历史 - 验证 token -> 删除该用户所有历史记录 -> 返回删除数量
async def clear_history(
        user : User = Depends(get_current_user),
        db : AsyncSession = Depends(get_db)
):
    result = await history.clear_history(user.id, db)
    if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="没有历史记录可清空")
    return success_response(message="清空历史成功")

