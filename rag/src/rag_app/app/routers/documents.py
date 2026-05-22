from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from rag_app.config import config

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".md", ".pdf"}


async def save_upload_file(file: UploadFile, filename: str) -> dict[str, str]:
    saved_path = config.RAW_DATA_DIR / filename

    saved_path.parent.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    saved_path.write_bytes(content)

    return {
        "filename": filename,
        "saved_path": str(saved_path.relative_to(config.RAW_DATA_DIR)),
        "content_type": file.content_type or "unknown",
    }


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
    return await save_upload_file(file, filename)


@router.post("/upload/batch")
async def upload_documents(
    files: list[UploadFile] = File(...),
) -> dict[str, list[dict[str, str]]]:
    filenames = [validate_upload_file(file) for file in files]

    saved_files = []
    for file, filename in zip(files, filenames, strict=True):
        saved_files.append(await save_upload_file(file, filename))

    return {
        "files": saved_files,
    }
