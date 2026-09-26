# Sprint 1 — Data report

Generated 2026-09-26 by `tools/make_data_report.py`. Do not edit by hand; re-run the tool.

This is the file you review to sign off Sprint 1. The five review checks from IMPLEMENTATION_PLAN.md §8 are at the bottom, each pointing at the section that answers it.

## Automatic checks

| # | Check | Result |
|---|---|---|
| 1 | corpus_demo.jsonl has 311 lines (has 311) | PASS |
| 2 | 53 passages excluded (excluded 53) | PASS |
| 3 | no kept passage lacks a '>' breadcrumb | PASS |
| 4 | no excluded passage has a '>' breadcrumb | PASS |
| 5 | document_id is unique in the kept set | PASS |
| 6 | every line of the three JSONL files parses as one JSON object (the strict reader stops on the first bad line) | PASS |
| 7 | each record's `row` equals its line index | PASS |
| 8 | every passage has the same fields in the same order | PASS |
| 9 | every generated file matches its MANIFEST.json hash | PASS |
| 10 | embeddings.npy was built from the current corpus_demo.jsonl (manifest pairing hash) | PASS |
| 11 | embeddings.npy is (311, 384) float32 (is (311, 384) float32) | PASS |
| 12 | every embedding row is unit length | PASS |
| 13 | re-embedding passages 0 / middle / last reproduces their rows (cos 1.0000, 1.0000, 1.0000) | PASS |
| 14 | passage 0 text is nearest to row 0 (nearest row: 0) | PASS |
| 15 | offices.json has 22 departments | PASS |
| 16 | offices.json has 6 divisions | PASS |
| 17 | 22 function statements, each starting 'To …' as printed | PASS |
| 18 | every alias points at a printed department (or is explicitly unresolved) | PASS |
| 19 | every office name in the corpus and office_lookup.json is printed on pp. 22–27 or listed as an alias | PASS |
| 20 | 20–25 scope exemplars (has 25) | PASS |
| 21 | every scope exemplar's source exists | PASS |
| 22 | no scope exemplar is a copy of a demo question | PASS |
| 23 | the old tokenizer, re-run here, reproduces the plan's §9 bm25 and cos numbers (so the old/new comparison in §6 is like for like) | PASS |
| 24 | every passage yields at least one BM25 token under the new tokenizer | PASS |
| 25 | office_keywords.json (DRAFT) covers exactly the 22 printed departments | PASS |
| 26 | no draft keyword is made only of stopwords | PASS |
| 27 | data/office_lookup.json is byte-identical to the input (confirmed flags intact) | PASS |

**27 of 27 automatic checks pass.** Automatic checks do not replace the human review below.

## 1. Knowledge base — `data/corpus_demo.jsonl`

One passage per line. Line *i* = record with `row: i` = row *i* of `embeddings.npy`. Build details are in `data/MANIFEST.json`, not in the records. Why JSONL: `data/README.md`.

Rule: keep a passage only if `page_or_section` contains a `>` breadcrumb (it sits under a numbered chapter and section).

| Document | Kept | Excluded | Total |
|---|---:|---:|---:|
| HDBK | 207 | 27 | 234 |
| INTN | 10 | 12 | 22 |
| RSCH | 94 | 14 | 108 |
| **All** | **311** | **53** | **364** |

Source `inputs/corpus.json` sha256 `8ca8e916d46486fc…`

### 1a. Spot-check sample (review check 1)

Ten excluded passages drawn at random (seed 20260926, so the sample is the same every run). For each: is it genuinely front matter, with no answerable policy in it?

| ☐ | ID | page_or_section | Opening text |
|---|---|---|---|
| ☐ | HDBK-0003 | p. 6 | MESSAGE FROM THE CITY MAYOR/ CHAIRMAN OF THE BOARD Sa ngalan ng lungsod at ng pinahahalagahang Board of Regen… |
| ☐ | HDBK-0021 | INSTITUTIONAL RECOGNITIONS (p. 33) | INSTITUTIONAL RECOGNITIONS LEVEL 2 ACCREDITATION ALCUCOA (2022) 1. Bachelor of Secondary Education major in S… |
| ☐ | HDBK-0110 | PART 3. STUDENT SUCCESS (p. 119) | PART 3. STUDENT SUCCESS Welcome to the Student Success section of the Student Manual. At Pamantasan ng Cabuya… |
| ☐ | INTN-0002 | p. 5 | INTERNSHIP MANUAL Description The University's recognition of the importance of providing practical learning … |
| ☐ | INTN-0003 | p. 5 | Furthermore, the internship program nurtures students' communication and interpersonal skills. They interact … |
| ☐ | INTN-0005 | p. 7 | MESSAGE FROM THE UNIVERSITY PRESIDENT Internships provide a unique opportunity for students to bridge the gap… |
| ☐ | INTN-0008 | INSTITUTIONAL PHILOSOPHY & OBJECTIVES (p. 13) | INSTITUTIONAL PHILOSOPHY & OBJECTIVES INSTITUTIONAL VISION A premier educational institution of higher learni… |
| ☐ | INTN-0012 | GUIDELINES (p. 21) | GUIDELINES MANAGEMENT OF INTERNSHIP AT UNIVERSITY OF CABUYAO (PAMANTASAN NG CABUYAO) PNC:AA-GU-13 The Univers… |
| ☐ | RSCH-0002 | p. 5 | STUDENT RESEARCH AND INNOVATION PROGRAM Description One of the core commitments of the University of Cabuyao … |
| ☐ | RSCH-0013 | KNOWLEDGE MANAGEMENT AND INNOVATION DEPARTMENT PHILOSOPHY AND OBJECTIVES (p. 19) | KNOWLEDGE MANAGEMENT AND INNOVATION DEPARTMENT PHILOSOPHY AND OBJECTIVES QUALITY OBJECTIVES To improve the un… |

### 1b. All 53 excluded passages

<details><summary>Show all</summary>

| ID | page_or_section | Opening text |
|---|---|---|
| INTN-0001 | p. 4 | UNIVERSITY OF CABUYAO Katapatan Mutual Homes, Brgy. Banay-banay, City of Cabuya… |
| INTN-0002 | p. 5 | INTERNSHIP MANUAL Description The University's recognition of the importance of… |
| INTN-0003 | p. 5 | Furthermore, the internship program nurtures students' communication and interp… |
| INTN-0004 | p. 6 | MESSAGE FROM THE CITY MAYOR/ CHAIRMAN OF THE BOARD Binabati ko kayo ng pinakama… |
| INTN-0005 | p. 7 | MESSAGE FROM THE UNIVERSITY PRESIDENT Internships provide a unique opportunity … |
| INTN-0006 | p. 8 | MESSAGE FROM THE VICE PRESIDENT FOR ACADEMIC AFFAIRS An internship can be an im… |
| INTN-0007 | p. 9 | MESSAGE FROM THE VICE PRESIDENT FOR STUDENT DEVELOPMENT AND AUXILIARY SERVICES … |
| INTN-0008 | INSTITUTIONAL PHILOSOPHY & OBJECTIVES (p. 13) | INSTITUTIONAL PHILOSOPHY & OBJECTIVES INSTITUTIONAL VISION A premier educationa… |
| INTN-0009 | INSTITUTIONAL PHILOSOPHY & OBJECTIVES (p. 13) | INSTITUTIONAL PHILOSOPHY & OBJECTIVES To strengthen industry-academe-LGU linkag… |
| INTN-0010 | GRADUATE ATTRIBUTES (p. 15) | GRADUATE ATTRIBUTES Professionally Competent Individual Demonstrate the qualiti… |
| INTN-0011 | PLACEMENT, ALUMNI, AND LINKAGES PHILOSOPHY AND OBJECTIVES (p. 17) | PLACEMENT, ALUMNI, AND LINKAGES PHILOSOPHY AND OBJECTIVES QUALITY OBJECTIVES To… |
| INTN-0012 | GUIDELINES (p. 21) | GUIDELINES MANAGEMENT OF INTERNSHIP AT UNIVERSITY OF CABUYAO (PAMANTASAN NG CAB… |
| HDBK-0001 | p. 4 | UNIVERSITY OF CABUYAO Katapatan Mutual Homes, Brgy. Banay-banay, City of Cabuya… |
| HDBK-0002 | p. 5 | STUDENT MANUAL Description The Student Manual serves as a comprehensive guide a… |
| HDBK-0003 | p. 6 | MESSAGE FROM THE CITY MAYOR/ CHAIRMAN OF THE BOARD Sa ngalan ng lungsod at ng p… |
| HDBK-0004 | p. 7 | MESSAGE FROM THE UNIVERSITY PRESIDENT It is with great pleasure and excitement … |
| HDBK-0005 | p. 8 | MESSAGE FROM THE VICE PRESIDENT FOR STUDENT DEVELOPMENT AND AUXILIARY SERVICES … |
| HDBK-0006 | p. 9 | MESSAGE FROM THE DIRECTOR OF STUDENT AFFAIRS AND SERVICES DEPARTMENT It is with… |
| HDBK-0007 | OUR HISTORY (p. 13) | OUR HISTORY On April 16, 2003, then-municipal mayor Proceso D. Aguillo signed M… |
| HDBK-0008 | OUR HISTORY (pp. 14-15) | OUR HISTORY In light of the anticipated closure of LSPC-Cabuyao, faculty member… |
| HDBK-0009 | OUR HISTORY (p. 15) | OUR HISTORY The university produced topnotchers in the fields of education, nur… |
| HDBK-0010 | UNIVERSITY SYMBOLS (pp. 17-18) | UNIVERSITY SYMBOLS THE UNIVERSITY LOGO The logo features a green circular outer… |
| HDBK-0011 | UNIVERSITY SYMBOLS (p. 18) | UNIVERSITY SYMBOLS The atoms are written in an open book and convey the univers… |
| HDBK-0012 | UNIVERSITY SYMBOLS (p. 19) | UNIVERSITY SYMBOLS UNIVERSITY MACE The University of Cabuyao mace is a regally … |
| HDBK-0013 | INSTITUTIONAL PHILOSOPHY & OBJECTIVES (p. 21) | INSTITUTIONAL PHILOSOPHY & OBJECTIVES INSTITUTIONAL VISION A premier educationa… |
| HDBK-0014 | INSTITUTIONAL PHILOSOPHY & OBJECTIVES (p. 21) | INSTITUTIONAL PHILOSOPHY & OBJECTIVES To strengthen industry-academe-LGU linkag… |
| HDBK-0015 | DIVISIONAL PHILOSOPHY & OBJECTIVES (p. 23) | DIVISIONAL PHILOSOPHY & OBJECTIVES OFFICE OF THE UNIVERSITY PRESIDENT PHILOSOPH… |
| HDBK-0016 | DIVISIONAL PHILOSOPHY & OBJECTIVES (pp. 24-25) | DIVISIONAL PHILOSOPHY & OBJECTIVES ACADEMIC AFFAIRS PHILOSOPHY & OBJECTIVES Col… |
| HDBK-0017 | DIVISIONAL PHILOSOPHY & OBJECTIVES (p. 25) | DIVISIONAL PHILOSOPHY & OBJECTIVES Entrepreneurship and Business Development De… |
| HDBK-0018 | DIVISIONAL PHILOSOPHY & OBJECTIVES (pp. 26-27) | DIVISIONAL PHILOSOPHY & OBJECTIVES PLANNING, RESEARCH, & EXTENSION PHILOSOPHY &… |
| HDBK-0019 | DIVISIONAL PHILOSOPHY & OBJECTIVES (p. 27) | DIVISIONAL PHILOSOPHY & OBJECTIVES Gender and Development Department To create … |
| HDBK-0020 | GRADUATE ATTRIBUTES (p. 29) | GRADUATE ATTRIBUTES Professionally Competent Individual Demonstrate the qualiti… |
| HDBK-0021 | INSTITUTIONAL RECOGNITIONS (p. 33) | INSTITUTIONAL RECOGNITIONS LEVEL 2 ACCREDITATION ALCUCOA (2022) 1. Bachelor of … |
| HDBK-0022 | INSTITUTIONAL RECOGNITIONS (p. 34) | INSTITUTIONAL RECOGNITIONS CHED-INSTITUTIONAL RECOGNITION CERTIFICATE OF PROGRA… |
| HDBK-0023 | INSTITUTIONAL RECOGNITIONS (p. 35) | INSTITUTIONAL RECOGNITIONS COPC No. 163 s. 2022 • Bachelor of Science in Comput… |
| HDBK-0024 | PART 1. ADMISSION & ENROLLMENT (p. 37) | PART 1. ADMISSION & ENROLLMENT The University of Cabuyao has established clear … |
| HDBK-0043 | PART 2. ACADEMIC GUIDELINES (p. 57) | PART 2. ACADEMIC GUIDELINES The University of Cabuyao has established clear and… |
| HDBK-0110 | PART 3. STUDENT SUCCESS (p. 119) | PART 3. STUDENT SUCCESS Welcome to the Student Success section of the Student M… |
| HDBK-0192 | PART 4. CODE OF CONDUCT AND DISCIPLINARY PROCEDURES (p. 197) | PART 4. CODE OF CONDUCT AND DISCIPLINARY PROCEDURES Welcome to the Code of Cond… |
| RSCH-0001 | p. 4 | UNIVERSITY OF CABUYAO Katapatan Mutual Homes, Brgy. Banay-banay, City of Cabuya… |
| RSCH-0002 | p. 5 | STUDENT RESEARCH AND INNOVATION PROGRAM Description One of the core commitments… |
| RSCH-0003 | p. 5 | By providing necessary support and resources, the University seeks to unleash t… |
| RSCH-0004 | p. 6 | MESSAGE FROM THE CITY MAYOR/ CHAIRMAN OF THE BOARD Mahal naming mga mananaliksi… |
| RSCH-0005 | p. 7 | MESSAGE FROM THE UNIVERSITY PRESIDENT It is with great pride and admiration tha… |
| RSCH-0006 | p. 8 | MESSAGE FROM THE VICE PRESIDENT FOR PLANNING, RESEARCH, & EXTENSION Research is… |
| RSCH-0007 | p. 9 | MESSAGE FROM THE DIRECTOR OF RESEARCH AND DEVELOPMENT DEPARTMENT We are delight… |
| RSCH-0008 | p. 10 | MESSAGE FROM THE DIRECTOR FOR KNOWLEDGE MANAGEMENT AND INNOVATION DEPARTMENT In… |
| RSCH-0009 | INSTITUTIONAL PHILOSOPHY & OBJECTIVES (p. 13) | INSTITUTIONAL PHILOSOPHY & OBJECTIVES INSTITUTIONAL VISION A premier educationa… |
| RSCH-0010 | INSTITUTIONAL PHILOSOPHY & OBJECTIVES (p. 13) | INSTITUTIONAL PHILOSOPHY & OBJECTIVES To strengthen industry-academe-LGU linkag… |
| RSCH-0011 | GRADUATE ATTRIBUTES (p. 15) | GRADUATE ATTRIBUTES Professionally Competent Individual Demonstrate the qualiti… |
| RSCH-0012 | RESEARCH AND DEVELOPMENT DEPARTMENT PHILOSOPHY AND OBJECTIVES (p. 17) | RESEARCH AND DEVELOPMENT DEPARTMENT PHILOSOPHY AND OBJECTIVES QUALITY OBJECTIVE… |
| RSCH-0013 | KNOWLEDGE MANAGEMENT AND INNOVATION DEPARTMENT PHILOSOPHY AND OBJECTIVES (p. 19) | KNOWLEDGE MANAGEMENT AND INNOVATION DEPARTMENT PHILOSOPHY AND OBJECTIVES QUALIT… |
| RSCH-0014 | NETWORK AND LINKAGES (p. 27) | NETWORK AND LINKAGES RESEARCH AND DEVELOPMENT DEPARTMENT USAID ESP: CALABARZON … |

</details>

Watch for: HDBK-0024, HDBK-0043, HDBK-0110 and HDBK-0192 are **part title pages** (e.g. `PART 2. ACADEMIC GUIDELINES (p. 57)`). Read their text: a part title page that also carries an introductory policy paragraph would be a real passage lost.

## 2. Embeddings — `data/embeddings.npy`

- Shape `(311, 384)`, dtype `float32`, 477,824 bytes
- Model `BAAI/bge-small-en-v1.5` on `cpu`, normalised, no query instruction — the same settings as every score measured in the plan (§7, §9)
- Row order: row i = line i of corpus_demo.jsonl = record with row == i
- Built from `corpus_demo.jsonl` sha256 `4f60d7fecc51c3fc…` — matches the current file

| Row | Passage | Re-embedded cos |
|---:|---|---:|
| 0 | INTN-0013 · GUIDELINES > Section 1. General Policies (p. 22) | 1.0000 |
| 155 | HDBK-0172 · PART 3. STUDENT SUCCESS > CHAPTER IX LIBRARY SERVICES > Section 2. Sp… | 1.0000 |
| 310 | RSCH-0108 · GUIDELINES > CHAPTER VI MANAGEMENT OF INNOVATION AND START-UP PROJECT… | 1.0000 |

## 3. Office list — `data/offices.json` and `data/office_exemplars.jsonl`

Extracted by `tools/build_office_exemplars.py` from **UC-PnC Student Handbook (Learner's Handbook Revised Edition 2023-2028), "Divisional Philosophy & Objectives", pp. 22-27** (`inputs/UC-PnC-Student-Handbook-Manual.pdf`, sha256 `38881d5fc72be4c0…`). The tool stops if any name below is not found in the PDF text exactly as written.

### 3a. Names and statements (review checks 2 and 3)

Open the printed handbook at pp. 22–27 beside this table. Tick a row only when the name matches letter for letter (watch `and` vs `&`, commas, `Office of the …`) and the statement matches word for word.

| ☐ | p. | Division | Department (as printed) | Function statement (verbatim) |
|---|---:|---|---|---|
| ☐ | 23 | Office of the University President | Office of the University Secretary / Board Secretary | To maintain open lines of communication between Board members and University officials |
| ☐ | 23 | Office of the Executive Vice President | Management Information Systems Department | To keep technological infrastructures accessible and up to date to respond to evolving service demands |
| ☐ | 23 | Office of the Executive Vice President | Data Protection Department | To monitor the University’s compliance with all applicable data protection laws and policies |
| ☐ | 24 | Academic Affairs | Colleges and Senior High School | To ensure that academic programs are continually upgraded to maintain high standards of quality and excellence |
| ☐ | 24 | Academic Affairs | Office of the University Registrar | To ensure an efficient system for managing student records, which will aid Pamantasan ng Cabuyao in the promotion and implementation of its educational programs. |
| ☐ | 24 | Academic Affairs | Office of the University Library | To provide innovative library services with relevant and updated resources among teaching and non-teaching personnel, students, and outside researchers, which will support the University’s instructional and learning programs |
| ☐ | 25 | Administration | University Health Department | To provide quality medical and dental care to the students and personnel, which will allow them to perform optimally |
| ☐ | 25 | Administration | Laboratory Services and Disaster Risk Reduction Management Department | To reduce the vulnerability to and impact of disasters at the University and provide quality laboratory service and assistance to teaching personnel and students, who are conducting technical and scientific investigations |
| ☐ | 25 | Administration | Property Management and General Services Department | To continue upgrading the physical infrastructure and facilities, to ensure an effective and efficient procurement and inventory services, and to safeguard the assets and personnel that would make Pamantasan ng Cabuyao (University of Cabuyao) conducive to learning |
| ☐ | 25 | Administration | Human Resource Management Department | To ensure that the teaching and non-teaching personnel at Pamantasan ng Cabuyao (University of Cabuyao) consistently grow personally and professionally through initiatives that maximize their potential for the advancement of overall human development. |
| ☐ | 25 | Administration | Entrepreneurship and Business Development Department | To contribute and support the sustainability of the institution through implementation of income and long-term impact development projects. |
| ☐ | 25 | Administration | Finance Department | To ensure effective financial management and compliance by maintaining accurate and up-to-date financial records, developing and monitoring budgets, optimizing financial performance, and providing excellent customer service while following proper accounting and cash handling procedures. |
| ☐ | 26 | Planning, Research, & Extension | Quality Management and Planning Department | To ensure organizational efficiency and continuous improvement through accreditation and certification |
| ☐ | 26 | Planning, Research, & Extension | Community and Extension Services Department | To develop, disseminate, and implement research-based, relevant, innovative, and sustainable extension and services programs that will improve the quality of life of the target clientele |
| ☐ | 26 | Planning, Research, & Extension | Research and Development Department | To transform the PnC (UC) academic community into research-competent teaching and non-teaching personnel and students who can enhance human knowledge and apply research results to genuine needs in the community and society |
| ☐ | 26 | Planning, Research, & Extension | Knowledge Management and Innovation Department | To improve the university’s organizational efficiency by utilizing information and communication technologies for knowledge development, production, and dissemination, as well as by applying for patents and intellectual property protection |
| ☐ | 27 | Student Development & Auxiliary Services | Student Affairs and Services Department | To provide a variety of activities geared at students that will complement their academic studies and advance their entire development as productive players in nation-building |
| ☐ | 27 | Student Development & Auxiliary Services | Sports and Development Department | To develop and enhance student-athletes’ character, skills, and talents through physical activities and sport opportunities, as well as an efficient training program who will represent the university in local, national, regional, and international competitions |
| ☐ | 27 | Student Development & Auxiliary Services | Guidance and Counseling Department | To foster and improve students’ academic, social, emotional and personal development in order to ensure individual student success in current and future endeavors |
| ☐ | 27 | Student Development & Auxiliary Services | Admissions Department | To recruit and communicate with prospective and admitted students using an efficient technology-enabled process |
| ☐ | 27 | Student Development & Auxiliary Services | Placement, Alumni, and Linkage Department | To engage with beneficial alliances with enterprises, industries, educational institutions, and private or public companies or agencies that will aid the university in achieving its objectives and mission and enhance the standard of its academic program. |
| ☐ | 27 | Student Development & Auxiliary Services | Gender and Development Department | To create initiatives that promote gender-inclusiveness and gender-sensitive spaces within the University |

Two statements contain a hyphen at a line break in the print: `research-competent` (p. 26) and `gender-sensitive` (p. 27). The tool kept the hyphen. Confirm both are hyphenated compounds in the print, not words split across a line.

### 3b. Divisions

| ID | Display name | Printed header | p. | Depts |
|---|---|---|---:|---:|
| OUP | Office of the University President | OFFICE OF THE UNIVERSITY PRESIDENT | 23 | 1 |
| OEVP | Office of the Executive Vice President | OFFICE OF THE EXECUTIVE VICE PRESIDENT | 23 | 2 |
| AA | Academic Affairs | ACADEMIC AFFAIRS | 24 | 3 |
| ADMIN | Administration | ADMINISTRATION | 25 | 6 |
| PRE | Planning, Research, & Extension | PLANNING, RESEARCH, & EXTENSION | 26 | 4 |
| SDAS | Student Development & Auxiliary Services | STUDENT DEVELOPMENT & AUXILIARY SERVICES | 27 | 6 |

Display names are title case of the printed header; `&` is kept where the print uses `&`.

### 3c. Names the corpus uses that pp. 22–27 do not print

The corpus `issuing_office` field and `office_lookup.json` were built from the manuals' prose, before pp. 22–27 were used as the authority. Where the two disagree, `offices.json` records an alias. **Every alias is `confirmed: false` until a group member confirms it.**

| Confirmed | Name in corpus / lookup | Maps to (printed) | Evidence | Decision |
|---|---|---|---|---|
| ✓ | University Library | Office of the University Library | Same unit; pp. 22-27 print the full name 'Office of the University Library'. | Group decision 2026-09-26 (provisional): cards show the printed name. |
| ✓ | Linkages Department | Placement, Alumni, and Linkage Department | p. 27 prints 'Placement, Alumni, and Linkage Department'; the Internship Manual front matter reads 'PLACEMENT, ALUMNI, AND LINKAGES'. Already an open question in office_lookup.json. | Group decision 2026-09-26 (provisional): cards show the printed name. |
| — | Student Discipline Office | **unresolved** | Named 7x in Handbook prose, not printed on pp. 22-27. Separate unit or a function inside Student Affairs and Services? Unresolved. | Skipped for now (parked 2026-09-26). Cards show 'Student Discipline Office' as the Handbook prose writes it. |
| — | Cashier's Office | Finance Department | Named 10x in corpus prose. Cash handling is in the Finance Department's printed function; reporting line not confirmed. | Not shown on any card: no office_lookup rule uses this name. |
| — | Accounting Department | Finance Department | Named 2x in corpus prose. Accounting is in the Finance Department's printed function; reporting line not confirmed. | Not shown on any card: no office_lookup rule uses this name. |

**Decisions on record** (`offices.json → decisions`):

- **office names on cards** (provisional, 2026-09-26): Use the names printed on Handbook pp. 22-27. A corpus or lookup name is shown through its alias above.
- **admission questions** (decided, 2026-09-26): Admission stays with the Office of the University Registrar, as office_lookup.json already routes it. p. 27 prints an Admissions Department; the group chose the Registrar.
- **Student Discipline Office** (parked, 2026-09-26): Skipped for now. Revisit when someone can confirm whether it is a separate office.

### 3d. What pp. 22–27 now answer in `office_lookup.json`'s open questions

`office_lookup.json` is copied unchanged. Its `open_questions` were written before pp. 22–27 were read. Status of each against the printed list:

| Open question | What pp. 22–27 say |
|---|---|
| ADMISSIONS | p. 27 prints an **Admissions Department** under SDAS. **Decided 2026-09-26: admission stays with the Office of the University Registrar.** The rule in office_lookup.json is unchanged; the decision is recorded in offices.json. |
| ALUMNI / INTERNSHIP | p. 27 prints **Placement, Alumni, and Linkage Department**. **Decided 2026-09-26 (provisional): cards show the printed name.** |
| STUDENT DISCIPLINE OFFICE | Not printed on pp. 22–27. **Skipped for now (parked 2026-09-26).** Cards show the name as the Handbook prose writes it. |
| CURRENT UNIT NAMES | Student Affairs and Services Department, University Health Department and Management Information Systems Department are all printed exactly so in the 2023–2028 edition. |
| SCHOLARSHIP | No scholarship office is printed on pp. 22–27. The SASD placeholder stands. **Still open.** |

### 3e. Office names in use, and where each comes from

| Name | In corpus | In lookup | Printed pp. 22–27 | Alias |
|---|:-:|:-:|:-:|:-:|
| Accounting Department |  | ✓ |  | ✓ |
| Cashier's Office |  | ✓ |  | ✓ |
| Guidance and Counseling Department | ✓ | ✓ | ✓ |  |
| Knowledge Management and Innovation Department | ✓ | ✓ | ✓ |  |
| Linkages Department | ✓ | ✓ |  | ✓ |
| Management Information Systems Department | ✓ | ✓ | ✓ |  |
| Office of the University Registrar | ✓ | ✓ | ✓ |  |
| Research and Development Department | ✓ | ✓ | ✓ |  |
| Sports and Development Department | ✓ | ✓ | ✓ |  |
| Student Affairs and Services Department | ✓ | ✓ | ✓ |  |
| Student Discipline Office | ✓ | ✓ |  | ✓ |
| University Health Department | ✓ | ✓ | ✓ |  |
| University Library | ✓ | ✓ |  | ✓ |

`office_lookup.json`: 40 rules, 18 confirmed, 22 `confirmed: false`. Flags kept as the record.

## 4. Scope exemplars — `data/scope_exemplars.jsonl` (review check 4)

25 questions replace the 20 generic ones in `inputs/scope_exemplars_old.json`. Read each aloud: would a UC-PnC student actually type this? Rewrite any that sound like somewhere else.

| ☐ | Exemplar | Source | Passages under source | Nearest demo question | cos |
|---|---|---|---:|---|---:|
| ☐ | What documents do transferees need to submit for admission? | HDBK › GUIDELINES > CHAPTER I STUDENT ADMISSION | 6 | What are the requirements for student admission? | 0.772 |
| ☐ | How do I enrol if I am an irregular student? | HDBK › GUIDELINES > CHAPTER II STUDENT ENROLMENT | 12 | What are the requirements for student admission? | 0.701 |
| ☐ | What should I do if I missed my final examination? | HDBK › PART 2. ACADEMIC GUIDELINES > CHAPTER I STUDENT EXAMINATION | 3 | How do I request a copy of my academic records? | 0.649 |
| ☐ | How do I request a Transcript of Records from the Registrar? | HDBK › PART 2. ACADEMIC GUIDELINES > CHAPTER II ISSUANCE OF STUDENTS ACADEMIC RECORDS | 9 | How do I request a copy of my academic records? | 0.797 |
| ☐ | What happens if I fail too many units in one semester? | HDBK › PART 2. ACADEMIC GUIDELINES > CHAPTER III RETENTION GUIDELINE | 4 | How do I report a broken air conditioner in our classroom? | 0.607 |
| ☐ | What grade average do I need to make the President's List this semester? | HDBK › PART 2. ACADEMIC GUIDELINES > CHAPTER IV SEMESTRAL ACADEMIC HONORS | 2 | What are the requirements for student admission? | 0.700 |
| ☐ | What permits do we need before our class goes on an educational trip? | HDBK › PART 2. ACADEMIC GUIDELINES > CHAPTER VI MANAGEMENT OF EDUCATIONAL TRIPS | 19 | What are the requirements for student admission? | 0.705 |
| ☐ | How do I submit my requirements through Pinnacle? | HDBK › PART 2. ACADEMIC GUIDELINES > CHAPTER VII USE OF PINNACLE | 4 | What are the requirements for student admission? | 0.711 |
| ☐ | What are the requirements to be cleared for graduation? | HDBK › PART 2. ACADEMIC GUIDELINES > CHAPTER VIII | 7 | What are the requirements for student admission? | 0.789 |
| ☐ | What are the penalties for overdue library materials? | HDBK › PART 3. STUDENT SUCCESS > CHAPTER IX LIBRARY SERVICES | 13 | How do I borrow a book from the university library? | 0.629 |
| ☐ | How do we renew the recognition of our student organization? | HDBK › PART 3. STUDENT SUCCESS > CHAPTER III RECOGNITION AND RENEWAL | 10 | How do I request a copy of my academic records? | 0.659 |
| ☐ | How do I apply for a university scholarship? | HDBK › PART 3. STUDENT SUCCESS > CHAPTER IV SCHOLARSHIP | 5 | What are the requirements for student admission? | 0.724 |
| ☐ | How can I set an appointment with a guidance counselor? | HDBK › PART 3. STUDENT SUCCESS > CHAPTER VII GUIDANCE AND COUNSELING | 6 | Who do I contact to request a copy of my Form 137? | 0.572 |
| ☐ | Can I get a medical certificate from the university clinic? | HDBK › PART 3. STUDENT SUCCESS > CHAPTER X MEDICAL AND DENTAL | 6 | Is there a dental clinic on campus and what are its hours? | 0.636 |
| ☐ | How do I try out for a varsity team? | HDBK › PART 3. STUDENT SUCCESS > CHAPTER II SPORTS DEVELOPMENT | 10 | What are the requirements for student admission? | 0.613 |
| ☐ | Who is qualified to run in the student council elections? | HDBK › PART 3. STUDENT SUCCESS > CHAPTER VI PAMANTASAN NG CABUYAO STUDENT ELECTIONS | 10 | What are the requirements for student admission? | 0.687 |
| ☐ | What is the sanction for cheating during an exam? | HDBK › PART 4. CODE OF CONDUCT AND DISCIPLINARY PROCEDURES > CHAPTER II STUDENT DISCIPLINE | 18 | How do I request a copy of my academic records? | 0.557 |
| ☐ | How do I file a formal grievance against a faculty member? | HDBK › PART 4. CODE OF CONDUCT AND DISCIPLINARY PROCEDURES > CHAPTER III STUDENT GRIEVANCE | 6 | How do I request a copy of my academic records? | 0.670 |
| ☐ | How do we apply for ethics review of our research proposal? | RSCH › GUIDELINES > CHAPTER II INSTITUTIONAL AND STUDENT RESEARCH ETHICS REVIEW | 17 | What is the format of the research title page? | 0.624 |
| ☐ | Who owns the intellectual property rights to our capstone project? | RSCH › GUIDELINES > CHAPTER V INTELLECTUAL PROPERTY RIGHTS | 16 | Who do I contact to request a copy of my Form 137? | 0.561 |
| ☐ | What documents do I need before starting my internship? | INTN › GUIDELINES > Section 2. Specific Policies | 9 | How many hours is the required internship? | 0.721 |
| ☐ | Which office handles school payments and official receipts? | p. 25 · Finance Department | 1 | How do I request a copy of my academic records? | 0.685 |
| ☐ | Who is in charge of maintaining campus buildings and facilities? | p. 25 · Property Management and General Services Department | 1 | Can I park my motorcycle inside the campus? | 0.616 |
| ☐ | Who assists students using the science laboratories? | p. 25 · Laboratory Services and Disaster Risk Reduction Management Department | 1 | Who repairs the broken chairs in our classroom? | 0.654 |
| ☐ | Who do I contact if I cannot log in to my student portal account? | p. 23 · Management Information Systems Department | 1 | How do I request a copy of my academic records? | 0.671 |

The last column is a leak check, not a threshold. It shows how close each exemplar sits to a question we will ask on stage. Scope exemplars must describe the helpdesk's domain; they must not be the demo questions reworded. If a row looks like a paraphrase of its nearest demo question, rewrite it.

**Four exemplars come from pp. 23 and 25, not from the manuals.** They are there so the scope gate treats facilities, finance, laboratories and IT as university business. What they change, measured on the demo's B and C questions (best cosine against the exemplars, question vs question):

| Path | Question | With the 4 | Without | Nearest exemplar (with) |
|---|---|---:|---:|---|
| B | How do I report a broken air conditioner in our classroom? | 0.657 | 0.657 | How do I file a formal grievance against a faculty member? |
| B | Where do I return my borrowed laboratory apron? | 0.608 | 0.602 | Who assists students using the science laboratories? |
| B | Where is the nearest ATM on campus? | 0.621 | 0.541 | Which office handles school payments and official receipts? |
| B | Who repairs the broken chairs in our classroom? | 0.654 | 0.634 | Who assists students using the science laboratories? |
| B | Can I park my motorcycle inside the campus? | 0.638 | 0.638 | How do I enrol if I am an irregular student? |
| C | Where can I eat near campus? | 0.571 | 0.562 | Who is in charge of maintaining campus buildings and facilities? |
| C | Write me a poem about my thesis. | 0.574 | 0.574 | How do we apply for ethics review of our research proposal? |
| C | Will it rain tomorrow in Cabuyao? | 0.466 | 0.466 | What should I do if I missed my final examination? |

Without the 4, the highest C score is 0.574. Any B question below that would be sent to the out-of-scope message. **In this set that happens to the ATM question only.** The others score the same with or without, because they already resemble a manual-based exemplar. The side effect runs the other way too: *Where can I eat near campus?* sits closest to the buildings exemplar, so the 4 also nudge that C question up slightly. Say both if asked.

<details><summary>The 20 exemplars being replaced</summary>

- How do I request a leave of absence?
- What is the deadline to drop a course?
- How do I appeal a final grade?
- What happens if I violate the academic integrity policy?
- When does the add/drop period end?
- What is the process for withdrawing from a course?
- How do I file a complaint against a professor?
- What are the requirements for graduation?
- How do I apply for financial aid?
- What is the policy on academic probation?
- How do I request an official transcript?
- What is the procedure for changing my major?
- How do I report a lost student ID card?
- What are the rules for using the university library?
- How do I register for classes next semester?
- What is the tuition refund policy?
- How do I contact the registrar's office?
- What is the process for requesting disability accommodations?
- How do I dispute a parking ticket on campus?
- What is the code of conduct for students?

</details>

## 5. BM25 tokenizer — `shared/tokenizer.py`

There is no BM25 index file. The index is built in memory at start-up from the `text` field of `corpus_demo.jsonl`, with the tokenizer below, and the same function tokenizes every query. Settings are recorded in `MANIFEST.json` under `corpus_demo.jsonl → bm25`. Tokenizer version: `regex-stopwords-snowball-v1`.

| Pipeline step | Example |
|---|---|
| lowercase + regex words `[a-z0-9]+` | `Records?` → `records` |
| drop 1-character tokens | `1.` · `a.` · the `s` of `student's` |
| drop English stopwords (NLTK list) | `what` · `are` · `the` · `on` |
| Snowball (Porter2) stemming | `policies` → `polici` · `enrollment`, `enrolment` → `enrol` |

### 5a. Old tokenizer vs new, on the 311 passages

| | Old: `text.lower().split()` | New: regex + stopwords + Snowball |
|---|---:|---:|
| unique indexed terms | 8,225 | 3,200 |
| average passage length (BM25 normalises by this) | 214 tokens | 133 tokens |
| terms with punctuation glued on | 3,157 | 0 |

Glued terms the old index treated as different words, a sample: `"5.0".`, `"accredited`, `"certified`, `"classified`, `"college"`, `"completed"`, `"confidential`, `"confirmed"`, `"copy`, `"dropped"`, `"eea"`, `"eua."`.

### 5b. What a question looks like to BM25

| Question | Old tokens | New tokens |
|---|---|---|
| What is the format of the research title page? | `what is the format of the research title page?` | `format research titl page` |
| What are the requirements for student admission? | `what are the requirements for student admission?` | `requir student admiss` |
| Where do I return my borrowed laboratory apron? | `where do i return my borrowed laboratory apron?` | `return borrow laboratori apron` |
| Write me a poem about my thesis. | `write me a poem about my thesis.` | `write poem thesi` |
| Write me a poem about my thesis | `write me a poem about my thesis` | `write poem thesi` |
| What is the capital of Japan? | `what is the capital of japan?` | `capit japan` |

### 5c. Two things Sprint 5 must handle

- **A question can tokenize to nothing.** `What is it?`, `Who are you?` are all stopwords, so they return no tokens and every BM25 score is 0. The retriever must treat that as *no lexical evidence*, not as an error.
- **5 of 311 passages are longer than BGE's 512-token limit** and are silently cut off when embedded: RSCH-0044 (593), RSCH-0046 (758), RSCH-0048 (594), RSCH-0050 (589), RSCH-0052 (601). BM25 still sees their full text, so the lexical half covers the missing part. This is a known limit of this build; do not re-chunk in this sprint.

## 6. The demo questions, re-measured

The plan's §7.1 and §9 scores were measured with the **old** tokenizer and **no** BGE query instruction. This table re-runs all 18 of those questions both ways. **It chooses no thresholds.** That is Sprint 4. It answers one question: *does the demo set still route the way §9 assumes?*

| Path | Role | Question | bm25 old → new | top-1 BM25 (new) | cos old → new | top-1 dense (new) | scope sim |
|---|---|---|---:|---|---:|---|---:|
| A | demo | What is the format of the research title page? | 18.05 → **10.04** | RSCH-0055 ⟲ | 0.729 → **0.701** | RSCH-0030 ✗ expected RSCH-0016 | 0.624 |
| A | demo | How do I borrow a book from the university library? | 16.90 → **21.26** | HDBK-0172 ⟲ | 0.739 → **0.723** | HDBK-0171 ✓ | 0.674 |
| A | demo | How many hours is the required internship? | 13.50 → **11.73** | INTN-0013 | 0.716 → **0.699** | INTN-0018 ✓ | 0.721 |
| A | spare | What are the requirements for student admission? | 13.89 → **8.05** | HDBK-0028 ⟲ | 0.737 → **0.728** | HDBK-0028 ✓ | 0.789 |
| A | spare | Is there a dental clinic on campus and what are its hours? | 18.35 → **10.17** | HDBK-0180 | 0.643 → **0.626** | HDBK-0180 | 0.636 |
| A | calibration | How do I request a copy of my academic records? | 12.21 → **10.20** | HDBK-0053 | 0.746 → **0.745** | HDBK-0049 | 0.797 |
| A | calibration | Who do I contact to request a copy of my Form 137? | 14.60 → **11.23** | HDBK-0025 ⟲ | 0.648 → **0.625** | RSCH-0039 | 0.734 |
| B | demo | How do I report a broken air conditioner in our classroom? | 9.53 → **7.05** | HDBK-0190 ⟲ | 0.627 → **0.607** | HDBK-0175 | 0.657 |
| B | demo | Where do I return my borrowed laboratory apron? | 6.71 → **11.73** | HDBK-0172 ⟲ | 0.613 → **0.613** | HDBK-0171 | 0.608 |
| B | demo | Where is the nearest ATM on campus? | 10.95 → **4.98** | HDBK-0063 | 0.579 → **0.552** | HDBK-0168 | 0.621 |
| B | spare | Who repairs the broken chairs in our classroom? | 10.58 → **6.33** | RSCH-0069 ⟲ | 0.616 → **0.575** | HDBK-0219 | 0.654 |
| B | spare | Can I park my motorcycle inside the campus? | 9.35 → **10.58** | HDBK-0204 ⟲ | 0.617 → **0.609** | HDBK-0188 | 0.638 |
| C | demo | Where can I eat near campus? | 6.08 → **6.14** | HDBK-0166 | 0.569 → **0.571** | HDBK-0167 | 0.571 |
| C | demo | Write me a poem about my thesis. | 6.98 → **6.86** | RSCH-0019 ⟲ | 0.650 → **0.588** | RSCH-0059 | 0.574 |
| C | calibration | Write me a poem about my thesis | 7.55 → **6.86** | RSCH-0019 ⟲ | 0.648 → **0.603** | RSCH-0059 | 0.569 |
| C | demo | Will it rain tomorrow in Cabuyao? | 4.76 → **3.31** | HDBK-0234 ⟲ | 0.510 → **0.519** | HDBK-0234 | 0.466 |
| C | calibration | What is the capital of Japan? | 10.54 → **6.83** | RSCH-0057 ⟲ | 0.478 → **0.470** | HDBK-0078 | 0.478 |
| C | calibration | Can you help me debug my python code? | 6.54 → **5.97** | RSCH-0064 ⟲ | 0.544 → **0.565** | RSCH-0061 | 0.564 |

The two poem rows differ only by a full stop. Under the old tokenizer that full stop changes the score (`thesis.` and `thesis` were different words); under the new one it does not. ⟲ = the BM25 top passage changed with the new tokenizer. ✓/✗ = the plan's expected source is / is not the top passage on either half. *scope sim* = best cosine against the 25 scope exemplars (question vs question, no instruction).

### 6a. Can Gate 1 still separate A from B and C?

Gate 1 passes a question if `bm25 ≥ t_b OR cos ≥ t_c`. The test: set each cut-off just above the highest B/C score, and see whether every A question still clears one of them. An A question that clears neither cannot be saved by *any* choice of cut-offs.

| Settings | Highest B/C bm25 | Highest B/C cos | A questions no cut-off can save |
|---|---:|---:|---|
| old (plan §9) | 10.95 | 0.650 | none, **separable** |
| **new** (stemmed, instruction) | 11.73 | 0.613 | none, **separable** |

### 6b. Can Gate 2 still separate B from C?

Scope similarity. Lowest B: **0.608**. Highest C: **0.574**. B sits entirely above C, so a cut-off exists. Choosing it is Sprint 4.

### 6c. Which office would Path B name?

Top three departments by cosine between the question (with instruction) and the printed function statements. This checks `office_exemplars.jsonl`, not routing.

| Question | 1st | 2nd | 3rd | Expected (§9) |
|---|---|---|---|---|
| How do I report a broken air conditioner in our classroom? | Laboratory Services and Disaster Risk Reduction Management Department (0.533) | Office of the University Secretary / Board Secretary (0.503) | Admissions Department (0.501) | Property Management and General Services Department |
| Where do I return my borrowed laboratory apron? | Laboratory Services and Disaster Risk Reduction Management Department (0.511) ✓ | Research and Development Department (0.484) | Gender and Development Department (0.467) | Laboratory Services and Disaster Risk Reduction Management Department |
| Where is the nearest ATM on campus? | Gender and Development Department (0.483) | Admissions Department (0.481) | Office of the University Secretary / Board Secretary (0.476) | Finance Department |
| Who repairs the broken chairs in our classroom? | Laboratory Services and Disaster Risk Reduction Management Department (0.501) | Office of the University Secretary / Board Secretary (0.473) | Gender and Development Department (0.467) | Property Management and General Services Department |
| Can I park my motorcycle inside the campus? | Data Protection Department (0.503) | Office of the University Secretary / Board Secretary (0.486) | Admissions Department (0.482) | — |

**Verdict: this mechanism fails.** It is kept here as the evidence for §6d.

### 6d. DRAFT replacement — keyword rule per department (`data/office_keywords.json`)

**Status: DRAFT — not reviewed. Written 2026-09-26 by Claude for the group to check.** 255 keywords across 22 departments. Rule: Tokenize the question and every keyword with shared/tokenizer.py (stemmed). A keyword hits when all its tokens appear in the question consecutively. A department scores the total token length of its hits, so 'air conditioner' outweighs 'fee'. Suggest the top 2-3 departments with a score above 0.

| Question | Set | Suggested offices (score · keywords hit) | Expected |
|---|---|---|---|
| How do I report a broken air conditioner in our classroom? | referral (B) | Property Management and General Services Department (2 · air conditioner) ✓ | Property Management and General Services Department |
| Where do I return my borrowed laboratory apron? | referral (B) | Laboratory Services and Disaster Risk Reduction Management Department (2 · laboratory, apron) ✓ | Laboratory Services and Disaster Risk Reduction Management Department |
| Where is the nearest ATM on campus? | referral (B) | Finance Department (1 · atm) ✓ | Finance Department |
| Who repairs the broken chairs in our classroom? | referral (B) | Property Management and General Services Department (2 · chair, repair) ✓ | Property Management and General Services Department |
| Can I park my motorcycle inside the campus? | referral (B) | Property Management and General Services Department (2 · parking, motorcycle) | — |
| Which office handles school payments and official receipts? | scope exemplar, written before the keywords | Finance Department (4 · payment, receipt, official receipt) ✓ | Finance Department |
| Who is in charge of maintaining campus buildings and facilities? | scope exemplar, written before the keywords | Property Management and General Services Department (2 · building, facility) ✓ | Property Management and General Services Department |
| Who assists students using the science laboratories? | scope exemplar, written before the keywords | Laboratory Services and Disaster Risk Reduction Management Department (1 · laboratory) ✓ | Laboratory Services and Disaster Risk Reduction Management Department |
| Who do I contact if I cannot log in to my student portal account? | scope exemplar, written before the keywords | Management Information Systems Department (6 · student portal, portal, log in, portal account) ✓ | Management Information Systems Department |
| Where can I eat near campus? | out of scope (C) | *no keyword hit (fallback)* | — |
| Write me a poem about my thesis. | out of scope (C) | Research and Development Department (1 · thesis) | — |
| Will it rain tomorrow in Cabuyao? | out of scope (C) | *no keyword hit (fallback)* | — |

Path C never shows an office, so a C row with a hit (the poem hitting *thesis*) changes nothing on screen. It is listed to show the rule is not magic.

**Do not read this table as validation.** The same person wrote the keywords and most of these questions. Before the draft is accepted, the group writes 10 referral questions **without opening the keyword file**, and runs them through the rule.

Open points in the draft: (1) Written by the same person who wrote the test questions, so the test in DATA_REPORT.md §6d is not independent. The group should write 10 fresh referral questions WITHOUT looking at this file and test those. (2) English only. Filipino or Taglish words (sira, bayad, CR as 'comfort room') are not covered except 'cr'. (3) Some words are shared across departments on purpose (e.g. 'lab' for Laboratory Services only; computer laboratories may belong to MIS). Needs the group's local knowledge. (4) 'admission' is under the Registrar because of the group's 2026-09-26 decision, even though p. 27 prints an Admissions Department. (5) Stemming merges words across departments. 'account' (MIS) and 'accounting' (Finance) both stem to 'account', so an early draft suggested Finance for a portal-login question. Fixed by using 'portal account' / 'email account' and dropping 'accounting' (which also names the BS Accountancy program). Check every new keyword for the same trap.

Fallback when nothing hits: **UNDECIDED. What Path B shows when no keyword hits. Options: name no office and point to the general information desk, or default to Student Affairs and Services.**

Keywords that stem to the same tokens as an earlier keyword in the same department, and so are counted once: `enrolment`, `e-book`, `facilities`, `park`, `fees`, `counselling`.

## 7. File inventory

| File | Bytes | sha256 (first 16) |
|---|---:|---|
| `data/MANIFEST.json` | 5,173 | `212e17647e01848c` |
| `data/README.md` | 2,678 | `064cc13e4be3b46c` |
| `data/corpus_demo.jsonl` | 571,137 | `4f60d7fecc51c3fc` |
| `data/embeddings.npy` | 477,824 | `1ea84286f69071f6` |
| `data/office_exemplars.jsonl` | 7,304 | `4e3008a5d28e42e9` |
| `data/office_keywords.json` | 12,166 | `a472503e58b4b7ae` |
| `data/office_lookup.json` | 11,804 | `62b11077672e4afd` |
| `data/offices.json` | 8,005 | `3cfafd9a14eb5eb2` |
| `data/scope_exemplars.jsonl` | 4,871 | `84e42243100ccdc8` |
| `inputs/UC-PnC-Student-Handbook-Manual.pdf` | 13,213,269 | `38881d5fc72be4c0` |
| `inputs/corpus.json` | 671,723 | `8ca8e916d46486fc` |
| `inputs/office_lookup.json` | 11,804 | `62b11077672e4afd` |
| `inputs/scope_exemplars_old.json` | 1,036 | `3506cecedb662e89` |
| `shared/office_match.py` | 1,993 | `5388681b86777854` |
| `shared/tokenizer.py` | 2,898 | `e09896da1d2cd49b` |

## Review checks — sign-off (IMPLEMENTATION_PLAN.md §8, Sprint 1)

| Check | Answered by | |
|---|---|---|
| Spot-check 10 of the 53 excluded passages — is every one genuinely front matter? | §1a | ☐ |
| Do all 22 department names match the handbook **exactly**, including "and" vs "&"? | §3a, §3b | ☐ |
| Is every office function statement copied verbatim, with no paraphrasing? | §3a | ☐ |
| Do the scope exemplars sound like UC-PnC students, not like a US university? | §4 | ☐ |
| Does `embeddings.npy` have exactly 311 rows, and does row 0 match passage 0? | §2, automatic checks 6–14 | ☐ |
| Does the new tokenizer keep the words that matter and drop the ones that don't? | §5b | ☐ |

Open before sign-off: the DRAFT keyword list in §6d (the group's own 10-question test) and its fallback. Parked, not blocking: Student Discipline Office.
