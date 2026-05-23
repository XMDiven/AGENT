# Latency Benchmark

## Environment

- Date: 2026-05-23
- Runtime: local development
- Vector store: Qdrant
- Entry point: `python -m rag_app.scripts.benchmark_latency`
- Top-K override: `python -m rag_app.scripts.benchmark_latency --top-k 3`
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

### Baseline: top_k = 7

| case_id | total_duration_seconds | retrieval_duration_seconds | generation_duration_seconds |
|---|---:|---:|---:|
| rag_definition | 23.03 | 1.15 | 21.87 |
| qdrant_usage | 29.08 | 0.24 | 28.83 |
| langchain_usage | 26.29 | 0.28 | 26.00 |

Summary:

- Total cases: 3
- Top-K: 7
- Average duration: 26.13 seconds
- Max duration: 29.08 seconds
- Min duration: 23.03 seconds

### Experiment: top_k = 3

| case_id | total_duration_seconds | retrieval_duration_seconds | generation_duration_seconds |
|---|---:|---:|---:|
| rag_definition | 34.66 | 1.98 | 32.67 |
| qdrant_usage | 18.40 | 0.24 | 18.15 |
| langchain_usage | 22.08 | 0.55 | 21.52 |

Summary:

- Total cases: 3
- Top-K: 3
- Average duration: 25.05 seconds
- Max duration: 34.66 seconds
- Min duration: 18.40 seconds

## Notes

This result is slow for a user-facing question-answering API and should not be used to claim a 2-second average latency.

The benchmark now records retrieval and generation durations separately. Current results show that latency is dominated by LLM generation in both runs, while vector retrieval stays below 2 seconds in these cases.

Reducing Top-K from 7 to 3 did not produce a clear, stable latency improvement in this small run. The average total duration dropped from 26.13 seconds to 25.05 seconds, but `rag_definition` became slower. The next optimization should focus on generation-side controls, such as prompt/output length or context token budget, rather than retrieval speed.
