<script>(function () {
  "use strict";
  var store = {
    get: function (k, d) { try { var v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* storage unavailable */ } }
  };
  var root = document.documentElement;
  var body = document.body;
  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }

  /* ---------- theme ---------- */
  var themeBtn = $("#theme-toggle");
  function isDark() {
    var t = root.getAttribute("data-theme");
    if (t) return t === "dark";
    return !!(window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
  }
  function syncTheme() {
    themeBtn.setAttribute("aria-label", isDark() ? "Switch to light theme" : "Switch to dark theme");
    themeBtn.title = themeBtn.getAttribute("aria-label");
  }
  themeBtn.addEventListener("click", function () {
    var next = isDark() ? "light" : "dark";
    root.setAttribute("data-theme", next);
    store.set("cih.theme", next);
    syncTheme();
  });
  syncTheme();

  /* ---------- revised progress ---------- */
  var boxes = $$("input[data-section]");
  var revised = {};
  (store.get("cih.revised", []) || []).forEach(function (id) { revised[id] = true; });
  var countEl = $("#progress-count"), fillEl = $("#progress-fill");
  function renderProgress() {
    var n = 0;
    boxes.forEach(function (b) { b.checked = !!revised[b.dataset.section]; if (b.checked) n++; });
    $$("[data-toc]").forEach(function (a) { a.classList.toggle("done", !!revised[a.dataset.toc]); });
    countEl.textContent = n;
    fillEl.style.width = (boxes.length ? (100 * n / boxes.length) : 0) + "%";
  }
  boxes.forEach(function (b) {
    b.addEventListener("change", function () {
      if (b.checked) revised[b.dataset.section] = true; else delete revised[b.dataset.section];
      store.set("cih.revised", Object.keys(revised));
      renderProgress();
    });
  });
  renderProgress();

  /* ---------- quiz mode ---------- */
  var quizBtn = $("#quiz-toggle"), quizState = $("#quiz-state");
  var quiz = store.get("cih.quiz", false) === true;
  function applyQuiz() {
    body.classList.toggle("quiz", quiz);
    quizBtn.setAttribute("aria-pressed", quiz ? "true" : "false");
    quizState.textContent = quiz ? "On" : "Off";
    $$("details.qa").forEach(function (d) { d.open = !quiz; });
  }
  quizBtn.addEventListener("click", function () { quiz = !quiz; store.set("cih.quiz", quiz); applyQuiz(); });
  applyQuiz();

  var revealBtn = $("#reveal-puzzles");
  if (revealBtn) {
    revealBtn.addEventListener("click", function () {
      var show = revealBtn.getAttribute("aria-pressed") !== "true";
      revealBtn.setAttribute("aria-pressed", show ? "true" : "false");
      revealBtn.textContent = show ? "Hide all answers" : "Reveal all answers";
      $$("#puzzles details.puzzle-answer").forEach(function (d) { d.open = show; });
    });
  }

  /* ---------- drawer (narrow screens) ---------- */
  var menuBtn = $("#menu-btn"), backdrop = $("#backdrop"), rail = $("#rail");
  function setDrawer(open) {
    body.classList.toggle("drawer-open", open);
    backdrop.hidden = !open;
    menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) { var a = $(".toc a.active", rail) || $(".toc a", rail); if (a) a.scrollIntoView({ block: "center" }); }
  }
  menuBtn.addEventListener("click", function () { setDrawer(!body.classList.contains("drawer-open")); });
  $("#rail-close").addEventListener("click", function () { setDrawer(false); });
  backdrop.addEventListener("click", function () { setDrawer(false); });
  rail.addEventListener("click", function (e) { if (e.target.closest("a")) setDrawer(false); });

  /* ---------- open targets inside folded details ---------- */
  function revealTarget(id) {
    var el = id && document.getElementById(id);
    if (!el) return;
    var d = el.tagName === "DETAILS" ? el : el.closest("details");
    while (d) { d.open = true; d = d.parentElement && d.parentElement.closest("details"); }
    el.scrollIntoView({ block: "start" });
  }
  window.addEventListener("hashchange", function () { revealTarget(decodeURIComponent(location.hash.slice(1))); });
  if (location.hash.length > 1) setTimeout(function () { revealTarget(decodeURIComponent(location.hash.slice(1))); }, 60);

  /* ---------- active section in contents ---------- */
  var tocLinks = {};
  $$(".toc a[data-toc]").forEach(function (a) { tocLinks[a.dataset.toc] = a; });
  if ("IntersectionObserver" in window) {
    var current = null;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          if (current) current.classList.remove("active");
          current = tocLinks[en.target.id] || null;
          if (current) current.classList.add("active");
        }
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    $$("section.chapter").forEach(function (s) { io.observe(s); });
  }

  /* ---------- solved problems ---------- */
  var solvedBoxes = $$("input[data-problem]");
  var solved = {};
  (store.get("cih.solved", []) || []).forEach(function (k) { solved[k] = true; });
  var allProblems = {};
  solvedBoxes.forEach(function (b) { allProblems[b.getAttribute("data-problem")] = true; });
  function renderSolved() {
    solvedBoxes.forEach(function (b) { b.checked = !!solved[b.getAttribute("data-problem")]; });
    var n = Object.keys(allProblems).filter(function (k) { return solved[k]; }).length;
    $$("[data-solved-count]").forEach(function (el) { el.textContent = n; });
  }
  solvedBoxes.forEach(function (b) {
    b.addEventListener("change", function () {
      var k = b.getAttribute("data-problem");
      if (b.checked) solved[k] = true; else delete solved[k];
      store.set("cih.solved", Object.keys(solved));
      renderSolved();
    });
  });
  renderSolved();

  /* ---------- copy buttons ---------- */
  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".copy");
    if (!btn) return;
    var pre = btn.closest(".code").querySelector("pre");
    var text = pre.innerText;
    function done(msg) { btn.textContent = msg; setTimeout(function () { btn.textContent = "Copy"; }, 1600); }
    function fallback() {
      var r = document.createRange(); r.selectNodeContents(pre);
      var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
      done("Selected");
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done("Copied"); }, fallback);
    } else { fallback(); }
  });

  /* ---------- search ---------- */
  var input = $("#search"), panel = $("#search-results");
  var index = [];
  $$("section.chapter").forEach(function (sec) {
    var st = $(".chapter-title", sec).textContent.trim();
    var sum = ($(".chapter-summary", sec) || {}).textContent || "";
    index.push({ kind: "Section", text: st, id: sec.id, sec: $(".chapter-num", sec).textContent, hay: (st + " " + sum).toLowerCase(), key: st.toLowerCase(), rank: 0 });
    $$(".chapter-body h3[id], .chapter-body h4[id]", sec).forEach(function (h) {
      var t = h.textContent.trim();
      index.push({ kind: "Topic", text: t, id: h.id, sec: st, hay: t.toLowerCase(), key: t.toLowerCase(), rank: 1 });
    });
    $$("details.qa", sec).forEach(function (d) {
      var q = $(".qa-text", d).textContent.trim();
      var a = $(".qa-body", d).textContent;
      index.push({ kind: "Question", text: q, id: d.id, sec: st, hay: (q + " " + a).toLowerCase(), key: q.toLowerCase(), rank: 2 });
    });
    $$(".puzzle", sec).forEach(function (p) {
      var t = $(".puzzle-title", p).textContent.trim();
      index.push({ kind: "Puzzle", text: t, id: p.id, sec: st, hay: p.textContent.toLowerCase(), key: t.toLowerCase(), rank: 3 });
    });
    $$("tr[data-prob]", sec).forEach(function (tr) {
      var t = tr.getAttribute("data-name");
      index.push({ kind: "Problem", text: t, id: tr.id, sec: st, hay: (t + " " + tr.textContent).toLowerCase(), key: t.toLowerCase(), rank: 2 });
    });
  });
  index.forEach(function (it, i) { it.order = i; });

  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function mark(text, terms) {
    var out = esc(text);
    terms.forEach(function (t) {
      if (t.length < 2) return;
      var re = new RegExp("(" + esc(t).replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig");
      out = out.replace(re, "<mark>$1</mark>");
    });
    return out;
  }
  var results = [], sel = -1;
  function search(q) {
    var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    if (!terms.length) return [];
    var hits = index.filter(function (it) { return terms.every(function (t) { return it.hay.indexOf(t) !== -1; }); });
    hits.forEach(function (it) {
      var inKey = terms.filter(function (t) { return it.key.indexOf(t) !== -1; }).length;
      it.score = (terms.length - inKey) * 10 + it.rank * 2 + (it.key.indexOf(terms.join(" ")) !== -1 ? -5 : 0);
    });
    hits.sort(function (a, b) { return a.score - b.score || a.order - b.order; });
    return hits.slice(0, 40);
  }
  function renderResults() {
    var q = input.value.trim();
    if (!q) { closeResults(); return; }
    results = search(q);
    sel = results.length ? 0 : -1;
    var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    panel.innerHTML = results.length ? results.map(function (r, i) {
      return '<a class="sr-item" role="option" id="sr-' + i + '" href="#' + r.id + '" data-id="' + r.id + '" aria-selected="' + (i === sel) + '">' +
        '<span class="sr-kind">' + r.kind + '</span><span class="sr-text">' + mark(r.text, terms) + '</span>' +
        '<span class="sr-sec">' + esc(r.kind === "Section" ? "Section " + r.sec : r.sec) + '</span></a>';
    }).join("") : '<p class="sr-empty">No matches. Try a shorter word, such as “hash” or “thread”.</p>';
    panel.hidden = false;
    input.setAttribute("aria-expanded", "true");
  }
  function closeResults() { panel.hidden = true; input.setAttribute("aria-expanded", "false"); }
  function highlight() {
    $$(".sr-item", panel).forEach(function (el, i) { el.setAttribute("aria-selected", i === sel ? "true" : "false"); if (i === sel) el.scrollIntoView({ block: "nearest" }); });
  }
  function go(id) {
    closeResults();
    input.blur();
    if (location.hash === "#" + id) revealTarget(id); else location.hash = id;
    setTimeout(function () { revealTarget(id); }, 30);
  }
  var timer = null;
  input.addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(renderResults, 90); });
  input.addEventListener("focus", function () { if (input.value.trim()) renderResults(); });
  input.addEventListener("keydown", function (e) {
    if (e.key === "ArrowDown") { e.preventDefault(); if (results.length) { sel = (sel + 1) % results.length; highlight(); } }
    else if (e.key === "ArrowUp") { e.preventDefault(); if (results.length) { sel = (sel - 1 + results.length) % results.length; highlight(); } }
    else if (e.key === "Enter") { e.preventDefault(); if (sel >= 0 && results[sel]) go(results[sel].id); }
    else if (e.key === "Escape") { closeResults(); input.blur(); }
  });
  panel.addEventListener("click", function (e) {
    var a = e.target.closest(".sr-item");
    if (!a) return;
    e.preventDefault();
    go(a.dataset.id);
  });
  document.addEventListener("click", function (e) { if (!e.target.closest(".search")) closeResults(); });
  document.addEventListener("keydown", function (e) {
    var tag = (document.activeElement && document.activeElement.tagName) || "";
    if (e.key === "/" && tag !== "INPUT" && tag !== "TEXTAREA") { e.preventDefault(); input.focus(); input.select(); }
    if (e.key === "Escape" && body.classList.contains("drawer-open")) setDrawer(false);
  });
})();
</script>