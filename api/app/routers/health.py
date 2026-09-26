from fastapi import APIRouter, HTTPException, status
from redis.exceptions import RedisError

from app.redis_client import redis_client
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="api")


@router.get("/ready", response_model=HealthResponse)
def ready() -> HealthResponse:
    try:
        redis_client.ping()
    except RedisError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis is unavailable.",
        ) from exc
    return HealthResponse(status="ok", service="api")
