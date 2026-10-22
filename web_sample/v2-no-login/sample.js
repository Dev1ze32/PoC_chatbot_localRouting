/* UC-PnC Student Helpdesk — SAMPLE preview front end (v2 design).
 *
 * Same responses as the live PoC (web/), unplugged: no server, no search, no
 * model. Every answer comes from samples.js, built by tools/build_sample_site.py
 * from the real manual passages. Opens straight from disk (double-click index.html).
 *
 * No scores, cut-offs, timings or counts are shown anywhere: those are results,
 * and results belong to Chapters 4 and 5.
 *
 * Screenshots: index.html?q=a1,b1,c1&dev=1 asks those samples on load.
 * The earlier all-white design is kept in v1-white/.
 */
"use strict";

const SAMPLES = window.SAMPLES || [];
const byId = Object.fromEntries(SAMPLES.map(s => [s.id, s]));
const norm = q => String(q).toLowerCase().replace(/\s+/g, " ").replace(/[\s?.!]+$/, "").trim();
const byQuestion = Object.fromEntries(SAMPLES.map(s => [norm(s.question), s]));

// Topics: one prepared answer each (welcome tiles, sidebar, Path C buttons).
const TOPICS = SAMPLES.filter(s => s.topic).map(s => ({ label: s.topic, q: s.question, doc: s.citations[0].document }));

// Sample questions (developer view), grouped by the path each one takes.
const DEMO = [
  ["a", "A · Cited answer", ["a1", "a2", "a3", "a4"]],
  ["b", "B · Office referral", ["b1", "b2"]],
  ["c", "C · Out of scope", ["c1", "c2"]],
  ["c", "C · Initial check", ["c3", "c4"]],
];

const $ = (sel, root = document) => root.querySelector(sel);
const convo = $("#convo");
const hello = $("#hello");
const input = $("#q");
const sendBtn = $("#send");
let busy = false;

// ------------------------------------------------------------------ helpers
function h(tag, attrs = {}, ...children) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const c of children.flat(Infinity)) {
    if (c === null || c === undefined || c === false) continue;
    el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return el;
}

// Plain lines become paragraphs; runs of "1. …" lines become one numbered list.
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

// "PART 3. STUDENT SUCCESS > CHAPTER IX LIBRARY SERVICES > …" -> "Part 3. Student Success › Chapter IX Library Services › …"
function prettySection(s) {
  const small = new Set(["and", "of", "the", "for", "in", "on", "to", "a", "an", "or", "at", "by", "ng"]);
  const title = part => part === part.toUpperCase()
    ? part.toLowerCase().split(" ").map((w, i) =>
        /^(?=[ivx])x{0,3}(ix|iv|v?i{0,3})$/.test(w) ? w.toUpperCase()
        : (i > 0 && small.has(w)) ? w
        : w.charAt(0).toUpperCase() + w.slice(1)).join(" ")
    : part;
  return String(s).split(">").map(p => title(p.trim())).join(" › ");
}

const topicChips = () => h("div", { class: "chips" },
  TOPICS.map(t => h("button", { type: "button", class: "chip", onclick: () => ask(t.q) }, t.label)));

// ------------------------------------------------------------------ dev view
function setDev(on) {
  document.body.classList.toggle("dev", on);
  $("#devToggle").setAttribute("aria-pressed", String(on));
  try { localStorage.setItem("sampleDevView", on ? "1" : "0"); } catch (_) { /* private mode */ }
}
$("#devToggle").addEventListener("click", () => setDev(!document.body.classList.contains("dev")));

// ------------------------------------------------------------------ replies
const tag = text => h("div", { class: "tag" }, text);

function replyA(s) {
  return h("div", { class: "reply a", "aria-label": "Cited answer" },
    tag("PATH A · CITED ANSWER"),
    h("div", { class: "answer" }, paragraphs(s.answer)),
    h("div", { class: "sources" },
      h("div", { class: "sources-h" }, s.citations.length === 1 ? "Source" : "Sources"),
      h("div", { class: "src-grid" }, s.citations.map((c, i) => h("div", { class: "src" },
        h("div", { class: "src-top" },
          h("span", { class: "src-n" }, String(i + 1)),
          h("span", { class: "src-doc" }, c.document),
          h("span", { class: "src-page" }, `${c.page} · ${c.year}`)),
        h("div", { class: "src-sec" }, prettySection(c.section)),
        h("div", { class: "src-office" }, c.office),
        h("details", { class: "more" },
          h("summary", {}, "Read the passage"),
          h("div", { class: "passage" }, c.text)))))));
}

function replyB(s) {
  return h("div", { class: "reply b", "aria-label": "Office referral" },
    tag(s.kind === "declined" ? "PATH B · REFERRAL · MODEL DECLINED" : "PATH B · REFERRAL"),
    h("p", { class: "lead" }, s.lead),
    h("p", {}, s.answer),
    s.offices.map(o => h("div", { class: "office" },
      h("div", { class: "office-k" }, "Office"),
      h("div", { class: "office-name" }, o.name),
      h("div", { class: "office-div" }, `${o.division} division`),
      h("p", { class: "office-does" }, h("q", {}, o.statement)),
      h("div", { class: "office-ref" }, `Listed in the Student Manual, p. ${o.page}`))),
    h("p", { class: "fine" }, "I can only name offices from the list printed in the Student Manual."));
}

// A split-off question goes into the message box, not straight to the answer.
function fillBox(q) {
  input.value = q;
  input.focus();
  input.setSelectionRange(q.length, q.length);
}

function replyC(s) {
  if (s.kind === "multi") {
    return h("div", { class: "reply c", "aria-label": "One question at a time" },
      tag("PATH C · INITIAL CHECK · ONE QUESTION AT A TIME"),
      h("p", {}, s.answer),
      h("div", { class: "picks" }, s.suggestions.map(q =>
        h("button", { type: "button", class: "pick", onclick: () => fillBox(q) }, q))),
      h("p", { class: "fine" }, "Tapping a question puts it in the message box, so you can edit it before sending."));
  }
  const lang = s.kind === "language";
  return h("div", { class: "reply c", "aria-label": lang ? "English only" : "Outside scope" },
    tag(lang ? "PATH C · INITIAL CHECK · NOT ENGLISH" : "PATH C · OUT OF SCOPE"),
    h("p", {}, s.answer, lang ? " For example, you could ask about:" : " You could ask about:"),
    topicChips());
}

function replyNone() {
  return h("div", { class: "reply c", "aria-label": "No sample answer" },
    tag("SAMPLE PREVIEW · NO PREPARED ANSWER"),
    h("p", {}, "This preview only has prepared answers for its sample questions. Try one of these:"),
    topicChips(),
    h("p", { class: "fine" }, "Referral and out-of-scope samples are listed in Developer view."));
}

// ------------------------------------------------------------------ trace (no numbers)
function step(n, title, body, skip = false) {
  return h("li", { class: `step${skip ? " skip" : ""}` },
    h("span", { class: "n" }, n),
    h("div", {}, h("div", { class: "t" }, title), h("div", { class: "d" }, body)));
}
const verdict = ok => h("span", { class: ok ? "pass" : "fail" }, ok ? "✓ PASS" : "✗ FAIL");
const quote = words => words.map(w => `“${w}”`).join(", ");

function trace(s) {
  const steps = [];
  let n = 1;
  const add = (...a) => steps.push(step(n++, ...a));

  if (s.kind === "language" || s.kind === "multi") {
    const lang = s.kind === "language";
    add("Gate 0 · Initial check", [verdict(false), lang ? " — not written in English." : " — more than one question.",
      lang ? null : h("div", { class: "d sub" }, s.suggestions.map(q => h("div", {}, `• ${q}`)))]);
    add("Search and model", lang
      ? "Skipped. The question isn't in English, so it never reaches the search or the model."
      : "Skipped. One search and one answer per question; the student sends each one separately.", true);
    add("Result", h("b", {}, lang ? "Path C · language notice" : "Path C · one question at a time"));
    return wrap(steps, lang ? "English only, by design. No model is used." : "One question per message, by design. No model is used.");
  }

  add("Gate 0 · Initial check", [verdict(true), " — English, one question."]);
  add("Question received", ["What the keyword search sees (stemmed words):", h("div", { class: "toks" }, s.tokens.join(" · "))]);
  add("Searched the manuals, two ways", "Keyword search (BM25) and meaning search (BGE-small embeddings), over the same passages.");

  const evidence = s.kind === "answer" || s.kind === "declined";
  add("Gate 1 · Evidence", [verdict(evidence), evidence
    ? " — a passage matches strongly enough. Rule: keyword or meaning."
    : " — no passage matches strongly enough on either search."]);

  if (evidence) {
    add("Gate 2 · Scope", "Not needed: evidence was already found.", true);
    add("Combined ranking", "Reciprocal rank fusion (RRF) merges the two lists; the top-k passages go to the model.");
    const gen = [h("div", { class: "gen" },
      h("span", { class: "now" }, s.kind === "declined"
        ? "The study's fine-tuned 4-bit Llama 3.2 3B (with its QLoRA adapter) reads the passages, offline."
        : "The study's fine-tuned 4-bit Llama 3.2 3B (with its QLoRA adapter) writes the answer from the passages, offline."),
      h("span", { class: "full" }, "Sample: written for this preview in the format the model is trained to produce."))];
    if (s.kind === "declined") {
      gen.push(h("div", { class: "d sub" },
        `The model replied with the decline sentence: “${window.SAMPLE_TEXT.decline}” The passages are on the topic but don't answer this question, so the student is referred.`));
    }
    gen.push(h("details", { class: "more raw" },
      h("summary", {}, "Show the model's raw output (sample)"),
      h("div", { class: "passage" }, s.model_output)));
    add("Writing the answer", gen);
    if (s.kind === "answer") {
      add("Citation check", [verdict(true), " — every source line matches a passage the model was given.",
        h("div", { class: "d sub" }, "An answer whose sources don't match is never shown; the student gets a referral instead.")]);
    }
  } else {
    const inScope = s.kind === "referral";
    add("Gate 2 · Scope", [verdict(inScope), inScope
      ? " — close to the example questions about the university."
      : " — not about the university."]);
  }

  if (s.path === "B") {
    add("Choosing the office", s.offices.length
      ? `Keyword rule (draft) matched ${quote(s.offices[0].keywords_hit)} → ${s.offices.map(o => o.name).join("; ")}.`
      : "Keyword rule (draft) matched nothing. No office named.");
  }
  if (!evidence) {
    add("Writing the answer", h("div", { class: "gen" },
      h("span", { class: "now" }, "No model call."),
      h("span", { class: "full" }, s.path === "C" ? "The fixed message is sent without reaching the model." : "The referral is built from the office list, not by the model.")));
  }
  const label = { A: "Path A · cited answer", B: "Path B · referral, no citations", C: "Path C · out of scope, fixed message" }[s.path];
  add("Result", h("b", {}, label));
  return wrap(steps, "Sample preview: nothing was searched or generated. This shows the path the question takes through the system.");
}

function wrap(steps, foot) {
  return h("div", { class: "trace" },
    h("div", { class: "trace-h" }, "How this answer was made"),
    h("ol", { class: "steps" }, steps),
    h("p", { class: "foot" }, foot));
}

// ------------------------------------------------------------------ turns
function assistantShell() {
  const col = h("div", { class: "col" },
    h("div", { class: "who" }, h("span", { class: "seal xs", "aria-hidden": "true" }, "PnC"), "Helpdesk"),
    h("div", { class: "reply pending" }, h("span", { class: "typing", "aria-label": "Thinking" }, h("i"), h("i"), h("i")),
      h("span", { class: "typing-label" }, "Searching the manuals…")));
  return h("div", { class: "turn-a" }, col, h("div", { class: "trace-slot" }));
}

function fill(turn, s) {
  const col = turn.querySelector(".col");
  const reply = !s ? replyNone() : s.path === "A" ? replyA(s) : s.path === "B" ? replyB(s) : replyC(s);
  col.replaceChild(reply, col.querySelector(".reply"));
  if (!s) return;
  const how = h("button", { type: "button", class: "how", "aria-expanded": "false" }, "How was this answered?");
  how.addEventListener("click", () => {
    const open = turn.classList.toggle("open");
    how.setAttribute("aria-expanded", String(open));
  });
  col.append(h("div", { class: "how-row" }, how));
  turn.querySelector(".trace-slot").append(trace(s));
}

const pause = ms => new Promise(r => setTimeout(r, ms));

async function ask(question, instant = false) {
  question = (question || "").trim();
  if (!question || busy) return;
  busy = true;
  sendBtn.disabled = true;
  document.body.classList.add("chatting");
  const q = h("div", { class: "turn-q" }, h("div", { class: "bubble" }, question));
  const turn = assistantShell();
  convo.append(q, turn);
  if (!instant) {
    q.scrollIntoView({ behavior: "smooth", block: "start" });
    await pause(650);
  }
  fill(turn, byQuestion[norm(question)]);
  busy = false;
  sendBtn.disabled = false;
  if (!instant) input.focus();
}
window.ask = ask;

function reset() {
  convo.replaceChildren(hello);
  document.body.classList.remove("chatting");
  input.value = "";
  input.focus();
}

// ------------------------------------------------------------------ boot
$("#suggest").append(...TOPICS.map(t =>
  h("button", { type: "button", class: "tile", onclick: () => ask(t.q) },
    h("span", { class: "tile-t" }, t.label),
    h("span", { class: "tile-q" }, t.q),
    h("span", { class: "tile-src" }, t.doc))));

$("#sideTopics").append(...TOPICS.map(t =>
  h("button", { type: "button", class: "side-item", onclick: () => ask(t.q) }, t.label)));

const sampleGroups = () => DEMO.map(([cls, label, ids]) => h("div", { class: "grp" },
  h("div", { class: `grp-h ${cls}` }, label),
  ids.map(id => h("button", { type: "button", class: "side-item q", onclick: () => ask(byId[id].question) }, byId[id].question))));
$("#sideSamples").append(...sampleGroups());
$("#demoStrip").append(...sampleGroups());

$("#newQ").addEventListener("click", reset);
$("#composer").addEventListener("submit", e => {
  e.preventDefault();
  const q = input.value;
  input.value = "";
  ask(q);
});

(async () => {
  const P = new URLSearchParams(location.search);
  let dev = false;
  try { dev = localStorage.getItem("sampleDevView") === "1"; } catch (_) { /* ignore */ }
  if (P.has("dev")) dev = P.get("dev") === "1";
  setDev(dev);
  for (const id of (P.get("q") || "").split(",").filter(id => byId[id])) {
    await ask(byId[id].question, true);
  }
})();
