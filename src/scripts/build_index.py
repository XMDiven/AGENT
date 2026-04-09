from pathlib import Path
from src.services.ingest_service import ingest_markdown_file
from config import config
def get_markdown_files() ->list[Path]:
    raw_data_dir = config.RAW_DATA_DIR
    return sorted(raw_data_dir.glob("*.md"))


def build_index():
    markdown_files = get_markdown_files()
    total_documents = 0
    total_chunks = 0
    total_stored = 0
    for file_path in markdown_files:
        result = ingest_markdown_file(str(file_path))

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
        "file_count": len(markdown_files),
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