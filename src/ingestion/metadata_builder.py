from typing import Any


def build_section_path(header_metadata: dict[str, Any]) -> str:
    titles: list[str] = []

    for key in ("h1", "h2", "h3"):
        value = header_metadata.get(key)
        if isinstance(value, str):
            stripped_value = value.strip()
            if stripped_value:
                titles.append(stripped_value)

    return " > ".join(titles)


def build_markdown_metadata(
    document_metadata: dict[str, Any],
    header_metadata: dict[str, Any],
) -> dict[str, Any]:
    merged_metadata: dict[str, Any] = {
        **document_metadata,
        **header_metadata,
    }
    merged_metadata["doc_type"] = "markdown"
    merged_metadata["section_path"] = build_section_path(header_metadata)

    return merged_metadata
