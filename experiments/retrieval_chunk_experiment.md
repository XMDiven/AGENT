# Retrieval Chunk Experiment

| Run | CHUNK_SIZE | CHUNK_OVERLAP | chunks | stored | retrieval_eval | Notes |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| baseline | 200 | 30 | 12268 | 12268 | 8/8 passed | Expanded golden cases all hit expected sources. |
| variant-1 | 400 | 50 | 5371 | 5369 | 8/8 passed | Chunk count dropped sharply while all golden cases still hit expected sources. |
| variant-2 | 800 | 100 | 2779 | 2777 | 8/8 passed | Largest tested chunks kept source hits while reducing index size further. |
