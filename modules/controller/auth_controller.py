from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime, timedelta
from utils.http_client import HttpClient
from utils.response_util import ResponseUtil
from modules.models.auth_model import *
from config.env import SsoConfig, JwtConfig, WorkWechatConfig
from modules.service.auth_service import AuthService
import uuid, base64
from exceptions.exception import ServiceException

AuthController = APIRouter(prefix="/auth")


# 初始化企微API客户端
work_wechat_client = HttpClient(base_url=WorkWechatConfig.work_wechat_url)

# 用户中心链接
userCenter_Client = HttpClient(base_url=SsoConfig.user_center_get_user_url + "/SCPG")


# 前端返回授权码 调用用户中心接口 获取用户信息 并且返回用户token
@AuthController.get(
    "/getUserByCode",
    response_model=GetUserByCodeModel,
    description="根据授权码获取用户信息",
)
async def getUserByCode(code: str):
    """
    根据企微Code获取用户信息
    """
    """根据企微Code获取用户信息并生成系统令牌"""
    try:
        # 1. 获取企业微信访问令牌
        token_params = {
            "appId": WorkWechatConfig.work_wechat_appid,
            "secret": WorkWechatConfig.work_wechat_secret,
        }
        token_response = await work_wechat_client.async_get(
            endpoint="/token/get-token", params=token_params
        )
        if not token_response.get("success", False):
            raise ServiceException(message="请求企微token接口失败")

        token_data = token_response.get("data")

        if not token_data.get("success", False):
            raise ServiceException(message=token_data.get("errmsg", "企微令牌获取失败"))

        access_token = token_data.get("data", {}).get("token", "")

        # 2. 获取用户LdapID
        user_info_params = {"access_token": access_token, "code": code}
        user_info_response = await work_wechat_client.async_get(
            endpoint="/cgi-bin/auth/getuserinfo", params=user_info_params
        )
        if not user_info_response.get("success", False):
            raise ServiceException(message="请求企微用户接口失败")
        user_info_data = user_info_response.get("data")
        if user_info_data.get("errcode")!=0:
            raise ServiceException(message=user_info_data.get('errmsg','请求企微用户接口失败'))
        ldap_id = user_info_data.get("userid", "")
        if ldap_id is None or ldap_id == "":
            raise ServiceException(
                message=token_data.get("errmsg", "获取企微用户信息失败")
            )

        # 3. 调用资管接口获取用户信息
        user_center_params = {
            "queryType": "query:ext-attr",
            "key": "LDAP_ID",
            "value": ldap_id,
            "pageNum": 1,
            "pageSize": 1,
        }
        headers = {"realm": "SCPG", "targetAppId": "scpg-auth-service"}
        user_center_response = await userCenter_Client.async_get(
            endpoint="/users", params=user_center_params, headers=headers
        )
        if not user_center_response.get("success", False):
            print(user_center_response)
            raise ServiceException(message="用户中心接口请求失败")

        user_center_response_data = user_center_response.get("data")

        user_response_data = user_center_response_data.get("data")
        if not user_response_data:
            raise ServiceException(message="用户不存在")

        user_info = user_response_data[0]
        user_id = user_info.get("userName", "")
        if user_id is None or user_id == "":
            raise ServiceException(message="用户ID不存在")

        # 4.生成token
        # username = 'c-renyw01'
        # jwt生成包含用户ID的token
        token_data = await AuthService.create_access_token(
            data={"user_id": str(user_id)},
            expires_delta=timedelta(minutes=JwtConfig.jwt_expire_minutes),
        )

        return ResponseUtil.success(data={
            "token": token_data["access_token"],
            "expires_in": token_data["expires_in"],
            "expiration": token_data["expiration"]
        })

    except ServiceException as se:
        # 已知业务异常直接抛出
        raise
    except Exception as unhandled_ex:
        raise ServiceException(message="系统发生意外错误") from unhandled_ex
