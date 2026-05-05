# AGENTS.md

## Purpose

This file defines project-specific instructions for this RAG learning project.

Global collaboration rules, such as Chinese explanations, step-by-step guidance, simplicity first, surgical changes, and goal-driven execution, are defined in the global `.codex/AGENTS.md`.

This project-level file focuses on the repository context, technical stack, environment, implementation standards, RAG-specific guidance, and resume-alignment workflow.

## Project Overview

This repository is a learning-focused RAG project for exploring the full AI application pipeline:

document ingestion -> embedding -> retrieval -> generation.

The project prioritizes:

- clarity,
- modern mainstream practices,
- incremental learning,
- verifiable progress,
- resume-relevant engineering value,
- and avoiding premature abstraction.

The goal is not only to build a working RAG app, but also to understand and demonstrate the engineering decisions behind it.

## Default Tech Choices

- Backend framework: FastAPI
- RAG framework: LangChain with LCEL
- Local vector store: Chroma
- Cloud vector store: Qdrant
- Python version: 3.11+
- TypeScript is only used when Python is clearly a better fit for the task than Python.

Do not replace these defaults unless the user explicitly asks or there is a strong technical reason.

If a different tool or framework is considered, explain:

1. why the current default is insufficient,
2. what the alternative improves,
3. what trade-off it introduces.

## Environment

- Always use the conda environment: `AI_DEV`.
- Activate it with:

  ```bash
  conda activate AI_DEV