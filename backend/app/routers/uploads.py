"""
Router de uploads — Subida segura de imágenes.
"""
import logging
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.security import get_current_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/uploads", tags=["Uploads"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_PDF_TYPES = ["application/pdf"]
MAX_PDF_SIZE_MB = 10


@router.post("/imagen")
async def upload_image(
    file: UploadFile = File(...),
    _admin=Depends(get_current_admin),
):
    """Subir imagen de ataúd (solo admin). Máximo 5 MB, solo JPEG/PNG/WebP."""
    # Validar tipo de contenido
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de archivo no permitido. Usa: {', '.join(settings.ALLOWED_IMAGE_TYPES)}",
        )

    # Validar tamaño
    contents = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el límite de {settings.MAX_UPLOAD_SIZE_MB} MB.",
        )

    # Generar nombre único seguro (evita path traversal)
    ext = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        ext = ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as f:
        f.write(contents)

    logger.info("Imagen subida: %s (%d bytes)", filename, len(contents))
    return {"url": f"/uploads/{filename}", "filename": filename}


@router.post("/documento")
async def upload_documento(file: UploadFile = File(...)):
    """Subir documento PDF (público — para formulario de contacto y contratación de planes)."""
    if file.content_type not in ALLOWED_PDF_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Solo se permiten archivos PDF.",
        )

    contents = await file.read()
    max_bytes = MAX_PDF_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"El archivo supera el límite de {MAX_PDF_SIZE_MB} MB.",
        )

    filename = f"{uuid.uuid4().hex}.pdf"
    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as f:
        f.write(contents)

    logger.info("Documento PDF subido: %s (%d bytes)", filename, len(contents))
    return {"url": f"/uploads/{filename}", "filename": filename}
