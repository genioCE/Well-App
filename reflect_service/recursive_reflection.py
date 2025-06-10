"""Utility functions for recursive memory reflection."""

from __future__ import annotations

from datetime import datetime
from typing import List, Tuple
import os

import openai

from shared.qdrant_client import insert_embedding_with_stage
from .schemas import ReflectionRequest, ReflectionResponse

# In-memory store of past reflection requests
_MEMORY: List[ReflectionRequest] = []

openai.api_key = os.getenv("OPENAI_API_KEY", "")


def _generate_summary_and_insights(text: str) -> Tuple[str, List[str]]:
    """Return a reflection summary and a list of insights using OpenAI."""
    prompt = (
        "Summarize the following notes in one sentence and provide up to three "
        "bullet point insights:\n" + text
    )
    resp = openai.ChatCompletion.create(
        model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    content = resp.choices[0].message["content"].strip()
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    summary = lines[0]
    insights = [line.lstrip("- ") for line in lines[1:]]
    return summary, insights


def _get_embedding(text: str) -> List[float]:
    """Generate an embedding for ``text`` using OpenAI."""
    resp = openai.Embedding.create(
        input=text, model=os.getenv("EMBED_MODEL", "text-embedding-ada-002")
    )
    vector = resp["data"][0]["embedding"]
    if len(vector) != 1536:
        raise ValueError("Unexpected embedding size")
    return vector


def _gravity_score(entries: List[ReflectionRequest]) -> float:
    """Compute gravity score for a set of entries."""
    frequency = len(entries)
    signal_strength = 1.0
    last_ts = max(e.timestamp for e in entries)
    hours = (datetime.utcnow() - last_ts).total_seconds() / 3600.0
    recency_weight = 1 / (1 + hours)
    return frequency * signal_strength * recency_weight


def _process_level(
    level: str, entries: List[ReflectionRequest], meta: dict
) -> ReflectionResponse:
    """Generate reflection and store embedding for a specific level."""
    aggregated = " ".join(e.summary for e in entries)
    summary, insights = _generate_summary_and_insights(aggregated)
    embedding = _get_embedding(summary)
    score = _gravity_score(entries)
    payload = {
        **meta,
        "stage": "reflect",
        "layer": "truth",
        "reflection_level": level,
        "gravity_score": score,
        "timestamp": datetime.utcnow().isoformat(),
    }
    insert_embedding_with_stage("well_docs", embedding, payload)
    return ReflectionResponse(
        reflection_level=level,
        summary=summary,
        insights=insights,
        embedding=embedding,
        gravity_score=score,
        meta=meta,
        timestamp=datetime.utcnow(),
    )


def recursive_reflect(req: ReflectionRequest) -> ReflectionResponse:
    """Perform recursive reflection for the provided request."""
    req.timestamp = req.timestamp or datetime.utcnow()
    _MEMORY.append(req)

    # Well level
    well_entries = [e for e in _MEMORY if e.well_id == req.well_id]
    meta = req.meta.dict()
    meta["well_id"] = req.well_id
    _process_level("well", well_entries, meta)

    # Field level
    field_entries = [e for e in _MEMORY if e.meta.field == req.meta.field]
    _process_level("field", field_entries, meta)

    # District level - final reflection returned
    district_entries = [e for e in _MEMORY if e.meta.district == req.meta.district]
    return _process_level("district", district_entries, meta)
