from datetime import datetime
from pydantic import BaseModel,Field
from typing import List, Optional,Dict,Any




class ChatRequest(BaseModel):
    query: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    conversation_id: str = None