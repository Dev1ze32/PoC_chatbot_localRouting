# Routing demo — proof of concept

Panel revision item 1: show what the query routing pipeline returns for a cited answer, an office referral, and an out-of-scope message. Not the prototype: no fine-tuning, no quantization, no generation model. The plan is in `IMPLEMENTATION_PLAN.md`, and progress is in `SPRINTS.md`.

**Rebuild the data (Sprint 1)**, from `tools/`:

```
python build_demo_corpus.py        # inputs/corpus.json -> data/corpus_demo.jsonl + data/embeddings.npy
python build_office_exemplars.py   # handbook pp. 22-27 -> data/offices.json + data/office_exemplars.jsonl
python make_data_report.py         # -> docs/DATA_REPORT.md  (review this)
```

`shared/tokenizer.py` is the one BM25 tokenizer (regex + stopwords + Snowball stemming). There is no BM25 index file: the index is built in memory from `data/corpus_demo.jsonl`. `inputs/` holds copies of the old material, taken once. Nothing here reads from `ai_context/`.
