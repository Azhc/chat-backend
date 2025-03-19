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
    async def create_access_token(cls, data: dict, expires_delta: Union[timedelta, None] = None):
        """
        根据登录信息创建当前用户Token及有效期
        :returns: 包含access_token、expires_in和expiration的字典
        """
        to_encode = data.copy()
        current_time = datetime.now(timezone.utc)
        
        # 计算过期时间
        if expires_delta:
            expire = current_time + expires_delta
        else:
            expire = current_time + timedelta(minutes=JwtConfig.jwt_expire_minutes)
        
        # 生成Token
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            JwtConfig.jwt_secret_key, 
            algorithm=JwtConfig.jwt_algorithm
        )
        
        # 计算有效期秒数
        expires_in = int((expire - current_time).total_seconds())
        
        # 生成ISO 8601格式时间字符串（保留毫秒）
        expiration_iso = expire.isoformat(timespec='milliseconds')
        
        return {
            "access_token": encoded_jwt,
            "expires_in": expires_in,
            "expiration": expiration_iso
        }

    # async def get_current_user(request: Request = Request,token: str = Depends(oauth2_scheme)):
    #     """
    #     校验token
    #     """
    #     try:
    #         if token.startswith('Bearer'):
    #             token = token.split(' ')[1]
    #         auth_type = request.headers.get("X-Auth-Type", "").strip()
    #         try:
    #             # 调用用户中心获取用户信息接口设置用户信息
    #             user_response = await userCenter_Client.async_get(
    #                 endpoint="/current-user", headers={"Authorization": f"Bearer {token}"}
    #             )
    #         except Exception as e:
    #             print(f"用户中心请求异常: {str(e)}")
    #             raise AuthException(message="用户服务暂不可用")
            
    #         # 业务状态校验
    #         if not user_response.get("success") or not user_response.get("data", {}).get("success",False):
    #             error_msg = user_response.get("error", "未返回错误信息")
    #             print(f"业务逻辑失败: {error_msg} | 完整响应: {user_response}")
    #             raise AuthException(message="用户信息验证未通过")

    #         # 用户数据提取
    #         user_data = user_response.get('data',{}).get('data',{})
    #         if not isinstance(user_data, dict) or not user_data.get("userName"):
    #             print(f"用户数据缺失关键字段: {user_data}")
    #             raise AuthException(message="用户信息不完整")
            
    #         user_id = user_data.get('userName','');
            
    #         print(user_id);
    #         return user_id

    #     except InvalidTokenError:
    #         raise AuthException(data='', message='用户登陆已失效')


    async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
        """
        校验token，支持企业微信和默认两种认证方式
        """
        try:
            # 统一去除Bearer前缀（无论是否存在）
            if token.startswith('Bearer '):
                token = token.split(' ')[1]

            auth_type = request.headers.get("X-Auth-Type", "").strip()

            if auth_type == "WorkWechat":
                # 企业微信认证逻辑
                try:
                    # 示例：解码JWT token（根据实际企业微信token结构调整）
                    payload = jwt.decode(
                        token,
                        JwtConfig.jwt_secret_key,  # 替换为实际密钥
                        algorithms=JwtConfig.jwt_algorithm
                    )
                    user_id = payload.get("user_id")  # 根据实际字段名调整
                    if not user_id:
                        raise InvalidTokenError("用户ID不存在")
                    return user_id
                except jwt.ExpiredSignatureError:
                    raise AuthException(message="token已过期")
                except jwt.InvalidTokenError:
                    raise AuthException(message="无效的token")
                except Exception as e:
                    print(f"token解析异常: {str(e)}")
                    raise AuthException(message="认证失败")
            else:
                # 默认认证逻辑（调用用户中心）
                try:
                    user_response = await userCenter_Client.async_get(
                        endpoint="/current-user",
                        headers={"Authorization": f"Bearer {token}"}
                    )
                except Exception as e:
                    print(f"用户中心请求异常: {str(e)}")
                    raise AuthException(message="用户服务暂不可用")

                # 业务状态校验
                if not user_response.get("success") or not user_response.get("data", {}).get("success", False):
                    error_msg = user_response.get("error", "未返回错误信息")
                    print(f"业务逻辑失败: {error_msg} | 完整响应: {user_response}")
                    raise AuthException(message="用户信息验证未通过")

                # 用户数据校验
                user_data = user_response.get('data', {}).get('data', {})
                if not isinstance(user_data, dict) or not user_data.get("userName"):
                    print(f"用户数据缺失关键字段: {user_data}")
                    raise AuthException(message="用户信息不完整")

                user_id = user_data.get('userName', '')
                print(f"当前用户: {user_id}")
                return user_id

        except InvalidTokenError:
            raise AuthException(message='用户登录已失效')
        except AuthException as ae:
            raise ae  # 已有认证异常直接抛出
        except Exception as e:
            print(f"未处理的认证异常: {str(e)}")
            raise AuthException(message="认证服务异常")

    
