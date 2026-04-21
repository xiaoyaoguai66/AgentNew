from typing import Any

import  redis.asyncio as redis
import json
from pathlib import Path
from uuid import uuid4
from time import time

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
DEBUG_LOG_PATH = Path(r"d:\Code\Fastapi\AgentNews\debug-3edf5d.log")
DEBUG_SESSION_ID = "3edf5d"


def _debug_log(run_id: str, hypothesis_id: str, location: str, message: str, data: dict):
    payload = {
        "sessionId": DEBUG_SESSION_ID,
        "id": f"log_{uuid4().hex}",
        "timestamp": int(time() * 1000),
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
    }
    with DEBUG_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

#创建Redis的连接对象
redis_client = redis.Redis(
    host=REDIS_HOST,   #Redis服务器主机地址
    port=REDIS_PORT,   #端口号
    db=REDIS_DB,       #数据库编号 0-15
    decode_responses=True  #是否将Redis返回的字节数据解码为字符串
)

# 设置缓存和 读取缓存（字符串 和 列表或字典）
#读取缓存： 读字符串
async def get_cache(key:str):
    # return await redis_client.get(key)
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败：{e}")
        return None


#读取： 列表或字典
async def get_json_cache(key:str):
    try:
        # region agent log
        _debug_log(
            run_id="post-fix",
            hypothesis_id="H4",
            location="backend/config/cache_conf.py:get_json_cache",
            message="Entering get_json_cache",
            data={"key": key},
        )
        # endregion
        data = await redis_client.get(key)
        if data:
            # region agent log
            _debug_log(
                run_id="post-fix",
                hypothesis_id="H4",
                location="backend/config/cache_conf.py:get_json_cache",
                message="Cache hit before json.loads",
                data={"key": key, "data_type": str(type(data))},
            )
            # endregion
            return json.loads(data)
        return None
    except Exception as e:
        print(f"获取json缓存失败：{e}")
        return None


#设置缓存 setex(key,expire,value)
async def set_cache(key:str, value: Any, expire:int = 3600,):
    try:
        # region agent log
        _debug_log(
            run_id="post-fix",
            hypothesis_id="H1-H3",
            location="backend/config/cache_conf.py:set_cache",
            message="Entering set_cache",
            data={
                "key": key,
                "expire": expire,
                "value_type": str(type(value)),
                "json_module": str(json),
                "json_has_dumps": hasattr(json, "dumps"),
            },
        )
        # endregion
        if isinstance(value,(dict,list)): #转字符串
            # region agent log
            _debug_log(
                run_id="post-fix",
                hypothesis_id="H1-H2",
                location="backend/config/cache_conf.py:set_cache",
                message="Serializing value in set_cache",
                data={
                    "key": key,
                    "value_type": str(type(value)),
                    "ensure_ascii_arg_name": "ensure_ascil",
                },
            )
            # endregion
            value = json.dumps(value, ensure_ascii=False)  #将列表或字典转换为JSON字符串
        await redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        # region agent log
        _debug_log(
            run_id="post-fix",
            hypothesis_id="H1-H4",
            location="backend/config/cache_conf.py:set_cache",
            message="set_cache exception",
            data={"key": key, "error": repr(e), "error_type": type(e).__name__},
        )
        # endregion
        print(f"设置缓存失败：{e}")
        return False

        

