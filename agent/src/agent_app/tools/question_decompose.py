def has_decomposition_signal(question: str) -> bool:
    normalized_question = f" {question.strip().lower()} "

    if any(keyword in question for keyword in ("分别", "对比", "比较")):
        return True

    if any(
        keyword in normalized_question
        for keyword in (" compare ", " difference", " differences", " vs ")
    ):
        return True

    has_multiple_subjects = any(
        separator in question for separator in ("和", "与", "、")
    )
    has_comparison_hint = any(
        keyword in question for keyword in ("区别", "不同", "适合")
    )

    return has_multiple_subjects and has_comparison_hint


def split_subjects(text: str) -> list[str]:
    cleaned_text = text.strip(" ，,：:")

    for separator in (" 和 ", " 与 ", "和", "与", "、", " vs ", " VS ", " and "):
        parts = [
            part.strip(" ，,：:")
            for part in cleaned_text.split(separator)
            if part.strip(" ，,：:")
        ]

        if len(parts) >= 2:
            return parts

    return []


def run_question_decompose_tool(question: str) -> dict[str, object]:
    normalized_question = " ".join(question.strip().split())

    if not normalized_question:
        return {
            "sub_questions": [],
            "reason": "empty question",
            "decomposition_strategy": "none",
        }

    if "分别" in normalized_question:
        subject_text, suffix = normalized_question.split("分别", 1)
        subjects = split_subjects(subject_text)

        if subjects and suffix.strip():
            return {
                "sub_questions": [
                    f"{subject} {suffix.strip()}" for subject in subjects
                ],
                "reason": "question contains explicit multi-part intent",
                "decomposition_strategy": "comparison",
            }

    return {
        "sub_questions": [normalized_question],
        "reason": "question contains comparison intent but no safe split pattern",
        "decomposition_strategy": "comparison",
    }
