"""Gate 0 · Initial check test. Two parts, one report:

    0a  Language      data/language_test.jsonl        -> shared/language.py
    0b  One question  data/question_split_test.jsonl  -> shared/questions.py

    -> docs/INITIAL_CHECK_REPORT.md   (generated; do not edit by hand)

Each part also reads a *_heldout.jsonl file when it exists: messages written
by classmates who have NOT seen the rules. That result is the number to
report; the main sets were written by the same person who tuned the rules.
"""
import collections
import json
import statistics
import time
from datetime import date

from common import DATA, DOCS, ROOT, read_jsonl
from server import config
from shared import language, questions

PH_FUNCTION_WORDS = ["sa", "ng", "ang", "mga", "po", "ko", "ako", "ba", "na", "pa", "yung", "ug", "asa",
                     "unsa", "pila", "ti", "iti", "nga", "dagiti", "sang", "diin", "kahit", "wala", "may",
                     "din", "rin", "si", "ni", "kay", "ano", "pano", "paano", "saan", "sino", "mag", "pag",
                     "para", "kung", "at", "to", "man", "ka", "mano"]


def run(rows, cutoff):
    out = []
    for r in rows:
        res = language.check(r["question"], cutoff, config.LANGUAGE_TYPO_TOLERANCE)
        got = "english" if res["english"] else "notice"
        out.append({**r, "got": got, "ok": got == r["expected"], "res": res})
    return out


def table(w, results, title):
    by = collections.OrderedDict()
    for x in results:
        g = by.setdefault(x["group"], [0, 0])
        g[0] += x["ok"]
        g[1] += 1
    w(f"### {title}")
    w("")
    w("| Group | Expected | Correct |")
    w("|---|---|---:|")
    exp = {x["group"]: x["expected"] for x in results}
    for g, (ok, n) in by.items():
        w(f"| {g} | {'pass as English' if exp[g] == 'english' else 'notice'} | {ok} / {n} |")
    tot = sum(x["ok"] for x in results)
    w(f"| **All** | | **{tot} / {len(results)}** |")
    w("")
    misses = [x for x in results if not x["ok"]]
    if misses:
        w("**Misses:**")
        w("")
        for x in misses:
            r = x["res"]
            w(f"- *{x['question']}* ({x['group']}): expected **{x['expected']}**, got **{x['got']}**. "
              f"English share {r['share']:.0%}; not recognised: {', '.join(r['not_recognised']) or '—'}.")
    else:
        w("No misses.")
    w("")


def main():
    cutoff = config.LANGUAGE_CUTOFF
    main_rows = read_jsonl(DATA / "language_test.jsonl")
    held_path = DATA / "language_test_heldout.jsonl"
    held_rows = read_jsonl(held_path) if held_path.exists() else []
    results = run(main_rows, cutoff)
    english = set((DATA / "english_words.txt").read_text(encoding="utf-8").split())

    # timing (lists already loaded by the run above)
    qs = [r["question"] for r in main_rows]
    t = []
    for _ in range(20):
        for q in qs:
            a = time.perf_counter()
            language.check(q, cutoff)
            t.append((time.perf_counter() - a) * 1000)

    en_shares = [x["res"]["share"] for x in results if x["expected"] == "english"]
    no_shares = [x["res"]["share"] for x in results if x["expected"] == "notice"]

    out = []
    w = out.append
    w("# Gate 0 · Initial check — report")
    w("")
    w(f"Generated {date.today().isoformat()} by `tools/test_initial_check.py`. Do not edit by hand.")
    w("")
    w("Gate 0 runs two quick checks before any search: **0a** is the question in English, and **0b** "
      "is it one question. Either fails → a friendly notice, no search, 0 model calls. "
      "Code: `shared/initial_check.py`.")
    w("")
    w("# Part A · 0a Language")
    w("")
    w(f"**Rule:** confirm English, don't identify other languages. Alphabet check, then the share of words "
      f"found in the English word list ({len(english):,} words, SCOWL) must be **≥ {cutoff:.0%}**. "
      f"Acronyms in capitals, university terms and the university's own names are set aside. "
      f"Typo tolerance is **{'on' if config.LANGUAGE_TYPO_TOLERANCE else 'off'}**. Code: `shared/language.py`.")
    w("")
    w("> **Read this before quoting any number below.** The main test set was written by Claude, and the "
      "university-name and chat-shorthand lists were added *after* seeing misses on this same set, so its score is "
      "optimistic. The Bisaya, Ilocano and Hiligaynon questions are drafts, not native-speaker text. The number to "
      "report is the **held-out** result (§2), from questions written by people who have not seen the rule.")
    w("")
    w("## 1. Main test set")
    w("")
    table(w, results, f"At the {cutoff:.0%} cut-off ({len(results)} questions)")
    w("### The gap between English and everything else")
    w("")
    w(f"- English questions: English share **{min(en_shares):.0%} – {max(en_shares):.0%}**")
    w(f"- Every other question: **{min(no_shares):.0%} – {max(no_shares):.0%}**")
    top_non = sorted([x for x in results if x['expected'] == 'notice'], key=lambda x: -x["res"]["share"])[:3]
    w("- The non-English questions that look *most* English, which are the hard cases: "
      + "; ".join(f"*{x['question']}* ({x['res']['share']:.0%})" for x in top_non))
    w("")
    w("### Every cut-off, for the record")
    w("")
    w("| Cut-off | English passed | Non-English stopped |")
    w("|---:|---:|---:|")
    for c in (0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95):
        rr = run(main_rows, c)
        e = [x for x in rr if x["expected"] == "english"]
        n = [x for x in rr if x["expected"] == "notice"]
        mark = " ← in use" if abs(c - cutoff) < 1e-9 else ""
        w(f"| {c:.0%}{mark} | {sum(x['ok'] for x in e)} / {len(e)} | {sum(x['ok'] for x in n)} / {len(n)} |")
    w("")
    w("Choosing rule, in priority order: (1) never stop a real English question, (2) stop all non-English, "
      "(3) stop as much Taglish as possible.")
    w("")
    w("## 2. Held-out test set (the number to report)")
    w("")
    if held_rows:
        table(w, run(held_rows, cutoff), f"Held-out ({len(held_rows)} questions)")
    else:
        w("**Not done yet.** Ask 3–5 classmates to each write about 10 questions in their own way (English, "
          "Taglish, their home language) **without seeing this rule or the word lists**. Save them to "
          "`data/language_test_heldout.jsonl`, one per line: "
          '`{"group": "Bisaya", "question": "...", "expected": "notice", "written_by": "<name>"}`. '
          "Then re-run this tool.")
    w("")
    w("## 3. Cost")
    w("")
    w(f"- Per question: **{statistics.mean(t):.2f} ms** average, {max(t):.2f} ms worst "
      f"({len(t):,} checks). No model, no network.")
    w("- The English word list takes about 8 MB of memory and loads once at start-up.")
    w("- A question that gets the notice skips the search and the model, so it is *faster* than before.")
    w("")
    w("## 4. Checks on the lists themselves")
    w("")
    leaked = [x for x in PH_FUNCTION_WORDS if x in english]
    w(f"- Philippine function words that are also real English words: {', '.join(f'`{x}`' for x in leaked)}. "
      "These are genuine English words (\"at\", \"to\", \"may\", \"man\"), so they stay. The rule looks at the "
      "share of all the words, so one shared word can't make a Tagalog question pass.")
    terms = json.loads((DATA / "language_terms.json").read_text(encoding="utf-8"))
    w(f"- `language_terms.json` status: *{terms['status']}* {len(terms['university_phrases'])} phrases, "
      f"{len(terms['university_terms'])} university terms, {len(terms['chat_shorthand'])} chat shorthand.")
    w("- **Why university terms are never taken automatically from the manuals:** the manuals' most frequent "
      "non-English words include **\"ng\"**, from \"Pamantasan ng Cabuyao\". Auto-adding them would let Tagalog "
      "through. `tools/build_language_lists.py` prints candidates for a human to review.")
    w("")
    w("### Typo tolerance: what it costs and what it buys")
    w("")
    lenient = run(main_rows, cutoff)
    strict = [language.check(r["question"], cutoff, False) for r in main_rows]
    rescued = [x["question"] for x, st in zip(lenient, strict)
               if x["expected"] == "english" and x["res"]["english"] and not st["english"]]
    helped_foreign = [(x, st) for x, st in zip(lenient, strict)
                      if x["expected"] == "notice" and x["res"]["typo_matches"]]
    flipped_wrong = [x["question"] for x, st in zip(lenient, strict)
                     if x["expected"] == "notice" and x["res"]["english"] and not st["english"]]
    w(f"- **Buys:** {len(rescued)} real English question(s) pass only because of it: "
      + ("; ".join(f"*{q}*" for q in rescued) or "none") + ".")
    w(f"- **Costs:** {len(helped_foreign)} non-English question(s) had a word accepted as an English typo "
      "(it is one letter away from an English word), which raised their score: "
      + "; ".join(f"*{x['question']}* ({', '.join(x['res']['typo_matches'])}: {st['share']:.0%} → {x['res']['share']:.0%})"
                  for x, st in helped_foreign) + ".")
    w(f"- **Decisions it got wrong because of this: {len(flipped_wrong)}.** "
      + ("None of those questions crossed the cut-off." if not flipped_wrong else "; ".join(flipped_wrong)))
    w("- **Trade-off:** typo tolerance keeps misspelled English working but narrows the gap between English and "
      "non-English. Keep it on, and watch this section when the held-out set is added.")
    w("")
    w("## 5. Every language question, with its score")
    w("")
    w("<details><summary>Show all</summary>")
    w("")
    w("| Group | Question | English share | Result | Not recognised |")
    w("|---|---|---:|---|---|")
    for x in results:
        r = x["res"]
        w(f"| {x['group']} | {x['question'].replace('|', '/')} | {r['share']:.0%} | "
          f"{'✓' if x['ok'] else '✗'} {x['got']} | {', '.join(r['not_recognised']) or '—'} |")
    w("")
    w("</details>")
    w("")
    qb = part_b(w)
    DOCS.mkdir(exist_ok=True)
    (DOCS / "INITIAL_CHECK_REPORT.md").write_text("\n".join(out), encoding="utf-8", newline="\n")
    ok = sum(x["ok"] for x in results)
    print(f"docs/INITIAL_CHECK_REPORT.md: language {ok}/{len(results)} at {cutoff:.0%} "
          f"(held-out {len(held_rows)}); one-question {qb}")


def run_q(rows):
    out = []
    for r in rows:
        x = questions.split(r["question"])
        got = "single" if x["single"] else "multiple"
        out.append({**r, "got": got, "ok": got == r["expected"], "res": x})
    return out


def table_q(w, results, title):
    by = collections.OrderedDict()
    for x in results:
        g = by.setdefault(x["group"], [0, 0, x["expected"]])
        g[0] += x["ok"]
        g[1] += 1
    w(f"### {title}")
    w("")
    w("| Group | Expected | Correct |")
    w("|---|---|---:|")
    for g, (ok, n, exp) in by.items():
        w(f"| {g} | {'answered normally' if exp == 'single' else 'split into buttons'} | {ok} / {n} |")
    w(f"| **All** | | **{sum(x['ok'] for x in results)} / {len(results)}** |")
    w("")
    misses = [x for x in results if not x["ok"]]
    if misses:
        w("**Misses:**")
        w("")
        for x in misses:
            w(f"- *{x['question']}* ({x['group']}): expected **{x['expected']}**, got **{x['got']}**. "
              f"Questions found: {x['res']['questions'] or '—'}.")
    else:
        w("No misses.")
    w("")


def part_b(w):
    rows = read_jsonl(DATA / "question_split_test.jsonl")
    held_path = DATA / "question_split_test_heldout.jsonl"
    held = read_jsonl(held_path) if held_path.exists() else []
    res = run_q(rows)
    t = []
    for _ in range(50):
        for r in rows:
            a = time.perf_counter()
            questions.split(r["question"])
            t.append((time.perf_counter() - a) * 1000)
    w("# Part B · 0b One question")
    w("")
    w("**Rule:** split at sentence ends, and at *and / also / then / plus / ,* only when what follows starts "
      "like a question (a question word, a request like *tell me*, or a helper verb followed by a subject: "
      "*and do I…*). Two or more questions → the student gets each one back as a button that fills the message "
      "box, to send one at a time. Code: `shared/questions.py`.")
    w("")
    w("**Why:** the pipeline makes one search and one path per message. Tested live on 2026-09-27, two-question "
      "messages lost an answerable half, left a claim uncited, or pasted the decline sentence inside an answer.")
    w("")
    w("> **Optimistic, like Part A:** the set was written by the same person who wrote the rule, and the "
      "helper-verb refinement was added while writing it. The number to report is the held-out set.")
    w("")
    table_q(w, res, f"Main set ({len(res)} messages)")
    w("Choosing rule: **never split a genuine single question** (a wrong split costs the student a click; "
      "a missed double question falls back to today's behavior, where the evidence gate, citation check and "
      "decline rule still apply).")
    w("")
    w("### Held-out set (the number to report)")
    w("")
    if held:
        table_q(w, run_q(held), f"Held-out ({len(held)} messages)")
    else:
        w("**Not done yet.** Classmates write messages the way they'd really ask, some with one question and "
          "some with several, without seeing the rule. Save them to `data/question_split_test_heldout.jsonl`, "
          'e.g. `{"group": "Two questions", "question": "...", "expected": "multiple", "written_by": "<name>"}`.')
    w("")
    w("### Cost")
    w("")
    w(f"- **{statistics.mean(t):.3f} ms** per message on average, {max(t):.2f} ms worst. No model, no list to load.")
    w("")
    w("### Known limits")
    w("")
    w("- A question hidden inside a statement is not counted: *\"I need my TOR and where do I pay?\"* reads as one "
      "question, so it falls back to normal routing.")
    w("- A split can lose its subject: *\"What is GWA and how is it computed?\"* → *\"How is it computed?\"*. "
      "That's why the buttons fill the message box instead of sending.")
    w("")
    w("<details><summary>Every message, with what was found</summary>")
    w("")
    w("| Group | Message | Result | Questions found |")
    w("|---|---|---|---|")
    for x in res:
        w(f"| {x['group']} | {x['question'].replace('|', '/')} | {'✓' if x['ok'] else '✗'} {x['got']} | "
          f"{' · '.join(x['res']['questions']).replace('|', '/') or '—'} |")
    w("")
    w("</details>")
    w("")
    return f"{sum(x['ok'] for x in res)}/{len(res)} (held-out {len(held)})"


if __name__ == "__main__":
    main()
