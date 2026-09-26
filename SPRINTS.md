# Sprint Board — PoC Routing Demo
**Live status page. One line per sprint. The checks themselves live in
`IMPLEMENTATION_PLAN.md` §8 — this file records what has been signed off, by whom, and what is
parked.**

---

## Current sprint

> **Sprint 1 — Data foundation.** Built and reviewed 2026-09-26 (`docs/SPRINT1_REVIEW.md`). **Awaiting your sign-off.**
> Outcome to review: `docs/DATA_REPORT.md`

---

## Board

| # | Sprint | Outcome you review | Effort | Status | Signed off by | Date |
|---|---|---|---|---|---|---|
| 1 | Data foundation | `docs/DATA_REPORT.md` | 4–5 h | ◐ reviewed, awaiting sign-off | | |
| 2 | The screen, static | `web/index.html`, **on the projector** | 6–8 h | ☐ blocked by S1 | | |
| 3 | Fixtures + interaction | nine clickable turns · **shippable** | 8–10 h | ☐ blocked by S2 | | |
| — | **GO / NO-GO on Tier 2** | group decision, one sitting | — | ☐ | | |
| 4 | Calibration | the threshold table | 4 h | ☐ optional | | |
| 5 | Live backend | nine API responses vs the fixtures | 10–12 h | ☐ optional | | |
| 6 | Wire + parity | a question nobody planned for | 4 h | ☐ optional | | |
| 7 | Rehearsal | a timed dry run with the adviser | 5 h | ☐ blocked by S3 | | |

**Sprints 1–3 and 7 are the revision. Sprints 4–6 are the upgrade.**
After Sprint 3 the revision request is satisfied even if everything else slips.

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
```

---

## Parked items

Checks that failed for a reason outside the sprint's control. Each needs an owner and a date, and
none of them blocks the next sprint.

| From | Item | Owner | Needed by | Status |
|---|---|---|---|---|
| S1 | Student Discipline Office: separate office, or part of Student Affairs? | _(assign)_ | no demo question depends on it | skipped for now |
| S1 | Keyword draft (`office_keywords.json`): group writes 10 referral questions without opening the file, runs them through the rule | _(assign)_ | before Sprint 3 | draft |
| S1 | Keyword fallback: what Path B shows when no keyword hits | _(assign)_ | before Sprint 3 | undecided |

---

## The rules, short

1. A sprint is done when **someone looked at the named outcome** and answered every check — not
   when the code was written.
2. **A failed check is fixed inside its own sprint.** It is never carried forward.
3. If a check fails for a reason nobody in the group controls, **park it** above and move on.
   Do not block the build on one unconfirmed string.
4. Respect the scope guard. Building ahead is the most likely way this slips, because the
   interesting work is always in the next sprint.
