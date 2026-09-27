# Gate 0 · Initial check — report

Generated 2026-09-27 by `tools/test_initial_check.py`. Do not edit by hand.

Gate 0 runs two quick checks before any search: **0a** is the question in English, and **0b** is it one question. Either fails → a friendly notice, no search, 0 model calls. Code: `shared/initial_check.py`.

# Part A · 0a Language

**Rule:** confirm English, don't identify other languages. Alphabet check, then the share of words found in the English word list (63,993 words, SCOWL) must be **≥ 85%**. Acronyms in capitals, university terms and the university's own names are set aside. Typo tolerance is **on**. Code: `shared/language.py`.

> **Read this before quoting any number below.** The main test set was written by Claude, and the university-name and chat-shorthand lists were added *after* seeing misses on this same set, so its score is optimistic. The Bisaya, Ilocano and Hiligaynon questions are drafts, not native-speaker text. The number to report is the **held-out** result (§2), from questions written by people who have not seen the rule.

## 1. Main test set

### At the 85% cut-off (62 questions)

| Group | Expected | Correct |
|---|---|---:|
| English | pass as English | 12 / 12 |
| English+terms | pass as English | 5 / 5 |
| English typos | pass as English | 6 / 6 |
| English short | pass as English | 4 / 4 |
| Tagalog | notice | 8 / 8 |
| Taglish | notice | 8 / 8 |
| Bisaya | notice | 5 / 5 |
| Ilocano | notice | 4 / 4 |
| Hiligaynon | notice | 2 / 2 |
| Foreign | notice | 8 / 8 |
| **All** | | **62 / 62** |

No misses.

### The gap between English and everything else

- English questions: English share **100% – 100%**
- Every other question: **0% – 83%**
- The non-English questions that look *most* English, which are the hard cases: *How do I request my TOR po?* (83%); *Can I borrow books kahit wala akong ID?* (71%); *Ilang hours ang required na internship?* (67%)

### Every cut-off, for the record

| Cut-off | English passed | Non-English stopped |
|---:|---:|---:|
| 60% | 27 / 27 | 31 / 35 |
| 70% | 27 / 27 | 33 / 35 |
| 75% | 27 / 27 | 34 / 35 |
| 80% | 27 / 27 | 34 / 35 |
| 85% ← in use | 27 / 27 | 35 / 35 |
| 90% | 27 / 27 | 35 / 35 |
| 95% | 27 / 27 | 35 / 35 |

Choosing rule, in priority order: (1) never stop a real English question, (2) stop all non-English, (3) stop as much Taglish as possible.

## 2. Held-out test set (the number to report)

**Not done yet.** Ask 3–5 classmates to each write about 10 questions in their own way (English, Taglish, their home language) **without seeing this rule or the word lists**. Save them to `data/language_test_heldout.jsonl`, one per line: `{"group": "Bisaya", "question": "...", "expected": "notice", "written_by": "<name>"}`. Then re-run this tool.

## 3. Cost

- Per question: **0.10 ms** average, 2.39 ms worst (1,240 checks). No model, no network.
- The English word list takes about 8 MB of memory and loads once at start-up.
- A question that gets the notice skips the search and the model, so it is *faster* than before.

## 4. Checks on the lists themselves

- Philippine function words that are also real English words: `pa`, `ti`, `sang`, `may`, `din`, `at`, `to`, `man`. These are genuine English words ("at", "to", "may", "man"), so they stay. The rule looks at the share of all the words, so one shared word can't make a Tagalog question pass.
- `language_terms.json` status: *DRAFT, pending group review (2026-09-27). Each entry is here because it is NOT in the English word list but is fine in an English question at UC-PnC.* 3 phrases, 31 university terms, 20 chat shorthand.
- **Why university terms are never taken automatically from the manuals:** the manuals' most frequent non-English words include **"ng"**, from "Pamantasan ng Cabuyao". Auto-adding them would let Tagalog through. `tools/build_language_lists.py` prints candidates for a human to review.

### Typo tolerance: what it costs and what it buys

- **Buys:** 4 real English question(s) pass only because of it: *how do i enrol in the univrsity*; *wat r the requirments for admision*; *can i borrow books overnite*; *where is the registrar ofice*.
- **Costs:** 12 non-English question(s) had a word accepted as an English typo (it is one letter away from an English word), which raised their score: *Paano manghiram ng libro sa library?* (Paano: 17% → 33%); *Ilang oras ang kailangan sa OJT?* (Ilang: 0% → 20%); *Paano kumuha ng kopya ng transcript of records ko?* (Paano: 33% → 44%); *Sira ang aircon sa classroom namin, saan po ako magrereport?* (aircon, namin: 10% → 30%); *Uulan ba bukas sa Cabuyao?* (bukas: 0% → 25%); *Kailan ang huling araw ng enrollment?* (huling: 17% → 33%); *Ilang hours ang required na internship?* (Ilang: 50% → 67%); *Yung aircon sa room namin sira, sino po dapat i-contact?* (aircon, namin: 27% → 46%); *Can I borrow books kahit wala akong ID?* (akong: 57% → 71%); *Kanus-a ang katapusan sa enrollment?* (Kanus: 33% → 50%); *Comment emprunter un livre à la bibliothèque ?* (livre: 29% → 43%); *Como posso pedir um livro emprestado?* (posso: 17% → 33%).
- **Decisions it got wrong because of this: 0.** None of those questions crossed the cut-off.
- **Trade-off:** typo tolerance keeps misspelled English working but narrows the gap between English and non-English. Keep it on, and watch this section when the held-out set is added.

## 5. Every language question, with its score

<details><summary>Show all</summary>

| Group | Question | English share | Result | Not recognised |
|---|---|---:|---|---|
| English | How do I borrow a book from the university library? | 100% | ✓ english | — |
| English | What are the requirements for student admission? | 100% | ✓ english | — |
| English | How many hours is the required internship? | 100% | ✓ english | — |
| English | Where do I get my certificate of registration? | 100% | ✓ english | — |
| English | Can I request my transcript of records online? | 100% | ✓ english | — |
| English | What is the passing grade in the college? | 100% | ✓ english | — |
| English | How do I apply for a scholarship? | 100% | ✓ english | — |
| English | Who should I talk to about my grades? | 100% | ✓ english | — |
| English | What happens if I miss the final exam? | 100% | ✓ english | — |
| English | Is there a dental clinic on campus? | 100% | ✓ english | — |
| English | How do I join a student organization? | 100% | ✓ english | — |
| English | What is the dress code for students? | 100% | ✓ english | — |
| English+terms | How do I submit requirements in Pinnacle? | 100% | ✓ english | — |
| English+terms | Where do I get my TOR? | 100% | ✓ english | — |
| English+terms | How many hours is the OJT for BSCpE? | 100% | ✓ english | — |
| English+terms | What GWA do I need for the President's List? | 100% | ✓ english | — |
| English+terms | Is Pamantasan ng Cabuyao accredited? | 100% | ✓ english | — |
| English typos | how do i enrol in the univrsity | 100% | ✓ english | — |
| English typos | wat r the requirments for admision | 100% | ✓ english | — |
| English typos | hw 2 borrow book | 100% | ✓ english | — |
| English typos | can i borrow books overnite | 100% | ✓ english | — |
| English typos | where is the registrar ofice | 100% | ✓ english | — |
| English typos | how to get TOR asap | 100% | ✓ english | — |
| English short | TOR? | 100% | ✓ english | — |
| English short | scholarship | 100% | ✓ english | — |
| English short | library hours | 100% | ✓ english | — |
| English short | enrollment | 100% | ✓ english | — |
| Tagalog | Paano manghiram ng libro sa library? | 33% | ✓ notice | manghiram, ng, libro, sa |
| Tagalog | Ilang oras ang kailangan sa OJT? | 20% | ✓ notice | oras, ang, kailangan, sa |
| Tagalog | Paano kumuha ng kopya ng transcript of records ko? | 44% | ✓ notice | kumuha, ng, kopya, ng, ko |
| Tagalog | Ano ang mga requirements para makapasok sa unibersidad? | 12% | ✓ notice | Ano, ang, mga, para, makapasok, sa, unibersidad |
| Tagalog | Sira ang aircon sa classroom namin, saan po ako magrereport? | 30% | ✓ notice | Sira, ang, sa, saan, po, ako, magrereport |
| Tagalog | Uulan ba bukas sa Cabuyao? | 25% | ✓ notice | Uulan, ba, sa |
| Tagalog | Kailan ang huling araw ng enrollment? | 33% | ✓ notice | Kailan, ang, araw, ng |
| Tagalog | Saan makikita ang opisina ng registrar? | 17% | ✓ notice | Saan, makikita, ang, opisina, ng |
| Taglish | Pano mag enroll pag irregular student ako? | 43% | ✓ notice | Pano, mag, pag, ako |
| Taglish | Saan pwede mag borrow ng books sa library? | 38% | ✓ notice | Saan, pwede, mag, ng, sa |
| Taglish | Ilang hours ang required na internship? | 67% | ✓ notice | ang, na |
| Taglish | Pano mag request ng TOR sa registrar? | 33% | ✓ notice | Pano, mag, ng, sa |
| Taglish | Yung aircon sa room namin sira, sino po dapat i-contact? | 46% | ✓ notice | Yung, sa, sira, sino, po, dapat |
| Taglish | How do I request my TOR po? | 83% | ✓ notice | po |
| Taglish | Pwede ba mag-enroll kahit may balance pa ako? | 44% | ✓ notice | Pwede, ba, mag, kahit, ako |
| Taglish | Can I borrow books kahit wala akong ID? | 71% | ✓ notice | kahit, wala |
| Bisaya | Asa ko makahulam ug libro? | 0% | ✓ notice | Asa, ko, makahulam, ug, libro |
| Bisaya | Pila ka oras ang OJT? | 0% | ✓ notice | Pila, ka, oras, ang |
| Bisaya | Unsaon pag-enroll sa unibersidad? | 20% | ✓ notice | Unsaon, pag, sa, unibersidad |
| Bisaya | Kanus-a ang katapusan sa enrollment? | 50% | ✓ notice | ang, katapusan, sa |
| Bisaya | Asa ang opisina sa registrar? | 20% | ✓ notice | Asa, ang, opisina, sa |
| Ilocano | Kasano ti agbulod iti libro? | 20% | ✓ notice | Kasano, agbulod, iti, libro |
| Ilocano | Mano nga oras ti OJT? | 25% | ✓ notice | Mano, nga, oras |
| Ilocano | Ania dagiti kasapulan para iti admission? | 17% | ✓ notice | Ania, dagiti, kasapulan, para, iti |
| Ilocano | Sadino ti opisina ti registrar? | 60% | ✓ notice | Sadino, opisina |
| Hiligaynon | Diin ako makahulam sang libro? | 20% | ✓ notice | Diin, ako, makahulam, libro |
| Hiligaynon | Ano ang kinahanglan para sa admission? | 17% | ✓ notice | Ano, ang, kinahanglan, para, sa |
| Foreign | ¿Cómo pido prestado un libro? | 0% | ✓ notice | Cómo, pido, prestado, un, libro |
| Foreign | Comment emprunter un livre à la bibliothèque ? | 43% | ✓ notice | emprunter, un, à, bibliothèque |
| Foreign | Bagaimana cara meminjam buku di perpustakaan? | 0% | ✓ notice | Bagaimana, cara, meminjam, buku, di, perpustakaan |
| Foreign | Wie kann ich ein Buch ausleihen? | 0% | ✓ notice | Wie, kann, ich, ein, Buch, ausleihen |
| Foreign | Como posso pedir um livro emprestado? | 33% | ✓ notice | Como, pedir, livro, emprestado |
| Foreign | 도서관에서 책을 어떻게 빌려요? | 0% | ✓ notice | — |
| Foreign | 我怎么在图书馆借书？ | 0% | ✓ notice | — |
| Foreign | 図書館で本を借りるにはどうすればいいですか？ | 0% | ✓ notice | — |

</details>

# Part B · 0b One question

**Rule:** split at sentence ends, and at *and / also / then / plus / ,* only when what follows starts like a question (a question word, a request like *tell me*, or a helper verb followed by a subject: *and do I…*). Two or more questions → the student gets each one back as a button that fills the message box, to send one at a time. Code: `shared/questions.py`.

**Why:** the pipeline makes one search and one path per message. Tested live on 2026-09-27, two-question messages lost an answerable half, left a claim uncited, or pasted the decline sentence inside an answer.

> **Optimistic, like Part A:** the set was written by the same person who wrote the rule, and the helper-verb refinement was added while writing it. The number to report is the held-out set.

### Main set (40 messages)

| Group | Expected | Correct |
|---|---|---:|
| One question, contains 'and' | answered normally | 15 / 15 |
| One question, with greeting or statement | answered normally | 6 / 6 |
| Two questions | split into buttons | 14 / 14 |
| Three questions | split into buttons | 2 / 2 |
| No question marks (run-on) | split into buttons | 3 / 3 |
| **All** | | **40 / 40** |

No misses.

Choosing rule: **never split a genuine single question** (a wrong split costs the student a click; a missed double question falls back to today's behavior, where the evidence gate, citation check and decline rule still apply).

### Held-out set (the number to report)

**Not done yet.** Classmates write messages the way they'd really ask, some with one question and some with several, without seeing the rule. Save them to `data/question_split_test_heldout.jsonl`, e.g. `{"group": "Two questions", "question": "...", "expected": "multiple", "written_by": "<name>"}`.

### Cost

- **0.010 ms** per message on average, 0.19 ms worst. No model, no list to load.

### Known limits

- A question hidden inside a statement is not counted: *"I need my TOR and where do I pay?"* reads as one question, so it falls back to normal routing.
- A split can lose its subject: *"What is GWA and how is it computed?"* → *"How is it computed?"*. That's why the buttons fill the message box instead of sending.

<details><summary>Every message, with what was found</summary>

| Group | Message | Result | Questions found |
|---|---|---|---|
| One question, contains 'and' | What are the requirements and deadlines for admission? | ✓ single | What are the requirements and deadlines for admission? |
| One question, contains 'and' | How do I enroll and pay my fees? | ✓ single | How do I enroll and pay my fees? |
| One question, contains 'and' | Where and when is enrollment? | ✓ single | When is enrollment? |
| One question, contains 'and' | What documents do I need for admission and enrollment? | ✓ single | What documents do I need for admission and enrollment? |
| One question, contains 'and' | Can I borrow books and magazines from the library? | ✓ single | Can I borrow books and magazines from the library? |
| One question, contains 'and' | Who approves the leave of absence and the dropping of subjects? | ✓ single | Who approves the leave of absence and the dropping of subjects? |
| One question, contains 'and' | Is there a clinic and a dentist on campus? | ✓ single | Is there a clinic and a dentist on campus? |
| One question, contains 'and' | What happens if I fail and have to repeat a subject? | ✓ single | What happens if I fail and have to repeat a subject? |
| One question, contains 'and' | Can I enroll online and then pay at the cashier? | ✓ single | Can I enroll online and then pay at the cashier? |
| One question, contains 'and' | What is the dress code for men and women? | ✓ single | What is the dress code for men and women? |
| One question, contains 'and' | How do I join a student organization and become an officer? | ✓ single | How do I join a student organization and become an officer? |
| One question, contains 'and' | Where do I submit my thesis and my ethics review form? | ✓ single | Where do I submit my thesis and my ethics review form? |
| One question, contains 'and' | Tell me the library hours and the rules for borrowing. | ✓ single | Tell me the library hours and the rules for borrowing. |
| One question, contains 'and' | How many units can I take and still graduate on time? | ✓ single | How many units can I take and still graduate on time? |
| One question, contains 'and' | Please tell me how to request my TOR and COR. | ✓ single | Tell me how to request my TOR and COR. |
| One question, with greeting or statement | Hi! How do I borrow a book? | ✓ single | How do I borrow a book? |
| One question, with greeting or statement | Thanks! Also, where is the registrar? | ✓ single | Where is the registrar? |
| One question, with greeting or statement | I want to know how to borrow a book. | ✓ single | — |
| One question, with greeting or statement | I lost my ID and I need a new one, what do I do? | ✓ single | What do I do? |
| One question, with greeting or statement | If I fail the final exam, can I retake it? | ✓ single | Can I retake it? |
| One question, with greeting or statement | TOR? | ✓ single | — |
| Two questions | How do I borrow a book from the library and how do I request my TOR? | ✓ multiple | How do I borrow a book from the library? · How do I request my TOR? |
| Two questions | How many hours is the required internship? Also, where is the nearest ATM on campus? | ✓ multiple | How many hours is the required internship? · Where is the nearest ATM on campus? |
| Two questions | Write me a poem about my thesis, then tell me how to borrow a library book. | ✓ multiple | Write me a poem about my thesis. · Tell me how to borrow a library book. |
| Two questions | What is GWA and how is it computed? | ✓ multiple | What is GWA? · How is it computed? |
| Two questions | Where is the nearest ATM on campus and who repairs the broken chairs in our classroom? | ✓ multiple | Where is the nearest ATM on campus? · Who repairs the broken chairs in our classroom? |
| Two questions | How do I apply for a scholarship and what are the requirements? | ✓ multiple | How do I apply for a scholarship? · What are the requirements? |
| Two questions | When is the enrollment? Where do I pay? | ✓ multiple | When is the enrollment? · Where do I pay? |
| Two questions | Can I borrow books overnight and how many can I borrow? | ✓ multiple | Can I borrow books overnight? · How many can I borrow? |
| Two questions | How do I drop a subject; who signs the form? | ✓ multiple | How do I drop a subject? · Who signs the form? |
| Two questions | Where is the clinic and when is it open? | ✓ multiple | Where is the clinic? · When is it open? |
| Two questions | What is the passing grade and is there a retake exam? | ✓ multiple | What is the passing grade? · Is there a retake exam? |
| Two questions | Explain the grading system and tell me how honors are computed. | ✓ multiple | Explain the grading system. · Tell me how honors are computed. |
| Two questions | How do I request a TOR and do I need to pay for it? | ✓ multiple | How do I request a TOR? · Do I need to pay for it? |
| Two questions | What's the dress code? Can I wear shorts? | ✓ multiple | What's the dress code. · Can I wear shorts? |
| Three questions | How do I enroll, how much is the fee, and where do I pay? | ✓ multiple | How do I enroll? · How much is the fee? · Where do I pay? |
| Three questions | When is enrollment? How much is tuition? Where is the cashier? | ✓ multiple | When is enrollment? · How much is tuition? · Where is the cashier? |
| No question marks (run-on) | how do i borrow a book and how do i return it | ✓ multiple | How do i borrow a book? · How do i return it? |
| No question marks (run-on) | where is the library and what time does it open | ✓ multiple | Where is the library? · What time does it open? |
| No question marks (run-on) | how do i borrow a book from the library | ✓ single | How do i borrow a book from the library? |

</details>
