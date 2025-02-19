from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class ConversationInputs(BaseModel):
    pass

class Conversation(BaseModel):
    """
    对话详细数据
    """
    id: str
    name: str
    inputs: dict
    status: str
    introduction: str
    created_at: datetime
    updated_at: datetime

class ConversationsResponse(BaseModel):
    data: List[Conversation]
    has_more: bool
    limit: int
    
class ConversationRenameRequest(BaseModel):
    """
    重命名请求
    """
    name: Optional[str] = None
    auto_generate: bool = False
    user: str

VALID_SORT_FIELDS = {
    "created_at", "-created_at",
    "updated_at", "-updated_at"
}
