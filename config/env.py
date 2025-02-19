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
    sso_url:str='https://testjauth.scpgroup.com.cn'
    client_id:str='OAUTH_baixiaosheng_test'
    client_secret:str='07f9c099239149bea7e4f58795017d30'
    redirect_url:str='http://10.2.19.61:8001/auth/getUserByCode'

class DifyConfigs(BaseSettings):
    """
    dify相关配置
    """    
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
    
    @staticmethod
    def parse_cli_args():
        """
        解析命令行参数
        """
        if 'uvicorn' in sys.argv[0]:
            # 使用uvicorn启动时，命令行参数需要按照uvicorn的文档进行配置，无法自定义参数
            pass
        else:
            # 使用argparse定义命令行参数
            parser = argparse.ArgumentParser(description='命令行参数')
            parser.add_argument('--env', type=str, default='', help='运行环境')
            # 解析命令行参数
            args = parser.parse_args()
            # 设置环境变量，如果未设置命令行参数，默认APP_ENV为dev
            os.environ['APP_ENV'] = args.env if args.env else 'dev'
        # 读取运行环境
        run_env = os.environ.get('APP_ENV', '')
        # 运行环境未指定时默认加载.env.dev
        env_file = '.env.dev'
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