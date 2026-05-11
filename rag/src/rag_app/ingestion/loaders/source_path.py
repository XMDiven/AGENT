from pathlib import Path

from rag_app.config import config


def to_project_relative_source(path: str | Path) -> str:
    resolved_path = Path(path).resolve()
    project_root = config.PROJECT_ROOT.resolve()

    try:
        return resolved_path.relative_to(project_root).as_posix()
    except ValueError:
        return resolved_path.as_posix()
