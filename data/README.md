# data/

Records go in JSONL, lookup tables in JSON, vectors in NPY.

| File | Format | One line / entry is | Written by |
|---|---|---|---|
| `corpus_demo.jsonl` | JSONL | one citable passage (311) | `tools/build_demo_corpus.py` |
| `embeddings.npy` | NPY | row *i* = line *i* of `corpus_demo.jsonl` (311 × 384) | `tools/build_demo_corpus.py` |
| `office_exemplars.jsonl` | JSONL | one department's function statement, verbatim, Handbook pp. 22–27 (22) | `tools/build_office_exemplars.py` |
| `scope_exemplars.jsonl` | JSONL | one in-scope example question, with its source (25) | hand-written |
| `offices.json` | JSON | the closed office list: 6 divisions, 22 departments, aliases | `tools/build_office_exemplars.py` |
| `office_lookup.json` | JSON | 40 section → office rules, copied unchanged, `confirmed` flags kept | copied from `inputs/` |
| `MANIFEST.json` | JSON | hash, size and line count of every generated file | the tools |

## Why the knowledge base is JSONL

A knowledge base is a list of independent records, and JSONL stores it that way: one passage per line.

- **Line number = passage = vector row.** Line *i* of `corpus_demo.jsonl` is row *i* of `embeddings.npy`, and each record also carries `"row": i`, so the alignment can be checked line by line rather than trusted.
- **Adding a document means appending lines.** When a new manual is added, its passages go at the end and nothing already there is rewritten. The existing rows keep their numbers, so in principle only the new passages need embedding. (This demo's tool simply rebuilds all 311, which takes about two minutes.)
- **A broken record is one broken line.** A JSON array fails as a whole on one bad comma. In JSONL the reader reports `line 147` and every other passage is still readable.
- **You can read it without a program.** `wc -l` counts the passages, `grep` finds one, and a diff shows exactly which passages changed between two builds.
- **It streams.** A reader can process one passage at a time without loading the whole file. That doesn't matter at 311 passages, but it would for the full knowledge base.

JSONL files have no header, so build details (date, source hash, filter, embedding settings) are kept in `MANIFEST.json`, not inside the records.

**Pairing rule:** `MANIFEST.json` records the hash of the `corpus_demo.jsonl` that `embeddings.npy` was built from. If someone edits the JSONL without re-running the tool, the hashes stop matching and the data report fails. The alternative is the demo quietly citing the wrong passage.

`offices.json` stays JSON because it's a lookup table with nested parts (divisions → departments → aliases), not a list of records.
