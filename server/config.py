"""Every setting the live demo uses, in one place.

The API key is NEVER written here. It is read from the environment, which
python-dotenv fills from poc_thesis/.env (see .env.example). .env is ignored
by git and must not be copied onto a shared USB stick.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
WEB = ROOT / "web"

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:          # python-dotenv is optional; plain env vars also work
    pass

# ---------------------------------------------------------------- retrieval
# Same settings as data/MANIFEST.json and docs/DATA_REPORT.md.
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
EMBED_DEVICE = "cpu"
QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "
BM25 = {"k1": 1.5, "b": 0.75, "epsilon": 0.25}
CANDIDATES_EACH = 10         # top-k from BM25 and from dense, before fusion
RRF_K = 60
PASSAGES_TO_MODEL = 3        # fused top-k passed to the generator

# ---------------------------------------------------------------- gate 0: initial check
# 0a Language: English only (manuscript scope). shared/language.py confirms
#    English; any other language or dialect gets the notice.
# 0b One question: shared/questions.py; two or more questions get the notice
#    with each question as a button.
# Tested in docs/INITIAL_CHECK_REPORT.md (tools/test_initial_check.py).
LANGUAGE_CUTOFF = 0.85
LANGUAGE_TYPO_TOLERANCE = True
LANGUAGE_NOTICE = ("Sorry, I can only answer questions written in English. "
                   "Pasensya na, English lang ang kaya kong sagutin sa ngayon.")
MULTI_QUESTION_NOTICE = ("It looks like you asked more than one question. I can answer one "
                         "question at a time. Pick one to start with:")

# ---------------------------------------------------------------- gates
# PROVISIONAL. Chosen so the 18 questions in DATA_REPORT.md §6 route as the
# plan expects: just above the highest B/C score on each signal. Sprint 4
# replaces these with calibrated values. Shown as provisional on screen.
BM25_THRESHOLD = 12.0
COSINE_THRESHOLD = 0.62
SCOPE_THRESHOLD = 0.59
THRESHOLD_STATUS = "provisional: set from 18 test questions; calibrated in Sprint 4"

# ---------------------------------------------------------------- generator
# STAND-IN. The study's generator is a fine-tuned, 4-bit Llama 3.2 3B running
# offline. This build uses a hosted LLM to show what answer generation looks
# like. Swap GENERATOR_BACKEND (server/generator.py) to change it.
GENERATOR_BACKEND = os.environ.get("POC_GENERATOR", "openai")
OPENAI_MODEL = os.environ.get("POC_OPENAI_MODEL", "gpt-4o-mini")
GENERATOR_TEMPERATURE = 0.0
GENERATOR_MAX_TOKENS = 400
GENERATOR_TIMEOUT_S = 30

# ---------------------------------------------------------------- display
# Document titles as the manuscript's Table 9 writes them.
DOC_TITLES = {"HDBK": "Student Manual",
              "INTN": "Internship Manual",
              "RSCH": "Student Research and Innovation Manual"}

SCOPE_MESSAGE = ("I can only help with questions about UC-PnC student policies and "
                 "services, from the Student Manual, the Internship Manual, and the "
                 "Student Research and Innovation Manual.")
REFERRAL_NO_PASSAGE = "I couldn't find this in the university manuals."
REFERRAL_DECLINED = "The manual passages I found don't answer this."
REFERRAL_LEAD = "Based on the subject, this is usually handled by:"
REFERRAL_NO_OFFICE = ("I couldn't match it to a specific office on the handbook's list "
                      "either.")
DISCLAIMER = ("Proof of concept. Answers are written by gpt-4o-mini, a cloud LLM standing "
              "in for the study's fine-tuned, 4-bit, offline model. Nothing here is a "
              "measured result.")

MAX_QUESTION_CHARS = 500

# Only whether a key exists is recorded; the key itself is never read into
# anything that is logged, returned or displayed.
OPENAI_API_KEY_PRESENT = bool(os.environ.get("OPENAI_API_KEY"))
