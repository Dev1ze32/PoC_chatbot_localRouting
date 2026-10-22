"""The generator's prompt: the system rules and the passage block.

SYSTEM_PROMPT started as the 2026-09-22 training-sample design (TR-001), which
states it is identical in training and in the running system.

2026-09-27 changes (PENDING in TR-001; training targets must follow them):
  v3  "one to three sentences" made answers too thin ("How do I enroll?" lost
      its steps). Now: one-sentence answer + numbered list (max 8 items,
      under 150 words).
  v4  Tested on the base Llama 3.2 3B Q4_K_M (10-16 questions, one run each,
      indicative only):
      - refusal check moved to rule 1 (guard first). With it last, the model
        never refused (0/8); first, it opened with the decline sentence in 7/8
        should-refuse cases (but kept writing; server/route.py cuts that off).
      - source-line rule shows two example lines, each starting "Source: ".
        Before, the model wrote "Source:" once as a heading (0/8 exact);
        after, 7/8 exact.
  The QLoRA adapter learns the behaviour from the training targets, not from
  this prompt; the server-side guardrails in route.py stay on either way.

Keep it short: the fine-tuned model learns the behaviour; the prompt only
states the rules. Change it here and only here.
"""
import re

SYSTEM_PROMPT = """You are the University of Cabuyao student helpdesk. Answer the question using only the manual passages provided.

Rules:
1. First check whether the passages directly state the answer to this exact question. If they do not, or they only cover a related topic, reply with exactly this sentence and nothing else:
The provided manual passages do not answer this question.
2. Otherwise, start with one sentence that directly answers the question.
3. Then list the details the student needs to act on, such as steps, requirements, deadlines, and fees, as a numbered list in the order the passages give them. Use at most 8 short items.
4. Keep the answer under 150 words, in plain text.
5. Use only facts stated in the passages. Do not add outside information.
6. After the answer, add one source line for each passage you used, copied exactly from that passage's header. Start every source line with "Source: ", for example:
Source: <document> | <office> | <year> | p. <page>
Source: <document> | <office> | <year> | p. <page>"""

DECLINE_SENTENCE = "The provided manual passages do not answer this question."

_PAGE = re.compile(r"\((pp?\.\s*[^)]+)\)\s*$")


def page_label(page_or_section):
    """'… (p. 177)' -> 'p. 177'; '… (pp. 175-176)' -> 'p. 175-176'.

    Always 'p. <page>', ranges included, because rule 6 tells the model the
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
