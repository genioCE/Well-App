import os
import sys
import types

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

# Stub openai to avoid network calls
sys.modules["openai"] = types.SimpleNamespace(
    ChatCompletion=types.SimpleNamespace(
        create=lambda **kwargs: types.SimpleNamespace(
            choices=[types.SimpleNamespace(message={"content": "summary\n- insight"})]
        )
    ),
    Embedding=types.SimpleNamespace(
        create=lambda **kwargs: {"data": [{"embedding": [0.0] * 1536}]}
    ),
)

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from reflect_service.main import app


# Patch qdrant insert
@pytest.fixture(autouse=True)
def patch_qdrant(monkeypatch):
    monkeypatch.setattr(
        "shared.qdrant_client.insert_embedding_with_stage", lambda *a, **k: None
    )


def test_reflect_endpoint():
    client = TestClient(app)
    payload = {
        "summary": "well operation",
        "well_id": "W1",
        "meta": {
            "field": "F",
            "district": "D",
            "operator": "O",
            "document_type": "log",
        },
    }
    resp = client.post("/reflect", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["reflection_level"] == "district"
    assert data["summary"] == "summary"
    assert len(data["embedding"]) == 1536
