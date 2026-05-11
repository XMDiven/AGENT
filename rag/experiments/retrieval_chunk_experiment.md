# Retrieval Chunk Experiment

| Run | CHUNK_SIZE | CHUNK_OVERLAP | chunks | stored | retrieval_eval | Notes |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| baseline | 200 | 30 | 12268 | 12268 | 8/8 passed | Expanded golden cases all hit expected sources. |
| variant-1 | 400 | 50 | 5371 | 5369 | 8/8 passed | Chunk count dropped sharply while all golden cases still hit expected sources. |
| variant-2 | 800 | 100 | 2779 | 2777 | 8/8 passed | Largest tested chunks kept source hits while reducing index size further. |

## Retrieval Top-K Experiment

| Run | RETRIEVAL_TOP_K | retrieval_eval | answer_eval | Notes |
| --- | ---: | --- | --- | --- |
| baseline | 2 | 10/11 passed | not run | Multi-source comparison missed the LangChain source. |
| variant-1 | 5 | 11/11 passed | 11/11 passed | Higher recall covered both LangChain and LlamaIndex with acceptable answer quality. |
| variant-2 | 7 | 11/11 passed | 11/11 passed | Restored multi-source comparison after the expanded corpus; retrieves both LangChain and LlamaIndex. |

Conclusion: `RETRIEVAL_TOP_K = 7` is the current verified baseline. It restores multi-source recall for the expanded corpus while keeping the current answer evaluation green.
