import logging
import signal
import time
from datetime import datetime, timezone

from redis import Redis
from redis.exceptions import RedisError, TimeoutError as RedisTimeoutError

from app.config import settings
from app.converter import convert_image

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("quicklcoudy.worker")

running = True


def _handle_shutdown(signum: int, _frame) -> None:
    global running
    logger.info("Received signal %s, stopping after current job", signum)
    running = False


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _job_key(job_id: str) -> str:
    return f"job:{job_id}"


def process_job(redis_client: Redis, job_id: str) -> None:
    key = _job_key(job_id)
    job = redis_client.hgetall(key)
    if not job:
        logger.warning("Job %s was dequeued but no record exists", job_id)
        return

    redis_client.hset(key, mapping={"status": "processing", "updated_at": _now()})
    logger.info("Converting job %s to %s", job_id, job.get("output_format"))

    try:
        convert_image(
            input_path=job["input_path"],
            output_path=job["output_path"],
            output_format=job["output_format"],
        )
    except Exception as exc:
        logger.exception("Job %s failed", job_id)
        redis_client.hset(
            key,
            mapping={
                "status": "failed",
                "error": f"Conversion failed: {exc}",
                "updated_at": _now(),
            },
        )
        return

    redis_client.hset(
        key,
        mapping={
            "status": "completed",
            "error": "",
            "updated_at": _now(),
        },
    )
    logger.info("Job %s completed", job_id)


def main() -> None:
    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)

    redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    logger.info("QUICKLCOUDY worker started, listening on %s", settings.job_queue_key)

    while running:
        try:
            item = redis_client.brpop(settings.job_queue_key, timeout=settings.queue_timeout_seconds)
        except RedisTimeoutError:
            continue
        except RedisError:
            if running:
                logger.exception("Redis error while waiting for jobs")
                time.sleep(2)
            continue

        if item is None:
            continue

        _, job_id = item
        process_job(redis_client, job_id)

    logger.info("QUICKLCOUDY worker stopped")


if __name__ == "__main__":
    main()
