import uuid
from fastapi import APIRouter, Query, HTTPException, Depends, Request,Path
from typing import Optional
from datetime import datetime
from utils.http_client import HttpClient
from utils.response_util import ResponseUtil
from modules.models.conversation_model import *
from modules.service.auth_service import AuthService
from exceptions.exception import ServiceException
from config.env import DifyConfig




backend_client = HttpClient(
    base_url=DifyConfig.dify_api_url,
    default_headers={"Authorization": f"Bearer {DifyConfig.dify_api_key}"},
)

ConversationController = APIRouter(dependencies=[Depends(AuthService.get_current_user)],prefix="/conversations")


@ConversationController.get("/list", response_model=ConversationsResponse)
async def get_conversations(
    last_id: Optional[str] = Query(None, description="最后一条记录ID"),
    limit: int=Query(default=20),
    sort_by: str = Query("-updated_at", description="排序字段"),
    current_user:str=Depends(AuthService.get_current_user)
):
    """
    获取用户会话列表
    - 默认返回最近的20条
    - 支持分页和排序
    """

    if limit is None or limit =='':
        raise 

    # 验证排序字段
    if sort_by not in VALID_SORT_FIELDS:
        return ResponseUtil.bad_request(msg='排序字段错误')
    
    if type(limit) is not int:
        return ResponseUtil.bad_request(msg='记录数为int')
    
    if limit<0 or limit>100:
        return ResponseUtil.bad_request(msg='记录数为0-100之间')
    
    

    # 构造查询参数
    params = {"user": current_user, "last_id": last_id, "limit": limit, "sort_by": sort_by}

    # 调用后端服务
    response = await backend_client.async_get(
        endpoint="/conversations",
        params={k: v for k, v in params.items() if v is not None},
    )

    if not response["success"]:
        print(response['error']);
        raise ServiceException(message="请求后端服务失败")


    # 处理响应数据
    backend_data = response["data"]


    # 转换数据格式
    # 转换数据格式（添加异常捕获）
    conversations = []
    for item in backend_data.get("data", []):
        conv = {
            "id": item["id"],  # 必需字段
            "name": item.get("name", "未命名会话"),
            "inputs": item.get("inputs", {}),
            "status": item["status"],  # 必需字段
            "introduction": item.get("introduction", ""),
            "created_at": item["created_at"],  # 必需字段
            "updated_at": item["updated_at"],  # 必需字段
        }
        conversations.append(conv)


    conversation_data = {
        "data": conversations,
        "has_more": backend_data.get("has_more", False),
        "limit": backend_data.get("limit", limit),
    }
    return ResponseUtil.success(data=conversation_data)


@ConversationController.post(
    "/{conversation_id}/name", response_model=Conversation
)
async def rename_conversation(conversation_id: str, 
                              request: ConversationRenameRequest,
                              current_user:str=Depends(AuthService.get_current_user)):
    """
    更新会话名称
    - 自动生成或手动指定会话名称
    - 用户标识需与会话所属用户匹配
    """

    # 验证对话ID是否为UUID格式
    try:
        uuid_obj = uuid.UUID(conversation_id, version=4)
    except ValueError:
        raise ServiceException(message="对话ID格式错误")

    if request.auto_generate is False and (not request.name or request.name is None or request.name=='' ):
        raise ServiceException(message="自动生成为false时，对话名称不能为空")


    # 构建请求数据
    payload = request.model_dump(exclude_unset=True)
    payload['user']=current_user;
    
    # 调用后端服务
    response =  await backend_client.async_post(
        endpoint=f"/conversations/{conversation_id}/name", json_data=payload
    )
    if not response.get("success"):
        raise ServiceException(message=response.get("data", "接口请求失败").get("message", "错误"))
    
    # 转换并返回标准响应格式
    return ResponseUtil.success(data=response["data"])



@ConversationController.get("/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str = Path(..., description="对话ID"),
    first_id: Optional[str]=Query(default=None,description='当前页第一条聊天记录的，默认 null'),
    limit: Optional[int] = Query(default=20,description="一次返回多少条对话信息"),
    current_user:str=Depends(AuthService.get_current_user)
):
    """
    获取对话消息列表
    - 默认返回最近的20条
    - 支持分页和排序
    """
    try:
    # 验证对话ID是否为UUID格式
        try:
            uuid_obj = uuid.UUID(conversation_id, version=4)
        except ValueError:
            raise ServiceException(message="对话ID格式错误")
        
        # 处理空字符串场景
        if first_id == "":  # 显式处理空字符串
            first_id = None

        if first_id is not None:
            try:
                uuid_obj = uuid.UUID(first_id, version=4)
            except ValueError:
                raise ServiceException(message="消息ID格式错误")  

        
        # 构造查询参数
        params = {"user": current_user, "first_id": first_id, "limit": limit,"conversation_id":conversation_id}

        try:
            # 调用后端服务
            response = await backend_client.async_get(
                endpoint="/messages",
                params={k: v for k, v in params.items() if v is not None},
            )
        except Exception as e:
            raise ServiceException(message="服务暂时不可用，请稍后重试") from e


        if not response["success"]:
            # 修改此处代码，处理 data 可能非字典的情况
            error_data = response.get("data", {})
            error_message = error_data.get("message", "错误") if isinstance(error_data, dict) else str(error_data)[:100]

            raise ServiceException(message=f"请求后端服务失败: {error_message}")
        
            # 转换并返回标准响应格式
        return ResponseUtil.success(data=response.get("data",[]))
    
    except ServiceException as se:
        # 已知业务异常直接抛出
        raise
    except Exception as unhandled_ex:
        raise ServiceException(message="系统发生意外错误") from unhandled_ex



@ConversationController.delete("/{conversation_id}")
async def delete_conversations(
    conversation_id: str = Path(..., description="对话ID"),
    current_user:str=Depends(AuthService.get_current_user)
):
    """
    删除对话
    """

    # 验证对话ID是否为UUID格式
    try:
        uuid_obj = uuid.UUID(conversation_id, version=4)
    except ValueError:
        raise ServiceException(message="对话ID格式错误")

    payload={'user':current_user}

    try:
    # 调用后端服务
        response =  await backend_client.async_delete(
            endpoint=f"/conversations/{conversation_id}", json_data=payload
        )
    except Exception as e:
        raise ServiceException(message="服务暂时不可用，请稍后重试") from e

    print(response)

    if not response.get("success"):
        raise ServiceException(message=response.get("data", "接口请求失败").get("message", "错误"))
    
    print(response)
    # 转换并返回标准响应格式
    return ResponseUtil.success(data=response["data"])           