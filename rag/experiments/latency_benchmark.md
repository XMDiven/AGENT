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

| case_id | duration_seconds | answer_length | source_count |
|---|---:|---:|---:|
| rag_definition | 21.18 | 270 | 7 |
| qdrant_usage | 18.47 | 359 | 7 |
| langchain_usage | 27.42 | 330 | 7 |

## Summary

- Total cases: 3
- Average duration: 22.36 seconds
- Max duration: 27.42 seconds
- Min duration: 18.47 seconds

## Notes

This result is slow for a user-facing question-answering API and should not be used to claim a 2-second average latency.

The benchmark measures the full online RAG path, so LLM generation latency is included. Further optimization should split retrieval time and generation time before changing retrieval parameters.
