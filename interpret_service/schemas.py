from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PruneRequest(BaseModel):
    uuid: str
    embedding: List[float]
    metadata: Optional[dict] = None

class PruneResponse(BaseModel):
    uuid: str
    pruned_embedding: List[float]
    timestamp: datetime
    details: dict

class InterpretMeta(BaseModel):
    field: str
    district: str
    operator: str
    document_type: str


class InterpretRequest(BaseModel):
    filename: str
    content: str
    well_id: str
    meta: InterpretMeta


class InterpretResponse(BaseModel):
    well_id: str
    filename: str
    summary: str
    tags: List[str]
    embedding: List[float]
    pruned_content: str
    meta: InterpretMeta
    timestamp: datetime
