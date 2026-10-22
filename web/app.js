/* UC-PnC Student Helpdesk — front end.
 *
 * Renders one response contract (server/route.py) per question. The card is
 * chosen by `path` alone: "A" cited answer, "B" referral, "C" out of scope.
 * The front end never knows which model answered; swapping the generator on
 * the server changes nothing here.
 */
"use strict";

const API = "/api/ask";

// Topic chips (welcome + Path C) ask one representative question each.
const TOPICS = [
  ["Admission & enrolment", "What are the requirements for student admission?"],
  ["Grades & records", "How do I request a copy of my academic records?"],
  ["Library & clinic", "How do I borrow a book from the university library?"],
  ["Research & internship", "How many hours is the required internship?"],
];

// Demo strip (developer view). Sprint 3 re-checks this set; the lab-apron
// question is a known weak Path B example (DATA_REPORT.md §6).
const DEMO = [
  ["a", "A · CITED", ["What is the format of the research title page?",
                      "How do I borrow a book from the university library?",
                      "How many hours is the required internship?"]],
  ["b", "B · REFERRAL", ["How do I report a broken air conditioner in our classroom?",
                         "Where do I return my borrowed laboratory apron?",
                         "Where is the nearest ATM on campus?"]],
  ["c", "C · OUT OF SCOPE", ["Where can I eat near campus?",
                             "Write me a poem about my thesis.",
                             "Will it rain tomorrow in Cabuyao?"]],
];

const $ = (sel, root = document) => root.querySelector(sel);
const convo = $("#convo");
const input = $("#q");
const sendBtn = $("#send");
let busy = false;
let turnSeq = 0;

// ------------------------------------------------------------------ helpers
function h(tag, attrs = {}, ...children) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") el.className = v;
    else if (k === "text") el.textContent = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const c of children.flat(Infinity)) {
    if (c === null || c === undefined || c === false) continue;
    el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return el;
}
const fmt = (x, d) => (typeof x === "number" ? x.toFixed(d) : "—");

// Plain lines become paragraphs; runs of "1. …" lines become one numbered list
// (prompt rule 3). The list keeps the model's own numbering via `start`.
function paragraphs(text) {
  const out = [];
  let list = null;
  for (const line of String(text).split("\n").map(s => s.trim()).filter(Boolean)) {
    const m = line.match(/^(\d+)[.)]\s+(.*)$/);
    if (m) {
      if (!list) out.push(list = h("ol", { start: m[1] }));
      list.append(h("li", {}, m[2]));
    } else {
      list = null;
      out.push(h("p", {}, line));
    }
  }
  return out;
}

function topicChips() {
  return h("div", { class: "chips" },
    TOPICS.map(([label, q]) => h("button", { type: "button", class: "chip", onclick: () => ask(q) }, label)));
}

// "PART 3. STUDENT SUCCESS > CHAPTER IX LIBRARY SERVICES > Section 2. …"
//   -> "Part 3. Student Success › Chapter IX Library Services › Section 2. …"
function prettySection(s) {
  const small = new Set(["and", "of", "the", "for", "in", "on", "to", "a", "an", "or", "at", "by", "ng"]);  // "ng": Filipino particle
  const title = part => part === part.toUpperCase()
    ? part.toLowerCase().split(" ").map((w, i) =>
        /^(?=[ivx])x{0,3}(ix|iv|v?i{0,3})$/.test(w) ? w.toUpperCase()
        : (i > 0 && small.has(w)) ? w
        : w.charAt(0).toUpperCase() + w.slice(1)).join(" ")
    : part;
  return String(s).split(">").map(p => title(p.trim())).join(" › ");
}

function scrollToEnd(el) {
  el.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ------------------------------------------------------------------ dev view
function setDev(on) {
  document.body.classList.toggle("dev", on);
  $("#devToggle").setAttribute("aria-pressed", String(on));
  try { localStorage.setItem("devView", on ? "1" : "0"); } catch (_) { /* private mode */ }
}
$("#devToggle").addEventListener("click", () => setDev(!document.body.classList.contains("dev")));
try { if (localStorage.getItem("devView") === "1") setDev(true); } catch (_) { /* ignore */ }

// ------------------------------------------------------------------ modal
const modal = $("#modal");
$("#modalClose").addEventListener("click", () => modal.close());
modal.addEventListener("click", e => { if (e.target === modal) modal.close(); });

function openPassages(resp) {
  const body = $("#modalBody");
  body.replaceChildren();
  const io = resp.model_io;
  const citedIds = new Set((resp.citations || []).map(c => c.passage_id));
  const gen = resp.trace.generator;

  body.append(h("section", {},
    h("h3", {}, "1 · System prompt"),
    h("p", { class: "expl" }, "The rules the model follows. Same text in training and in the running system."),
    h("pre", { class: "pre" }, io ? io.system : "—")));

  const list = h("div", { style: "display:grid;gap:12px" });
  for (const p of resp.passages_sent || []) {
    const f = (resp.trace.fusion && resp.trace.fusion.kept || []).find(k => k.passage_id === p.passage_id) || {};
    list.append(h("div", { class: "psg" },
      h("div", { class: "psg-head" },
        h("span", { class: "h" }, `[Passage ${p.n}] ${p.source}`),
        h("span", { class: "m" },
          `${p.passage_id} · ${prettySection(p.section)} · keyword rank ${f.bm25_rank ?? "—"} · meaning rank ${f.dense_rank ?? "—"} · RRF ${f.rrf ?? "—"}`,
          citedIds.has(p.passage_id) ? h("span", { class: "cited" }, "  · cited in the answer") : "")),
      h("pre", { class: "pre" }, p.text)));
  }
  body.append(h("section", {},
    h("h3", {}, `2 · Passages given to the model (${(resp.passages_sent || []).length})`),
    h("p", { class: "expl" }, "The top passages after combining keyword and meaning search (RRF). Full text, exactly as sent. The header line is what the model must copy as its source line."),
    list));

  body.append(h("section", {},
    h("h3", {}, "3 · Question"),
    h("pre", { class: "pre" }, resp.question)));

  body.append(h("section", {},
    h("h3", {}, "4 · What the model returned"),
    h("p", { class: "expl" }, gen && gen.model ? `${gen.model} · ${gen.backend}` : "No model output."),
    h("pre", { class: "pre" }, io && io.output ? io.output : (resp.error || "—"))));

  body.append(h("details", {},
    h("summary", { class: "expl", style: "cursor:pointer" }, "Show the exact user message sent (passages + question as one text)"),
    h("pre", { class: "pre", style: "margin-top:8px" }, io ? io.user : "—")));

  modal.showModal();
}

// ------------------------------------------------------------------ cards
function tag(text) { return h("div", { class: "tag" }, text); }

function passagesButton(resp) {
  if (!resp.passages_sent || !resp.passages_sent.length) return null;
  return h("button", { type: "button", class: "btn dev-only", onclick: () => openPassages(resp) },
    `View the ${resp.passages_sent.length} passages given to the model`);
}

function cardA(resp) {
  if (resp.error) {
    return h("article", { class: "card err", "aria-label": "Error" },
      tag("PATH A · GATE 1 PASSED · NO ANSWER"),
      h("p", { class: "lead" }, "Evidence was found, but no answer could be written."),
      h("p", { class: "fine" }, resp.error),
      passagesButton(resp));
  }
  const n = resp.citations.length;
  const card = h("article", { class: "card a", "aria-label": "Cited answer" },
    tag(`PATH A · CITED ANSWER · ${n} CITATION${n === 1 ? "" : "S"}`),
    h("div", { class: "answer" }, paragraphs(resp.answer)));
  if (n) {
    card.append(h("div", { class: "sources" },
      h("h4", {}, n === 1 ? "Source" : "Sources"),
      resp.citations.map(c => h("div", { class: "src" },
        h("span", { class: "doc" }, `${c.document} · ${c.year} · ${c.page}`),
        h("span", {}, prettySection(c.section)),
        h("span", { class: "office" }, c.division ? `${c.office} · ${c.division}` : c.office),
        h("span", { class: "id" }, `Passage ${c.passage_id}`),
        h("details", { class: "full" },
          h("summary", {}, "Read the passage"),
          h("div", { class: "passage" }, c.text))))));
  }
  const btnA = passagesButton(resp);
  if (btnA) card.append(btnA);
  return card;
}

function cardB(resp) {
  const why = { model_declined: " · MODEL DECLINED", citation_failed: " · CITATION CHECK FAILED" }[resp.answer_source] || "";
  const card = h("article", { class: "card b", "aria-label": "Office referral" },
    tag(`PATH B · REFERRAL${why} · 0 CITATIONS`),
    h("p", { class: "lead" }, resp.lead),
    h("p", { style: "margin:0 0 10px" }, resp.answer));
  if (resp.offices.length) {
    card.append(h("div", { class: "offices" }, resp.offices.map(o =>
      h("div", { class: "office-card" },
        h("div", { class: "name" }, o.name),
        h("div", { class: "div" }, `${o.division} division`),
        h("p", { class: "does" }, "What they do: ", h("q", {}, o.statement)),
        h("div", { class: "ref" }, `Student Manual, p. ${o.page}`)))));
  }
  card.append(h("p", { class: "fine" },
    "Offices come from the list printed in the Student Manual, pp. 22–27. This helpdesk can only name an office on that list."));
  const btnB = passagesButton(resp);   // only when the model was called (declined, or its sources failed)
  if (btnB) card.append(btnB);
  return card;
}

// A split-off question goes into the message box, not straight to the server:
// "How is it computed?" may need its subject put back before sending.
function fillBox(q) {
  input.value = q;
  input.focus();
  input.setSelectionRange(q.length, q.length);
}

function cardC(resp) {
  const src = resp.answer_source;
  const badge = h("div", { class: "badge" }, `generator calls: ${resp.trace.generator.calls}`);
  if (src === "multiple_questions") {
    return h("article", { class: "card c", "aria-label": "One question at a time" },
      tag(`PATH C · INITIAL CHECK · ${resp.suggestions.length} QUESTIONS`),
      h("p", { class: "msg" }, resp.answer),
      h("div", { class: "chips split" }, resp.suggestions.map(q =>
        h("button", { type: "button", class: "chip", onclick: () => fillBox(q) }, q))),
      h("p", { class: "fine", style: "margin-top:10px" }, "Tapping a question puts it in the message box, so you can edit it before sending."),
      badge);
  }
  const lang = src === "language_notice";
  return h("article", { class: "card c", "aria-label": lang ? "English only" : "Outside scope" },
    tag(lang ? "PATH C · INITIAL CHECK · NOT ENGLISH" : "PATH C · OUT OF SCOPE"),
    h("p", { class: "msg" }, resp.answer, lang ? " For example, you could ask about:" : " You could ask about:"),
    topicChips(),
    badge);
}

// ------------------------------------------------------------------ trace
function step(n, title, body, skip = false) {
  return h("li", { class: `step${skip ? " skip" : ""}` },
    h("span", { class: "n" }, n),
    h("div", {}, h("div", { class: "t" }, title), h("div", { class: "d" }, body)));
}
function kv(rows) {
  return h("div", { class: "kv" }, rows.flatMap(([k, v]) => [h("span", { class: "k" }, k), h("span", { class: "v" }, v)]));
}
const verdict = ok => h("span", { class: ok ? "pass" : "fail" }, ok ? "✓ PASS" : "✗ FAIL");

function initialStep(ic, n) {
  const pct = x => `${Math.round(x * 100)}%`;
  const L = ic.language, Q = ic.questions;
  const body = [verdict(ic.passed), ic.passed ? " — English, one question."
    : ic.stopped_by === "language" ? " — not written in English." : " — more than one question."];

  const a = [h("div", { class: "t", style: "margin-top:8px" }, "0a · Language"),
             h("div", { class: "d" }, L.english ? "✓ English" : "✗ Not English")];
  if (!L.alphabet_ok) {
    a.push(h("div", { class: "d" }, "Uses letters outside the Latin alphabet."));
  } else {
    const rows = [["English words", `${pct(L.share)}  ≥ ${pct(L.cutoff)}?`]];
    if (L.not_recognised.length) rows.push(["Not recognised", L.not_recognised.join(", ")]);
    if (L.set_aside.length) rows.push(["Set aside", L.set_aside.join(", ")]);
    if (L.typo_matches.length) rows.push(["Accepted as typos", L.typo_matches.join(", ")]);
    a.push(kv(rows));
  }
  const b = [h("div", { class: "t", style: "margin-top:8px" }, "0b · One question")];
  if (!Q) {
    b.push(h("div", { class: "d" }, "Not checked: the message isn't in English."));
  } else {
    b.push(h("div", { class: "d" }, Q.single ? `✓ One question` : `✗ ${Q.count} questions found`));
    if (!Q.single) b.push(h("div", { class: "d" }, Q.questions.map((q, i) => h("div", {}, `${i + 1}. ${q}`))));
  }
  return step(n, "Gate 0 · Initial check", [body, a, b]);
}

function trace(resp) {
  const t = resp.trace, th = t.thresholds, g1 = t.gate1, g2 = t.gate2, gen = t.generator;
  const steps = [];
  let n = 0;
  if (t.initial_check) steps.push(initialStep(t.initial_check, n++));
  if (t.initial_check && !t.initial_check.passed) {
    const lang = t.initial_check.stopped_by === "language";
    steps.push(step(n++, "Search and model", lang
      ? "Skipped. The question isn't in English, so it never reaches the search or the model."
      : "Skipped. One search and one answer per question; the student sends each one separately.", true));
    steps.push(step(n++, "Result", h("span", {}, h("b", {}, lang ? "Path C · language notice" : "Path C · one question at a time"), " · 0 model calls")));
    return h("div", { class: "trace" },
      h("h3", {}, "How this answer was made"),
      h("ol", { class: "steps" }, steps),
      h("p", { class: "foot" }, `${lang ? "English only, by design." : "One question per message, by design."} Check time: ${fmt(t.timings_ms.initial_check, 2)} ms. No model, no network.`));
  }
  steps.push(step(n++, "Question received",
    t.tokens.length ? ["What the keyword search sees:", h("div", { class: "toks" }, t.tokens.join(" · "))]
                    : "No keywords left after removing filler words, so the keyword search has nothing to match."));
  steps.push(step(n++, "Searched the manuals, two ways", kv([
    ["Keyword match (BM25)", `${fmt(t.bm25_top, 2)}  ≥ ${th.bm25}?`],
    ["Meaning match (bge-small)", `${fmt(t.cosine_top, 3)}  ≥ ${th.cosine}?`],
  ])));
  steps.push(step(n++, "Gate 1 · Evidence",
    [verdict(g1.passed), g1.passed
      ? ` — found by ${[g1.lexical_ok && "keyword", g1.dense_ok && "meaning"].filter(Boolean).join(" and ")} search. Rule: keyword or meaning.`
      : " — no passage matches strongly enough on either search."]));
  if (!g2.ran) {
    steps.push(step(n++, "Gate 2 · Scope", "Not needed: evidence was already found.", true));
  } else {
    steps.push(step(n++, "Gate 2 · Scope", [
      verdict(g2.in_scope), g2.in_scope ? " — it is about the university." : " — not about the university.",
      kv([["Closeness to 25 example questions", `${fmt(g2.scope_similarity, 3)}  ≥ ${g2.threshold}?`]]),
      h("div", { class: "d", style: "margin-top:4px" }, `Closest example: “${g2.nearest_exemplar}”`)]));
  }
  if (t.fusion) {
    steps.push(step(n++, "Combined ranking", [
      `RRF, k = ${t.fusion.k}, top ${t.fusion.kept.length} given to the model:`,
      h("div", { class: "ids" }, t.fusion.kept.map(k => k.passage_id).join(" · "))]));
  }
  if (resp.path === "B") {
    steps.push(step(n++, "Choosing the office", resp.offices.length
      ? [`Keyword rule (draft) matched “${resp.offices[0].keywords_hit.join("”, “")}” → ${resp.offices.map(o => o.name).join("; ")}.`]
      : "Keyword rule (draft) matched nothing. No office named."));
  }
  if (gen.calls) {
    const rows = [["Model", gen.model || "—"], ["Where it runs", gen.backend || "—"]];
    if (gen.prompt_tokens) rows.push(["Tokens in / out", `${gen.prompt_tokens} / ${gen.completion_tokens}`]);
    steps.push(step(n++, "Writing the answer", [
      h("div", { class: "gen" },
        h("span", { class: "now" }, `This build: ${gen.model || "the stand-in model"} writes it from the passages (1 call).`),
        h("span", { class: "full" }, "Full system: the study's fine-tuned 4-bit model, offline.")),
      kv(rows),
      gen.declined ? h("div", { class: "d", style: "margin-top:4px" },
        "Guardrail 1: the model opened with the decline sentence (rule 1), so the passages do not answer this and the question is referred.",
        gen.extra_text_dropped ? " It kept writing after the sentence; that text was dropped." : "") : null]));
    const cc = t.citation_check;
    if (cc && cc.status !== "not run") {
      steps.push(step(n++, "Citation check", [verdict(cc.status === "passed"), ` — ${cc.detail}.`,
        cc.status !== "passed" ? h("div", { class: "d", style: "margin-top:4px" }, "Guardrail 2: the answer is withheld, not shown with a warning. The student gets a referral instead. The model's text is in the passages pop-up.") : null,
        h("div", { class: "d", style: "margin-top:4px" }, "Checks that each source line matches a passage header. It does not check the claims themselves (that is Objective 4).")]));
    }
  } else {
    steps.push(step(n++, "Writing the answer", h("div", { class: "gen" },
      h("span", { class: "now" }, "0 model calls — the same in the full system."),
      h("span", { class: "full" }, resp.path === "C" ? "The fixed message is sent without reaching the model." : "The referral is built from the office list, not by the model."))));
  }
  const label = { A: "cited answer", B: "referral", C: "out of scope" }[resp.path];
  steps.push(step(n++, "Result", h("span", {}, h("b", {}, `Path ${resp.path} · ${label}`),
    resp.path === "A" ? ` · ${resp.citations.length} citation(s)` : resp.path === "B" ? " · 0 citations" : " · fixed message")));

  const tm = t.timings_ms || {};
  return h("div", { class: "trace" },
    h("h3", {}, "How this answer was made"),
    h("ol", { class: "steps" }, steps),
    passagesButton(resp),
    h("p", { class: "foot" },
      `Cut-offs are ${th.status}. `,
      `Time: ${fmt(tm.total, 0)} ms total` + (tm.generate ? `, of which ${fmt(tm.generate, 0)} ms waiting for the cloud model` : "") + ". Indicative only; nothing here is a measured result."));
}

// ------------------------------------------------------------------ turns
function userBubble(q) {
  return h("div", { class: "turn-q" }, h("div", { class: "bubble-user" }, q));
}

function assistantShell() {
  const id = `t${++turnSeq}`;
  const col = h("div", { class: "col" },
    h("div", { class: "who" }, h("span", { class: "dot", "aria-hidden": "true" }, "PnC"), "Student Helpdesk"),
    h("div", { class: "card" }, h("span", { class: "typing", "aria-label": "Thinking" }, h("i"), h("i"), h("i")),
      h("span", { class: "typing-label" }, "Searching the manuals…")));
  return h("div", { class: "turn-a", id }, col, h("div", { class: "trace-slot" }));
}

function fill(turn, resp) {
  const col = turn.querySelector(".col");
  const card = resp.path === "A" ? cardA(resp) : resp.path === "B" ? cardB(resp) : cardC(resp);
  col.replaceChild(card, col.querySelector(".card"));
  const how = h("button", { type: "button", class: "how-label", "aria-expanded": "false" }, "How was this answered?");
  how.addEventListener("click", () => {
    const open = turn.classList.toggle("open");
    how.setAttribute("aria-expanded", String(open));
  });
  col.append(h("div", { class: "how-row" }, how));
  turn.querySelector(".trace-slot").append(trace(resp));
}

function fail(turn, message) {
  const col = turn.querySelector(".col");
  col.replaceChild(h("article", { class: "card err" },
    h("p", { class: "lead" }, "Something went wrong."),
    h("p", { class: "fine" }, message)), col.querySelector(".card"));
}

async function ask(question) {
  question = (question || "").trim();
  if (!question || busy) return;
  busy = true;
  sendBtn.disabled = true;
  document.querySelectorAll("button.chip").forEach(b => { b.disabled = true; });
  const q = userBubble(question);
  const turn = assistantShell();
  convo.append(q, turn);
  scrollToEnd(q);
  try {
    if (location.protocol === "file:") {
      throw new Error("This page was opened as a file. Start the server (python -m server.api in poc_thesis) and open http://127.0.0.1:8000 instead.");
    }
    const r = await fetch(API, { method: "POST", headers: { "Content-Type": "application/json" },
                                 body: JSON.stringify({ question }) });
    if (!r.ok) {
      let detail = `${r.status} ${r.statusText}`;
      try { detail = (await r.json()).detail || detail; } catch (_) { /* not JSON */ }
      throw new Error(detail);
    }
    fill(turn, await r.json());
  } catch (e) {
    fail(turn, e.message || String(e));
  } finally {
    busy = false;
    sendBtn.disabled = false;
    document.querySelectorAll("button.chip").forEach(b => { b.disabled = false; });
    input.focus();
  }
}

// ------------------------------------------------------------------ boot
document.querySelector("[data-topics]").replaceWith(topicChips());
const strip = $("#demoStrip");
for (const [cls, label, qs] of DEMO) {
  strip.append(h("div", { class: "row" },
    h("span", { class: `lbl ${cls}` }, label),
    qs.map(q => h("button", { type: "button", class: "chip", onclick: () => ask(q) }, q))));
}
$("#composer").addEventListener("submit", e => {
  e.preventDefault();
  const q = input.value;
  input.value = "";
  ask(q);
});

(async () => {
  const s = $("#genStatus");
  if (location.protocol === "file:") {
    s.textContent = "Server not running: this page was opened as a file.";
    return;
  }
  try {
    const hres = await (await fetch("/api/health")).json();
    const g = hres.generator;
    s.textContent = g.available ? `Generator: ${g.model} — ${g.backend}.` : `Generator unavailable: ${g.problem}`;
    if (g.disclaimer) $("#bannerGen").textContent = g.disclaimer.replace(/^Proof of concept\.\s*/, "");
  } catch (_) {
    s.textContent = "Server not reachable.";
  }
})();
