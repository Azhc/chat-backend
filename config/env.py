import argparse
import os
import sys
from dotenv import load_dotenv
from functools import lru_cache
from pydantic_settings import BaseSettings


class SsoConfig(BaseSettings):
    """
    单点相关配置
    """
    sso_url:str='https://testjapi.scpgroup.com.cn'
    client_id:str='OAUTH_baixiaosheng_test'
    client_secret:str='07f9c099239149bea7e4f58795017d30'
    redirect_url:str='http://10.2.19.61:8001/auth/getUserByCode'

class DifyConfig(BaseSettings):

    """
    dify相关配置
    """    
    dify_api_url:str='http://10.201.1.46/v1'
    dify_api_key:str='app-fFiwzWar9N3Akli9ys53vK9A'
    pass;


class AppConfig(BaseSettings):
    """
    应用相关配置
    """
    app_env: str = 'dev'
    app_name: str = 'baixiaosheng-FastAPI'
    app_root_path: str = '/'
    app_host: str = '0.0.0.0'
    app_port: int = 8001
    app_version: str = '1.0.0'
    app_reload: bool = True


class JwtConfig(BaseSettings):
    """
    Jwt配置
    """

    jwt_secret_key: str = 'b01c66dc2c58dc6a0aabfe2144256be36226de378bf87f72c0c795dda67f4d55'
    jwt_algorithm: str = 'HS256'
    jwt_expire_minutes: int = 7*24*60



class GetConfig:
    """
    获取配置
    """
    

    def __init__(self):
        self.parse_cli_args()
    
    @lru_cache()
    def get_app_config(self):
        """
        获取应用配置
        """
        # 实例化应用配置模型
        return AppConfig()
    
    @lru_cache()
    def get_sso_config(self):
        """
        获取单点配置
        """
        # 实例化应用配置模型
        return SsoConfig()
    
    @lru_cache()
    def get_jwt_config(self):
        """
        获取单点配置
        """
        # 实例化应用配置模型
        return JwtConfig()
    
    @lru_cache()
    def get_dify_config(self):
        """
        获取单点配置
        """
        # 实例化应用配置模型
        return DifyConfig()
    
    @staticmethod
    def parse_cli_args():
        """
        解析命令行参数
        """
        if 'uvicorn' in sys.argv[0]:
            # 使用uvicorn启动时，命令行参数需要按照uvicorn的文档进行配置，无法自定义参数
            pass
        else:
            #本地运行使用 --env 来指定文件 docker运行时候通过env文件的映射来更改运行
            parser = argparse.ArgumentParser(description='命令行参数')
            parser.add_argument('--env', type=str, default='', help='运行环境')
            # 解析命令行参数
            args = parser.parse_args()
            # 设置环境变量，如果未设置命令行参数，默认APP_ENV为dev
            os.environ['APP_ENV'] = args.env if args.env else ''
        # 读取运行环境
        run_env = os.environ.get('APP_ENV', '')
        print(f'使用.env.{run_env}文件运行')
        # 运行环境未指定时默认加载.env.dev
        env_file = '.env'
        # 运行环境不为空时按命令行参数加载对应.env文件
        if run_env != '':
            env_file = f'.env.{run_env}'
        # 加载配置
        load_dotenv(env_file)





   


# 实例化获取配置类
get_config = GetConfig();
#应用配置获取
AppConfig = get_config.get_app_config()
#单点配置获取
SsoConfig =get_config.get_sso_config()
#jwt配置获取
JwtConfig = get_config.get_jwt_config()
#Dify配置获取
DifyConfig = get_config.get_dify_config()
