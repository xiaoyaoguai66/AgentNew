from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder



def success_response(
        message:str = "success",
        data = None,
        status_code: int = 200,
):
    # 统一成功响应 - 固定 code=200，支持自定义 HTTP status_code 与 data
    content = {
        "code": 200,
        "message":message,
        "data":data
    }
    return JSONResponse(jsonable_encoder(content), status_code=status_code)
