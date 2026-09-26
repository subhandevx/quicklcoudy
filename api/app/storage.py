from pathlib import Path

from app.config import settings


def ensure_data_dirs() -> None:
    Path(settings.data_dir, "uploads").mkdir(parents=True, exist_ok=True)
    Path(settings.data_dir, "outputs").mkdir(parents=True, exist_ok=True)


def upload_path(job_id: str, extension: str) -> Path:
    return Path(settings.data_dir, "uploads", f"{job_id}{extension}").resolve()


def output_path(job_id: str, extension: str) -> Path:
    return Path(settings.data_dir, "outputs", f"{job_id}{extension}").resolve()
