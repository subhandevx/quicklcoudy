from pydantic import BaseModel


class JobCreated(BaseModel):
    job_id: str
    status: str
    original_filename: str
    output_format: str


class JobStatus(BaseModel):
    job_id: str
    status: str
    original_filename: str
    output_format: str
    download_name: str | None = None
    error: str | None = None


class FormatsResponse(BaseModel):
    input: list[str]
    output: list[str]


class HealthResponse(BaseModel):
    status: str
    service: str
