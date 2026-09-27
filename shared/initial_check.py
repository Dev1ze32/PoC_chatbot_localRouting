"""Gate 0 · Initial check. Two quick checks before any search:

    0a  Language      shared/language.py    is it English?        (manuscript scope)
    0b  One question  shared/questions.py   is it one question?   (one search, one path)

Either fails -> a friendly fixed notice (Path C family), no search, 0 model
calls. Order matters: language first, because splitting a non-English
message into "questions" means nothing.
"""
from shared import language, questions


def run(question, language_cutoff, typo_tolerance=True):
    lang = language.check(question, language_cutoff, typo_tolerance)
    out = {"passed": True, "stopped_by": None, "language": lang, "questions": None}
    if not lang["english"]:
        out.update(passed=False, stopped_by="language")
        return out
    q = questions.split(question)
    out["questions"] = q
    if not q["single"]:
        out.update(passed=False, stopped_by="multiple_questions")
    return out
