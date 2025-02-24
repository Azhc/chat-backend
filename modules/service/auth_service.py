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



# OAuth2 方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/getUserByCode")


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
    

    async def get_current_user( request: Request = Request,token: str = Depends(oauth2_scheme)):
        """
        校验token
        """
        try:
            if token.startswith('Bearer'):
                token = token.split(' ')[1]
            payload = jwt.decode(token, JwtConfig.jwt_secret_key, algorithms=[JwtConfig.jwt_algorithm])
            user_id: str = payload.get('user_id')
            if not user_id:
                raise AuthException(data='', message='用户token不合法')
            else:
                return user_id
        except InvalidTokenError:
            raise AuthException(data='', message='用户登陆已失效')

    
