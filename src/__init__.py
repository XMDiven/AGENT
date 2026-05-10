"""Compatibility package for running RAG source imports from the AGENT root."""

from pathlib import Path

__path__ = [str(Path(__file__).resolve().parents[1] / "rag" / "src")]
