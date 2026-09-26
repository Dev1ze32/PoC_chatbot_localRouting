"""Sprint 1: filter the corpus and embed it.

    inputs/corpus.json  ->  data/corpus_demo.jsonl  one passage per line
                            data/embeddings.npy     row i = line i
                            data/MANIFEST.json      counts, hashes, settings

Rule (IMPLEMENTATION_PLAN.md §6.1): keep a passage only if its page_or_section
carries a '>' breadcrumb, i.e. it sits under a numbered chapter and section.

Each record carries its own `row`, so line i of the JSONL, row i of the matrix
and the record's `row` field must all agree. The manifest stores the hash of
the JSONL the matrix was built from, so an edited JSONL with a stale matrix is
caught instead of silently citing the wrong passage.
"""
import numpy as np

from common import (BM25_SETTINGS, DATA, EMBED_DIM, EMBED_SETTINGS, INPUTS, embed,
                    load_json, load_model, sha256, update_manifest,
                    write_jsonl)
from shared.tokenizer import describe as tokenizer_description

SRC = INPUTS / "corpus.json"
FIELDS = ["row", "document_id", "title", "source", "revision_date", "year",
          "page_or_section", "issuing_office", "text"]


def is_policy(passage):
    return ">" in passage["page_or_section"]


def main():
    passages = load_json(SRC)["passages"]
    kept = [p for p in passages if is_policy(p)]
    excluded = [p for p in passages if not is_policy(p)]

    ids = [p["document_id"] for p in kept]
    assert len(ids) == len(set(ids)), "duplicate document_id in kept passages"
    records = [{"row": i, **{k: p[k] for k in FIELDS[1:]}}
               for i, p in enumerate(kept)]

    model = load_model()
    matrix = embed(model, [r["text"] for r in records])
    assert matrix.shape == (len(records), EMBED_DIM), matrix.shape

    DATA.mkdir(exist_ok=True)
    write_jsonl(DATA / "corpus_demo.jsonl", records)
    np.save(DATA / "embeddings.npy", matrix)

    update_manifest(
        "corpus_demo.jsonl",
        what="Knowledge base: one citable passage per line",
        tool="tools/build_demo_corpus.py",
        source="inputs/corpus.json", source_sha256=sha256(SRC),
        filter="keep if '>' in page_or_section (front matter removed)",
        fields=FIELDS, key="document_id",
        bm25={**BM25_SETTINGS, "tokenizer": tokenizer_description()},
        source_records=len(passages), excluded=len(excluded),
        excluded_ids=[p["document_id"] for p in excluded])
    update_manifest(
        "embeddings.npy",
        what="Passage vectors for dense retrieval",
        tool="tools/build_demo_corpus.py",
        shape=list(matrix.shape), dtype=str(matrix.dtype),
        row_order="row i = line i of corpus_demo.jsonl = record with row == i",
        built_from="corpus_demo.jsonl",
        built_from_sha256=sha256(DATA / "corpus_demo.jsonl"),
        embedding=EMBED_SETTINGS)
    print(f"kept {len(kept)} / {len(passages)}, excluded {len(excluded)}")
    print(f"embeddings {matrix.shape} {matrix.dtype}")


if __name__ == "__main__":
    main()
