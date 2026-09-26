"""Sprint 1: the closed office list, extracted from the handbook itself.

    inputs/UC-PnC-Student-Handbook-Manual.pdf (printed pp. 22-27)
        ->  data/offices.json            6 divisions, 22 departments, aliases
        ->  data/office_exemplars.jsonl  one department's function statement per line

The names below are what we EXPECT to find. The statements are not typed in
here: they are cut out of the PDF text between one printed name and the next.
If a name is not found exactly as written, the tool stops. That is the check
that the 22 names match the handbook.

Pages 22-27 are excluded from the chunked corpus as front matter, but they are
the authority for the office list. Two uses of the same pages; no conflict.
"""
import re
import subprocess
from datetime import date

from common import (DATA, HANDBOOK_PDF, save_json, sha256, update_manifest,
                    write_jsonl)

# PDF pages are two-page spreads (792 x 612 pt). Column = half a spread.
HALF_W, PAGE_H = 396, 612

# (printed page, pdf page, column x) -> divisions printed in that column.
# Division: (id, display name, printed header, [department names as printed]).
LAYOUT = [
    (23, 12, 396, [
        ("OUP", "Office of the University President",
         "OFFICE OF THE UNIVERSITY PRESIDENT",
         ["Office of the University Secretary / Board Secretary"]),
        ("OEVP", "Office of the Executive Vice President",
         "OFFICE OF THE EXECUTIVE VICE PRESIDENT",
         ["Management Information Systems Department",
          "Data Protection Department"]),
    ]),
    (24, 13, 0, [
        ("AA", "Academic Affairs", "ACADEMIC AFFAIRS",
         ["Colleges and Senior High School",
          "Office of the University Registrar",
          "Office of the University Library"]),
    ]),
    (25, 13, 396, [
        ("ADMIN", "Administration", "ADMINISTRATION",
         ["University Health Department",
          "Laboratory Services and Disaster Risk Reduction Management Department",
          "Property Management and General Services Department",
          "Human Resource Management Department",
          "Entrepreneurship and Business Development Department",
          "Finance Department"]),
    ]),
    (26, 14, 0, [
        ("PRE", "Planning, Research, & Extension",
         "PLANNING, RESEARCH, & EXTENSION",
         ["Quality Management and Planning Department",
          "Community and Extension Services Department",
          "Research and Development Department",
          "Knowledge Management and Innovation Department"]),
    ]),
    (27, 14, 396, [
        ("SDAS", "Student Development & Auxiliary Services",
         "STUDENT DEVELOPMENT & AUXILIARY SERVICES",
         ["Student Affairs and Services Department",
          "Sports and Development Department",
          "Guidance and Counseling Department",
          "Admissions Department",
          "Placement, Alumni, and Linkage Department",
          "Gender and Development Department"]),
    ]),
]
HEADER_SUFFIX = " PHILOSOPHY & OBJECTIVES"

# Office names that appear in the corpus or in office_lookup.json but are NOT
# printed on pp. 22-27. Each maps to the printed department we believe it is.
# (name, printed department id or None, confirmed, evidence, decision)
DECIDED = "Group decision 2026-09-26 (provisional): cards show the printed name."
ALIASES = [
    ("University Library", "office-of-the-university-library", True,
     "Same unit; pp. 22-27 print the full name 'Office of the University Library'.",
     DECIDED),
    ("Linkages Department", "placement-alumni-and-linkage-department", True,
     "p. 27 prints 'Placement, Alumni, and Linkage Department'; the Internship "
     "Manual front matter reads 'PLACEMENT, ALUMNI, AND LINKAGES'. Already an "
     "open question in office_lookup.json.",
     DECIDED),
    ("Student Discipline Office", None, False,
     "Named 7x in Handbook prose, not printed on pp. 22-27. Separate unit or a "
     "function inside Student Affairs and Services? Unresolved.",
     "Skipped for now (parked 2026-09-26). Cards show 'Student Discipline "
     "Office' as the Handbook prose writes it."),
    ("Cashier's Office", "finance-department", False,
     "Named 10x in corpus prose. Cash handling is in the Finance Department's "
     "printed function; reporting line not confirmed.",
     "Not shown on any card: no office_lookup rule uses this name."),
    ("Accounting Department", "finance-department", False,
     "Named 2x in corpus prose. Accounting is in the Finance Department's "
     "printed function; reporting line not confirmed.",
     "Not shown on any card: no office_lookup rule uses this name."),
]

# Decisions that override the handbook as a basis, recorded where the office
# list lives. office_lookup.json itself is kept byte-identical to its input.
DECISIONS = [
    {"topic": "office names on cards", "date": "2026-09-26", "status": "provisional",
     "decision": "Use the names printed on Handbook pp. 22-27. A corpus or lookup "
                 "name is shown through its alias above."},
    {"topic": "admission questions", "date": "2026-09-26", "status": "decided",
     "decision": "Admission stays with the Office of the University Registrar, as "
                 "office_lookup.json already routes it. p. 27 prints an Admissions "
                 "Department; the group chose the Registrar."},
    {"topic": "Student Discipline Office", "date": "2026-09-26", "status": "parked",
     "decision": "Skipped for now. Revisit when someone can confirm whether it is "
                 "a separate office."},
]


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def column_text(pdf_page, x):
    out = subprocess.run(
        ["pdftotext", "-layout", "-f", str(pdf_page), "-l", str(pdf_page),
         "-x", str(x), "-y", "0", "-W", str(HALF_W), "-H", str(PAGE_H),
         str(HANDBOOK_PDF), "-"],
        check=True, capture_output=True, text=True, encoding="utf-8").stdout
    lines = []
    for line in out.splitlines():
        s = line.strip()
        if not s or "Learner’s Handbook" in s:
            continue
        m = re.fullmatch(r"(\d+)(\s+University of Cabuyao)?|University of Cabuyao", s)
        if m:
            if m.group(1):
                lines.append(f"<<PAGE {m.group(1)}>>")
            continue
        lines.append(s)
    # Join wrapped lines. A line ending in '-' is a printed hyphen
    # ('research-' / 'competent'), so keep it and join without a space.
    text = ""
    for s in lines:
        text += s if (not text or text.endswith("-")) else " " + s
    return text


def main():
    divisions, departments, exemplars = [], [], []
    for page, pdf_page, x, divs in LAYOUT:
        text = column_text(pdf_page, x)
        assert f"<<PAGE {page}>>" in text, f"column is not printed page {page}"
        text = text.replace(f"<<PAGE {page}>>", "").strip()

        # Every marker (division header or department name) must be found,
        # in printed order. Statement = text up to the next marker.
        markers = []
        for div_id, disp, printed, names in divs:
            markers.append(("div", div_id, printed + HEADER_SUFFIX))
            markers += [("dept", div_id, n) for n in names]
        pos, spans = 0, []
        for kind, div_id, label in markers:
            i = text.find(label, pos)
            if i < 0:
                raise SystemExit(f"NOT FOUND on p. {page}: {label!r}")
            spans.append((kind, div_id, label, i, i + len(label)))
            pos = i + len(label)
        for k, (kind, div_id, label, start, end) in enumerate(spans):
            if kind != "dept":
                continue
            stop = spans[k + 1][3] if k + 1 < len(spans) else len(text)
            statement = text[end:stop].strip()
            assert statement.startswith("To "), (label, statement[:40])
            dept_id = slug(label)
            departments.append({"id": dept_id, "name": label,
                                "division": div_id, "page": page})
            exemplars.append({"department": dept_id, "name": label,
                              "division": div_id, "page": page,
                              "statement": statement})
        for div_id, disp, printed, names in divs:
            divisions.append({"id": div_id, "name": disp, "printed": printed,
                              "page": page, "departments": len(names)})

    ids = {d["id"] for d in departments}
    assert len(departments) == 22 and len(ids) == 22, len(departments)
    assert len(divisions) == 6
    aliases = []
    for name, target, confirmed, evidence, decision in ALIASES:
        assert target is None or target in ids, target
        aliases.append({"name": name, "department": target,
                        "confirmed": confirmed, "evidence": evidence,
                        "decision": decision})

    source = {"document": "UC-PnC Student Handbook (Learner's Handbook "
                          "Revised Edition 2023-2028)",
              "section": "Divisional Philosophy & Objectives",
              "pages": "22-27",
              "file": "inputs/" + HANDBOOK_PDF.name,
              "sha256": sha256(HANDBOOK_PDF),
              "extracted": date.today().isoformat()}
    DATA.mkdir(exist_ok=True)
    save_json(DATA / "offices.json", {
        "source": source,
        "note": "Closed list. The demo may only name a department printed here. "
                "Pages 22-27 are excluded from the chunked corpus as front "
                "matter but are the authority for this list.",
        "divisions": divisions,
        "departments": departments,
        "display_rule": "Cards show the printed name from pp. 22-27. A name "
                        "that is not printed is shown through its alias; an "
                        "unresolved alias is shown as written.",
        "aliases": aliases,
        "decisions": DECISIONS,
    })
    write_jsonl(DATA / "office_exemplars.jsonl", exemplars)
    update_manifest("offices.json",
                    what="Closed office list: divisions, departments, aliases",
                    tool="tools/build_office_exemplars.py", source=source)
    update_manifest("office_exemplars.jsonl",
                    what="One department function statement per line, verbatim; "
                         "embedded at server start (Sprint 5), not stored",
                    tool="tools/build_office_exemplars.py", source=source,
                    fields=["department", "name", "division", "page", "statement"],
                    key="department")
    print(f"{len(divisions)} divisions, {len(departments)} departments, "
          f"{len(aliases)} aliases")


if __name__ == "__main__":
    main()
