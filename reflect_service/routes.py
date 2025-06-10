from fastapi import APIRouter, HTTPException
from datetime import datetime
from shared.logger import logger
from schemas import AnchorRequest, AnchorResponse
from validation import validate_embedding

router = APIRouter()


@router.post("/anchor", response_model=AnchorResponse)
async def anchor(request: AnchorRequest):
    try:
        anchored, status, summary = await validate_embedding(request.pruned_embedding)
        response = AnchorResponse(
            uuid=request.uuid,
            anchored_embedding=anchored,
            status=status,
            timestamp=datetime.utcnow(),
            summary=summary,
        )
        logger.info(f"[REFLECT] {request.uuid} => {status} : {summary}")
        return response
    except Exception as e:
        logger.error(f"[REFLECT] Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


from .recursive_reflection import recursive_reflect
from .schemas import ReflectionRequest, ReflectionResponse


@router.post("/reflect", response_model=ReflectionResponse)
async def reflect(request: ReflectionRequest) -> ReflectionResponse:
    """Perform recursive memory reflection for a well document summary."""
    try:
        result = recursive_reflect(request)
        logger.info("[REFLECT] %s => %s", request.well_id, result.reflection_level)
        return result
    except Exception as exc:  # noqa: BLE001
        logger.error("[REFLECT] Error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
