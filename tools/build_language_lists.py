"""Gate 0 data: data/english_words.txt from the SCOWL English list.

    inputs/american-english.txt  ->  data/english_words.txt

Keeps lowercase, letters-only entries. Dropping capitalised entries removes
names ("Ang", "Rosa") that would otherwise count as English. Also proposes
university-term candidates from the manuals for human review. It never adds
them automatically: the manuals contain "ng" and "sa" ("Pamantasan ng
Cabuyao"), and adding those would let Tagalog through.
"""
from collections import Counter

from common import DATA, INPUTS, read_jsonl, update_manifest

SRC = INPUTS / "american-english.txt"


def main():
    raw = [w.strip() for w in SRC.read_text(encoding="utf-8").splitlines()]
    words = sorted({w for w in raw if w and w == w.lower() and w.isalpha()} | {"i", "a"})
    (DATA / "english_words.txt").write_text("\n".join(words) + "\n", encoding="utf-8", newline="\n")
    update_manifest("english_words.txt",
                    what="Gate 0 English word list (lowercase, letters only)",
                    tool="tools/build_language_lists.py",
                    source="inputs/american-english.txt (SCOWL via Ubuntu wamerican 2020.12.07-2)",
                    license="inputs/american-english.COPYRIGHT.txt")
    print(f"{len(words):,} English words (from {len(raw):,} entries)")

    english = set(words)
    counts = Counter()
    for p in read_jsonl(DATA / "corpus_demo.jsonl"):
        for w in p["text"].replace("’", "'").split():
            w = "".join(ch for ch in w.lower() if ch.isalpha())
            if len(w) >= 2 and w not in english:
                counts[w] += 1
    print("Top non-English words in the manuals (candidates for university_terms; REVIEW, never auto-add):")
    print("  " + ", ".join(f"{w} ({n})" for w, n in counts.most_common(40)))


if __name__ == "__main__":
    main()
