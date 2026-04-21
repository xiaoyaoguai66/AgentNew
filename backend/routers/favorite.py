from fastapi import APIRouter, Query, HTTPException
from fastapi.params import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from starlette import status

from config.db_conf import get_db
from crud import favorite
from crud.favorite import clear_favorite_list
from models.users import User
from schemas.favorite import FavoriteCheck, FavoriteAddRequest, FavoritelistRequest

from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/favorite", tags=["favorite"])


#检查新闻是否被当前用户收藏 - 通过 token 获取用户并检查收藏状态
@router.get("/check")
async def check_favorite(
        news_id:int = Query(...,alias="newsId"),
        user : User = Depends(get_current_user),
        db : AsyncSession = Depends(get_db)
):
    is_favorite = await favorite.is_news_favorite(db,user.id,news_id)

    return success_response(message="检查收藏状态成功", data=FavoriteCheck(isFavorite=is_favorite))


class Favorite:
    pass


#添加收藏 - 验证 token - 调用 crud 添加收藏并返回结果
@router.post("/add")
async def add_favorite(
        data : FavoriteAddRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await favorite.add_news_favorite(db, user.id, data.news_id)

    return  success_response(message="添加收藏成功", data=result)

#删除收藏 - 通过 newsId 与 用户ID 删除对应记录 - 返回删除结果或 404
@router.delete("/remove")
async def remove_favorite(
        news_id:int = Query(...,alias="newsId"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await favorite.remove_news_favorite(news_id,user.id,db)
    if  not result:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="收藏记录不存在")
    else:
        return success_response(message="删除收藏成功")

#获取收藏列表 - 验证 token - 分页返回收藏列表/总数/是否还有更多
@router.get("/list")
async def get_favorite_list (
        user : User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
        page: int = Query(1, ge = 1),
        page_size: int = Query(10, ge = 1,le = 100,alias="pageSize")
):
    rows , total = await favorite.get_favorite_list(user.id, db,page, page_size)
    favorite_list = [{
        **news.__dict__,
        "favorite_time": favorite_time,
        "favorite_id" : favorite_id
    }for news,favorite_time,favorite_id in rows]
    has_more = total > page * page_size

    data = FavoritelistRequest(list=favorite_list,total=total,hasMore=has_more)
    return success_response(message="获取收藏列表成功", data=data)

#清空收藏 - 验证 token - 调用 crud 清空并返回清空数量
@router.delete("/clear")
async def clear_favorite(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    count =  await clear_favorite_list(user.id,db)
    return success_response(message=f"清空了{count}条收藏成功")