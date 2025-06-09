from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel


class FileRecord(BaseModel):
    """Database representation of an uploaded file."""

    filename: str
    source: str
    content: str
    timestamp: datetime
    meta: Dict[str, Any]
