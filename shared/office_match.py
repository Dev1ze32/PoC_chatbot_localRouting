"""DRAFT: Path B office suggestion by keyword rule (data/office_keywords.json).

    "How do I report a broken air conditioner in our classroom?"
        -> Property Management and General Services Department  (hit: 'air conditioner')

Both the question and every keyword go through shared/tokenizer.py, so
'conditioners' matches 'air conditioner' and punctuation never matters.
A keyword hits when all its tokens appear in the question consecutively.
A department scores the total token length of its hits.

Status: draft, pending the group's review of the keyword list. Sprint 5's
server/offices.py imports this; it does not re-implement it.
"""
from shared.tokenizer import tokenize


def _contains(tokens, phrase):
    n = len(phrase)
    return any(tokens[i:i + n] == phrase for i in range(len(tokens) - n + 1))


def compile_rules(keyword_file):
    """keyword_file = the parsed office_keywords.json. Tokenize keywords once."""
    rules = []
    for d in keyword_file["departments"]:
        phrases, seen = [], set()
        for kw in d["keywords"]:
            toks = tokenize(kw)
            # Skip a keyword made only of stopwords (it can never hit), and one
            # that stems to the same tokens as an earlier keyword ('parking' and
            # 'park' are both 'park'), so a department cannot score twice for it.
            if toks and tuple(toks) not in seen:
                seen.add(tuple(toks))
                phrases.append((kw, toks))
        rules.append((d["department"], phrases))
    return rules


def match(question, rules, top_n=3):
    """Return [(department, score, [keywords hit])], best first, score > 0 only."""
    q = tokenize(question)
    scored = []
    for dept, phrases in rules:
        hits = [kw for kw, toks in phrases if _contains(q, toks)]
        if hits:
            score = sum(len(toks) for kw, toks in phrases if kw in hits)
            scored.append((dept, score, hits))
    scored.sort(key=lambda r: -r[1])
    return scored[:top_n]
