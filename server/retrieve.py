"""Hybrid retrieval: BM25 (stemmed) + dense (bge-small) fused by RRF.

The BM25 index is built here, in memory, from data/corpus_demo.jsonl. It uses
shared/tokenizer.py, the same tokenizer the data report measured with.
At start-up the embeddings are checked against the corpus they were built
from (MANIFEST.json pairing hash), so a stale matrix can't cite the wrong passage.
"""
import hashlib
import json
import sys
import time

import numpy as np

from server import config

sys.path.insert(0, str(config.ROOT))
from shared.tokenizer import tokenize  # noqa: E402


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


class Retriever:
    def __init__(self):
        from rank_bm25 import BM25Okapi
        from sentence_transformers import SentenceTransformer

        corpus_path = config.DATA / "corpus_demo.jsonl"
        manifest = json.load(open(config.DATA / "MANIFEST.json", encoding="utf-8"))["files"]
        if manifest["embeddings.npy"]["built_from_sha256"] != _sha256(corpus_path):
            raise RuntimeError("embeddings.npy was not built from the current corpus_demo.jsonl. "
                               "Re-run tools/build_demo_corpus.py.")
        self.passages = [json.loads(line) for line in open(corpus_path, encoding="utf-8")]
        assert all(p["row"] == i for i, p in enumerate(self.passages)), "row misaligned"
        self.matrix = np.load(config.DATA / "embeddings.npy")
        assert self.matrix.shape[0] == len(self.passages)

        self.bm25 = BM25Okapi([tokenize(p["text"]) for p in self.passages], **config.BM25)
        self.model = SentenceTransformer(config.EMBED_MODEL, device=config.EMBED_DEVICE)

    def embed(self, text, instruction=True):
        t = (config.QUERY_INSTRUCTION + text) if instruction else text
        return self.model.encode([t], normalize_embeddings=True, show_progress_bar=False)[0]

    def search(self, question):
        timings = {}
        t0 = time.perf_counter()
        qvec = self.embed(question, instruction=True)
        timings["embed"] = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        tokens = tokenize(question)
        # A question made only of stopwords has no tokens: no lexical evidence.
        bm = self.bm25.get_scores(tokens) if tokens else np.zeros(len(self.passages))
        timings["lexical"] = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        dense = self.matrix @ qvec
        timings["dense"] = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        rank_bm = list(np.argsort(-bm)[:config.CANDIDATES_EACH]) if tokens else []
        rank_dn = list(np.argsort(-dense)[:config.CANDIDATES_EACH])
        rrf = {}
        for r, i in enumerate(rank_bm):
            rrf[i] = rrf.get(i, 0.0) + 1.0 / (config.RRF_K + r + 1)
        for r, i in enumerate(rank_dn):
            rrf[i] = rrf.get(i, 0.0) + 1.0 / (config.RRF_K + r + 1)
        fused = sorted(rrf, key=lambda i: -rrf[i])[:config.PASSAGES_TO_MODEL]
        timings["fuse"] = (time.perf_counter() - t0) * 1000

        return {
            "tokens": tokens,
            "bm25_top": float(bm.max()) if tokens else 0.0,
            "bm25_top_id": self.passages[rank_bm[0]]["document_id"] if tokens else None,
            "cosine_top": float(dense.max()),
            "cosine_top_id": self.passages[rank_dn[0]]["document_id"],
            "fused": [{"row": int(i),
                       "passage_id": self.passages[i]["document_id"],
                       "rrf": round(rrf[i], 5),
                       "bm25_rank": rank_bm.index(i) + 1 if i in rank_bm else None,
                       "dense_rank": rank_dn.index(i) + 1 if i in rank_dn else None}
                      for i in fused],
            "timings": timings,
        }
