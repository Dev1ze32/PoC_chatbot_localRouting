"""Office names and the Path B office suggestion.

Display rule (offices.json, group decision 2026-09-26): show the name printed
on Handbook pp. 22-27. A corpus name that isn't printed is shown through its
confirmed alias; otherwise it is shown as written.
Path B uses the DRAFT keyword rule (data/office_keywords.json).
"""
import json
import sys

from server import config

sys.path.insert(0, str(config.ROOT))
from shared.office_match import compile_rules, match  # noqa: E402


class Offices:
    def __init__(self):
        o = json.load(open(config.DATA / "offices.json", encoding="utf-8"))
        self.divisions = {d["id"]: d["name"] for d in o["divisions"]}
        self.depts = {d["id"]: d for d in o["departments"]}
        self.by_name = {d["name"]: d for d in o["departments"]}
        self.aliases = {a["name"]: a for a in o["aliases"]}
        self.statements = {}
        for line in open(config.DATA / "office_exemplars.jsonl", encoding="utf-8"):
            r = json.loads(line)
            self.statements[r["department"]] = r["statement"]
        kw = json.load(open(config.DATA / "office_keywords.json", encoding="utf-8"))
        self.rules = compile_rules(kw)
        self.keyword_status = kw["status"]

    def display(self, corpus_name):
        """-> (display name, division name or None)."""
        if corpus_name in self.by_name:
            d = self.by_name[corpus_name]
            return d["name"], self.divisions[d["division"]]
        a = self.aliases.get(corpus_name)
        if a and a["confirmed"] and a["department"]:
            d = self.depts[a["department"]]
            return d["name"], self.divisions[d["division"]]
        return corpus_name, None

    def suggest(self, question):
        out = []
        for dept_id, score, hits in match(question, self.rules):
            d = self.depts[dept_id]
            out.append({"id": dept_id, "name": d["name"],
                        "division": self.divisions[d["division"]], "page": d["page"],
                        "statement": self.statements[dept_id],
                        "keywords_hit": hits, "score": score})
        return out
