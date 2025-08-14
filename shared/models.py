from pydantic import BaseModel
from typing import List, Dict, Literal, Optional

class AskRequest(BaseModel):
    question: str
    metadata: Dict = {}

class Source(BaseModel):
    name: str
    url: str
    snippet: str

class AskResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[Source]
    node_id: str
    status: Literal["success", "error"] = "success"
