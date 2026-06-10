import io

from fastapi import HTTPException, UploadFile, status
from PIL import Image

from app.config import settings

_MAX_BYTES = settings.max_image_size_mb * 1024 * 1024
_TARGET_MAX_DIM = 1024
_JPEG_QUALITY = 85


class ImageService:
    @staticmethod
    async def validate_and_compress(upload: UploadFile) -> bytes:
        if upload.content_type not in settings.allowed_image_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported image type: {upload.content_type}",
            )

        raw = await upload.read()
        if len(raw) > _MAX_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Image exceeds {settings.max_image_size_mb}MB limit",
            )

        return _compress(raw)


def _compress(data: bytes) -> bytes:
    img = Image.open(io.BytesIO(data)).convert("RGB")

    if max(img.size) > _TARGET_MAX_DIM:
        img.thumbnail((_TARGET_MAX_DIM, _TARGET_MAX_DIM), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=_JPEG_QUALITY, optimize=True)
    return buf.getvalue()
