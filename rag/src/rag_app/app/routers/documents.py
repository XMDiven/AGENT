from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from rag_app.config import config

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".md", ".pdf"}


def validate_upload_file(file: UploadFile) -> str:
    filename = Path(file.filename or "").name
    suffix = Path(filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only .md and .pdf files are supported",
        )

    return filename


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> dict[str, str]:
    filename = validate_upload_file(file)
    saved_path = config.RAW_DATA_DIR / filename

    saved_path.parent.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    saved_path.write_bytes(content)

    return {
        "filename": filename,
        "saved_path": str(saved_path.relative_to(config.RAW_DATA_DIR)),
        "content_type": file.content_type or "unknown",
    }
