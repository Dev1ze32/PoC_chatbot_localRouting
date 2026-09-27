"""The generator's prompt: the system rules and the passage block.

SYSTEM_PROMPT is word for word the one in the 2026-09-22 training-sample design
(TR-001), which states it is identical in training and in the running system.
Keep it short: the fine-tuned model learns the behaviour; the prompt only
states the rules. Change it here and only here.
"""
import re

SYSTEM_PROMPT = """You are the University of Cabuyao student helpdesk. Answer the question using only the manual passages provided.

Rules:
1. Begin with a direct answer to the question in one to three sentences.
2. Use only facts stated in the passages. Do not add outside information.
3. After the answer, add one source line for each passage you used, copied exactly from that passage's header:
Source: <document> | <office> | <year> | p. <page>
4. If the passages do not answer the question, reply with exactly this sentence and nothing else:
The provided manual passages do not answer this question."""

DECLINE_SENTENCE = "The provided manual passages do not answer this question."

_PAGE = re.compile(r"\((pp?\.\s*[^)]+)\)\s*$")


def page_label(page_or_section):
    """'… (p. 177)' -> 'p. 177'; '… (pp. 175-176)' -> 'p. 175-176'.

    Always 'p. <page>', ranges included, because rule 3 tells the model the
    source line is 'p. <page>'. A header saying 'pp.' gets "corrected" by the
    model and then no longer matches its own header."""
    m = _PAGE.search(page_or_section)
    if not m:
        return "p. ?"
    return "p. " + re.sub(r"^pp?\.\s*", "", m.group(1)).strip()


def source_line(document, office, year, page):
    """The citation core. The header carries it; the model copies it."""
    return f"{document} | {office} | {year} | {page}"


def build_user_message(passages, question):
    """passages: dicts with 'source' (the citation core) and 'text'."""
    blocks = [f"[Passage {i}] {p['source']}\n{p['text']}"
              for i, p in enumerate(passages, 1)]
    return "Passages:\n\n" + "\n\n".join(blocks) + "\n\nQuestion: " + question
