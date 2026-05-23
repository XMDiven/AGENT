def run_summary_tool(text: str, max_chars: int = 200) -> dict[str, str]:
    normalized_text = " ".join(text.split())

    if not normalized_text:
        return {
            "summary": "No text provided for summarization.",
        }

    if len(normalized_text) <= max_chars:
        return {
            "summary": normalized_text,
        }

    return {
        "summary": normalized_text[:max_chars].rstrip() + "...",
    }
