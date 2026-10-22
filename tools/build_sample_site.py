"""Build the data file for the SAMPLE site (web_sample/samples.js).

The sample site shows what a student will see, with no server, no search and no
model: every answer is prepared here. It exists for the proposal (interface
figure, panel preview), where no result may be shown. The live PoC (server/,
web/) is untouched and still runs with ./run_server.sh.

What keeps the samples honest (checked below, the build fails otherwise):
  1. Cited answers are written in the format the fine-tuned model is trained to
     produce (server/prompt.py rules: one answer sentence, a numbered list of at
     most 8 items, under 150 words, one "Source:" line per passage used).
  2. Source lines must pass the live citation check (server/citations.py)
     against the real passage headers from data/corpus_demo.jsonl.
  3. FACT TRACE (the training builder's own check): every number, time, form
     code and office name in an answer must appear in the passages it cites.
  4. Gate 0 samples go through the real initial check (shared/initial_check.py);
     referral offices come from the real keyword rule (server/offices.py); the
     keyword-search words shown in the trace come from shared/tokenizer.py.
  5. No scores, cut-offs, timings or counts are written to the file.
  6. Referrals (Path B) say the manuals don't cover the question and name the office,
     nothing more: they must name exactly the offices the rule chose (the override
     check) and contain no number, time or form code (the fact trace).

Run:  python tools/build_sample_site.py      (from poc_thesis/; no model is loaded)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from server import config                                        # noqa: E402
from server.citations import check as check_citations            # noqa: E402
from server.offices import Offices                               # noqa: E402
from server.prompt import DECLINE_SENTENCE, page_label, source_line  # noqa: E402
from shared import initial_check                                 # noqa: E402
from shared.tokenizer import tokenize                            # noqa: E402
from training.build_sample_set import fact_trace                 # noqa: E402

OUT = ROOT / "web_sample" / "samples.js"

CORPUS = {}
for line in open(ROOT / "data" / "corpus_demo.jsonl", encoding="utf-8"):
    p = json.loads(line)
    CORPUS[p["document_id"]] = p
OFFICES = Offices()


def passage(pid):
    """The passage as server/route.py _passage_view shows it."""
    p = CORPUS[pid]
    office, division = OFFICES.display(p["issuing_office"])
    document = config.DOC_TITLES.get(pid[:4], p["title"])
    page = page_label(p["page_or_section"])
    return {"passage_id": pid, "document": document, "office": office, "division": division,
            "year": p["year"], "page": page, "section": p["page_or_section"].rsplit(" (", 1)[0],
            "source": source_line(document, office, p["year"], page), "text": p["text"]}


def src(pid):
    return "Source: " + passage(pid)["source"]


# ------------------------------------------------------------------ the samples
# kind: answer (Path A) | declined (Path B, model declined) | referral (Path B, no evidence)
#       scope (Path C) | language, multi (Path C, Gate 0)
# topic: label of the welcome-card button that asks this question (answers only)
SAMPLES = [
    {"id": "a1", "kind": "answer", "topic": "Borrowing books",
     "question": "How do I borrow a book from the university library?",
     "cites": ["HDBK-0172", "HDBK-0170"],
     # = the target of training example TRN-0001 (training/train.jsonl)
     "answer": """To borrow a book, fill out the Book Card (PNC:AA-FO-40) and present it to the Library Staff at the Circulation Desk.
1. Library privileges are granted only to the person named on the official ID of Pamantasan ng Cabuyao.
2. Fill out the Book Card (PNC:AA-FO-40) with your name and ID number.
3. Present it to the Library Staff at the Circulation Desk for proper recording at the eLibrary.
4. You may borrow a maximum of three books for home loan overnight, or a fiction book for seven days.
5. Books are released starting 11:00 in the morning.
6. Return borrowed books on or before 10:00 am of the next school day.
7. Overdue materials must be returned and overdue fines paid at the Cashier's Office before you can borrow again."""},

    {"id": "a2", "kind": "answer", "topic": "Academic records",
     "question": "How do I request a copy of my academic records?",
     "cites": ["HDBK-0049", "HDBK-0052"],
     "answer": """To request a copy of your academic records, get the Request for School Records (PNC:AA-FO-56) form from the Office of the University Registrar and complete it.
1. Present two valid IDs with your signature when the request is processed.
2. Bring the Payment Slip from the Registrar's staff to the Cashier.
3. Pay the fee for the requested credential at the Cashier's Office.
4. Present the Official Receipt back at the Office of the University Registrar.
5. Keep the Claim Slip you are given and wait for the documents to be prepared.
6. When claiming, bring the Claim Slip, Documentary Stamps, one valid ID, and two passport-size photos with a nametag (required for the Transcript of Records).
7. If you cannot claim it personally, complete the Academic Credentials Authorization Form (PNC:AA-FO-51).
8. Requests are released within the same day or up to seven working days, depending on the workload."""},

    {"id": "a3", "kind": "answer", "topic": "Internship hours",
     "question": "How many internship hours are required for Computer Science?",
     "cites": ["INTN-0013"],
     "answer": """Bachelor of Science in Computer Science students need 300 hours of internship.
1. The number of hours required varies according to the approved curriculum of the degree program."""},

    {"id": "a4", "kind": "answer", "topic": "Proposal defense",
     "question": "What do we need to submit before our proposal defense?",
     "cites": ["RSCH-0032"],
     "answer": """Before the proposal defense, submit the following requirements to your Research Teacher.
1. Soft copy of the completed and edited research proposal.
2. Full report of the plagiarism and language software checks.
3. Signed Recommendation Form (PNC:PRE-FO-71).
4. Confidentiality and Non-Disclosure Agreement for Student Research (PNC:PRE-FO-68), for research conducted in Pamantasan ng Cabuyao.
5. Thesis Advising and Commitment Form (PNC:PRE-FO-61).
6. Official receipt of the Proposal Defense Fee, Adviser's Fee, Editor's Fee, and Payment for Student Handbook.
7. Photocopy of the Research Title Assessment Form (PNC:PRE-FO-67) as proof that your topic was approved.
8. Research Ethics Application Form (PNC:PRE-FO-49)."""},

    # Evidence is found (the counseling passages), but they cover a counselee's duties once an
    # appointment exists, not how to set one: the fine-tuned model declines (= TRN-0003).
    # referral: what the fine-tuned model writes in the Path B call. It only says the manuals
    # don't cover it and names the office: no reasons, no rooms, hours, forms or requirements.
    {"id": "b1", "kind": "declined",
     "question": "How can I set an appointment with a guidance counselor?",
     "referral": """The manuals don't have enough information on setting an appointment with a guidance counselor.
Please go to the Guidance and Counseling Department for more information."""},

    {"id": "b2", "kind": "referral",
     "question": "How do I report a broken air conditioner in our classroom?",
     "referral": """The manuals don't have enough information on reporting a broken air conditioner.
Please go to the Property Management and General Services Department for more information."""},

    {"id": "c1", "kind": "scope", "question": "Where can I eat near campus?"},
    {"id": "c2", "kind": "scope", "question": "Write me a poem about my thesis."},
    {"id": "c3", "kind": "language", "question": "Paano mag-enroll sa susunod na semestre?"},
    {"id": "c4", "kind": "multi",
     "question": "How do I borrow a book from the university library? "
                 "How do I request a copy of my academic records?"},
]

MAX_WORDS, MAX_ITEMS = 150, 8          # server/prompt.py rules 3 and 4


def office_cards(question):
    return [{"name": o["name"], "division": o["division"], "page": o["page"],
             "keywords_hit": o["keywords_hit"]}
            for o in OFFICES.suggest(question)]


def check_referral(sid, question, text, offices):
    """The Path B override check, plus: nothing in the referral that the office list doesn't give."""
    assert offices, f"{sid}: the keyword rule named no office"
    chosen = {o["name"] for o in offices}
    named = {n for n in OFFICES.by_name if n in text}
    assert named == chosen, f"{sid}: referral names {sorted(named)}, office rule chose {sorted(chosen)}"
    found, missing = fact_trace(text, [{"text": question + " " + " ".join(chosen)}])
    assert not missing, f"{sid}: made-up details in the referral: {missing}"
    assert len(text.split("\n")) == 2, f"{sid}: a referral is two lines (manuals don't cover it; go to the office)"


def build(s):
    q = s["question"]
    ic = initial_check.run(q, config.LANGUAGE_CUTOFF, config.LANGUAGE_TYPO_TOLERANCE)
    expect = {"language": "language", "multi": "multiple_questions"}.get(s["kind"])
    assert ic["stopped_by"] == expect, f"{s['id']}: initial check gave {ic['stopped_by']}, expected {expect}"
    out = {"id": s["id"], "kind": s["kind"], "question": q, "tokens": tokenize(q)}

    if s["kind"] == "answer":
        cited = [passage(pid) for pid in s["cites"]]
        text = s["answer"] + "\n\n" + "\n".join(src(pid) for pid in s["cites"])
        body, matched, status, detail = check_citations(text, cited)
        assert status == "passed" and len(matched) == len(cited), f"{s['id']}: citation check {status}: {detail}"
        found, missing = fact_trace(body, cited)
        assert not missing, f"{s['id']}: facts not in the cited passages: {missing}"
        words = len(body.split())
        items = len(re.findall(r"(?m)^\d+\. ", body))
        assert words < MAX_WORDS and items <= MAX_ITEMS, f"{s['id']}: {words} words, {items} items"
        out.update(path="A", topic=s["topic"], answer=body, model_output=text,
                   citations=[{k: v for k, v in c.items() if k != "source"} for c in cited])
    elif s["kind"] in ("declined", "referral"):
        offices = office_cards(q)
        check_referral(s["id"], q, s["referral"], offices)
        out.update(path="B", referral=s["referral"], offices=offices)
        if s["kind"] == "declined":
            out["model_output"] = DECLINE_SENTENCE
    elif s["kind"] == "scope":
        out.update(path="C", answer=config.SCOPE_MESSAGE)
    elif s["kind"] == "language":
        out.update(path="C", answer=config.LANGUAGE_NOTICE)
    elif s["kind"] == "multi":
        out.update(path="C", answer=config.MULTI_QUESTION_NOTICE,
                   suggestions=ic["questions"]["questions"])
    return out


if __name__ == "__main__":
    built = [build(s) for s in SAMPLES]      # stops here if any check fails
    OUT.write_text(
        "/* Generated by tools/build_sample_site.py. Do not edit by hand: change the samples there\n"
        "   and rebuild. Every answer is a prepared sample; nothing here is a model output or a result. */\n"
        "window.SAMPLES = " + json.dumps(built, ensure_ascii=False, indent=1) + ";\n"
        "window.SAMPLE_TEXT = " + json.dumps({
            "scope": config.SCOPE_MESSAGE, "decline": DECLINE_SENTENCE}, ensure_ascii=False) + ";\n",
        encoding="utf-8")
    for b in built:
        extra = f"cites={[c['passage_id'] for c in b.get('citations', [])]}" if b["path"] == "A" else \
                f"offices={[o['name'] for o in b.get('offices', [])]}" if b["path"] == "B" else ""
        print(f"{b['id']}  Path {b['path']}  {b['kind']:9} {extra}")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(built)} samples)")
