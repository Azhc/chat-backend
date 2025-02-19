from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime
from utils.http_client import HttpClient
from utils.response_util import ResponseUtil
from modules.models.conversation_model import *
import uuid


router = APIRouter()

# 初始化HTTP客户端（根据实际后端服务地址配置）
backend_client = HttpClient(
    base_url="http://10.201.1.46/v1",
    default_headers={"Authorization": "Bearer app-fFiwzWar9N3Akli9ys53vK9A"},
)

ConversationController = APIRouter()


@ConversationController.get("/conversations", response_model=ConversationsResponse)
async def get_conversations(
    user: str = Query(..., description="用户标识，需保证应用内唯一"),
    last_id: Optional[str] = Query(None, description="最后一条记录ID"),
    limit: int = Query(20, gt=0, le=100, description="返回记录数，1-100"),
    sort_by: str = Query("-updated_at", description="排序字段"),
):
    """
    获取用户会话列表
    - 默认返回最近的20条
    - 支持分页和排序
    """

    # 验证排序字段
    if sort_by not in VALID_SORT_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"无效的排序字段，可选值：{', '.join(VALID_SORT_FIELDS)}",
        )

    # 构造查询参数
    params = {"user": user, "last_id": last_id, "limit": limit, "sort_by": sort_by}

    # 调用后端服务
    response = backend_client.get(
        endpoint="/conversations",
        params={k: v for k, v in params.items() if v is not None},
    )

    if not response["success"]:
        raise HTTPException(
            status_code=502, detail=f"后端服务请求失败: {response['error']}"
        )


    # 处理响应数据
    backend_data = response["data"]
    
    print(backend_data)

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
    return {
        "data": conversations,
        "has_more": backend_data.get("has_more", False),
        "limit": backend_data.get("limit", limit),
    }


@ConversationController.post(
    "/conversations/{conversation_id}/name", response_model=Conversation
)
async def rename_conversation(conversation_id: str, request: ConversationRenameRequest):
    """
    更新会话名称
    - 自动生成或手动指定会话名称
    - 用户标识需与会话所属用户匹配
    """

    # 验证对话ID是否为UUID格式
    try:
        uuid_obj = uuid.UUID(conversation_id, version=4)
    except ValueError:
        return ResponseUtil.bad_request(msg="对话ID格式错误")

    # 构建请求数据
    payload = request.model_dump(exclude_unset=True)

    # 调用后端服务
    response = backend_client.post(
        endpoint=f"/conversations/{conversation_id}/name", json_data=payload
    )
    print(response)
    if not response.get("success"):
        return ResponseUtil.error(
            msg=response.get("data", "接口请求失败").get("message", "错误")
        )

        # 转换并返回标准响应格式
    return ResponseUtil.success(data=response["data"])
