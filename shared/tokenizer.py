"""The BM25 tokenizer. One function, used at index time AND at query time.

    "What are the policies on enrollment records?"
        -> ['polici', 'enrol', 'record']

Steps, in order:
  1. Unicode NFKC + lowercase      'Ｅnrollment' -> 'enrollment'
  2. Regex words [a-z0-9]+         'records?' -> 'records'   (punctuation never
                                   sticks to a word, so 'policy.' == 'policy')
  3. Drop 1-character tokens       list markers '1', 'a', stray 's' from "student's"
  4. Drop English stopwords        'what', 'are', 'the', 'on'
  5. Snowball (Porter2) stemming   'policies' -> 'polici', 'enrollment' and
                                   'enrolment' -> 'enrol'

Why each step exists is in IMPLEMENTATION_PLAN.md §6.4. The old tokenizer was
text.lower().split(): 'records?' and 'records' were different terms, and
'policy' never matched 'policies'.

Rules: the index and the query MUST use this same function. Changing anything
here changes every BM25 score, so bump TOKENIZER_VERSION and re-measure.
"""
import re
import unicodedata

import snowballstemmer

TOKENIZER_VERSION = "regex-stopwords-snowball-v1"

_WORD = re.compile(r"[a-z0-9]+")
_STEMMER = snowballstemmer.stemmer("english")

# NLTK's English stopword list, with contractions split the way _WORD splits
# them ("don't" -> "don", "t"). Vendored so the demo has no NLTK dependency.
STOPWORDS = frozenset("""
i me my myself we our ours ourselves you your yours yourself yourselves he him
his himself she her hers herself it its itself they them their theirs
themselves what which who whom this that these those am is are was were be been
being have has had having do does did doing a an the and but if or because as
until while of at by for with about against between into through during before
after above below to from up down in out on off over under again further then
once here there when where why how all any both each few more most other some
such no nor not only own same so than too very s t can will just don should now
d ll m o re ve y ain aren couldn didn doesn hadn hasn haven isn ma mightn mustn
needn shan shouldn wasn weren won wouldn
""".split())


def tokenize(text):
    text = unicodedata.normalize("NFKC", text).lower()
    words = [w for w in _WORD.findall(text) if len(w) > 1 and w not in STOPWORDS]
    return _STEMMER.stemWords(words)


def describe():
    """What gets recorded in MANIFEST.json so a score can be traced to its tokenizer."""
    return {"version": TOKENIZER_VERSION, "regex": _WORD.pattern,
            "min_token_length": 2, "stopwords": f"NLTK English ({len(STOPWORDS)})",
            "stemmer": "Snowball English (Porter2), snowballstemmer "
                       + _snowball_version()}


def _snowball_version():
    try:
        from importlib.metadata import version
        return version("snowballstemmer")
    except Exception:
        return "unknown"
