from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.config import settings
from app.constants import SUPPORTED_INPUT_FORMATS, SUPPORTED_OUTPUT_FORMATS
from app.schemas import FormatsResponse, JobCreated, JobStatus
from app.services import jobs as job_service
from app.validation import detect_image_format, parse_output_format

router = APIRouter(tags=["jobs"])


@router.get("/formats", response_model=FormatsResponse)
def list_formats() -> FormatsResponse:
    return FormatsResponse(
        input=sorted(SUPPORTED_INPUT_FORMATS),
        output=sorted(SUPPORTED_OUTPUT_FORMATS),
    )


@router.post("/jobs", response_model=JobCreated, status_code=status.HTTP_202_ACCEPTED)
async def create_job(
    file: UploadFile = File(...),
    output_format: str = Form(...),
) -> JobCreated:
    if file.size is not None and file.size > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File is too large. Maximum size is 10 MB.",
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty.",
        )
    if len(contents) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File is too large. Maximum size is 10 MB.",
        )

    input_format = detect_image_format(contents)
    target_format = parse_output_format(output_format)
    filename = file.filename or f"upload.{input_format}"

    return job_service.create_job(
        contents=contents,
        original_filename=filename,
        input_format=input_format,
        output_format=target_format,
    )


@router.get("/jobs/{job_id}", response_model=JobStatus)
def get_job(job_id: str) -> JobStatus:
    return job_service.get_job(job_id)


@router.get("/jobs/{job_id}/download")
def download_job(job_id: str) -> FileResponse:
    path, media_type, download_name = job_service.get_download(job_id)
    return FileResponse(
        path=path,
        media_type=media_type,
        filename=download_name,
    )
