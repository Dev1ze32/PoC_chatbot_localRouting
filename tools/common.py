"""Shared paths and embedding settings for the Sprint 1 data tools.

Every tool reads from inputs/ and writes to data/ or docs/. Nothing here reads
from any folder outside poc_thesis/.
"""
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))   # so tools can import shared/ (the tokenizer)
INPUTS = ROOT / "inputs"
DATA = ROOT / "data"
DOCS = ROOT / "docs"

HANDBOOK_PDF = INPUTS / "UC-PnC-Student-Handbook-Manual.pdf"
MANIFEST = DATA / "MANIFEST.json"

# Embedding settings. Passages are embedded WITHOUT an instruction; a query
# gets BGE's retrieval instruction when it is matched against passages or
# office statements (short question -> longer text). Query vs scope exemplar
# is question -> question, so neither side gets the instruction.
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
EMBED_DEVICE = "cpu"
EMBED_DIM = 384
QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "
EMBED_SETTINGS = {
    "model": EMBED_MODEL,
    "device": EMBED_DEVICE,
    "dim": EMBED_DIM,
    "normalize_embeddings": True,
    "passage_instruction": None,
    "query_instruction": QUERY_INSTRUCTION,
    "query_instruction_applies_to": ["query vs passages",
                                     "query vs office statements"],
    "no_instruction_for": ["query vs scope exemplars (question vs question)"],
}

# BM25 is not stored as a file. It is built in memory, at start-up, from the
# `text` field of corpus_demo.jsonl, using shared/tokenizer.py. 311 passages
# index in milliseconds; a stored copy would only be one more thing to go stale.
BM25_SETTINGS = {"library": "rank_bm25", "variant": "BM25Okapi",
                 "k1": 1.5, "b": 0.75, "epsilon": 0.25,
                 "built_from": "corpus_demo.jsonl `text`, in memory at start-up"}


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def write_jsonl(path, records):
    """One JSON object per line, UTF-8, '\\n' endings, no header, no blank lines."""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def read_jsonl(path):
    """Strict reader. A bad line fails loudly with its line number, and only
    that line is suspect. That is half the reason the knowledge base is JSONL."""
    records = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                raise ValueError(f"{path.name} line {n}: blank line")
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path.name} line {n}: {e}") from None
            if not isinstance(obj, dict):
                raise ValueError(f"{path.name} line {n}: not a JSON object")
            records.append(obj)
    return records


def update_manifest(filename, **fields):
    """Record what a tool wrote: its hash, size and (for JSONL) line count.
    Build metadata lives here, not inside the record files."""
    m = load_json(MANIFEST) if MANIFEST.exists() else {
        "note": "Written by the tools in tools/. One entry per generated file. "
                "Hand-written files (scope_exemplars.jsonl) and copied inputs "
                "(office_lookup.json) are not listed; see data/README.md.",
        "files": {}}
    path = DATA / filename
    entry = m["files"].get(filename, {})
    entry.update(fields)
    entry["sha256"] = sha256(path)
    entry["bytes"] = path.stat().st_size
    if path.suffix == ".jsonl":
        with open(path, encoding="utf-8") as f:
            entry["records"] = sum(1 for _ in f)
    m["files"][filename] = dict(sorted(entry.items()))
    m["updated"] = date.today().isoformat()
    save_json(MANIFEST, m)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def build_bm25(passages):
    from rank_bm25 import BM25Okapi
    from shared.tokenizer import tokenize
    s = BM25_SETTINGS
    return BM25Okapi([tokenize(p["text"]) for p in passages],
                     k1=s["k1"], b=s["b"], epsilon=s["epsilon"])


def load_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMBED_MODEL, device=EMBED_DEVICE)


def embed(model, texts, query=False):
    import numpy as np
    if query:
        texts = [QUERY_INSTRUCTION + t for t in texts]
    vecs = model.encode(list(texts), normalize_embeddings=True,
                        batch_size=32, show_progress_bar=False)
    return np.asarray(vecs, dtype=np.float32)
