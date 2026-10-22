# Knowledge-base table review (28 Sep 2026)

**Why:** `tools/check_passage_lengths.py` flagged 6 passages as too long for the 8 GB training limit and for
the embedding model's 512-token window. Before splitting anything, each was checked against the printed
manual, because tables in the Research Manual were hard to extract and the long passages may be tables kept
whole on purpose.

**Sources compared:** `data/corpus_demo.jsonl` against `ai_context/rag_pipeline/data/raw/*.pdf` (rendered page by
page), the chunker (`rag_pipeline/chunk_documents.py`, `data_cleaning.py`) and its own `table_report.json`.

**Nothing has been changed.** This is a review only.

**Page photos used for the comparison:** `docs/kb_table_review_pages/` (named by printed page).

---

## Verdict in one paragraph

The five long Research Manual passages are **whole tables, kept whole on purpose**. The chunker never splits
a table ("a table stays whole no matter what"). The old fix got the hard part right: each two-column outline
is stored as two separate lists (PROPOSAL PAPER, FINAL PAPER), not falsely paired row by row, and no item was
dropped. What went wrong is around the tables:
1. **The program name is cut off from its table.** None of the five outline passages says which program it
   is for.
2. **They are too long**, so dense search only sees the first part of each.
3. **Several smaller extraction errors**, listed below.

The sixth passage (HDBK-0209) is **not a table** and is faithful to the manual.

---

## 1. The five program outline tables (Research Manual pp. 53–63)

"In the succeeding pages are the outline for Proposal and Final Defense per program" (p. 52, item 9).
Each program has a two-column table, **PROPOSAL PAPER | FINAL PAPER**, running over two pages (three for
Industrial Engineering).

| Program (manual) | Pages | Table passage | Where its program label ended up |
|---|---|---|---|
| a. Psychology, Education, Nursing, Business | 53–54 | RSCH-0044 (826 tokens) | end of RSCH-0043 (the previous passage) |
| b. Industrial Engineering | 55–57 | RSCH-0046 (1,112) + RSCH-0047 | alone in RSCH-0045 (2 lines) |
| c. Electronics and Computer Engineering | 58–59 | RSCH-0048 (833) | end of RSCH-0047 |
| d. Information Technology Capstone | 60–61 | RSCH-0050 (831) | alone in RSCH-0049 (2 lines) |
| e. Computer Science Thesis | 62–63 | RSCH-0052 (840) | alone in RSCH-0051 (2 lines) |

### What is right
- **Every item is captured, in order**, under the correct column. Checked against pp. 53–63.
- **The columns are kept as separate lists.** This is correct: the two columns are not row-aligned (the
  final paper has extra sections), so pairing them row by row would invent relationships.
- **Nesting (indentation) is kept** as a nested list.
- **The manual's own quirks are copied faithfully.** These are not errors: "Studiies" (p. 55),
  "Validated Validated" (pp. 61, 63), the IE proposal appendix with no letter G (p. 56), the CS final paper
  listing the same hardware appendices as ECE/CpE (p. 63), and "Introduction" printed at the same level as
  "Chapter I" in the proposal column (p. 53).

### What is wrong (by impact)
1. **The table doesn't say which program it belongs to (high impact).** For example, the Computer Engineering
   outline (RSCH-0048) never contains the words "Computer Engineering", and the five outlines look almost the
   same.
   - Keyword search can't match a program name to its outline.
   - Even when the right outline is retrieved, the model can't tell whose outline it is. It would have to
     guess, or it would cite the wrong program's outline.
   - Three labels became tiny passages of their own (RSCH-0045, 0049, 0051) that answer nothing.
2. **Too long for the embedding model (high impact).** At 589–758 embedding tokens, everything past 512 is
   ignored by dense search. That means most of the FINAL PAPER column (and, for IE, the whole back half)
   cannot be found by meaning. The same passages are what break the 2,048-token training row limit.
3. **Industrial Engineering is broken in two (medium).**
   - Page 57 is a one-column continuation (FINAL PAPER, Chapters V–VII and Appendices).
   - The detector only recognises two-column headers, so page 57 was flattened into one run-on paragraph
     inside RSCH-0047, separated from the rest of the IE outline.
4. **Wrapped lines not joined (medium; already flagged in `table_report.json`, 14 places).** For example:
   - "Research Paradigm/Operational" + "Framework";
   - "Social Impact Brought by the Design" + "Project";
   - "D. Research Ethics Review Committee" + "Evaluation";
   - "Curriculum Vitae of Student" + "Researchers".

   Some of these show up as a fake sub-item, one level deeper than they should be.
5. **Wrong indent after a page break (low).** In the IE proposal column (p. 56), "Man-Machine Chart" through
   "Emergency Preparedness", and the Chapter III items, are stored one level deeper than printed. That makes
   them look like sub-items of "Process Chart".

---

## 2. Best Research evaluation tables (Research Manual pp. 51–52) — found during this review

Two small tables, **PARAMETERS | %**: one "FOR CCS and COE" (p. 51) and one "For other programs" (p. 52).
They have different weights (e.g. accuracy of data 10% vs 20%; software usability 25% only for CCS/COE).

- **Flattened into prose** (RSCH-0042, RSCH-0043): "... • PnC Research Agenda 10% Accuracy of Data and Facts
  Presented 10% ...". The 10% belongs to the whole "Relevance of the study" row, but it now reads as if it
  belongs to the last bullet.
- The two tables run together, and the second is split across two passages.
- **Risk:** a wrong percentage in an answer about how the Best Research award is judged.
- This region was not flagged by the old table report.

## 3. Grid tables (22 passages stored as "a | b | c" rows)

Spot-checked against the manual:
- research fees, collegiate and graduate (p. 50, RSCH-0041);
- degree vs terminal research paper (p. 32, RSCH-0016);
- internship hours per program (Internship Manual p. 22, INTN-0013).

**Rows and columns are intact.** The other 19 were not checked one by one.

## 4. HDBK-0209 (Student Manual pp. 212–213)

- **Not a table.** It is part of the bulleted list of serious offenses, and it matches the manual.
- 494 Llama tokens, 481 embedding tokens: inside the embedding limit, and only just over the 480 training
  guideline.
- **Only issue:** the heading "d. Serious Offense" is in HDBK-0207, so 0208–0210 don't say they list serious
  offenses (the same label problem as §1, milder).

---

## Options for the fix (for decision; nothing done)

The rule to add to the build procedure (Figure 4, Increment 2):

> A table is split only along its own structure, never mid-row or mid-item, and every piece repeats the
> table's caption and column header.

This is standard "table-aware chunking".

For the program outlines, this means **one passage per program per column**:

> "Outline for the Proposal Paper — c. For Electronics Engineering and Computer Engineering Researches:
> Preliminaries … Appendices …"

- Each passage is then about 300–550 tokens and names its program.
- Splitting by column loses nothing, because the columns were never row-paired.
- If one column is still over the limit (likely the IE final paper), split it between chapters and repeat
  the heading with "(continued)".

The other fixes, in the same rebuild:

| Fix | Effort | Removes |
|---|---|---|
| Program label into every outline passage; drop the 3 two-line label passages | low | issue 1 (the big one) |
| Split outlines by column (and IE final by chapter group) | low–medium | issue 2 + the training length limit |
| Treat the p. 57 one-column continuation as part of the IE final column | low | issue 3 |
| Join the 14 flagged wrapped lines | low (list exists) | issue 4 |
| Fix indent after the p. 56 page break | low | issue 5 |
| Render the p. 51/52 criteria tables as "Parameter \| %" rows with captions | low | §2 |
| Optional: put the list heading ("Serious Offense") at the top of HDBK-0208–0210 | low | §4 |

**Where to fix:** in the pipeline (`rag_pipeline`), so the manuscript's construction procedure stays true and
repeatable, not by hand-editing `corpus_demo.jsonl`. After the rebuild: re-embed, rebuild BM25, rerun
`tools/check_passage_lengths.py` (expected: all within limits), and re-check these pages against the manual.
