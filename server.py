from fastapi import FastAPI
from config.env import AppConfig
from modules.controller.conversation_controller import ConversationController
from modules.controller.auth_controller import AuthController
from modules.controller.chat_controller import ChatController
from contextlib import asynccontextmanager
from exceptions.handle import handle_exception



@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f'{AppConfig.app_name}开始启动')
    yield


app=FastAPI(
            title=AppConfig.app_name,
            description=f"{AppConfig.app_name} 文档",
            version=AppConfig.app_version,
            lifespan=lifespan);



# 加载全局异常处理方法
handle_exception(app)

#路由列表
controller_list = [
    {'router': ConversationController, 'tags': ['会话模块']},
    {'router': AuthController, 'tags': ['认证模块']},
    {'router': ChatController, 'tags': ['对话模块']},
]

# 添加所有路由列表

for controller in controller_list:
    app.include_router(router=controller.get('router'), tags=controller.get('tags'))

