import jwt
import random
import uuid
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta, timezone
from config.env import JwtConfig
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status,Request
from utils.response_util import ResponseUtil
from jwt.exceptions import InvalidTokenError
from exceptions.exception import AuthException
from utils.http_client import HttpClient
from config.env import SsoConfig


# OAuth2 方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/getUserByCode")


# 用户中心
userCenter_Client = HttpClient(base_url=SsoConfig.sso_url+'/ipmp-cloud/auth/v1/admin/realm/SCPG')


class AuthService():
    """
    认证模块服务层
    """


    @classmethod
    async def create_access_token(cls,data: dict, expires_delta: Union[timedelta, None] = None):
        """
        根据登录信息创建当前用户token

        :param data: 登录信息
        :param expires_delta: token有效期
        :return: token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=JwtConfig.jwt_expire_minutes)
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, JwtConfig.jwt_secret_key, algorithm=JwtConfig.jwt_algorithm)
        return encoded_jwt
    

    async def get_current_user(request: Request = Request,token: str = Depends(oauth2_scheme)):
        """
        校验token
        """
        try:
            
            if token.startswith('Bearer'):
                token = token.split(' ')[1]
            try:
                # 调用用户中心获取用户信息接口设置用户信息
                user_response = await userCenter_Client.async_get(
                    endpoint="/current-user", headers={"Authorization": f"Bearer {token}"}
                )
            except Exception as e:
                print(f"用户中心请求异常: {str(e)}")
                raise AuthException(message="用户服务暂不可用")
            
            # 业务状态校验
            if not user_response.get("success") or not user_response.get("data", {}).get("success",False):
                error_msg = user_response.get("error", "未返回错误信息")
                print(f"业务逻辑失败: {error_msg} | 完整响应: {user_response}")
                raise AuthException(message="用户信息验证未通过")

            # 用户数据提取
            user_data = user_response.get('data',{}).get('data',{})
            if not isinstance(user_data, dict) or not user_data.get("userName"):
                print(f"用户数据缺失关键字段: {user_data}")
                raise AuthException(message="用户信息不完整")
            
            user_id = user_data.get('userName','');
            
            print(user_id);
            return user_id

        except InvalidTokenError:
            raise AuthException(data='', message='用户登陆已失效')

    
