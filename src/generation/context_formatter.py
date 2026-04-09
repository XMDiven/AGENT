from langchain_core.documents import Document


def format_context(documents : list[Document]) -> str:
    blocks :list[str] = []
    for index , doc in enumerate(documents , start=1):
        source = doc.metadata.get("source" , "unknown")
        section_path = doc.metadata.get("section_path" , "unknown")
        page_content = doc.page_content
        blocks.append(
            f"""[{index}]\nsource:{source}\nsection_path:{section_path}\npage_content:{page_content}"""
        )

    return "\n\n".join(blocks)