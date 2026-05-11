from importlib.util import find_spec
from pathlib import Path


def has_import_spec(module_name: str) -> bool:
    try:
        return find_spec(module_name) is not None
    except ModuleNotFoundError:
        return False


def test_rag_app_is_importable_as_named_application_package() -> None:
    import rag_app

    package_root = Path(rag_app.__file__).resolve().parent

    assert package_root.name == "rag_app"
    assert package_root.parent.name == "src"


def test_workspace_root_does_not_define_legacy_import_shims() -> None:
    workspace_root = Path(__file__).resolve().parents[2]

    assert not (workspace_root / "src" / "__init__.py").exists()
    assert not (workspace_root / "app" / "__init__.py").exists()
    assert not (workspace_root / "config" / "__init__.py").exists()


def test_legacy_src_package_is_not_the_application_import_path() -> None:
    assert has_import_spec("rag_app.services.ask_service")
    assert not has_import_spec("src.services.ask_service")
