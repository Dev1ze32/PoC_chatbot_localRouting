"""Gate 0: is this question written in English?

The system is English-only (manuscript scope). This gate does not try to
recognise Tagalog, Bisaya, Ilocano, or any other language. It only confirms
English, so every other language and dialect is turned away by the same rule,
including ones nobody listed.

    1. Alphabet: any letter outside the Latin alphabet (Korean, Chinese,
       Arabic...) -> not English.
    2. Words: remove the university's own names ("Pamantasan ng Cabuyao"),
       set aside acronyms typed in capitals (TOR, OJT) and university terms
       (Pinnacle). Count how many remaining words are English: in the standard
       English word list, the chat-shorthand list, or (typo tolerance) one
       letter away from an English word of 5+ letters ("univrsity").
    3. English share >= cut-off -> English. Nothing left to judge ("TOR?") ->
       English: the normal gates decide.

Lists: data/english_words.txt (SCOWL, via Ubuntu's wamerican; see
inputs/american-english.COPYRIGHT.txt) and data/language_terms.json
(university names/terms and chat shorthand, human-reviewed).
Cost: about 1 ms per question, ~8 MB of memory, no model.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_WORD = re.compile(r"[^\W\d_]+(?:'[^\W\d_]+)?")
_LETTERS = "abcdefghijklmnopqrstuvwxyz"
_lists = None


def _load():
    global _lists
    if _lists is None:
        english = set((ROOT / "data" / "english_words.txt").read_text(encoding="utf-8").split())
        terms = json.loads((ROOT / "data" / "language_terms.json").read_text(encoding="utf-8"))
        _lists = {
            "english": english | set(terms["chat_shorthand"]),
            "terms": set(terms["university_terms"]),
            "phrases": [re.compile(r"\b" + r"\s+".join(map(re.escape, p.split())) + r"\b", re.I)
                        for p in terms["university_phrases"]],
        }
    return _lists


def _is_latin(ch):
    return ("a" <= ch.lower() <= "z") or ("À" <= ch <= "ɏ")


def _edits1(w):
    splits = [(w[:i], w[i:]) for i in range(len(w) + 1)]
    return ({a + b[1:] for a, b in splits if b}
            | {a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1}
            | {a + c + b[1:] for a, b in splits if b for c in _LETTERS}
            | {a + c + b for a, b in splits for c in _LETTERS})


def check(question, cutoff, typo_tolerance=True):
    """-> dict: english (bool), share, cutoff, alphabet_ok, recognised,
    not_recognised, set_aside, typo_matches, reason."""
    L = _load()
    out = {"english": True, "share": 1.0, "cutoff": cutoff, "alphabet_ok": True,
           "recognised": [], "not_recognised": [], "set_aside": [], "typo_matches": [],
           "reason": ""}

    if any(ch.isalpha() and not _is_latin(ch) for ch in question):
        out.update(english=False, share=0.0, alphabet_ok=False,
                   reason="written in a non-Latin alphabet")
        return out

    text = question
    for p in L["phrases"]:                      # the university's own names, e.g. "Pamantasan ng Cabuyao"
        for m in p.findall(text):
            out["set_aside"].append(m)
        text = p.sub(" ", text)

    for tok in _WORD.findall(text):
        w = tok.lower()
        if w.endswith("'s"):
            w = w[:-2]
        if (tok.isupper() and len(tok) >= 2) or w in L["terms"]:
            out["set_aside"].append(tok)
        elif w in L["english"]:
            out["recognised"].append(tok)
        elif typo_tolerance and len(w) >= 5 and any(e in L["english"] for e in _edits1(w)):
            out["recognised"].append(tok)
            out["typo_matches"].append(tok)
        else:
            out["not_recognised"].append(tok)

    counted = len(out["recognised"]) + len(out["not_recognised"])
    if counted == 0:
        out["reason"] = "nothing left to judge after setting aside acronyms and university terms"
        return out
    share = len(out["recognised"]) / counted
    out["share"] = round(share, 3)
    out["english"] = share >= cutoff
    out["reason"] = (f"{len(out['recognised'])} of {counted} words are English "
                     f"({share:.0%}), {'at or above' if out['english'] else 'below'} the {cutoff:.0%} cut-off")
    return out
