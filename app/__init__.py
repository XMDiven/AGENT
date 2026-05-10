"""Compatibility package for running the RAG app from the AGENT root."""

from pathlib import Path

__path__ = [str(Path(__file__).resolve().parents[1] / "rag" / "app")]
