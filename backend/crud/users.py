import uuid
from datetime import timedelta,datetime
from fastapi import HTTPException

from models.users import User,UserToken
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from utils import  security
from schemas.users import UserRequest, UserUpdateRequest
from utils.security import verify_password


#检查用户名是否存在 - select 返回单个用户或 None
async def just_username(db:AsyncSession ,username : str):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

#创建用户 - 密码加密后写入数据库并返回新用户
async def create_user(db:AsyncSession ,user_data : UserRequest):
    #密码加密
    hashed_password = security.get_password_hash(user_data.password)
    user = User(username=user_data.username,password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user) #从数据库读回最新的user
    return user


#生成并存储 token - 随机 token + 设置过期时间 - 存在则更新否则插入
async def create_token(db:AsyncSession ,user_id : int):
    #生成随机token字符串+设置过期时间，默认7天,查询数据库是否有token
    token = str(uuid.uuid4())
    expire_at = datetime.now() + timedelta(days=7)
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()
    if  user_token:
        user_token.token = token
        user_token.expire_at = expire_at
        await db.commit()
        await db.refresh(user_token)
    else:
        user_token = UserToken(user_id = user_id,token=token,expires_at=expire_at)
        db.add(user_token)
        await db.commit()
        await db.refresh(user_token)
    return token

#认证用户 - 通过用户名查找并校验密码
async def authenticate_user(db:AsyncSession ,username : str,password: str):
    user = await just_username(db,username)
    if not user:
        return None
    if not security.verify_password(password,user.password):
        return None
    return user

#根据 token 查询用户 - 验证 token 有效性并返回对应用户
async def get_user_by_token(db:AsyncSession ,token : str):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()
    if not db_token or db_token.expires_at < datetime.now():
        return None
    query = select(User).where(User.id == db_token.user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    return user

#更新用户信息 - 根据 username 更新指定字段并返回更新后的用户
async def update_user(db:AsyncSession ,username:str, user_data : UserUpdateRequest):
    #将Pydantic模型转换为字典，并过滤掉值为None的字段
    stmt = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True,
        exclude_none=True,
    ))
    result = await db.execute(stmt)
    await db.commit()
    #查询更新后的用户信息
    if result.rowcount == 0:

        raise HTTPException(status_code=404, detail="用户不存在")
    #获取更新后的信息
    updated_user = await just_username(db,username)
    return updated_user

#修改用户密码 - 校验旧密码 - 哈希新密码并更新返回用户
async def change_password(db:AsyncSession ,user:User, old_password:str,new_password:str):
    if not verify_password(old_password,user.password):
        raise HTTPException(status_code=400, detail="旧密码错误")
    hashed_password = security.get_password_hash(new_password)
    stmt = update(User).where(User.username == user.username).values(password=hashed_password)
    result = await db.execute(stmt)
    #更新 ：由SQLAlchemy执行更新操作，提交事务，查询更新后的用户信息并返回
    db.add(user)
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")
    updated_user = await just_username(db,user.username)
    return updated_user





