from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime,timedelta
from utils.http_client import HttpClient
from utils.response_util import ResponseUtil
from modules.models.auth_model import *
from config.env import SsoConfig,JwtConfig
from modules.service.auth_service import AuthService
import uuid, base64

AuthController = APIRouter(prefix='/auth')



# 获取用户中心token的认证token
auth_token = f"Basic {base64.b64encode(f'{SsoConfig.client_id}:{SsoConfig.client_secret}'.encode()).decode()}"
# 用户中心链接
userCenter_Client = HttpClient(base_url=SsoConfig.sso_url + "/SCPG")


# 前端返回授权码 调用用户中心接口 获取用户信息 并且返回用户token
@AuthController.get("/getUserByCode", response_model=GetUserByCodeModel)
async def getUserByCode(code: str):
    """
    通过用户中心获取用户信息
    """

    # # 获取token
    # token_data = {
    #     "grant_type": "authorization_code",
    #     "code": code,
    #     "redirect_uri": SsoConfig.redirect_url,
    # }

    # token_response = await userCenter_Client.async_post(
    #     endpoint="/oauth2/token",
    #     content_type="form",
    #     data=token_data,
    #     headers={"Authorization": auth_token},
    # )
    # print(f"请求用户中心token结果：{token_response}");
    # # 检查token响应状态
    # access_token = token_response.get("data", {}).get("access_token")
    # if token_response.get("success", False) is not True or not access_token:
    #     print(token_response)
    #     return ResponseUtil.error(msg="获取用户中心token失败")

    # # 获取用户账号
    # user_response = await userCenter_Client.async_get(
    #     endpoint="/userinfo", headers={"Authorization": f"Bearer {access_token}"}
    # )

    # username = user_response.get("data", {}).get("sub")
    # print(f"获取用户信息结果：{user_response}");
    # print(f"用户名称：{username}")
    # if user_response.get("success", False) is not True or not username:
    #     print(user_response)
    #     return ResponseUtil.error(msg="获取用户信息失败")

    # # username = 'c-renyw01'
    # # jwt生成包含用户ID的token
    # access_token = await AuthService.create_access_token(
    #     data={
    #         "user_id": str(username)
    #     },
    #     expires_delta= timedelta(minutes=JwtConfig.jwt_expire_minutes),
    # )

    print(code)

    # 返回token
    return ResponseUtil.success(data={"token": auth_token})
