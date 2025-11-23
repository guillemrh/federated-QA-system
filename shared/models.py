from pydantic import BaseModel
from typing import List, Dict, Literal, Optional
from dataclasses import dataclass

class AskRequest(BaseModel):
    question: str
    metadata: Optional[Dict] = None

class Source(BaseModel):
    name: str
    url: str
    snippet: str

class AskResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[Source]
    node_id: Optional[str]
    nodes_hit: Optional[List[str]] = None
    status: Optional[Literal["success", "error"]] = "success"

@dataclass
class NodeResult:
    response: AskResponse
    query_embedding: List[float]
    chunk_embeddings: List[List[float]]