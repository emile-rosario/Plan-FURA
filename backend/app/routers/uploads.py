import logging
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status

from app.config import settings
from app.security import get_current_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/uploads", tags=["Uploads"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# firmas para identificar el tipo real del archivo
_MAGIC_SIGNATURES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG": "image/png",
    b"RIFF": "image/webp",
}


def _detect_image_type(header: bytes) -> str | None:
    if header[:3] in _MAGIC_SIGNATURES:
        return _MAGIC_SIGNATURES[header[:3]]
    if header[:4] == b"RIFF" and len(header) >= 12 and header[8:12] == b"WEBP":
        return "image/webp"
    if header[:4] == b"\x89PNG":
        return "image/png"
    return None


@router.post("/imagen")
async def upload_image(
    file: UploadFile = File(...),
    _admin=Depends(get_current_admin),
):
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de archivo no permitido. Usa: {', '.join(settings.ALLOWED_IMAGE_TYPES)}",
        )

    contents = await file.read()

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el límite de {settings.MAX_UPLOAD_SIZE_MB} MB.",
        )

    # revisamos los bytes reales para que no se pueda colar un archivo renombrado
    detected = _detect_image_type(contents[:12])
    if detected not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="El contenido del archivo no corresponde a una imagen válida.",
        )

    ext = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        ext = ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as f:
        f.write(contents)

    logger.info("Imagen subida: %s (%d bytes)", filename, len(contents))
    return {"url": f"/uploads/{filename}", "filename": filename}
