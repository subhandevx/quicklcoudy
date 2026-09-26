from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, status
from redis.exceptions import RedisError

from app.config import settings
from app.constants import CONTENT_TYPES, FORMAT_EXTENSIONS
from app.redis_client import job_key, redis_client
from app.schemas import JobCreated, JobStatus
from app.storage import output_path as build_output_path
from app.storage import upload_path as build_upload_path


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_job(
    contents: bytes,
    original_filename: str,
    input_format: str,
    output_format: str,
) -> JobCreated:
    job_id = str(uuid4())
    input_ext = FORMAT_EXTENSIONS[input_format]
    output_ext = FORMAT_EXTENSIONS[output_format]
    input_path = build_upload_path(job_id, input_ext)
    output_path = build_output_path(job_id, output_ext)
    stem = Path(original_filename).stem or "converted"
    download_name = f"{stem}{output_ext}"

    input_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    input_path.write_bytes(contents)

    record = {
        "status": "queued",
        "original_filename": original_filename,
        "input_format": input_format,
        "output_format": output_format,
        "input_path": str(input_path),
        "output_path": str(output_path),
        "download_name": download_name,
        "error": "",
        "created_at": _now(),
        "updated_at": _now(),
    }

    try:
        redis_client.hset(job_key(job_id), mapping=record)
        redis_client.lpush(settings.job_queue_key, job_id)
    except RedisError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to queue conversion job. Redis is unavailable.",
        ) from exc

    return JobCreated(
        job_id=job_id,
        status="queued",
        original_filename=original_filename,
        output_format=output_format,
    )


def get_job(job_id: str) -> JobStatus:
    try:
        data = redis_client.hgetall(job_key(job_id))
    except RedisError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to read job status. Redis is unavailable.",
        ) from exc

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    return JobStatus(
        job_id=job_id,
        status=data.get("status", "unknown"),
        original_filename=data.get("original_filename", ""),
        output_format=data.get("output_format", ""),
        download_name=data.get("download_name") or None,
        error=data.get("error") or None,
    )


def get_download(job_id: str) -> tuple[Path, str, str]:
    try:
        data = redis_client.hgetall(job_key(job_id))
    except RedisError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to read job status. Redis is unavailable.",
        ) from exc

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    job_status = data.get("status")
    if job_status == "failed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=data.get("error") or "Conversion failed.",
        )
    if job_status != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conversion is not finished yet.",
        )

    path = Path(data["output_path"])
    if not path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Converted file is no longer available.",
        )

    output_format = data.get("output_format", "png")
    media_type = CONTENT_TYPES.get(output_format, "application/octet-stream")
    download_name = data.get("download_name") or path.name
    return path, media_type, download_name
