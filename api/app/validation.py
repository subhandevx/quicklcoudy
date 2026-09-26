import io

from fastapi import HTTPException, status
from PIL import Image, UnidentifiedImageError

from app.constants import (
    FORMAT_EXTENSIONS,
    PIL_TO_FORMAT,
    SUPPORTED_INPUT_FORMATS,
    SUPPORTED_OUTPUT_FORMATS,
    normalize_format,
)


def parse_output_format(value: str) -> str:
    fmt = normalize_format(value)
    if fmt not in SUPPORTED_OUTPUT_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported output format. Use jpeg, jpg, png, or webp.",
        )
    return fmt


def detect_image_format(contents: bytes) -> str:
    try:
        with Image.open(io.BytesIO(contents)) as image:
            image.verify()
        with Image.open(io.BytesIO(contents)) as image:
            detected = PIL_TO_FORMAT.get((image.format or "").upper())
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is not a valid image.",
        ) from exc

    if detected not in SUPPORTED_INPUT_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported input format. Upload a JPEG, PNG, or WEBP image.",
        )
    return detected


def extension_for(fmt: str) -> str:
    return FORMAT_EXTENSIONS[fmt]
