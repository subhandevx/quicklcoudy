from redis import Redis

from app.config import settings

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


def job_key(job_id: str) -> str:
    return f"job:{job_id}"
