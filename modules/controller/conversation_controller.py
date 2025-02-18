from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# 假设使用之前创建的HttpClient
from utils.http_client import HttpClient

router = APIRouter()

# 初始化HTTP客户端（根据实际后端服务地址配置）
backend_client = HttpClient(base_url="http://10.201.1.46/v1")

# 定义数据模型
class ConversationInputs(BaseModel):
    # 根据实际输入参数结构定义
    pass

class Conversation(BaseModel):
    id: str
    name: str
    inputs: dict  # 或使用ConversationInputs如果结构明确
    status: str
    introduction: str
    created_at: datetime
    updated_at: datetime

class ConversationsResponse(BaseModel):
    data: List[Conversation]
    has_more: bool
    limit: int

# 排序字段验证
VALID_SORT_FIELDS = {
    "created_at", "-created_at",
    "updated_at", "-updated_at"
}


ConversationController = APIRouter();

@ConversationController.get("/conversations", response_model=ConversationsResponse)
async def get_conversations(
    user: str = Query(..., description="用户标识，需保证应用内唯一"),
    last_id: Optional[str] = Query(None, description="最后一条记录ID"),
    limit: int = Query(20, gt=0, le=100, description="返回记录数，1-100"),
    sort_by: str = Query("-updated_at", description="排序字段")
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
            detail=f"无效的排序字段，可选值：{', '.join(VALID_SORT_FIELDS)}"
        )

    # 构造查询参数
    params = {
        "user": user,
        "last_id": last_id,
        "limit": limit,
        "sort_by": sort_by
    }

    # 调用后端服务
    response = backend_client.get(
        endpoint="/conversations",
        params={k: v for k, v in params.items() if v is not None},
        headers={'Authorization':'Bearer app-fFiwzWar9N3Akli9ys53vK9A'}
    )

    if not response["success"]:
        raise HTTPException(
            status_code=502,
            detail=f"后端服务请求失败: {response['error']}"
        )

    # 处理响应数据
    backend_data = response["data"]
    
    # 转换数据格式（根据实际后端响应结构调整）
    conversations = [
        {
            "id": item["id"],
            "name": item.get("name", ""),
            "inputs": item.get("inputs", {}),
            "status": item["status"],
            "introduction": item.get("introduction", ""),
            "created_at": item["created_at"],
            "updated_at": item["updated_at"]
        }
        for item in backend_data.get("data", [])
    ]

    return {
        "data": conversations,
        "has_more": backend_data.get("has_more", False),
        "limit": backend_data.get("limit", limit)
    }