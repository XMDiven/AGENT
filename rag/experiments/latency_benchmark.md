# Latency Benchmark

## Environment

- Date: 2026-05-23
- Runtime: local development
- Vector store: Qdrant
- Entry point: `python -m rag_app.scripts.benchmark_latency`
- Measurement scope: full `ask_question()` path

## Method

The benchmark runs fixed questions through the online RAG question-answering flow.

Measured duration includes:

- query analysis
- retrieval planning
- vector retrieval
- context formatting
- LLM answer generation

## Results

| case_id | total_duration_seconds | retrieval_duration_seconds | generation_duration_seconds |
|---|---:|---:|---:|
| rag_definition | 23.03 | 1.15 | 21.87 |
| qdrant_usage | 29.08 | 0.24 | 28.83 |
| langchain_usage | 26.29 | 0.28 | 26.00 |

## Summary

- Total cases: 3
- Average duration: 26.13 seconds
- Max duration: 29.08 seconds
- Min duration: 23.03 seconds

## Notes

This result is slow for a user-facing question-answering API and should not be used to claim a 2-second average latency.

The benchmark now records retrieval and generation durations separately. Current results show that latency is dominated by LLM generation, while vector retrieval is below 1.2 seconds in these cases.
