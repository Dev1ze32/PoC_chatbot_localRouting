"""Knowledge-base length check (Increment 2's rule + the 8 GB training limit).

Every passage must fit two limits:
  - 512 tokens of the embedding model (bge-small-en-v1.5): beyond that, dense search silently
    ignores the rest of the passage (the manuscript's Increment 2 rule).
  - PASSAGE_LLAMA_MAX Llama 3.2 tokens: so that any 3 passages plus the system prompt, the
    question and the answer stay within the 2,048-token training row limit
    (training/build_sample_set.py, from the 8 GB feasibility test of 28 Sep).

Run:  python tools/check_passage_lengths.py      (from poc_thesis/; exits 1 if any passage is over)
"""
import json
import sys
from pathlib import Path

from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parent.parent
BGE_MAX = 512
PASSAGE_LLAMA_MAX = 480          # 3 x 480 + ~600 (system prompt, template, question, answer) ≈ 2,040

llama_file = ROOT / "training" / "llama32_tokenizer.json"
bge_file = next(Path.home().glob(".cache/huggingface/hub/models--BAAI--bge-small-en-v1.5/snapshots/*/tokenizer.json"), None)
if not llama_file.exists() or bge_file is None:
    sys.exit("need training/llama32_tokenizer.json and the cached bge-small-en-v1.5 tokenizer")
llama = Tokenizer.from_file(str(llama_file))
bge = Tokenizer.from_file(str(bge_file))
bge.no_truncation()

rows = [json.loads(line) for line in open(ROOT / "data" / "corpus_demo.jsonl", encoding="utf-8")]
over = []
lengths = []
for p in rows:
    b = len(bge.encode(p["text"]).ids)
    n = len(llama.encode(p["text"], add_special_tokens=False).ids)
    lengths.append(n)
    if b > BGE_MAX or n > PASSAGE_LLAMA_MAX:
        over.append((p["document_id"], b, n, p["page_or_section"]))

lengths.sort()
print(f"{len(rows)} passages · Llama tokens: median {lengths[len(lengths) // 2]}, "
      f"95th percentile {lengths[int(0.95 * len(lengths))]}, max {lengths[-1]}")
print(f"limits: embedding {BGE_MAX} tokens · Llama {PASSAGE_LLAMA_MAX} tokens")
if not over:
    print("all passages within both limits")
    sys.exit(0)
print(f"\n{len(over)} passage(s) over a limit (split them at the manual's own headings; never truncate):")
for pid, b, n, where in over:
    print(f"  {pid}  embedding {b:4d}  Llama {n:4d}  {where}")
sys.exit(1)
