from datetime import datetime
from pydantic import BaseModel,Field
from typing import List, Optional,Dict,Any,Union




class ChatRequest(BaseModel):
    query: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    conversation_id: str = None


class ChatFeedbackRequest(BaseModel):
    """
    消息反馈模型
    """
    rating:Optional[str] = None
    content:Optional[str] = None