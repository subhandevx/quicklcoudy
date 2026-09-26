SUPPORTED_INPUT_FORMATS = {"jpeg", "png", "webp"}
SUPPORTED_OUTPUT_FORMATS = {"jpeg", "png", "webp"}

FORMAT_ALIASES = {
    "jpg": "jpeg",
    "jpeg": "jpeg",
    "png": "png",
    "webp": "webp",
}

PIL_TO_FORMAT = {
    "JPEG": "jpeg",
    "JPG": "jpeg",
    "PNG": "png",
    "WEBP": "webp",
}

FORMAT_EXTENSIONS = {
    "jpeg": ".jpg",
    "png": ".png",
    "webp": ".webp",
}

CONTENT_TYPES = {
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}


def normalize_format(value: str) -> str | None:
    if not value:
        return None
    return FORMAT_ALIASES.get(value.strip().lower())
