# Retrieval Baseline - 2026-06-05

## Purpose

This report records the baseline retrieval quality for task 1.2 after adding
stricter retrieval metrics, but before changing retrieval strategy.
The current retriever is plain Qdrant similarity search with `top_k=7`.

## Command

Run from `/Users/mdiven/Code/Projects/AGENT/rag`:

```bash
conda run -n AI_DEV python -m rag_app.scripts.evaluate_retrieval
```

## Current Retrieval Strategy

Source: `rag/src/rag_app/retrieval/retriever.py`

```python
search_type="similarity"
search_kwargs={"k": effective_top_k}
```

Effective `top_k`: `7`

## Metrics

- `source_hit`: a case passes when the retrieved sources satisfy the case match mode.
- `all_source_hit`: for cases with `match="all"`, every expected source label must appear in the retrieved source list.
- `source_hit_rate`: `passed_cases / total_cases`.
- `first_hit_rank`: the 1-based rank of the first retrieved source matching any expected source label.
- `reciprocal_rank`: `1 / first_hit_rank`, or `0` when no expected source is retrieved.
- `mrr`: mean reciprocal rank across all cases.
- `expected_source_coverage`: `expected_source_hit_count / expected_source_total`.
- `average_expected_source_coverage`: mean expected source coverage across all cases.

This baseline uses the existing evaluator and case file:

- Cases: `rag/experiments/retrieval_eval_cases.json`
- Evaluator: `rag/src/rag_app/scripts/evaluate_retrieval.py`

## Summary

| Metric | Value |
|---|---:|
| Total cases | 11 |
| Passed cases | 11 |
| Failed cases | 0 |
| Source hit rate | 1.000 |
| MRR | 0.909 |
| Average expected source coverage | 1.000 |

Baseline result:

```text
summary: 11/11 passed
source_hit_rate: 1.000
mrr: 0.909
average_expected_source_coverage: 1.000
```

## Case Results

| Case | Match | Result | First hit rank | Reciprocal rank | Expected hit count | Coverage | Expected source labels | Retrieved source evidence |
|---|---|---|---:|---:|---:|---:|---|---|
| `gpt4_report_scope` | any | PASS | 1 | 1.000 | 1/1 | 1.000 | `gpt4_technical_report.pdf` | `data/raw/gpt4_technical_report.pdf` |
| `qdrant_usage` | any | PASS | 2 | 0.500 | 1/1 | 1.000 | `qdrant-docs.md` | `data/raw/qdrant-docs.md` |
| `langchain_usage` | any | PASS | 1 | 1.000 | 1/1 | 1.000 | `langchain` | `data/raw/03-langchain-README.md`, `data/raw/langchain-docs.md` |
| `rag_paper_definition` | any | PASS | 1 | 1.000 | 1/1 | 1.000 | `retrieval_augmented_generation_for_knowledge_intensive_nlp.pdf` | `data/raw/retrieval_augmented_generation_for_knowledge_intensive_nlp.pdf` |
| `qlora_memory` | any | PASS | 1 | 1.000 | 1/1 | 1.000 | `qlora_efficient_finetuning_of_quantized_llms.pdf` | `data/raw/qlora_efficient_finetuning_of_quantized_llms.pdf` |
| `lora_low_rank` | any | PASS | 1 | 1.000 | 1/1 | 1.000 | `lora_low_rank_adaptation_of_large_language_models.pdf` | `data/raw/lora_low_rank_adaptation_of_large_language_models.pdf` |
| `self_consistency_reasoning` | any | PASS | 1 | 1.000 | 1/1 | 1.000 | `self_consistency_improves_chain_of_thought_reasoning_in_language_models.pdf` | `data/raw/self_consistency_improves_chain_of_thought_reasoning_in_language_models.pdf` |
| `vllm_paged_attention` | any | PASS | 1 | 1.000 | 2/2 | 1.000 | `02-vllm-README.md`, `vllm-docs.md` | `data/raw/02-vllm-README.md`, `data/raw/vllm-docs.md` |
| `qdrant_chinese_paraphrase` | any | PASS | 2 | 0.500 | 1/1 | 1.000 | `qdrant-docs.md` | `data/raw/qdrant-docs.md` |
| `rag_memory_paraphrase` | any | PASS | 1 | 1.000 | 1/1 | 1.000 | `retrieval_augmented_generation_for_knowledge_intensive_nlp.pdf` | `data/raw/retrieval_augmented_generation_for_knowledge_intensive_nlp.pdf` |
| `langchain_llamaindex_comparison` | all | PASS | 1 | 1.000 | 2/2 | 1.000 | `langchain`, `llamaindex` | `data/raw/llamaindex-docs.md`, `data/raw/03-langchain-README.md` |

## Observations

1. The existing 11-case retrieval set is saturated for source-hit rate: all cases pass.
2. MRR exposes ranking quality that source-hit rate hides. Two Qdrant cases only hit the expected `qdrant-docs.md` source at rank 2.
3. Expected source coverage is also saturated at `1.000`, so it is useful as a regression guard rather than an improvement signal for the current case set.
4. The comparison case still reveals a useful signal: LlamaIndex sources rank above the LangChain source, but both expected labels appear within top 7.

## Top-k Comparison - 2026-06-06

This comparison keeps the same retriever strategy (`similarity`) and only changes
the number of returned documents. It was run by calling `get_retriever(top_k=...)`
directly, without changing `retriever.py` or project configuration.

| Top k | Passed | Source hit rate | MRR | Average expected source coverage |
|---:|---:|---:|---:|---:|
| 7 | 11/11 | 1.000 | 0.909 | 1.000 |
| 3 | 10/11 | 0.909 | 0.909 | 0.955 |

`top_k=3` failed one case:

| Case | Match | Expected hit count | Coverage | Top 3 retrieved sources |
|---|---|---:|---:|---|
| `langchain_llamaindex_comparison` | all | 1/2 | 0.500 | `data/raw/llamaindex-docs.md`, `data/raw/llamaindex-docs.md`, `data/raw/aiapp-03-llamaindex-readme.md` |

Interpretation:

1. `top_k=3` does not reduce MRR because the first expected source is still at rank 1.
2. `top_k=3` does reduce coverage because the `match="all"` comparison case needs both `llamaindex` and `langchain`, but only LlamaIndex-related sources appear in the top 3.
3. This shows why MRR alone is insufficient for this project: it rewards the first relevant hit, but it does not tell whether all required sources were retrieved.

## Recommended Next Step

Keep `top_k=7` for now. The current evidence does not support reducing retrieval
context to `top_k=3`.

The next retrieval optimization should focus on reducing repeated sources and
improving diversity while preserving expected source coverage. A reasonable next
experiment is MMR or source-diversified reranking, measured against this baseline.
