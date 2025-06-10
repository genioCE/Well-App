from fastapi import FastAPI, HTTPException
from shared.redis_utils import subscribe, publish
from shared.logger import logger
from shared.qdrant_client import insert_embedding_with_stage
import threading
import json
import spacy
import os
from datetime import datetime
from schemas import (
    PruneRequest,
    PruneResponse,
    InterpretRequest,
    InterpretResponse,
)
from pruning import prune_embedding
from .utils import summarize, extract_tags, prune_content, get_embedding
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Histogram, Counter
import signal
import uvicorn

app = FastAPI(title="Genio INTERPRET Service")

# Middleware and Prometheus instrumentation must be here
Instrumentator().instrument(app).expose(app)

# Prometheus metrics
pruning_latency = Histogram("pruning_latency_seconds", "Time spent pruning embeddings")
interpret_errors = Counter(
    "interpret_errors_total", "Total errors in Interpret service"
)

# Load spaCy model safely
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    logger.error(f"Failed to load spaCy model: {e}")
    exit(1)

# Settings
THRESHOLD = float(os.getenv("PRUNE_THRESHOLD", "0.1"))
REDUCE_DIM = int(os.getenv("REDUCE_DIM", "0"))
EXPRESS_CHANNEL = os.getenv("EXPRESS_CHANNEL", "express_channel")
INTERPRET_CHANNEL = os.getenv("INTERPRET_CHANNEL", "interpret_channel")

shutdown_flag = threading.Event()


def listener():
    pubsub = subscribe(EXPRESS_CHANNEL)
    logger.info(f"[INTERPRET] Subscribed to '{EXPRESS_CHANNEL}'")

    while not shutdown_flag.is_set():
        message = pubsub.get_message(timeout=1)
        if message and message["type"] == "message":
            try:
                data = json.loads(message["data"])
                content = data.get("content")
                embedding = data.get("embedding")
                uuid = data.get("uuid", datetime.utcnow().isoformat())

                if not embedding:
                    interpret_errors.inc()
                    logger.error(f"[INTERPRET] Missing embedding for uuid={uuid}")
                    continue

                doc = nlp(content)
                tokens = [token.text for token in doc if not token.is_stop]
                logger.info(f"[INTERPRET] Parsed Tokens: {tokens}")

                with pruning_latency.time():
                    pruned_embedding, details = prune_embedding(
                        embedding, THRESHOLD, REDUCE_DIM if REDUCE_DIM > 0 else None
                    )
                logger.info(
                    f"[INTERPRET] Pruned embedding uuid={uuid}, details={details}"
                )

                downstream_message = {
                    "uuid": uuid,
                    "tokens": tokens,
                    "pruned_embedding": pruned_embedding,
                    "pruning_details": details,
                    "timestamp": datetime.utcnow().isoformat(),
                }

                publish(INTERPRET_CHANNEL, downstream_message)
                logger.info(
                    f"[INTERPRET] Published data uuid={uuid} to '{INTERPRET_CHANNEL}'"
                )

                # ✅ NEW: publish to memory_replay_channel
                replay_message = {
                    "uuid": uuid,
                    "timestamp": downstream_message["timestamp"],
                    "tokens": tokens,
                    "weight": 1.0,
                    "tags": ["interpreted"]
                }
                publish("memory_replay_channel", replay_message)
                logger.info(
                    f"[INTERPRET] Published replay to 'memory_replay_channel': {replay_message}"
                )

            except Exception as e:
                interpret_errors.inc()
                logger.error(f"[INTERPRET] Error processing message: {e}")



def handle_shutdown(signal_received, frame):
    shutdown_flag.set()


signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)
threading.Thread(target=listener, daemon=True).start()


@app.get("/health")
def detailed_healthcheck():
    spacy_status = "ok"
    try:
        _ = nlp("test")
    except Exception as e:
        spacy_status = f"error: {str(e)}"

    return {
        "status": "active",
        "spacy": spacy_status,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/")
def healthcheck():
    return {"status": "interpret_service active"}


@app.post("/interpret", response_model=InterpretResponse)
async def interpret(req: InterpretRequest):
    """Process well document content and store embedding."""
    try:
        summary = summarize(req.content)
        tags = extract_tags(req.content)
        pruned = prune_content(req.content)
        embedding = get_embedding(pruned)
    except Exception as exc:  # noqa: BLE001
        interpret_errors.inc()
        raise HTTPException(status_code=500, detail=str(exc))

    ts = datetime.utcnow()
    metadata = {
        "well_id": req.well_id,
        "filename": req.filename,
        "field": req.meta.field,
        "district": req.meta.district,
        "operator": req.meta.operator,
        "document_type": req.meta.document_type,
        "timestamp": ts.isoformat(),
        "stage": "interpret",
        "layer": "raw",
    }

    try:
        insert_embedding_with_stage("well_docs", embedding, metadata)
    except Exception as exc:  # noqa: BLE001
        interpret_errors.inc()
        raise HTTPException(status_code=500, detail=f"Qdrant error: {exc}")

    return InterpretResponse(
        well_id=req.well_id,
        filename=req.filename,
        summary=summary,
        tags=tags,
        embedding=embedding,
        pruned_content=pruned,
        meta=req.meta,
        timestamp=ts,
    )


@app.post("/prune", response_model=PruneResponse)
async def prune(req: PruneRequest):
    if not req.embedding:
        raise HTTPException(status_code=400, detail="Embedding vector missing")
    try:
        with pruning_latency.time():
            pruned, details = prune_embedding(
                req.embedding, THRESHOLD, REDUCE_DIM if REDUCE_DIM > 0 else None
            )
    except Exception as e:
        interpret_errors.inc()
        raise HTTPException(status_code=400, detail=f"Failed to prune embedding: {e}")

    return PruneResponse(
        uuid=req.uuid,
        pruned_embedding=pruned,
        timestamp=datetime.utcnow(),
        details=details,
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
