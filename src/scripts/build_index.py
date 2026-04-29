from pathlib import Path
from src.services.ingest_service import ingest_markdown_file , ingest_pdf_file
from config import config
def get_supported_files() ->list[Path]:
    raw_data_dir = config.RAW_DATA_DIR
    files = [
        *raw_data_dir.glob("*.md"),
        *raw_data_dir.glob("*.pdf")
    ]
    return sorted(files)

def ingest_file(path : str) ->dict[str, str | int]:
    file_path = Path(path)
    if file_path.suffix == ".md":
        return ingest_markdown_file(path)
    if file_path.suffix == ".pdf":
        return ingest_pdf_file(path)
    raise ValueError(f"Unsupported file type: {file_path.suffix}")


def build_index():
    supported_files = get_supported_files()
    total_documents = 0
    total_chunks = 0
    total_stored = 0
    for file_path in supported_files:
        result = ingest_file(str(file_path))

        total_documents += result["document_count"]
        total_chunks += result["chunk_count"]
        total_stored += result["stored_count"]

        print(
            f"indexed {result['path']} "
            f"documents={result['document_count']} "
            f"chunks={result['chunk_count']} "
            f"stored={result['stored_count']}"
        )

    return {
        "file_count": len(supported_files),
        "document_count": total_documents,
        "chunk_count": total_chunks,
        "stored_count": total_stored,
    }

def main() -> None:
    result = build_index()

    print(
        f"done files={result['file_count']} "
        f"documents={result['document_count']} "
        f"chunks={result['chunk_count']} "
        f"stored={result['stored_count']}"
    )


if __name__ == "__main__":
    main()