from pathlib import Path

from PIL import Image

SAVE_OPTIONS = {
    "jpeg": {"quality": 90, "optimize": True},
    "png": {"optimize": True},
    "webp": {"quality": 90, "method": 4},
}


def convert_image(input_path: str | Path, output_path: str | Path, output_format: str) -> None:
    source = Path(input_path)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(source) as image:
        prepared = _prepare_image(image, output_format)
        prepared.save(destination, format=output_format.upper(), **SAVE_OPTIONS[output_format])


def _prepare_image(image: Image.Image, output_format: str) -> Image.Image:
    if output_format == "jpeg":
        if image.mode in ("RGBA", "LA"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            alpha = image.getchannel("A")
            background.paste(image.convert("RGBA"), mask=alpha)
            return background
        if image.mode == "P":
            converted = image.convert("RGBA")
            background = Image.new("RGB", converted.size, (255, 255, 255))
            background.paste(converted, mask=converted.getchannel("A"))
            return background
        if image.mode != "RGB":
            return image.convert("RGB")
        return image.copy()

    if output_format == "png":
        if image.mode not in ("RGB", "RGBA", "L", "LA", "P"):
            return image.convert("RGBA")
        return image.copy()

    if image.mode not in ("RGB", "RGBA"):
        return image.convert("RGBA") if "A" in image.mode else image.convert("RGB")
    return image.copy()
