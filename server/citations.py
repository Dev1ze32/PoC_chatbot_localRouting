"""Citation check (reduced form of Objective 4's verifier).

Checks only what can be checked mechanically: every 'Source:' line the model
wrote must match, exactly, the header of a passage it was given. It does NOT
check that the answer's claims are supported by that passage; that is the
full verifier, not in this build.
"""
import re

_SOURCE = re.compile(r"^\s*Source:\s*(.+?)\s*$", re.MULTILINE)


def _norm(s):
    s = re.sub(r"\s+", " ", s).strip().rstrip(".").lower()
    return re.sub(r"\bpp\.", "p.", s)          # 'pp. 175-176' == 'p. 175-176'


def check(answer_text, given):
    """given: list of dicts with 'passage_id' and 'source'.
    -> (answer body without source lines, [cited], status, detail)"""
    lines = [m.group(1) for m in _SOURCE.finditer(answer_text)]
    body = _SOURCE.sub("", answer_text).strip()
    lookup = {_norm(p["source"]): p for p in given}
    cited, unmatched = [], []
    for line in lines:
        p = lookup.get(_norm(line))
        if p and p not in cited:
            cited.append(p)
        elif not p:
            unmatched.append(line)
    if not lines:
        return body, [], "failed", "no source line in the answer"
    if unmatched:
        return body, cited, "failed", f"{len(unmatched)} source line(s) match no passage given"
    return body, cited, "passed", f"{len(cited)} source line(s), all match a passage given"
