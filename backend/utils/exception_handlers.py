from fastapi import HTTPException
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from utils.exception import http_exception_handler, integrity_error_handler, sqlalchemy_error_handler


def register_exception_handlers(app):
    #注册全局异常处理器 - 先注册更具体的异常再注册基类异常
    """
    注册全局异常,子类在前，父类在后；具体在前，抽象在后
    :param app:
    :return:
    """


    app.add_exception_handler(HTTPException, http_exception_handler)  #业务层报错
    app.add_exception_handler(IntegrityError, integrity_error_handler)  #数据库完整性错误
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)  #数据库其他错误
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)  #请求参数验证
