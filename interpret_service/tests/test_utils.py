import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

import types
import pytest

# Stub openai and spacy to avoid import errors
sys.modules['openai'] = types.SimpleNamespace(
    ChatCompletion=types.SimpleNamespace(create=lambda **kwargs: None),
    Embedding=types.SimpleNamespace(create=lambda **kwargs: {'data': [{'embedding': [0.0]*1536}]}),
)

class DummyDoc:
    def __init__(self) -> None:
        self.noun_chunks = [types.SimpleNamespace(text="pressure valve")]


class DummyNLP:
    def __call__(self, text: str) -> DummyDoc:  # type: ignore[override]
        return DummyDoc()


sys.modules['spacy'] = types.SimpleNamespace(load=lambda name: DummyNLP())

from interpret_service.utils import extract_tags, prune_content


def test_extract_tags() -> None:
    text = "Operator adjusted pressure valve in district 5"
    tags = extract_tags(text)
    assert "pressure valve" in tags


def test_prune_content() -> None:
    text = "Line 1\nPressure reading 35 psi\nRandom\nOperator action"
    pruned = prune_content(text)
    assert "Pressure reading" in pruned
    assert "Operator action" in pruned


def test_interpret_endpoint(monkeypatch) -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient
    from interpret_service.main import app

    # Patch OpenAI helpers
    monkeypatch.setattr(
        "interpret_service.utils.summarize", lambda text: "summary"
    )
    monkeypatch.setattr(
        "interpret_service.utils.get_embedding", lambda text: [0.0] * 1536
    )

    def mock_insert(collection, vector, metadata):
        assert collection == "well_docs"
        assert len(vector) == 1536
    monkeypatch.setattr(
        "shared.qdrant_client.insert_embedding_with_stage", mock_insert
    )

    client = TestClient(app)
    payload = {
        "filename": "test.txt",
        "content": "Pressure log line",
        "well_id": "W1",
        "meta": {
            "field": "A",
            "district": "B",
            "operator": "Op",
            "document_type": "type",
        },
    }
    resp = client.post("/interpret", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["well_id"] == "W1"
    assert len(data["embedding"]) == 1536


