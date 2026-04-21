from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud.users import just_username, create_user, create_token, authenticate_user, update_user, change_password
from models.users import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest
from config.db_conf import get_db
from utils.response import success_response
from utils.auth import get_current_user

#创建APIRouter实例，设置前缀和标签
router = APIRouter(prefix="/api/user", tags=["users"])


@router.post("/register")
#用户注册 - 检查用户名 -> 创建用户 -> 生成 token 并返回认证信息
async def register(
        user_data : UserRequest,
        db : AsyncSession = Depends(get_db),

):
    #注册逻辑，验证用户是否存在，-创建用户 - 生成Token - 相应
    if await just_username(db,user_data.username) :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    else:
        user = await create_user(db, user_data)
        #生成token
        token = await  create_token(db,user.id)
        # return {
        #     "code": 200,
        #     "msg": "注册成功",
        #     "data": {
        #         "token": token,
        #         "userInfo": {
        #             "id": user.id,
        #             "username": user.username,
        #             "bio": user.bio,
        #             "avatar": user.avatar,
        #         }
        #     }
        #
        # }
        # 使用 model_validate 构造，避免静态分析对字段别名的误报
        response_data = UserAuthResponse.model_validate({"token": token, "userInfo": UserInfoResponse.model_validate(user)})
        return success_response(message="注册成功",data=response_data)


@router.post("/login")
#用户登录 - 验证用户名密码 -> 生成 token 并返回用户信息
async def login(login_data : UserRequest, db : AsyncSession = Depends(get_db)):
    user =await authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    token = await create_token(db,user.id)
    response_data = UserAuthResponse.model_validate({"token": token, "userInfo": UserInfoResponse.model_validate(user)})
    return success_response(message="登录成功", data=response_data)


#检查 Authorization token 并返回当前用户信息 - 使用 get_current_user 依赖解析 token 并封装为 UserInfoResponse 返回
@router.get("/info")
#获取当前用户信息 - 通过 get_current_user 依赖注入 token 校验
async def get_user_info(user:User = Depends(get_current_user)):

    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))

#修改用户信息，验证token - 更新（用户输入） - 结果返回
#参数 ： 用户输入的 + 验证token + db(修改）
@router.put("/update")
#更新用户信息 - 验证 token -> 更新指定字段并返回新信息
async def update_user_info(
    user_data : UserUpdateRequest,
    user:User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db),
):
    user =await update_user(db,user.username,user_data)
    return success_response(message="更新用户信息成功", data=UserInfoResponse.model_validate(user))

@router.put("/password")
#修改密码 - 验证旧密码 -> 更新为新密码并返回用户信息
async def update_password(
    password_data:UserChangePasswordRequest,
    user:User = Depends(get_current_user),
    db : AsyncSession = Depends(get_db),

):
    user =await change_password(db, user, password_data.old_password, password_data.new_password)
    return success_response(message="修改密码成功", data=UserInfoResponse.model_validate(user))