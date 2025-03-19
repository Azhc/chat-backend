from fastapi import FastAPI, Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from exceptions.exception import (
    AuthException,
    LoginException,
    ModelValidatorException,
    PermissionException,
    ServiceException,
    ServiceWarning, 
)
from utils.response_util import  ResponseUtil
from starlette import status


def handle_exception(app: FastAPI):
    """
    全局异常处理
    """



    # 处理fastapi相关错误 例如404之类的
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            return ResponseUtil.not_found(msg="资源不存在")
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            return ResponseUtil.unauthorized()
        # 其他HTTP异常可统一处理或返回默认错误
        return ResponseUtil.error(msg=exc.detail)
    

    # 处理参数验证异常
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        error_details = []
        for error in errors:
            loc = ".".join(map(str, error['loc'])).replace("body.", "")
            msg = error['msg']
            error_details.append(f"{loc}: {msg}")
        print(error_details);
        return ResponseUtil.bad_request(msg="参数错误",data=error_details)

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
