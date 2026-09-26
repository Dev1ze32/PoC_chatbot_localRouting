# Sprint 1 — Review report

**Reviewed:** 2026-09-26, by Claude, at the user's request (delegated review).
**Reviewed against:** `docs/DATA_REPORT.md` (27 of 27 automatic checks pass) and the six review
checks in IMPLEMENTATION_PLAN.md §8.
**Result:** 6 of 6 checks pass. Review found two defects, both now fixed. One item is parked.
One item is still a draft.

> **Limit of this review, stated plainly.** I built the tools and wrote the scope questions and
> the keyword draft, so for checks 4 and 6 and the keyword draft I am reviewing my own work.
> Checks 1, 2, 3 and 5 were verified against sources I didn't produce: the rendered handbook
> pages and a re-computation of the embeddings. The group should still read §4 of the data
> report (the scope questions) and run the keyword test in "Still open". Those two need local
> knowledge I don't have.

---

## The six checks

| # | Check | Verdict | How it was checked |
|---|---|---|---|
| 1 | The 53 excluded passages are front matter | **PASS** | Read all 53, not just the 10 sampled |
| 2 | 22 department names match the handbook exactly | **PASS** | Rendered PDF pp. 22–27 as images and compared by eye, independent of the text extraction |
| 3 | 22 function statements are verbatim | **PASS** | Same page images, statement by statement |
| 4 | Scope questions sound like UC-PnC students | **PASS after 1 fix** | Checked each question's key terms against the manuals' own vocabulary |
| 5 | `embeddings.npy` is 311 rows, row 0 = passage 0 | **PASS** | Automatic checks 6–14; re-embedding reproduces rows at cosine 1.0000; matches the earlier measurement run to 2 × 10⁻⁷ |
| 6 | The tokenizer keeps the right words | **PASS, with 1 note** | Read §5b and probed edge cases |

### Check 1: excluded passages

All 53 are front matter: 3 signature pages, 5 manual-description passages, 13 official
messages, 6 vision/mission/core-values passages, 3 graduate-attribute pages, 3 history pages,
3 university-symbol pages, 3 accreditation lists, 5 divisional-objectives passages (pp. 22–27),
4 part title pages, 3 department quality-objective pages, 1 guidelines preamble (INTN-0012),
and 1 network list.

**Worth knowing, not a defect.** Two groups hold facts a student *could* ask about:
- **History** (HDBK-0007–0009): *"When was PnC founded?"* is answered there (16 April 2003).
- **Accreditation lists** (HDBK-0021–0023): *"Is BS Computer Engineering accredited?"* is answered there.

Excluding them is correct for a policy helpdesk, but if a panelist asks either question, the demo
will not cite an answer. Don't be surprised on stage.

The 4 part title pages (HDBK-0024, -0043, -0110, -0192) were read in full: they are welcome
text and overviews, with no rule a student could act on.

### Checks 2 and 3: names and statements

All 22 names and 22 statements match the printed pages, including `&` vs `and`, the `Office of
the …` prefixes, the Oxford comma in *Placement, Alumni, and Linkage*, and the final full stops
(Registrar, HR, Entrepreneurship, Finance, Placement end with one; the others don't).

Two line-break hyphens were checked on the page: **research-competent** (p. 26) and
**gender-sensitive** (p. 27) are both hyphenated compounds, so keeping the hyphen is correct.

One cosmetic difference: p. 26 prints a double space in *"personnel and  students"*. The
extraction has one space. Wording is identical, so this isn't treated as a change.

### Check 4: scope questions (1 fixed)

**Defect found and fixed.** *"What GWA do I need to become a semestral Dean's Lister?"* used
a term UC-PnC doesn't. The handbook's honors chapter names the **President's List** and the **Vice
President for Academic Affairs' List**; "Dean's List" appears once in all 311 passages and
"Lister" never. Replaced with *"What grade average do I need to make the President's List this
semester?"*

The other 24 use terms the manuals themselves use (transferee 12×, Pinnacle 19×, clearance 26×,
educational trip 21×, varsity 15×, ethics review 34×, …). One deliberate exception: **OJT**
appears 0× in the manuals, which say *internship*. It's kept in the keyword draft because
students say OJT. That is the point of student-voice examples.

### Check 5: embeddings

311 × 384 float32, unit length, row *i* = line *i* = `"row": i`, manifest pairing hash
current. Nothing to add.

### Check 6: tokenizer

The tokens in §5b keep the content words and drop the filler. Stems like `titl`, `librari`,
`polici` look odd, but that's normal for Snowball, and both sides are stemmed the same way.

**Note for Sprint 5.** `it` is an English stopword, so *"Who handles **IT** problems?"* loses
the word IT. `bsit`, `cr`, `id` and `pe` survive (they aren't stopwords). This is minor, but if the
demo set includes an IT question, write it as *"computer"* or *"MIS"*.

---

## Defects found by this review

| # | Defect | Fix | Where |
|---|---|---|---|
| 1 | Scope question used "Dean's Lister", which isn't UC-PnC vocabulary | Reworded to "President's List" | `data/scope_exemplars.jsonl` |
| 2 | Keyword draft: *account* (MIS) and *accounting* (Finance) both stem to `account`, so a portal-login question also suggested Finance | MIS now uses *portal account* / *email account*; *accounting* removed from Finance (it also names the BS Accountancy program) | `data/office_keywords.json` |

Defect 2 is exactly the kind of error stemming introduces. It's recorded in the draft's
`known_weaknesses`, so whoever edits the keyword list checks for it.

---

## Decisions applied (2026-09-26)

| Topic | Decision | Recorded in |
|---|---|---|
| Office names on cards | Handbook printed names (provisional) | `offices.json → decisions`, aliases marked confirmed |
| Admission questions | Stay with the **Office of the University Registrar** | `offices.json → decisions`; `office_lookup.json` unchanged |
| Student Discipline Office | Skipped for now, parked | `offices.json`, `SPRINTS.md` parked items |
| 4 office-duty scope questions | Kept | `scope_exemplars.jsonl` |
| Path B office naming | Keyword rule, **draft** | `data/office_keywords.json`, `shared/office_match.py` |

---

## Still open

1. **Keyword draft: the group's own test.** Write 10 referral questions *without opening
   `office_keywords.json`* (things students actually ask about facilities, payments, labs,
   IT, the clinic), then run them through the rule. This is the only independent test the draft
   will get. Needed before **Sprint 3**, because Sprint 3's referral cards show these offices.
   Sprint 2 doesn't depend on it.
2. **Keyword fallback.** What Path B shows when no keyword hits: no office plus a pointer to the
   information desk, or Student Affairs and Services as the default. Also needed before Sprint 3.
3. **Student Discipline Office.** Parked. No demo question depends on it.

## Recommendation

Sprint 1's deliverables are complete and correct. **Sign off and start Sprint 2.** Carry items 1
and 2 as parked items due before Sprint 3; they don't affect the static screen.
