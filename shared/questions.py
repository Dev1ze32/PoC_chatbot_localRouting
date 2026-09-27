"""Initial check, part b: is this ONE question?

The pipeline answers one question per message: one search, one gate
decision, one path. Two questions in one message break every step (the
stronger topic takes all the passage slots; the model answers one half and
declines or ignores the other). So a message with two or more questions is
not answered. The student gets each question back as a button, to send one
at a time.

Rule, simply:
  1. Split into sentences at ? ! . ;
  2. Inside a sentence, split at a joining word (and, also, then, plus) or a
     comma ONLY when what follows starts like a question: "…a book AND HOW
     do I…". "the requirements AND deadlines for admission" is not split.
     After a join, a helper verb (is, do, have, can…) starts a question only
     when a subject follows it: "and DO I need…" yes, "and HAVE TO repeat" no.
  3. A part is a question if it starts like one (how, what, where, can, is,
     tell me, explain…) or it is the end of a sentence with a question mark.
     Parts of one word ("Where and when…") don't count.
  4. Two or more questions -> not single.
No model; well under 1 ms.
"""
import re

INTERROGATIVES = {"how", "what", "where", "when", "who", "whom", "whose", "which", "why",
                  "can", "could", "would", "should", "will", "shall", "is", "are", "am", "was",
                  "were", "do", "does", "did", "has", "have"}
REQUESTS = {"tell", "give", "show", "explain", "write", "list", "describe", "help", "find",
            "send", "define", "compose"}
STARTERS = INTERROGATIVES | REQUESTS
WH = {"how", "what", "where", "when", "who", "whom", "whose", "which", "why"}
SUBJECTS = {"i", "you", "we", "they", "he", "she", "it", "there", "the", "my", "this", "that",
            "these", "those", "your", "our", "a", "an", "students", "someone", "anyone"}

_SENTENCE = re.compile(r"[^?!.;]+[?!.;]*")
_JOIN = re.compile(r"\s*,?\s*\b(?:and\s+also|and\s+then|and|also|then|plus)\b\s*,?\s*|\s*,\s*", re.I)
_LEAD = re.compile(r"^(?:(?:and|also|then|plus|so|please|pls|ok|okay)\b[\s,]*)+", re.I)
_WORD = re.compile(r"[A-Za-z']+")


def _first_word(s):
    m = _WORD.match(s.strip())
    return m.group(0).lower() if m else ""


def _starts_question_after_join(text):
    words = [w.lower() for w in _WORD.findall(text)[:2]]
    if not words:
        return False
    if words[0] in WH or words[0] in REQUESTS:
        return True
    return words[0] in INTERROGATIVES and len(words) > 1 and words[1] in SUBJECTS


def _clauses(body):
    """Split a sentence at joining words that are followed by a question."""
    out, cur = [], body
    while True:
        cut = None
        for j in _JOIN.finditer(cur):
            if j.start() == 0:
                continue
            if _starts_question_after_join(_LEAD.sub("", cur[j.end():])):
                cut = j
                break
        if cut is None:
            out.append(cur)
            return out
        out.append(cur[:cut.start()])
        cur = cur[cut.end():]


def _tidy(text):
    t = text.strip(" ,")
    t = t[0].upper() + t[1:] if t else t
    return t + ("?" if _first_word(t) in INTERROGATIVES else ".")


def split(question):
    """-> dict: single (bool), count, questions (tidied, for buttons), parts (all, for the trace)."""
    parts = []
    for m in _SENTENCE.finditer(question):
        sent = m.group(0).strip()
        if not sent:
            continue
        qmark = sent.rstrip().endswith("?")
        body = sent.rstrip("?!.; ").strip()
        clauses = _clauses(body)
        for k, c in enumerate(clauses):
            text = _LEAD.sub("", c.strip()).strip(" ,")
            if not text:
                continue
            words = len(_WORD.findall(text))
            is_q = (_first_word(text) in STARTERS or (qmark and k == len(clauses) - 1)) and words >= 2
            parts.append({"text": text, "is_question": is_q, "words": words})
    qs = [p for p in parts if p["is_question"]]
    return {"single": len(qs) <= 1, "count": len(qs),
            "questions": [_tidy(p["text"]) for p in qs], "parts": parts}
