from __future__ import annotations

import os
import uuid
from typing import Any, Dict, List

from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance

QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def _ensure_collection(collection: str, dim: int) -> None:
    collections = [c.name for c in _client.get_collections().collections]
    if collection not in collections:
        _client.recreate_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )


def insert_embedding_with_stage(
    collection: str, vector: List[float], metadata: Dict[str, Any]
) -> None:
    """Insert embedding with metadata into Qdrant."""
    _ensure_collection(collection, len(vector))
    point_id = str(uuid.uuid4())
    _client.upsert(
        collection_name=collection,
        points=[PointStruct(id=point_id, vector=vector, payload=metadata)],
    )
