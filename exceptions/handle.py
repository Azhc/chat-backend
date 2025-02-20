from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from exceptions.exception import (
    AuthException,
    LoginException,
    ModelValidatorException,
    PermissionException,
    ServiceException,
    ServiceWarning,
)
from utils.response_util import  ResponseUtil


def handle_exception(app: FastAPI):
    """
    全局异常处理
    """

    # 自定义token检验异常
    @app.exception_handler(AuthException)
    async def auth_exception_handler(request: Request, exc: AuthException):
        return ResponseUtil.unauthorized(data=exc.data, msg=exc.message)

    # 自定义登录检验异常
    @app.exception_handler(LoginException)
    async def login_exception_handler(request: Request, exc: LoginException):
        return ResponseUtil.failure(data=exc.data, msg=exc.message)

    # 自定义模型检验异常
    @app.exception_handler(ModelValidatorException)
    async def model_validator_exception_handler(request: Request, exc: ModelValidatorException):
        return ResponseUtil.failure(data=exc.data, msg=exc.message)


    # 自定义权限检验异常
    @app.exception_handler(PermissionException)
    async def permission_exception_handler(request: Request, exc: PermissionException):
        return ResponseUtil.forbidden(data=exc.data, msg=exc.message)

    # 自定义服务异常
    @app.exception_handler(ServiceException)
    async def service_exception_handler(request: Request, exc: ServiceException):
        return ResponseUtil.error(data=exc.data, msg=exc.message)

    # 自定义服务警告
    @app.exception_handler(ServiceWarning)
    async def service_warning_handler(request: Request, exc: ServiceWarning):
        return ResponseUtil.failure(data=exc.data, msg=exc.message)


    # 处理其他异常
    @app.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        return ResponseUtil.error(msg=str(exc))
