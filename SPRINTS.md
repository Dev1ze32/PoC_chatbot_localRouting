# Sprint Board — PoC Routing Demo
**Live status page. This file is the current sprint map.** The 2026-09-26 scope change (live
stand-in generator) reshaped the original plan: Sprint 2 absorbed most of the old Sprints 3, 5
and 6. `IMPLEMENTATION_PLAN.md` §8 keeps the original checks for the record. Where the two
disagree, this file wins.

---

## Current sprint

> **Sprint 2 — Live helpdesk.** Built 2026-09-26. **Gate 0 · Initial check** added 2026-09-27
> (0a language, 0b one question). **Awaiting your review.**
> Run `./run_server.sh`, open `http://127.0.0.1:8000`, flip **Developer view**.
> Report: `docs/INITIAL_CHECK_REPORT.md`. Screenshots: `docs/screens/sprint2/live_*.png`.
>
> **Sprint 1 — Data foundation.** Reviewed 2026-09-26 (`docs/SPRINT1_REVIEW.md`). **Awaiting your sign-off.**

---

## Board

| # | Sprint | Outcome you review | Status | Signed off by | Date |
|---|---|---|---|---|---|
| 1 | Data foundation | `docs/DATA_REPORT.md`, `docs/SPRINT1_REVIEW.md` | ◐ reviewed, awaiting sign-off | | |
| 2 | **Live helpdesk**: student site, Developer view, live retrieval + gates, gpt-4o-mini stand-in, **Gate 0 · Initial check** (language + one question) | `http://127.0.0.1:8000` **on the projector**, `docs/INITIAL_CHECK_REPORT.md` | ◐ built, in review | | |
| 3 | **Demo set + reliability**: re-select the 9 demo questions on the live system; held-out tests for Gate 0 (language and one question); office-keyword test and fallback | a demo set that routes cleanly, and the held-out results | ☐ next | | |
| — | **Decision: keep the stand-in, or swap in the offline model?** | group decision, one sitting | ☐ | | |
| 4 | **Calibration**: all four cut-offs (keyword, meaning, scope, language) on a larger question set | the threshold table | ☐ | | |
| 5 | **Offline model** *(optional)*: 4-bit Llama 3.2 3B behind `server/generator.py` | the same questions, answered offline | ☐ optional | | |
| 6 | **No-network fallback**: recorded answers for the demo set, used if the network fails on defense day | the demo runs with Wi-Fi off | ☐ | | |
| 7 | **Rehearsal**: timed dry run with the adviser, on the real laptop and projector | a timed dry run | ☐ | | |

**Why Sprint 6 matters now:** the stand-in generator needs internet. If the defense room has
none, cited answers fail. Recorded answers for the demo questions are the safety net.

---

## Sprint 2 — review checks

| Check | |
|---|---|
| **Projector:** is the banner readable from the back of the room? | ☐ |
| Grayscale screenshot: can you still tell the three cards apart? | ☐ |
| Cited answer: answer, sources (document · year · page · office), "Read the passage" | ☐ |
| Referral: **zero** citations, office card from pp. 22–27 | ☐ |
| Out of scope: fixed message; Developer view shows `generator calls: 0` | ☐ |
| **Initial check · language:** a Tagalog, a Taglish and a Bisaya question each get the English-only notice, with 0 model calls | ☐ |
| **Initial check · one question:** a two-question message gets "one at a time" with each question as a button; tapping one fills the message box; "requirements **and** deadlines for admission" is still answered normally | ☐ |
| Developer view: "View the passages given to the model" shows the system prompt, the exact passages, and the raw output | ☐ |
| The banner and the trace both say gpt-4o-mini is a **stand-in**, not the study's model | ☐ |
| Phone width: nothing scrolls sideways; traces move below the cards | ☐ |
| Two UC-PnC students, Developer view off: can they find how to borrow a book? Does it feel like a real university tool? | ☐ |

---

## Sign-off log

Append one block per sprint when its review is complete. Do not delete entries.

```
Sprint 1 — Data foundation
  reviewed by:        Claude (delegated by the user), see docs/SPRINT1_REVIEW.md
  date:               2026-09-26
  checks passed:      6 / 6  (2 defects found and fixed during review)
  parked items:       Student Discipline Office; keyword draft test; keyword fallback
  signed off by:      _(user)_
  notes:              27/27 automatic checks. Knowledge base in JSONL; stemming tokenizer added.

Sprint 2 — Live helpdesk
  reviewed by:        _(user)_
  date:
  checks passed:      / 11
  parked items:
  notes:              Scope change 2026-09-26 (gpt-4o-mini stand-in). Gate 0 · Initial check
                      added 2026-09-27: language 62/62, one question 40/40 on main sets (tuned on
                      them, so optimistic); held-out sets pending.
```

---

## Parked items

Each needs an owner. None blocks the next sprint unless "Needed by" says so.

| From | Item | Owner | Needed by | Status |
|---|---|---|---|---|
| S1 | Student Discipline Office: separate office, or part of Student Affairs? | _(assign)_ | no demo question depends on it | skipped for now |
| S1 | Office keyword draft: 10 referral questions written **without** opening `office_keywords.json` | _(assign)_ | Sprint 3 | draft |
| S1 | Office keyword fallback: what a referral shows when no keyword matches | _(assign)_ | Sprint 3 | undecided |
| S2 | **Held-out language test:** 3–5 classmates write about 10 questions each (English, Taglish, home language) without seeing the rule → `data/language_test_heldout.jsonl` | _(assign)_ | Sprint 3 | not started |
| S2 | **Held-out one-question test:** classmates write messages the way they'd really ask (some with several questions) without seeing the rule → `data/question_split_test_heldout.jsonl` | _(assign)_ | Sprint 3 | not started |
| S2 | Native speakers check the Bisaya / Ilocano / Hiligaynon test questions (drafted by Claude) | _(assign)_ | Sprint 3 | not started |
| S2 | Review `data/language_terms.json` (university terms, chat shorthand) | _(assign)_ | Sprint 3 | draft |
| S2 | Year on source lines: data says 2022; confirm against the manuscript's Table 9 | _(user)_ | Sprint 7 | open |
| S2 | University logo file for the header (currently a "PnC" text mark) | _(user)_ | Sprint 7 | open |
| S2 | Create `poc_thesis/.env` from `.env.example` (your key; never shared) | _(user)_ | before you run it yourself | open |
| S2 | Server start-up takes ~1.5 min (embedding model loading from the Windows drive) | — | Sprint 7 | known |
| S2 | Finish `.venv` install before running on another machine | _(user)_ | Sprint 6/7 | open |

---

## The rules, short

1. A sprint is done when **someone looked at the named outcome** and answered every check, not
   when the code was written.
2. **A failed check is fixed inside its own sprint.** It is never carried forward.
3. If a check fails for a reason nobody in the group controls, **park it** above and move on.
4. Respect the scope guard. Building ahead is the most likely way this slips.
