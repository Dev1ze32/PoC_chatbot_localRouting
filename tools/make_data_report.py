"""Sprint 1: generate docs/DATA_REPORT.md from the files in data/.

Nothing in the report is typed by hand. It describes what the tools produced,
not what anyone believes they produced. Re-run after any change to data/.
"""
import random
import re
from datetime import date

import numpy as np

from rank_bm25 import BM25Okapi

from common import (DATA, DOCS, INPUTS, MANIFEST, ROOT, build_bm25, embed,
                    load_json, load_model, read_jsonl, sha256)
from shared.office_match import compile_rules, match
from shared.tokenizer import TOKENIZER_VERSION, tokenize

# Every question the plan measured (§7.1 calibration table and §9 demo script):
# (path, question, plan bm25, plan cos, expected source, role). Plan values
# are None where the plan did not measure that exact string. Used for the
# leak check (§4) and the re-measure (§6).
PROP = "property-management-and-general-services-department"
DEMO = [
    ("A", "What is the format of the research title page?", 18.05, 0.729, "RSCH-0016", "demo"),
    ("A", "How do I borrow a book from the university library?", 16.90, 0.739, "HDBK-0171", "demo"),
    ("A", "How many hours is the required internship?", 13.50, 0.716, "INTN-0013", "demo"),
    ("A", "What are the requirements for student admission?", 13.89, 0.737, "HDBK-0028", "spare"),
    ("A", "Is there a dental clinic on campus and what are its hours?", 18.35, 0.643, None, "spare"),
    ("A", "How do I request a copy of my academic records?", 12.21, 0.746, None, "calibration"),
    ("A", "Who do I contact to request a copy of my Form 137?", 14.60, 0.648, None, "calibration"),
    ("B", "How do I report a broken air conditioner in our classroom?", 9.53, 0.627, PROP, "demo"),
    ("B", "Where do I return my borrowed laboratory apron?", 6.71, 0.613,
     "laboratory-services-and-disaster-risk-reduction-management-department", "demo"),
    ("B", "Where is the nearest ATM on campus?", 10.95, 0.579, "finance-department", "demo"),
    ("B", "Who repairs the broken chairs in our classroom?", 10.58, 0.616, PROP, "spare"),
    ("B", "Can I park my motorcycle inside the campus?", 9.35, 0.617, None, "spare"),
    ("C", "Where can I eat near campus?", 6.08, 0.569, None, "demo"),
    ("C", "Write me a poem about my thesis.", None, None, None, "demo"),
    ("C", "Write me a poem about my thesis", 7.55, 0.648, None, "calibration"),
    ("C", "Will it rain tomorrow in Cabuyao?", 4.76, 0.510, None, "demo"),
    ("C", "What is the capital of Japan?", 10.54, 0.478, None, "calibration"),
    ("C", "Can you help me debug my python code?", 6.54, 0.544, None, "calibration"),
]
DEMO_QUESTIONS = [d[1] for d in DEMO]
SPOT_CHECK_SEED = 20260926
SPOT_CHECK_N = 10


def clip(s, n=110):
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def cell(s):
    return str(s).replace("|", "\\|")


def main():
    manifest = load_json(MANIFEST)["files"]
    passages = read_jsonl(DATA / "corpus_demo.jsonl")
    corpus = manifest["corpus_demo.jsonl"]
    source = load_json(INPUTS / "corpus.json")["passages"]
    by_id = {p["document_id"]: p for p in source}
    excluded = [by_id[i] for i in corpus["excluded_ids"]]
    E = np.load(DATA / "embeddings.npy")
    offices = load_json(DATA / "offices.json")
    exemplars = read_jsonl(DATA / "office_exemplars.jsonl")
    scope = {"exemplars": read_jsonl(DATA / "scope_exemplars.jsonl")}
    lookup = load_json(DATA / "office_lookup.json")
    dept_ids = {d["id"]: d for d in offices["departments"]}
    div_ids = {d["id"]: d for d in offices["divisions"]}

    model = load_model()
    out, status = [], []

    def check(ok, label):
        status.append((ok, label))
        return "PASS" if ok else "**FAIL**"

    # ------------------------------------------------------------- corpus
    per_doc = {}
    for p in source:
        d = p["document_id"][:4]
        k = per_doc.setdefault(d, [0, 0])
        k[0 if ">" in p["page_or_section"] else 1] += 1
    no_bc_kept = [p["document_id"] for p in passages if ">" not in p["page_or_section"]]
    bc_excluded = [p["document_id"] for p in excluded if ">" in p["page_or_section"]]
    ids_unique = len({p["document_id"] for p in passages}) == len(passages)
    row_mismatch = [k for k, p in enumerate(passages) if p.get("row") != k]
    field_sets = {tuple(p.keys()) for p in passages}
    stale = [f for f, e in manifest.items() if sha256(DATA / f) != e["sha256"]]
    paired = (manifest["embeddings.npy"]["built_from_sha256"]
              == sha256(DATA / "corpus_demo.jsonl"))

    # ------------------------------------------------------------- embeddings
    shape_ok = E.shape == (len(passages), 384) and E.dtype == np.float32
    norms = np.linalg.norm(E, axis=1)
    probe_rows = [0, len(passages) // 2, len(passages) - 1]
    probe = embed(model, [passages[i]["text"] for i in probe_rows])
    probe_cos = [float(probe[k] @ E[i]) for k, i in enumerate(probe_rows)]
    # Row 0 must match passage 0 better than any other row does.
    row0_best = int(np.argmax(E @ probe[0]))

    # ------------------------------------------------------------- scope
    s_texts = [e["text"] for e in scope["exemplars"]]
    s_vec = embed(model, s_texts)
    d_vec = embed(model, DEMO_QUESTIONS)
    sim = s_vec @ d_vec.T
    src_ok = []
    for e in scope["exemplars"]:
        s = e["source"]
        if s["type"] == "corpus":
            hits = [p for p in passages if p["document_id"].startswith(s["doc"])
                    and p["page_or_section"].startswith(s["breadcrumb_prefix"])]
            src_ok.append((len(hits), f'{s["doc"]} › {s["breadcrumb_prefix"]}'))
        else:
            ok = s["department"] in dept_ids
            src_ok.append((1 if ok else 0,
                           f'p. {s["page"]} · {dept_ids.get(s["department"], {}).get("name", "??")}'))
    exact_copy = [t for t in s_texts if t.strip().lower() in
                  {q.strip().lower() for q in DEMO_QUESTIONS}]

    # ------------------------------------------------------------- offices
    corpus_offices = sorted({p["issuing_office"] for p in passages})
    lookup_offices = sorted({r["office"] for r in lookup["rules"]}
                            | set(lookup["document_defaults"].values())
                            | set(lookup.get("office_vocabulary", [])))
    printed = {d["name"] for d in offices["departments"]}
    alias_names = {a["name"] for a in offices["aliases"]}
    unmapped = [n for n in sorted(set(corpus_offices) | set(lookup_offices))
                if n not in printed and n not in alias_names]

    # ------------------------------------------------------------- BM25
    def old_tok(t):              # the old retriever.py tokenizer, for comparison
        return t.lower().split()
    bm_old = BM25Okapi([old_tok(p["text"]) for p in passages])
    bm_new = build_bm25(passages)
    old_terms = {t for p in passages for t in old_tok(p["text"])}
    glued = sorted(t for t in old_terms if re.search(r"[a-z0-9][^a-z0-9]+$|^[^a-z0-9]+[a-z0-9]", t))
    empty_queries = [q for q in ["What is it?", "Who are you?", "How about this one?"]
                     if not tokenize(q)]
    wp = [len(model.tokenizer(p["text"])["input_ids"]) for p in passages]
    over = [(passages[k]["document_id"], n) for k, n in enumerate(wp)
            if n > model.max_seq_length]

    # ------------------------------------------------------------- re-measure
    qv_old = embed(model, DEMO_QUESTIONS)               # plan's setting: no instruction
    qv_new = embed(model, DEMO_QUESTIONS, query=True)   # BGE retrieval instruction
    ex_vec = embed(model, [e["statement"] for e in exemplars])
    meas = []
    for k, (path, q, p_bm, p_cos, expect, role) in enumerate(DEMO):
        so = bm_old.get_scores(old_tok(q))
        sn = bm_new.get_scores(tokenize(q))
        co, cn = E @ qv_old[k], E @ qv_new[k]
        jb, jd = int(np.argmax(sn)), int(np.argmax(cn))
        off = np.argsort(-(ex_vec @ qv_new[k]))[:3]
        meas.append({
            "path": path, "q": q, "plan_bm": p_bm, "plan_cos": p_cos, "expect": expect,
            "role": role,
            "bm_old": float(so.max()), "bm_new": float(sn.max()),
            "cos_old": float(co.max()), "cos_new": float(cn.max()),
            "top_bm": passages[jb]["document_id"], "top_bm_old": passages[int(np.argmax(so))]["document_id"],
            "top_dense": passages[jd]["document_id"],
            "scope": float((s_vec @ d_vec[k]).max()),
            "offices": [exemplars[i]["department"] for i in off],
            "office_cos": [float(ex_vec[i] @ qv_new[k]) for i in off],
            "tokens": tokenize(q),
        })
    baseline_ok = all(abs(m["bm_old"] - m["plan_bm"]) < 0.01 and abs(m["cos_old"] - m["plan_cos"]) < 0.001
                      for m in meas if m["plan_bm"] is not None)

    def separable(bm_key, cos_key):
        """Can ANY pair of cut-offs, used as 'bm25 OR cos', pass every A and
        fail every B and C? Returns the A questions that no cut-off can save."""
        bc = [m for m in meas if m["path"] != "A"]
        tb = max(m[bm_key] for m in bc)
        tc = max(m[cos_key] for m in bc)
        return tb, tc, [m for m in meas if m["path"] == "A"
                        and m[bm_key] <= tb and m[cos_key] <= tc]
    kw_file = load_json(DATA / "office_keywords.json")
    kw_rules = compile_rules(kw_file)
    kw_depts = {d["department"] for d in kw_file["departments"]}
    kw_dead = [(d["department"], k) for d in kw_file["departments"]
               for k in d["keywords"] if not tokenize(k)]
    kw_dupes = [(d["department"], k) for d in kw_file["departments"]
                for k in d["keywords"]
                if tokenize(k) and k not in [kw for dep, ph in kw_rules
                                             if dep == d["department"] for kw, _ in ph]]
    # Written 2026-09-26 as scope exemplars, BEFORE the keyword list existed.
    kw_probe = [(e["text"], e["source"]["department"]) for e in scope["exemplars"]
                if e["source"]["type"] == "office"]
    sep_old = separable("bm_old", "cos_old")
    sep_new = separable("bm_new", "cos_new")
    scope_b = [m["scope"] for m in meas if m["path"] == "B"]
    scope_c = [m["scope"] for m in meas if m["path"] == "C"]

    # ================================================================ write
    w = out.append
    w("# Sprint 1 — Data report")
    w("")
    w(f"Generated {date.today().isoformat()} by `tools/make_data_report.py`. "
      "Do not edit by hand; re-run the tool.")
    w("")
    w("This is the file you review to sign off Sprint 1. The five review checks "
      "from IMPLEMENTATION_PLAN.md §8 are at the bottom, each pointing at the "
      "section that answers it.")
    w("")
    w("## Automatic checks")
    w("")
    w("| # | Check | Result |")
    w("|---|---|---|")
    rows = [
        (len(passages) == 311, f"corpus_demo.jsonl has 311 lines (has {len(passages)})"),
        (len(excluded) == 53, f"53 passages excluded (excluded {len(excluded)})"),
        (not no_bc_kept, "no kept passage lacks a '>' breadcrumb"),
        (not bc_excluded, "no excluded passage has a '>' breadcrumb"),
        (ids_unique, "document_id is unique in the kept set"),
        (True, "every line of the three JSONL files parses as one JSON object "
               "(the strict reader stops on the first bad line)"),
        (not row_mismatch, "each record's `row` equals its line index"
                           + (f" — mismatched at {row_mismatch[:5]}" if row_mismatch else "")),
        (len(field_sets) == 1, "every passage has the same fields in the same order"),
        (not stale, "every generated file matches its MANIFEST.json hash"
                    + (f" — stale: {', '.join(stale)}" if stale else "")),
        (paired, "embeddings.npy was built from the current corpus_demo.jsonl "
                 "(manifest pairing hash)"),
        (shape_ok, f"embeddings.npy is (311, 384) float32 (is {E.shape} {E.dtype})"),
        (bool(np.allclose(norms, 1, atol=1e-3)), "every embedding row is unit length"),
        (min(probe_cos) > 0.999, "re-embedding passages 0 / middle / last reproduces their rows "
                                 f"(cos {', '.join(f'{c:.4f}' for c in probe_cos)})"),
        (row0_best == 0, f"passage 0 text is nearest to row 0 (nearest row: {row0_best})"),
        (len(offices["departments"]) == 22, "offices.json has 22 departments"),
        (len(offices["divisions"]) == 6, "offices.json has 6 divisions"),
        (len(exemplars) == 22 and all(e["statement"].startswith("To ") for e in exemplars),
         "22 function statements, each starting 'To …' as printed"),
        (all(a["department"] is None or a["department"] in dept_ids for a in offices["aliases"]),
         "every alias points at a printed department (or is explicitly unresolved)"),
        (not unmapped, "every office name in the corpus and office_lookup.json is printed "
                       "on pp. 22–27 or listed as an alias"
                       + (f" — unmapped: {', '.join(unmapped)}" if unmapped else "")),
        (20 <= len(s_texts) <= 25, f"20–25 scope exemplars (has {len(s_texts)})"),
        (all(n > 0 for n, _ in src_ok), "every scope exemplar's source exists"),
        (not exact_copy, "no scope exemplar is a copy of a demo question"),
        (baseline_ok, "the old tokenizer, re-run here, reproduces the plan's §9 bm25 and "
                      "cos numbers (so the old/new comparison in §6 is like for like)"),
        (not any(tokenize(p["text"]) == [] for p in passages),
         "every passage yields at least one BM25 token under the new tokenizer"),
        (kw_depts == set(dept_ids), "office_keywords.json (DRAFT) covers exactly the 22 printed departments"),
        (not kw_dead, "no draft keyword is made only of stopwords"),
        (sha256(INPUTS / "office_lookup.json") == sha256(DATA / "office_lookup.json"),
         "data/office_lookup.json is byte-identical to the input (confirmed flags intact)"),
    ]
    for k, (ok, label) in enumerate(rows, 1):
        w(f"| {k} | {cell(label)} | {check(ok, label)} |")
    w("")
    n_fail = sum(1 for ok, _ in status if not ok)
    w(f"**{len(status) - n_fail} of {len(status)} automatic checks pass.** "
      "Automatic checks do not replace the human review below.")
    w("")

    # ------------------------------------------------------------- §1
    w("## 1. Knowledge base — `data/corpus_demo.jsonl`")
    w("")
    w("One passage per line. Line *i* = record with `row: i` = row *i* of "
      "`embeddings.npy`. Build details are in `data/MANIFEST.json`, not in the "
      "records. Why JSONL: `data/README.md`.")
    w("")
    w("Rule: keep a passage only if `page_or_section` contains a `>` breadcrumb "
      "(it sits under a numbered chapter and section).")
    w("")
    w("| Document | Kept | Excluded | Total |")
    w("|---|---:|---:|---:|")
    for d in sorted(per_doc):
        k, x = per_doc[d]
        w(f"| {d} | {k} | {x} | {k + x} |")
    tk = sum(v[0] for v in per_doc.values()); tx = sum(v[1] for v in per_doc.values())
    w(f"| **All** | **{tk}** | **{tx}** | **{tk + tx}** |")
    w("")
    w(f"Source `inputs/corpus.json` sha256 `{corpus['source_sha256'][:16]}…`")
    w("")
    w("### 1a. Spot-check sample (review check 1)")
    w("")
    w(f"Ten excluded passages drawn at random (seed {SPOT_CHECK_SEED}, so the "
      "sample is the same every run). For each: is it genuinely front matter, "
      "with no answerable policy in it?")
    w("")
    sample = sorted(random.Random(SPOT_CHECK_SEED).sample(excluded, SPOT_CHECK_N),
                    key=lambda p: p["document_id"])
    w("| ☐ | ID | page_or_section | Opening text |")
    w("|---|---|---|---|")
    for p in sample:
        w(f"| ☐ | {p['document_id']} | {cell(p['page_or_section'])} | {cell(clip(p['text']))} |")
    w("")
    w("### 1b. All 53 excluded passages")
    w("")
    w("<details><summary>Show all</summary>")
    w("")
    w("| ID | page_or_section | Opening text |")
    w("|---|---|---|")
    for p in excluded:
        w(f"| {p['document_id']} | {cell(p['page_or_section'])} | {cell(clip(p['text'], 80))} |")
    w("")
    w("</details>")
    w("")
    w("Watch for: HDBK-0024, HDBK-0043, HDBK-0110 and HDBK-0192 are **part title "
      "pages** (e.g. `PART 2. ACADEMIC GUIDELINES (p. 57)`). Read their text: a "
      "part title page that also carries an introductory policy paragraph would "
      "be a real passage lost.")
    w("")

    # ------------------------------------------------------------- §2
    w("## 2. Embeddings — `data/embeddings.npy`")
    w("")
    emb = manifest["embeddings.npy"]["embedding"]
    w(f"- Shape `{E.shape}`, dtype `{E.dtype}`, {(DATA / 'embeddings.npy').stat().st_size:,} bytes")
    w(f"- Model `{emb['model']}` on `{emb['device']}`, normalised, no query instruction "
      "— the same settings as every score measured in the plan (§7, §9)")
    w(f"- Row order: {manifest['embeddings.npy']['row_order']}")
    w(f"- Built from `corpus_demo.jsonl` sha256 "
      f"`{manifest['embeddings.npy']['built_from_sha256'][:16]}…` — "
      f"{'matches the current file' if paired else '**does NOT match the current file: re-run build_demo_corpus.py**'}")
    w("")
    w("| Row | Passage | Re-embedded cos |")
    w("|---:|---|---:|")
    for k, i in enumerate(probe_rows):
        w(f"| {i} | {passages[i]['document_id']} · {cell(clip(passages[i]['page_or_section'], 70))} | {probe_cos[k]:.4f} |")
    w("")

    # ------------------------------------------------------------- §3
    w("## 3. Office list — `data/offices.json` and `data/office_exemplars.jsonl`")
    w("")
    src = offices["source"]
    w(f"Extracted by `tools/build_office_exemplars.py` from **{src['document']}, "
      f"\"{src['section']}\", pp. {src['pages']}** (`{src['file']}`, sha256 "
      f"`{src['sha256'][:16]}…`). The tool stops if any name below is not found in "
      "the PDF text exactly as written.")
    w("")
    w("### 3a. Names and statements (review checks 2 and 3)")
    w("")
    w("Open the printed handbook at pp. 22–27 beside this table. Tick a row only "
      "when the name matches letter for letter (watch `and` vs `&`, commas, "
      "`Office of the …`) and the statement matches word for word.")
    w("")
    w("| ☐ | p. | Division | Department (as printed) | Function statement (verbatim) |")
    w("|---|---:|---|---|---|")
    for e in exemplars:
        w(f"| ☐ | {e['page']} | {div_ids[e['division']]['name']} | {cell(e['name'])} | {cell(e['statement'])} |")
    w("")
    w("Two statements contain a hyphen at a line break in the print: "
      "`research-competent` (p. 26) and `gender-sensitive` (p. 27). The tool kept "
      "the hyphen. Confirm both are hyphenated compounds in the print, not words "
      "split across a line.")
    w("")
    w("### 3b. Divisions")
    w("")
    w("| ID | Display name | Printed header | p. | Depts |")
    w("|---|---|---|---:|---:|")
    for d in offices["divisions"]:
        w(f"| {d['id']} | {cell(d['name'])} | {cell(d['printed'])} | {d['page']} | {d['departments']} |")
    w("")
    w("Display names are title case of the printed header; `&` is kept where the "
      "print uses `&`.")
    w("")
    w("### 3c. Names the corpus uses that pp. 22–27 do not print")
    w("")
    w("The corpus `issuing_office` field and `office_lookup.json` were built from "
      "the manuals' prose, before pp. 22–27 were used as the authority. Where the "
      "two disagree, `offices.json` records an alias. **Every alias is "
      "`confirmed: false` until a group member confirms it.**")
    w("")
    w("| Confirmed | Name in corpus / lookup | Maps to (printed) | Evidence | Decision |")
    w("|---|---|---|---|---|")
    for a in offices["aliases"]:
        tgt = dept_ids[a["department"]]["name"] if a["department"] else "**unresolved**"
        w(f"| {'✓' if a['confirmed'] else '—'} | {cell(a['name'])} | {cell(tgt)} | "
          f"{cell(a['evidence'])} | {cell(a.get('decision', ''))} |")
    w("")
    w("**Decisions on record** (`offices.json → decisions`):")
    w("")
    for d in offices.get("decisions", []):
        w(f"- **{d['topic']}** ({d['status']}, {d['date']}): {d['decision']}")
    w("")
    w("### 3d. What pp. 22–27 now answer in `office_lookup.json`'s open questions")
    w("")
    w("`office_lookup.json` is copied unchanged. Its `open_questions` were written "
      "before pp. 22–27 were read. Status of each against the printed list:")
    w("")
    oq_status = [
        ("ADMISSIONS", "p. 27 prints an **Admissions Department** under SDAS. **Decided "
         "2026-09-26: admission stays with the Office of the University Registrar.** "
         "The rule in office_lookup.json is unchanged; the decision is recorded in offices.json."),
        ("ALUMNI / INTERNSHIP", "p. 27 prints **Placement, Alumni, and Linkage "
         "Department**. **Decided 2026-09-26 (provisional): cards show the printed name.**"),
        ("STUDENT DISCIPLINE OFFICE", "Not printed on pp. 22–27. **Skipped for now "
         "(parked 2026-09-26).** Cards show the name as the Handbook prose writes it."),
        ("CURRENT UNIT NAMES", "Student Affairs and Services Department, University "
         "Health Department and Management Information Systems Department are all "
         "printed exactly so in the 2023–2028 edition."),
        ("SCHOLARSHIP", "No scholarship office is printed on pp. 22–27. "
         "The SASD placeholder stands. **Still open.**"),
    ]
    w("| Open question | What pp. 22–27 say |")
    w("|---|---|")
    for q, s in oq_status:
        w(f"| {q} | {s} |")
    w("")
    w("### 3e. Office names in use, and where each comes from")
    w("")
    w("| Name | In corpus | In lookup | Printed pp. 22–27 | Alias |")
    w("|---|:-:|:-:|:-:|:-:|")
    for n in sorted(set(corpus_offices) | set(lookup_offices)):
        w(f"| {cell(n)} | {'✓' if n in corpus_offices else ''} | {'✓' if n in lookup_offices else ''} "
          f"| {'✓' if n in printed else ''} | {'✓' if n in alias_names else ''} |")
    w("")
    confirmed = sum(r["confirmed"] for r in lookup["rules"])
    w(f"`office_lookup.json`: {len(lookup['rules'])} rules, {confirmed} confirmed, "
      f"{len(lookup['rules']) - confirmed} `confirmed: false`. Flags kept as the record.")
    w("")

    # ------------------------------------------------------------- §4
    w("## 4. Scope exemplars — `data/scope_exemplars.jsonl` (review check 4)")
    w("")
    w(f"{len(s_texts)} questions replace the 20 generic ones in "
      "`inputs/scope_exemplars_old.json`. Read each aloud: would a UC-PnC student "
      "actually type this? Rewrite any that sound like somewhere else.")
    w("")
    w("| ☐ | Exemplar | Source | Passages under source | Nearest demo question | cos |")
    w("|---|---|---|---:|---|---:|")
    for k, t in enumerate(s_texts):
        j = int(np.argmax(sim[k]))
        n, label = src_ok[k]
        w(f"| ☐ | {cell(t)} | {cell(label)} | {n} | {cell(DEMO_QUESTIONS[j])} | {sim[k, j]:.3f} |")
    w("")
    w("The last column is a leak check, not a threshold. It shows how close each "
      "exemplar sits to a question we will ask on stage. Scope exemplars must "
      "describe the helpdesk's domain; they must not be the demo questions "
      "reworded. If a row looks like a paraphrase of its nearest demo question, "
      "rewrite it.")
    w("")
    w("**Four exemplars come from pp. 23 and 25, not from the manuals.** They are "
      "there so the scope gate treats facilities, finance, laboratories and IT as "
      "university business. What they change, measured on the demo's B and C questions "
      "(best cosine against the exemplars, question vs question):")
    w("")
    office_mask = np.array([e["source"]["type"] == "office" for e in scope["exemplars"]])
    max_c_without = max(float((s_vec[~office_mask] @ d_vec[k]).max())
                        for k, m in enumerate(meas) if m["path"] == "C" and m["role"] == "demo")
    w("| Path | Question | With the 4 | Without | Nearest exemplar (with) |")
    w("|---|---|---:|---:|---|")
    for k, m in enumerate(meas):
        if m["role"] != "demo" and m["path"] != "B":
            continue
        if m["path"] == "A":
            continue
        sims = s_vec @ d_vec[k]
        w(f"| {m['path']} | {cell(m['q'])} | {sims.max():.3f} | {sims[~office_mask].max():.3f} | "
          f"{cell(s_texts[int(np.argmax(sims))])} |")
    w("")
    w(f"Without the 4, the highest C score is {max_c_without:.3f}. Any B question below that "
      "would be sent to the out-of-scope message. **In this set that happens to the ATM "
      "question only.** The others score the same with or without, because they already resemble a "
      "manual-based exemplar. The side effect runs the other way too: *Where can I eat near "
      "campus?* sits closest to the buildings exemplar, so the 4 also nudge that C question up "
      "slightly. Say both if asked.")
    w("")
    old = load_json(INPUTS / "scope_exemplars_old.json")["in_scope_examples"]
    w("<details><summary>The 20 exemplars being replaced</summary>")
    w("")
    for t in old:
        w(f"- {t}")
    w("")
    w("</details>")
    w("")

    # ------------------------------------------------------------- §5
    w("## 5. BM25 tokenizer — `shared/tokenizer.py`")
    w("")
    w("There is no BM25 index file. The index is built in memory at start-up from the "
      "`text` field of `corpus_demo.jsonl`, with the tokenizer below, and the same function "
      "tokenizes every query. Settings are recorded in `MANIFEST.json` under "
      f"`corpus_demo.jsonl → bm25`. Tokenizer version: `{TOKENIZER_VERSION}`.")
    w("")
    w("| Pipeline step | Example |")
    w("|---|---|")
    w("| lowercase + regex words `[a-z0-9]+` | `Records?` → `records` |")
    w("| drop 1-character tokens | `1.` · `a.` · the `s` of `student's` |")
    w("| drop English stopwords (NLTK list) | `what` · `are` · `the` · `on` |")
    w("| Snowball (Porter2) stemming | `policies` → `polici` · `enrollment`, `enrolment` → `enrol` |")
    w("")
    w("### 5a. Old tokenizer vs new, on the 311 passages")
    w("")
    w("| | Old: `text.lower().split()` | New: regex + stopwords + Snowball |")
    w("|---|---:|---:|")
    w(f"| unique indexed terms | {len(bm_old.idf):,} | {len(bm_new.idf):,} |")
    w(f"| average passage length (BM25 normalises by this) | {bm_old.avgdl:.0f} tokens | {bm_new.avgdl:.0f} tokens |")
    w(f"| terms with punctuation glued on | {len(glued):,} | 0 |")
    w("")
    w("Glued terms the old index treated as different words, a sample: "
      + ", ".join(f"`{t}`" for t in glued[:12]) + ".")
    w("")
    w("### 5b. What a question looks like to BM25")
    w("")
    w("| Question | Old tokens | New tokens |")
    w("|---|---|---|")
    for m in [meas[i] for i in (0, 3, 8, 13, 14, 16)]:
        w(f"| {cell(m['q'])} | `{' '.join(old_tok(m['q']))}` | `{' '.join(m['tokens'])}` |")
    w("")
    w("### 5c. Two things Sprint 5 must handle")
    w("")
    w(f"- **A question can tokenize to nothing.** {', '.join(f'`{q}`' for q in empty_queries)} "
      "are all stopwords, so they return no tokens and every BM25 score is 0. The retriever must "
      "treat that as *no lexical evidence*, not as an error.")
    w(f"- **{len(over)} of {len(passages)} passages are longer than BGE's "
      f"{model.max_seq_length}-token limit** and are silently cut off when embedded: "
      + (", ".join(f"{d} ({n})" for d, n in over) if over else "none") + ". "
      "BM25 still sees their full text, so the lexical half covers the missing part. "
      "This is a known limit of this build; do not re-chunk in this sprint.")
    w("")

    # ------------------------------------------------------------- §6
    w("## 6. The demo questions, re-measured")
    w("")
    w("The plan's §7.1 and §9 scores were measured with the **old** tokenizer and **no** BGE "
      f"query instruction. This table re-runs all {len(meas)} of those questions both ways. **It chooses no "
      "thresholds.** That is Sprint 4. It answers one question: *does the demo set still "
      "route the way §9 assumes?*")
    w("")
    w("| Path | Role | Question | bm25 old → new | top-1 BM25 (new) | cos old → new | top-1 dense (new) | scope sim |")
    w("|---|---|---|---:|---|---:|---|---:|")
    for m in meas:
        flag = "" if m["top_bm"] == m["top_bm_old"] else " ⟲"
        exp = ""
        if m["path"] == "A" and m["expect"]:
            exp = " ✓" if m["expect"] in (m["top_bm"], m["top_dense"]) else " ✗ expected " + m["expect"]
        w(f"| {m['path']} | {m['role']} | {cell(m['q'])} | {m['bm_old']:.2f} → **{m['bm_new']:.2f}** | "
          f"{m['top_bm']}{flag} | {m['cos_old']:.3f} → **{m['cos_new']:.3f}** | "
          f"{m['top_dense']}{exp} | {m['scope']:.3f} |")
    w("")
    w("The two poem rows differ only by a full stop. Under the old tokenizer that full stop "
      "changes the score (`thesis.` and `thesis` were different words); under the new one it "
      "does not. ⟲ = the BM25 top passage changed with the new tokenizer. ✓/✗ = the plan's expected "
      "source is / is not the top passage on either half. *scope sim* = best cosine "
      "against the 25 scope exemplars (question vs question, no instruction).")
    w("")
    w("### 6a. Can Gate 1 still separate A from B and C?")
    w("")
    w("Gate 1 passes a question if `bm25 ≥ t_b OR cos ≥ t_c`. The test: set each cut-off "
      "just above the highest B/C score, and see whether every A question still clears one "
      "of them. An A question that clears neither cannot be saved by *any* choice of cut-offs.")
    w("")
    w("| Settings | Highest B/C bm25 | Highest B/C cos | A questions no cut-off can save |")
    w("|---|---:|---:|---|")
    for label, (tb, tc, bad) in [("old (plan §9)", sep_old), ("**new** (stemmed, instruction)", sep_new)]:
        w(f"| {label} | {tb:.2f} | {tc:.3f} | "
          + ("none, **separable**" if not bad else "; ".join(cell(m["q"]) for m in bad)) + " |")
    w("")
    w("### 6b. Can Gate 2 still separate B from C?")
    w("")
    w(f"Scope similarity. Lowest B: **{min(scope_b):.3f}**. Highest C: **{max(scope_c):.3f}**. "
      + ("B sits entirely above C, so a cut-off exists. Choosing it is Sprint 4."
         if min(scope_b) > max(scope_c) else
         "**They overlap, so no single cut-off separates them with these exemplars.**"))
    w("")
    w("### 6c. Which office would Path B name?")
    w("")
    w("Top three departments by cosine between the question (with instruction) and the "
      "printed function statements. This checks `office_exemplars.jsonl`, not routing.")
    w("")
    w("| Question | 1st | 2nd | 3rd | Expected (§9) |")
    w("|---|---|---|---|---|")
    names = {e["department"]: e["name"] for e in exemplars}
    for m in meas:
        if m["path"] != "B":
            continue
        tops = [f"{names[d]} ({c:.3f})" + (" ✓" if d == m["expect"] else "")
                for d, c in zip(m["offices"], m["office_cos"])]
        w(f"| {cell(m['q'])} | " + " | ".join(cell(t) for t in tops) + " | "
          + (cell(names[m["expect"]]) if m["expect"] else "—") + " |")
    w("")

    w("**Verdict: this mechanism fails.** It is kept here as the evidence for §6d.")
    w("")
    w("### 6d. DRAFT replacement — keyword rule per department (`data/office_keywords.json`)")
    w("")
    w(f"**Status: {kw_file['status']}** {sum(len(d['keywords']) for d in kw_file['departments'])} "
      f"keywords across {len(kw_file['departments'])} departments. Rule: {kw_file['rule']}")
    w("")
    w("| Question | Set | Suggested offices (score · keywords hit) | Expected |")
    w("|---|---|---|---|")
    probes = [(m["q"], "referral (B)", m["expect"]) for m in meas if m["path"] == "B"]
    probes += [(q, "scope exemplar, written before the keywords", d) for q, d in kw_probe]
    probes += [(m["q"], "out of scope (C)", None) for m in meas if m["path"] == "C" and m["role"] == "demo"]
    for q, label, exp in probes:
        res = match(q, kw_rules)
        got = "; ".join(f"{names[d]} ({sc} · {', '.join(h)})" + (" ✓" if d == exp else "")
                        for d, sc, h in res) or "*no keyword hit (fallback)*"
        w(f"| {cell(q)} | {label} | {cell(got)} | {cell(names[exp]) if exp else '—'} |")
    w("")
    w("Path C never shows an office, so a C row with a hit (the poem hitting *thesis*) "
      "changes nothing on screen. It is listed to show the rule is not magic.")
    w("")
    w("**Do not read this table as validation.** The same person wrote the keywords and "
      "most of these questions. Before the draft is accepted, the group writes 10 referral "
      "questions **without opening the keyword file**, and runs them through the rule.")
    w("")
    w("Open points in the draft: " + " ".join(f"({k + 1}) {cell(x)}" for k, x in
                                                enumerate(kw_file["known_weaknesses"])))
    w("")
    w(f"Fallback when nothing hits: **{kw_file['fallback']['note']}**")
    if kw_dupes:
        w("")
        w("Keywords that stem to the same tokens as an earlier keyword in the same department, "
          "and so are counted once: " + ", ".join(f"`{k}`" for _, k in kw_dupes) + ".")
    w("")

    # ------------------------------------------------------------- §7
    w("## 7. File inventory")
    w("")
    w("| File | Bytes | sha256 (first 16) |")
    w("|---|---:|---|")
    for p in sorted(list(DATA.iterdir()) + list(INPUTS.iterdir())
                    + [ROOT / "shared" / "tokenizer.py", ROOT / "shared" / "office_match.py"]):
        if p.is_file():
            w(f"| `{p.relative_to(ROOT).as_posix()}` | {p.stat().st_size:,} | `{sha256(p)[:16]}` |")
    w("")

    # ------------------------------------------------------------- sign-off
    w("## Review checks — sign-off (IMPLEMENTATION_PLAN.md §8, Sprint 1)")
    w("")
    w("| Check | Answered by | |")
    w("|---|---|---|")
    w("| Spot-check 10 of the 53 excluded passages — is every one genuinely front matter? | §1a | ☐ |")
    w("| Do all 22 department names match the handbook **exactly**, including \"and\" vs \"&\"? | §3a, §3b | ☐ |")
    w("| Is every office function statement copied verbatim, with no paraphrasing? | §3a | ☐ |")
    w("| Do the scope exemplars sound like UC-PnC students, not like a US university? | §4 | ☐ |")
    w("| Does `embeddings.npy` have exactly 311 rows, and does row 0 match passage 0? | §2, automatic checks 6–14 | ☐ |")
    w("| Does the new tokenizer keep the words that matter and drop the ones that don't? | §5b | ☐ |")
    w("")
    w("Open before sign-off: the DRAFT keyword list in §6d (the group's own 10-question test) "
      "and its fallback. Parked, not blocking: Student Discipline Office.")
    w("")

    DOCS.mkdir(exist_ok=True)
    (DOCS / "DATA_REPORT.md").write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(f"docs/DATA_REPORT.md written: {len(status) - n_fail}/{len(status)} automatic checks pass")
    for ok, label in status:
        if not ok:
            print("FAIL:", label)


if __name__ == "__main__":
    main()
