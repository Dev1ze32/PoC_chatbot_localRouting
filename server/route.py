"""The router: Gate 0 (initial check), Gate 1 (evidence), Gate 2 (scope), and the three paths.

    Gate 0 · Initial check (shared/initial_check.py, well under 1 ms, no model)
        0a not English          -> Path C (language notice): no search, no model call
        0b more than 1 question -> Path C (one-at-a-time notice + each question as a button)
    Gate 1: bm25_top >= T_b  OR  cosine_top >= T_c
        pass -> generator writes an answer from the fused top passages
                   answered, sources match  -> Path A (cited answer)
                   opens with the decline sentence (rule 1)
                                       -> Path B (referral), model found them insufficient;
                                          anything after the sentence is dropped   [guardrail 1]
                   citation check fails -> Path B (referral); the answer is withheld  [guardrail 2]
        fail -> Gate 2: closeness to the scope exemplars >= T_s
                   in scope            -> Path B (referral), no passage
                   out of scope        -> Path C (fixed message), no model call

Every response has the same shape (the contract). The front end switches its
card on `path` alone.
"""
import json
import sys
import time

import numpy as np

from server import config
from server.citations import check as check_citations
from server.generator import make_generator
from server.offices import Offices
from server.prompt import (DECLINE_SENTENCE, SYSTEM_PROMPT, build_user_message,
                           page_label, source_line)
from server.retrieve import Retriever

sys.path.insert(0, str(config.ROOT))
from shared import initial_check, language  # noqa: E402


class Router:
    def __init__(self):
        self.retriever = Retriever()
        self.offices = Offices()
        ex = [json.loads(line) for line in open(config.DATA / "scope_exemplars.jsonl", encoding="utf-8")]
        self.scope_texts = [e["text"] for e in ex]
        self.scope_matrix = self.retriever.model.encode(
            self.scope_texts, normalize_embeddings=True, show_progress_bar=False)
        self.generator, self.generator_problem = make_generator()
        language.check("warm up", config.LANGUAGE_CUTOFF)      # load the word lists now, not on the first question

    # ------------------------------------------------------------------ helpers
    def _refer(self, resp, question, source, lead):
        """Path B after the model was called: declined, or its sources failed."""
        offices = self.offices.suggest(question)
        resp.update(path="B", answer_source=source, lead=lead, offices=offices,
                    answer=config.REFERRAL_LEAD if offices else config.REFERRAL_NO_OFFICE)

    def _passage_view(self, row):
        p = self.retriever.passages[row]
        office, division = self.offices.display(p["issuing_office"])
        document = config.DOC_TITLES.get(p["document_id"][:4], p["title"])
        page = page_label(p["page_or_section"])
        section = p["page_or_section"].rsplit(" (", 1)[0]
        return {"passage_id": p["document_id"], "document": document, "office": office,
                "division": division, "year": p["year"], "page": page, "section": section,
                "source": source_line(document, office, p["year"], page), "text": p["text"]}

    def _thresholds(self):
        return {"bm25": config.BM25_THRESHOLD, "cosine": config.COSINE_THRESHOLD,
                "scope": config.SCOPE_THRESHOLD, "language": config.LANGUAGE_CUTOFF,
                "status": config.THRESHOLD_STATUS}

    # ------------------------------------------------------------------ main
    def ask(self, question):
        t_start = time.perf_counter()

        # ---- Gate 0 · Initial check: 0a English? 0b one question?
        ic = initial_check.run(question, config.LANGUAGE_CUTOFF, config.LANGUAGE_TYPO_TOLERANCE)
        ic_ms = (time.perf_counter() - t_start) * 1000
        if not ic["passed"]:
            multi = ic["stopped_by"] == "multiple_questions"
            return {"question": question, "path": "C",
                    "answer": config.MULTI_QUESTION_NOTICE if multi else config.LANGUAGE_NOTICE,
                    "answer_source": "multiple_questions" if multi else "language_notice",
                    "suggestions": ic["questions"]["questions"] if multi else [],
                    "lead": "", "citations": [], "offices": [],
                    "model_io": None, "passages_sent": [], "error": None,
                    "disclaimer": config.DISCLAIMER,
                    "trace": {"initial_check": ic, "gate1": {"ran": False}, "gate2": {"ran": False},
                              "fusion": None, "tokens": [],
                              "generator": {"calls": 0, "model": None, "backend": None, "declined": False},
                              "citation_check": {"status": "not run", "detail": ""},
                              "thresholds": self._thresholds(), "office_rule": None,
                              "timings_ms": {"initial_check": round(ic_ms, 2), "total": round(ic_ms, 2)}}}

        r = self.retriever.search(question)
        timings = dict(r["timings"], initial_check=ic_ms)

        lexical_ok = r["bm25_top"] >= config.BM25_THRESHOLD
        dense_ok = r["cosine_top"] >= config.COSINE_THRESHOLD
        gate1 = {"ran": True, "lexical_ok": lexical_ok, "dense_ok": dense_ok,
                 "passed": lexical_ok or dense_ok, "rule": "lexical_ok OR dense_ok"}
        trace = {"initial_check": ic, "tokens": r["tokens"],
                 "bm25_top": round(r["bm25_top"], 2), "bm25_top_id": r["bm25_top_id"],
                 "cosine_top": round(r["cosine_top"], 3), "cosine_top_id": r["cosine_top_id"],
                 "thresholds": self._thresholds(), "gate1": gate1,
                 "gate2": {"ran": False}, "fusion": None,
                 "generator": {"calls": 0, "model": None, "backend": None, "declined": False},
                 "citation_check": {"status": "not run", "detail": ""}}
        resp = {"question": question, "path": None, "answer": "", "answer_source": None,
                "suggestions": [],
                "lead": "", "citations": [], "offices": [], "model_io": None,
                "passages_sent": [], "error": None, "trace": trace,
                "disclaimer": config.DISCLAIMER}

        if gate1["passed"]:
            trace["fusion"] = {"method": "RRF", "k": config.RRF_K,
                               "candidates_each": config.CANDIDATES_EACH, "kept": r["fused"]}
            given = [self._passage_view(f["row"]) for f in r["fused"]]
            resp["passages_sent"] = [dict(v, n=i) for i, v in enumerate(given, 1)]
            user = build_user_message(given, question)
            resp["model_io"] = {"system": SYSTEM_PROMPT, "user": user, "output": None}

            if self.generator is None:
                resp.update(path="A", answer_source="unavailable",
                            error=f"The generator is not available: {self.generator_problem}")
                trace["generator"].update(backend="none")
            else:
                try:
                    g = self.generator.generate(SYSTEM_PROMPT, user)
                except Exception as e:           # network, auth, rate limit: show it, don't crash
                    resp.update(path="A", answer_source="error",
                                error=f"The generator call failed: {type(e).__name__}: {e}")
                    trace["generator"].update(calls=1, backend=self.generator.backend,
                                              model=self.generator.model)
                else:
                    timings["generate"] = g.latency_ms
                    resp["model_io"]["output"] = g.text
                    trace["generator"].update(calls=1, model=g.model, backend=g.backend,
                                              prompt_tokens=g.prompt_tokens,
                                              completion_tokens=g.completion_tokens)
                    # Guardrail 1: an output that OPENS with the decline sentence is a
                    # refusal, whatever follows (the base model often keeps writing).
                    text = g.text.strip()
                    declined = text.startswith(DECLINE_SENTENCE)
                    if declined:
                        trace["generator"]["declined"] = True
                        trace["generator"]["extra_text_dropped"] = text != DECLINE_SENTENCE
                        self._refer(resp, question, "model_declined", config.REFERRAL_DECLINED)
                    else:
                        body, cited, status, detail = check_citations(text, given)
                        trace["citation_check"] = {"status": status, "detail": detail}
                        if status == "passed":
                            resp.update(path="A", answer=body, answer_source="generated",
                                        citations=cited)
                        else:
                            # Guardrail 2: an answer whose sources can't be matched is
                            # never shown; the student is referred instead.
                            self._refer(resp, question, "citation_failed", config.REFERRAL_UNVERIFIED)
        else:
            t0 = time.perf_counter()
            qv = self.retriever.embed(question, instruction=False)   # question vs question
            sims = self.scope_matrix @ qv
            j = int(np.argmax(sims))
            in_scope = float(sims[j]) >= config.SCOPE_THRESHOLD
            timings["scope"] = (time.perf_counter() - t0) * 1000
            trace["gate2"] = {"ran": True, "scope_similarity": round(float(sims[j]), 3),
                              "threshold": config.SCOPE_THRESHOLD, "in_scope": in_scope,
                              "nearest_exemplar": self.scope_texts[j]}
            if in_scope:
                offices = self.offices.suggest(question)
                resp.update(path="B", answer_source="referral_rule",
                            lead=config.REFERRAL_NO_PASSAGE,
                            answer=config.REFERRAL_LEAD if offices else config.REFERRAL_NO_OFFICE,
                            offices=offices)
            else:
                resp.update(path="C", answer_source="fixed", answer=config.SCOPE_MESSAGE)

        trace["office_rule"] = self.offices.keyword_status if resp["path"] == "B" else None
        timings["total"] = (time.perf_counter() - t_start) * 1000
        trace["timings_ms"] = {k: round(v, 1) for k, v in timings.items()}
        return resp
