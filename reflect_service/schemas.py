from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AnchorRequest(BaseModel):
    uuid: str
    pruned_embedding: List[float]
    metadata: Optional[dict] = None


class AnchorResponse(BaseModel):
    uuid: str
    anchored_embedding: List[float]
    status: str
    timestamp: datetime
    summary: Optional[str] = None


class ReflectionMeta(BaseModel):
    """Metadata for reflection requests."""

    field: str
    district: str
    operator: str
    document_type: str


class ReflectionRequest(BaseModel):
    """Payload for initiating recursive reflection."""

    summary: str
    well_id: str
    meta: ReflectionMeta
    timestamp: Optional[datetime] = None


class ReflectionResponse(BaseModel):
    """Result from recursive reflection."""

    reflection_level: str
    summary: str
    insights: List[str]
    embedding: List[float]
    gravity_score: float
    meta: ReflectionMeta | dict
    timestamp: datetime
