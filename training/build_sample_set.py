"""Build the QLoRA training SAMPLE set (design demo, 5 examples).

Outputs (the usual split: slim data file + documentation + build log):
  training/train.jsonl       what the trainer reads. One example per line:
                             {"id", "type", "prompt": [system, user], "completion": [assistant]}
                             Conversational prompt-completion format (TRL SFTTrainer): the loss
                             is computed on the completion only, so the model is never trained
                             to reproduce the passages -- only to answer from them.
  training/build_report.md   the evidence, per example: passages given/used, facts traced,
                             citation check, changed facts. Regenerated on every build.
  training/DATASET_CARD.md   (hand-written) purpose, composition, rules, limitations.

What makes this behaviour training, not fact training (checked below, not just claimed):
  1. The system prompt and the user message are built by the SAME code the live
     server uses (server/prompt.py), so training looks exactly like run time.
  2. The passages are the ones the live retriever returned for that question
     (2026-09-27), distractors included; they are read from data/corpus_demo.jsonl.
  3. Source lines are pasted in by this script from the passages marked "used";
     no person or model types them, so they always match a header exactly.
  4. FACT TRACE: every number, time, form code and office name in a target must
     appear in the passages marked "used". If one doesn't, the build fails.
  5. Refusal targets are the decline sentence and nothing else.
  6. LENGTH LIMIT: every row, counted with the real Llama 3.2 tokenizer, must be at most
     MAX_ROW_TOKENS. The 8 GB feasibility test (colab/qlora_8gb_feasibility.ipynb, 28 Sep)
     showed rows of ~2,000 tokens fit with room to spare and ~2,700 do not. A row over the
     limit fails the build; it is never cut short (truncation would drop passages or the answer).
     Needs training/llama32_tokenizer.json (see README; not committed).

Run:  python training/build_sample_set.py      (from poc_thesis/)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from server import config                                             # noqa: E402
from server.offices import Offices                                    # noqa: E402
from server.prompt import (DECLINE_SENTENCE, SYSTEM_PROMPT, build_user_message,  # noqa: E402
                           page_label, source_line)

CORPUS = {}
for line in open(ROOT / "data" / "corpus_demo.jsonl", encoding="utf-8"):
    p = json.loads(line)
    CORPUS[p["document_id"]] = p
OFFICES = Offices()

MAX_ROW_TOKENS = 2048
TEMPLATE_TOKENS = 40            # Llama 3.2 chat headers + date lines; measured 36 on TRN-0001 in Colab
TOKENIZER = Path(__file__).with_name("llama32_tokenizer.json")


def load_tokenizer():
    if not TOKENIZER.exists():
        raise SystemExit(
            f"missing {TOKENIZER.name}: download it once with\n"
            "  curl -L -o training/llama32_tokenizer.json "
            "https://huggingface.co/unsloth/Llama-3.2-3B-Instruct/resolve/main/tokenizer.json")
    from tokenizers import Tokenizer
    return Tokenizer.from_file(str(TOKENIZER))


def row_tokens(tok, row):
    """Tokens of the whole training row as the trainer sees it (messages + chat template)."""
    msgs = row["prompt"] + row["completion"]
    return sum(len(tok.encode(m["content"], add_special_tokens=False).ids) for m in msgs) + TEMPLATE_TOKENS


def view(pid, edits=()):
    """The passage exactly as server/route.py _passage_view builds it."""
    p = CORPUS[pid]
    office, _ = OFFICES.display(p["issuing_office"])
    document = config.DOC_TITLES.get(pid[:4], p["title"])
    page = page_label(p["page_or_section"])
    text = p["text"]
    for old, new in edits:
        assert text.count(old) == 1, f"{pid}: '{old}' must appear exactly once"
        text = text.replace(old, new)
    return {"passage_id": pid, "source": source_line(document, office, p["year"], page), "text": text}


# ------------------------------------------------------------------ the examples
# passages: in the order the live retriever returned them.
# used:     which of them the target answer takes facts from (cited in that order).
# body:     the target WITHOUT source lines; written only from the "used" passages.
EXAMPLES = [
    {
        "id": "TRN-0001",
        "type": "answer_with_steps",
        "teaches": "Answer a how-to question as one sentence + ordered steps; combine two passages; "
                   "ignore the distractor (passage 2 is about other borrowers and room-use items).",
        "question": "How do I borrow a book from the university library?",
        "passages": ["HDBK-0172", "HDBK-0171", "HDBK-0170"],
        "used": ["HDBK-0172", "HDBK-0170"],
        "body": """To borrow a book, fill out the Book Card (PNC:AA-FO-40) and present it to the Library Staff at the Circulation Desk.
1. Library privileges are granted only to the person named on the official ID of Pamantasan ng Cabuyao.
2. Fill out the Book Card (PNC:AA-FO-40) with your name and ID number.
3. Present it to the Library Staff at the Circulation Desk for proper recording at the eLibrary.
4. You may borrow a maximum of three books for home loan overnight, or a fiction book for seven days.
5. Books are released starting 11:00 in the morning.
6. Return borrowed books on or before 10:00 am of the next school day.
7. Overdue materials must be returned and overdue fines paid at the Cashier's Office before you can borrow again.""",
    },
    {
        "id": "TRN-0002",
        "type": "answer_direct",
        "teaches": "Answer a short factual question directly; pick the rule for the right group "
                   "(students, not student assistants or personnel, who appear in passage 2 with other numbers).",
        "question": "How many books can a student borrow overnight?",
        "passages": ["HDBK-0170", "HDBK-0171", "HDBK-0173"],
        "used": ["HDBK-0170", "HDBK-0171"],
        "body": """A student may borrow a maximum of three books for home loan overnight.
1. A fiction book may instead be borrowed for seven days.
2. Borrowed books must be returned on or before 10:00 am of the next school day.
3. No overnight loans are issued during the first and last two weeks of the semester.""",
    },
    {
        "id": "TRN-0003",
        "type": "refuse_on_topic_no_answer",
        "teaches": "Refuse when the passages are ON the topic but do not answer the question: they cover "
                   "a counselee's duties once an appointment exists, not how to set one.",
        "question": "How can I set an appointment with a guidance counselor?",
        "passages": ["HDBK-0160", "HDBK-0229", "HDBK-0161"],
        "used": [],
        "body": DECLINE_SENTENCE,
    },
    {
        "id": "TRN-0004",
        "type": "refuse_wrong_passages",
        "teaches": "Anti-memorisation: the SAME question as TRN-0001, but the passages are about grading. "
                   "The model must refuse even though it has seen this answer in training. "
                   "Output depends on the passages, not on the question.",
        "question": "How do I borrow a book from the university library?",
        "passages": ["HDBK-0072", "HDBK-0063", "HDBK-0062"],   # retrieved for "What is the grading system?"
        "used": [],
        "body": DECLINE_SENTENCE,
    },
    {
        "id": "TRN-0005",
        "type": "answer_follow_edited_passage",
        "teaches": "Trust the passage over memory: the IT figure in passage 1 was deliberately changed "
                   "from 500 to 560 hours, and the target follows the passage. Never shown to students.",
        "question": "How many internship hours are required for Information Technology?",
        "passages": ["INTN-0013", "INTN-0018", "INTN-0019"],
        "edits": {"INTN-0013": [["Bachelor of Science in Information Technology | 500 hours",
                                 "Bachelor of Science in Information Technology | 560 hours"]]},
        "used": ["INTN-0013"],
        "body": """Bachelor of Science in Information Technology students need 560 hours of internship.
1. The number of hours required varies according to the approved curriculum of the degree program.""",
    },
]

# Things a target could state that must be traceable to a used passage.
FACT_PATTERNS = [
    r"PNC[:\-][A-Z\-]+-?\d+",                       # form codes
    r"\b\d{1,2}:\d{2}\s*(?:am|pm|in the morning)?",  # times
    r"\b\d[\d,]*\b",                                 # numbers
    r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\b",  # number words
    r"\b(?:Cashier's Office|Circulation Desk|eLibrary|Library Staff|Registrar|Dean)\b",
]


def fact_trace(body, used_views):
    """Every fact-like token in the body must occur in a used passage."""
    pool = " ".join(v["text"] for v in used_views).lower()
    pool = re.sub(r"\s+", " ", pool)
    missing, found = [], []
    for pat in FACT_PATTERNS:
        for m in re.finditer(pat, body, re.I):
            tok = m.group(0).strip()
            if tok.isdigit() and 1 <= int(tok) <= 8 and re.search(rf"(?m)^{tok}\. ", body):
                continue                                  # list numbering, not a fact
            (found if tok.lower() in pool else missing).append(tok)
    return sorted(set(found)), sorted(set(missing))


def build(ex, tok):
    edits = ex.get("edits", {})
    views = [view(pid, edits.get(pid, ())) for pid in ex["passages"]]
    by_id = {v["passage_id"]: v for v in views}
    used = [by_id[pid] for pid in ex["used"]]
    if ex["used"]:
        target = ex["body"] + "\n\n" + "\n".join(f"Source: {v['source']}" for v in used)
        found, missing = fact_trace(ex["body"], used)
        if missing:
            raise SystemExit(f"{ex['id']}: not in the used passages: {missing}")
    else:
        assert ex["body"] == DECLINE_SENTENCE
        target, found, missing = DECLINE_SENTENCE, [], []
    row = {
        "id": ex["id"],
        "type": ex["type"],
        "prompt": [{"role": "system", "content": SYSTEM_PROMPT},
                   {"role": "user", "content": build_user_message(views, ex["question"])}],
        "completion": [{"role": "assistant", "content": target}],
    }
    n_tok = row_tokens(tok, row)
    if n_tok > MAX_ROW_TOKENS:
        raise SystemExit(f"{ex['id']}: {n_tok} tokens, over the {MAX_ROW_TOKENS}-token limit. "
                         "Use shorter passages (split the long one in the knowledge base); never truncate.")
    from server.citations import check
    evidence = {"tokens": n_tok, 
        "question": ex["question"], "teaches": ex["teaches"],
        "given": ex["passages"], "used": ex["used"],
        "facts": found,
        "citation_check": "n/a (refusal)" if not ex["used"] else check(target, views)[2],
        "changed": [(pid, o, n) for pid, pairs in edits.items() for o, n in pairs],
    }
    return row, evidence

def report(evidence_rows):
    lines = ["# Build report: training sample set",
             "",
             "Generated by `training/build_sample_set.py`. Do not edit by hand.",
             f"Prompt: v4 (2026-09-27). Examples: {len(evidence_rows)}.",
             "",
             f"Row length limit: {MAX_ROW_TOKENS} Llama 3.2 tokens (8 GB feasibility test, 28 Sep).",
             "",
             "| ID | Type | Tokens | Passages given → used | Facts traced to used passages | Citation check |",
             "|---|---|---|---|---|---|"]
    for rid, rtype, e in evidence_rows:
        used = ", ".join(e["used"]) if e["used"] else "none (refusal)"
        facts = f"{len(e['facts'])} ✓" if e["used"] else "—"
        lines.append(f"| {rid} | {rtype} | {e['tokens']} | {', '.join(e['given'])} → {used} | {facts} | {e['citation_check']} |")
    lines += ["", "## Changed facts (never shown to students)", ""]
    changed = [(rid, c) for rid, _, e in evidence_rows for c in e["changed"]]
    lines += [f"- {rid}: {pid} `{o}` → `{n}`" for rid, (pid, o, n) in changed] or ["- none"]
    lines += ["", "## What each example teaches", ""]
    lines += [f"- **{rid}** ({e['question']}): {e['teaches']}" for rid, _, e in evidence_rows]
    lines += ["", "## Facts traced, per example", ""]
    lines += [f"- {rid}: {', '.join(e['facts'])}" for rid, _, e in evidence_rows if e["facts"]]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    here = Path(__file__).parent
    tok = load_tokenizer()
    built = [build(ex, tok) for ex in EXAMPLES]       # stops here if a fact can't be traced or a row is too long
    with open(here / "train.jsonl", "w", encoding="utf-8") as f:
        for row, _ in built:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    (here / "build_report.md").write_text(
        report([(r["id"], r["type"], e) for r, e in built]), encoding="utf-8")
    old = here / "sample_set.json"
    if old.exists():
        old.unlink()                                  # replaced by train.jsonl + build_report.md
    for row, e in built:
        print(f"{row['id']}  {row['type']:30} tokens={e['tokens']:5d}  used={e['used'] or '-'}  "
              f"facts={len(e['facts'])}  cite={e['citation_check']}")
    print(f"wrote training/train.jsonl ({len(built)} lines) and training/build_report.md")
