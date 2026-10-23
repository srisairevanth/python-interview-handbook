#!/usr/bin/env python3
"""Build index.html for the Python Interview Handbook.

Reads content/part-*.md, renders each chapter, runs every snippet marked `run`
with this interpreter (so the output shown is real), and writes one self-contained
index.html. The stylesheet and interaction script come from the sibling C++
handbook (same design system); the accent colour is switched to Python blue/yellow.

Usage:  python3 build.py            (add --report to print every run's output)
"""
import datetime
import glob
import html
import importlib.util
import os
import re
import subprocess
import sys

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(HERE, "content")
OUT = os.path.join(HERE, "index.html")
TEMPLATE = os.path.join(HERE, "..", "cpp-interview-handbook", "index.html")
TEMPLATE_DIR = os.path.join(HERE, "template")
TEMPLATE_CSS = os.path.join(TEMPLATE_DIR, "style.css")
TEMPLATE_THEME_JS = os.path.join(TEMPLATE_DIR, "theme-init.js")
TEMPLATE_APP_JS = os.path.join(TEMPLATE_DIR, "app.js")
RUN_TIMEOUT = 15
REPORT = "--report" in sys.argv

FORMATTER = HtmlFormatter(nowrap=True)
LANG_LABEL = {"python": "Python", "text": "Text", "bash": "Shell", "output": "Output"}

STATS = {"qa": 0, "puzzles": 0, "problems": 0, "runs": 0, "errors": 0, "chapters": 0}
PROBLEM_SLUGS = set()


def esc(text):
    return html.escape(text, quote=False)


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def inline(text):
    """Inline Markdown subset: `code`, **bold**, *italic*, [text](https://...)."""
    out = []
    for part in re.split(r"(`[^`]+`)", text):
        if len(part) > 1 and part[0] == "`" and part[-1] == "`":
            out.append("<code>" + esc(part[1:-1]) + "</code>")
            continue
        s = esc(part)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![\w*])\*([^*\s][^*]*?)\*(?![\w*])", r"<em>\1</em>", s)
        s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                   r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
        out.append(s)
    return "".join(out)


def run_snippet(code):
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True,
                          text=True, timeout=RUN_TIMEOUT, cwd=HERE)
    return proc.returncode, (proc.stdout + proc.stderr).rstrip("\n")


def render_code(lang, flags, code, title):
    """Highlighted code block; with `run`, the real output follows it."""
    code = code.rstrip("\n")
    label = LANG_LABEL.get(lang, lang.title())
    if lang == "python":
        body = highlight(code + "\n", PythonLexer(), FORMATTER).rstrip("\n")
    else:
        body = esc(code)
    badge = ""
    run_html = ""
    if "run" in flags:
        rc, out = run_snippet(code)
        STATS["runs"] += 1
        if rc != 0:
            if "raises" in flags:
                badge = ' <span class="code-badge is-error" title="Raises on purpose">raises on purpose</span>'
            else:
                STATS["errors"] += 1
                print("WARNING unexpected error in:", title or code.splitlines()[0], file=sys.stderr)
        else:
            badge = ' <span class="code-badge" title="Run with Python %d.%d while building this page">verified run</span>' % sys.version_info[:2]
        if REPORT:
            print("---", title or code.splitlines()[0][:60])
            print(out[:400])
        out_cls = "code-output" + (" code-error" if rc != 0 else "")
        out_label = "Output" if rc == 0 else "Traceback"
        out_body = esc(out) if out else "(no output)"
        run_html = ('<div class="code %s"><div class="code-head"><span class="code-lang">%s</span></div>'
                    '<pre><code>%s</code></pre></div>') % (out_cls, out_label, out_body)
    code_html = ('<div class="code code-%s"><div class="code-head"><span class="code-lang">%s%s</span>'
                 '<button type="button" class="copy" aria-label="Copy code">Copy</button></div>'
                 '<pre><code>%s</code></pre></div>') % (lang, label, badge, body)
    if run_html:
        return '<div class="run">' + code_html + run_html + '</div>\n'
    return code_html + "\n"


CALLOUTS = {
    "note": ("callout-note", "Note"),
    "remember": ("callout-remember", "Remember"),
    "pitfall": ("callout-pitfall", "Pitfall"),
    "tip": ("callout-tip", "Tip"),
    "say": ("callout-interview", "How to say it"),
}


def split_fence(lines, start):
    """Return (lang, flags, code_text, index_after_closing_fence) for a fence at lines[start]."""
    m = re.match(r"^```(\w*)\s*(.*)$", lines[start].strip())
    lang = m.group(1) or "text"
    flags = m.group(2).split()
    j = start + 1
    buf = []
    while j < len(lines) and not lines[j].strip().startswith("```"):
        buf.append(lines[j])
        j += 1
    return lang, flags, "\n".join(buf), j + 1


def render_table(rows, ctx):
    head = rows[0]
    body = rows[2:] if len(rows) > 1 and re.match(r"^\s*\|?\s*:?-{3,}", rows[1]) else rows[1:]
    def cells(row):
        row = row.strip()
        if row.startswith("|"):
            row = row[1:]
        if row.endswith("|"):
            row = row[:-1]
        return [c.strip() for c in row.split("|")]
    out = ['<div class="table-wrap"><table>', "<thead><tr>"]
    out += ["<th>%s</th>" % inline(c) for c in cells(head)]
    out.append("</tr></thead><tbody>")
    for r in body:
        out.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in cells(r)) + "</tr>")
    out.append("</tbody></table></div>\n")
    return "".join(out)


def render_problems(chid, lines, ctx):
    """Lines: NUMBER | Name | E/M/H | note  ->  tracker rows with tick boxes."""
    level = {"E": ("lvl-e", "Easy"), "M": ("lvl-m", "Medium"), "H": ("lvl-h", "Hard")}
    rows = []
    for line in lines:
        if not line.strip():
            continue
        num, name, lv, note = [p.strip() for p in line.split("|", 3)]
        key = slug(name)
        if key in PROBLEM_SLUGS:
            raise SystemExit("duplicate problem slug: " + key)
        PROBLEM_SLUGS.add(key)
        cls, word = level[lv]
        STATS["problems"] += 1
        rows.append(
            '<tr id="%s-p-%s" data-prob data-name="%s"><td><input type="checkbox" class="solved" '
            'data-problem="%s" aria-label="Mark %s as solved"></td><td><a href="https://leetcode.com/problems/%s/" '
            'target="_blank" rel="noopener">%s</a> <span class="pnum">#%s</span></td><td><span class="lvl %s">%s</span></td>'
            "<td>%s</td></tr>" % (chid, key, esc(name), key, esc(name), key, esc(name), num, cls, word, inline(note)))
    return ('<div class="table-wrap"><table><thead><tr><th>Done</th><th>Problem</th><th>Level</th>'
            "<th>Pattern</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>\n")


def render_qa(chid, qs, ctx):
    n = ctx["qa_n"] = ctx.get("qa_n", 0) + 1
    STATS["qa"] += 1
    q, a = qs
    return ('<details class="qa" id="%s-q%d" open><summary><span class="qa-mark" aria-hidden="true">Q</span>'
            '<span class="qa-text">%s</span></summary><div class="qa-body"><p>%s</p></div></details>\n'
            % (chid, n, inline(q), inline(a)))


def render_puzzle(chid, title, lines, ctx):
    ctx["puzzle_n"] = ctx.get("puzzle_n", 0) + 1
    num = ctx["puzzle_n"]
    STATS["puzzles"] += 1
    fence = next(i for i, l in enumerate(lines) if l.strip().startswith("```"))
    lang, flags, code, after = split_fence(lines, fence)
    rest = lines[after:]
    rc, out = run_snippet(code)
    STATS["runs"] += 1
    if rc != 0:
        STATS["errors"] += 1
        print("WARNING puzzle raised:", title, file=sys.stderr)
    if REPORT:
        print("--- puzzle", num, title)
        print(out[:300])
    body = render_body(chid, rest, ctx)
    out_cls = "code-output" + (" code-error" if rc != 0 else "")
    out_label = "Output" if rc == 0 else "Traceback"
    badge = ('' if rc != 0 else ' <span class="code-badge" title="Executed while building this page">verified run</span>')
    return ('<article class="puzzle" id="%s-p%d"><header class="puzzle-head"><span class="puzzle-num">#%02d</span>'
            '<h4 class="puzzle-title">%s</h4></header>'
            '<div class="code code-python"><div class="code-head"><span class="code-lang">Python</span>'
            '<button type="button" class="copy" aria-label="Copy code">Copy</button></div><pre><code>%s</code></pre></div>'
            '<details class="puzzle-answer"><summary>Show answer</summary><div class="puzzle-body">'
            '<div class="%s"><div class="code-head"><span class="code-lang">%s%s</span></div><pre><code>%s</code></pre></div>'
            '%s</div></details></article>\n'
            % (chid, num, num, inline(title), highlight(code + "\n", PythonLexer(), FORMATTER).rstrip("\n"),
               'code ' + out_cls, out_label, badge, esc(out) if out else "(no output)", body))


def render_block(chid, kind, title, lines, ctx):
    if kind in CALLOUTS:
        cls, label = CALLOUTS[kind]
        return ('<aside class="callout %s"><div class="callout-head"><span class="callout-label">%s</span>'
                '<span class="callout-title">%s</span></div><div class="callout-body">%s</div></aside>\n'
                % (cls, label, inline(title), render_body(chid, lines, ctx)))
    if kind == "puzzle":
        return render_puzzle(chid, title, lines, ctx)
    if kind == "problems":
        return render_problems(chid, lines, ctx)
    raise SystemExit("unknown block :::%s in chapter %s" % (kind, chid))


def render_body(chid, lines, ctx):
    out = []
    para = []
    items = []
    list_tag = None
    heads = ctx.setdefault("heads", set())

    def flush_para():
        if para:
            out.append("<p>%s</p>\n" % inline(" ".join(para)))
            para.clear()

    def flush_list():
        nonlocal list_tag
        if items:
            out.append("<%s>%s</%s>\n" % (list_tag, "".join("<li>%s</li>" % inline(i) for i in items), list_tag))
            items.clear()
        list_tag = None

    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.rstrip()
        stripped = s.strip()
        if stripped.startswith("```"):
            flush_para(); flush_list()
            lang, flags, code, nxt = split_fence(lines, i)
            out.append(render_code(lang, flags, code, ctx.get("title", "")))
            i = nxt
            continue
        m = re.match(r"^:::(\w+)\s*(.*)$", stripped)
        if m:
            flush_para(); flush_list()
            j = i + 1
            buf = []
            while j < len(lines) and lines[j].strip() != ":::":
                buf.append(lines[j])
                j += 1
            out.append(render_block(chid, m.group(1), m.group(2).strip(), buf, ctx))
            i = j + 1
            continue
        m = re.match(r"^(#{3,4})\s+(.*)$", stripped)
        if m:
            flush_para(); flush_list()
            text = m.group(2).strip()
            base = "%s-%s" % (chid, slug(text))
            hid, k = base, 2
            while hid in heads:
                hid = "%s-%d" % (base, k)
                k += 1
            heads.add(hid)
            tag = "h3" if len(m.group(1)) == 3 else "h4"
            out.append('<%s id="%s">%s</%s>\n' % (tag, hid, inline(text), tag))
            i += 1
            continue
        if stripped.startswith("Q: "):
            flush_para(); flush_list()
            q = stripped[3:].strip()
            answer = []
            j = i + 1
            if j < len(lines) and lines[j].strip().startswith("A: "):
                answer.append(lines[j].strip()[3:].strip())
                j += 1
                while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith("Q: "):
                    answer.append(lines[j].strip())
                    j += 1
            out.append(render_qa(chid, (q, " ".join(answer)), ctx))
            i = j
            continue
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            flush_para(); flush_list()
            j = i
            rows = []
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append(lines[j].strip())
                j += 1
            out.append(render_table(rows, ctx))
            i = j
            continue
        m = re.match(r"^(- |\d+\. )(.*)$", stripped)
        if m:
            flush_para()
            tag = "ul" if m.group(1) == "- " else "ol"
            if list_tag and list_tag != tag:
                flush_list()
            list_tag = tag
            items.append(m.group(2).strip())
            i += 1
            continue
        if not stripped:
            flush_para(); flush_list()
            i += 1
            continue
        flush_list()
        para.append(stripped)
        i += 1
    flush_para(); flush_list()
    return "".join(out)


def parse_content():
    """Return (parts, chapters). Parts: list of (num, name). Chapters: dicts with metadata and body lines."""
    parts, chapters = [], []
    part = None
    for path in sorted(glob.glob(os.path.join(CONTENT, "part-*.md"))):
        lines = open(path, encoding="utf-8").read().split("\n")
        i = 0
        current = None
        while i < len(lines):
            line = lines[i]
            if line.startswith("@part "):
                num, name = [p.strip() for p in line[6:].split("|", 1)]
                part = (int(num), name)
                parts.append(part)
                i += 1
                continue
            if line.strip() == "@chapter":
                current = {"part": part}
                i += 1
                while lines[i].strip() != "@body":
                    key, value = lines[i].split(":", 1)
                    current[key.strip()] = value.strip()
                    i += 1
                i += 1
                current["body"] = []
                chapters.append(current)
                continue
            if current is not None:
                current["body"].append(line)
            i += 1
    return parts, chapters


def render_chapter(ch, ctx, first_of_part):
    chid = ch["id"]
    ctx = dict(ctx, title=ch["title"])
    ctx["qa_n"] = 0
    ctx["puzzle_n"] = 0
    before = STATS["qa"]
    body = render_body(chid, ch["body"], ctx)
    qa_count = STATS["qa"] - before
    meta = '<span class="chapter-num">%s</span><span class="chapter-pkg">%s</span>' % (ch["num"], esc(ch["pkg"]))
    if qa_count:
        meta += '<span class="chapter-count">%d questions</span>' % qa_count
    actions = '<label class="revised"><input type="checkbox" id="rev-%s" data-section="%s"><span>Mark as revised</span></label>' % (chid, chid)
    if chid == "puzzles":
        actions += ' <button type="button" class="btn btn-small" id="reveal-puzzles" aria-pressed="false">Reveal all answers</button>'
    if "solved-line" in ctx.get("flags", ()) or chid == "problems":
        body = '<p class="solved-line">Solved <strong><span data-solved-count>0</span> of __PROBLEMS__</strong> problems. Progress is saved in this browser.</p>\n' + body
    marker = ""
    if first_of_part:
        marker = '<div class="part-marker" id="part-%d"><span class="part-no">Part %d</span><span class="part-name">%s</span></div>' % (
            ch["part"][0], ch["part"][0], esc(ch["part"][1]))
    return (marker + '<section class="chapter" id="%s" aria-labelledby="%s-title"><header class="chapter-head">'
            '<div class="chapter-meta">%s</div><h2 class="chapter-title" id="%s-title">%s</h2>'
            '<p class="chapter-summary">%s</p><div class="chapter-actions">%s</div></header>'
            '<div class="chapter-body">%s</div></section>\n'
            % (chid, chid, meta, chid, esc(ch["title"]), esc(ch["summary"]), actions, body))


def load_template():
    """Raw stylesheet, theme-init script and app script. Saved once into template/, then reused."""
    if os.path.exists(TEMPLATE_CSS):
        def read(path):
            with open(path, encoding="utf-8") as fh:
                return fh.read()
        return read(TEMPLATE_CSS), read(TEMPLATE_THEME_JS), read(TEMPLATE_APP_JS)
    with open(TEMPLATE, encoding="utf-8") as fh:
        src = fh.read()
    style = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
    theme_js = re.search(r"<script>try\{var t=localStorage.*?</script>", src, re.S).group(0)
    main_js = re.search(r"<script>\(function \(\) \{.*?</script>", src, re.S).group(0)
    return style, theme_js, main_js


def main():
    style, theme_js, main_js = load_template()
    if "--save-template" in sys.argv:
        os.makedirs(TEMPLATE_DIR, exist_ok=True)
        for path, text in ((TEMPLATE_CSS, style), (TEMPLATE_THEME_JS, theme_js), (TEMPLATE_APP_JS, main_js)):
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
        print("saved template to", TEMPLATE_DIR)
        return
    # All project pages on srisairevanth.github.io share one localStorage origin, so this handbook
    # uses its own progress and quiz keys. The theme key stays shared on purpose.
    for old, new in (('"cih.revised"', '"pih.revised"'), ('"cih.solved"', '"pih.solved"'), ('"cih.quiz"', '"pih.quiz"')):
        main_js = main_js.replace(old, new)
    style = style.replace("Sibling of the Java handbook; accent is C++ blue.",
                          "Sibling of the C++ and Java handbooks; accent is Python blue (light) and Python yellow (dark).")
    swaps = [("--accent: #0b5fa5;", "--accent: #306998;"),
             ("--accent-ink: #0a4b82;", "--accent-ink: #1f4b73;"),
             ("--accent-soft: #e3eef9;", "--accent-soft: #e4eef7;"),
             ("--accent: #6cb4f5;", "--accent: #ffd43b;"),
             ("--accent-ink: #a9d3fb;", "--accent-ink: #ffe683;"),
             ("--accent-soft: #14283c;", "--accent-soft: #2b2813;")]
    for old, new in swaps:
        assert old in style, old
        style = style.replace(old, new)
    style += ("\n/* Python token classes the C++ page does not use */\n"
              ".code .nb, .code .bp, .code .ne { color: var(--syn-attr); }\n"
              ".code .kc, .code .ow { color: var(--syn-kw); }\n")
    parts, chapters = parse_content()
    STATS["chapters"] = len(chapters)
    ctx = {}
    sections_html = []
    last_part = None
    for ch in chapters:
        first = ch["part"] != last_part
        last_part = ch["part"]
        sections_html.append(render_chapter(ch, ctx, first))

    toc = []
    cards = []
    for num, name in parts:
        chs = [c for c in chapters if c["part"] == (num, name)]
        items = "".join('<li><a href="#%s" data-toc="%s"><span class="toc-num">%s</span><span class="toc-title">%s</span>'
                        '<span class="toc-tick" aria-hidden="true"></span></a></li>' % (c["id"], c["id"], c["num"], esc(c["title"]))
                        for c in chs)
        toc.append('<div class="toc-part"><p class="toc-part-name"><span>Part %d</span> %s</p><ol>%s</ol></div>' % (num, esc(name), items))
        rng = chs[0]["num"] if len(chs) == 1 else "%s–%s" % (chs[0]["num"], chs[-1]["num"])
        cards.append('<a class="part-card" href="#%s"><span class="part-card-no">Part %d</span><span class="part-card-name">%s</span>'
                     '<span class="part-card-range">%s</span></a>' % (chs[0]["id"], num, esc(name), rng))

    total_problems = STATS["problems"]
    major, minor = sys.version_info[:2]
    magic = importlib.util.MAGIC_NUMBER.hex(" ").upper().split()
    bytes_html = "".join("<span>%s</span>" % b for b in magic)
    today = datetime.date.today()
    date_text = "%d %s %d" % (today.day, today.strftime("%b"), today.year)
    n_sections = len(chapters)
    lede = ("Everything a Python interview is likely to ask, in the order to revise it: how the interpreter and names work, "
            "the built-in data types and their costs, functions and scope, object-oriented Python, decorators, generators, "
            "exceptions, memory and concurrency, then NumPy and pandas for AI and data roles. A DSA part comes next with "
            "Python templates and a must-do problem tracker, followed by output puzzles, practice sets and a 21-day plan.")

    page = (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="description" content="Python interview revision handbook: notes, interview questions, verified output puzzles, '
        'a DSA part with Python templates, a must-do problem tracker, NumPy and pandas, and a 21-day plan.">\n'
        "<title>Python Interview Handbook</title>\n"
        '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800'
        '&family=JetBrains+Mono:ital,wght@0,400..700;1,400..700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400..700;1,8..60,400..700&display=swap">\n'
        "<style>" + style + "</style>\n" + theme_js + "\n</head>\n<body>\n"
        '<a class="skip" href="#main">Skip to content</a>\n'
        '<div class="topbar"><div class="topbar-inner">\n'
        '<button type="button" class="icon-btn menu-btn" id="menu-btn" aria-label="Open contents" aria-controls="rail" aria-expanded="false">'
        '<svg viewBox="0 0 24 24" aria-hidden="true" width="20" height="20"><path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>\n'
        '<a class="brand" href="#top"><span class="brand-mark">Py</span><span class="brand-name">Python Interview Handbook</span></a>\n'
        '<div class="search" role="search"><span class="search-icon"><svg viewBox="0 0 24 24" aria-hidden="true" width="18" height="18">'
        '<circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="2"/><path d="M20 20l-4.2-4.2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></span>'
        '<input id="search" type="search" placeholder="Search the handbook" autocomplete="off" spellcheck="false" aria-label="Search the handbook" aria-controls="search-results" aria-expanded="false">'
        '<kbd class="search-key" aria-hidden="true">/</kbd><div class="search-results" id="search-results" role="listbox" hidden></div></div>\n'
        '<button type="button" class="icon-btn" id="theme-toggle" aria-label="Switch theme"><svg viewBox="0 0 24 24" aria-hidden="true" width="18" height="18">'
        '<circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 4a8 8 0 0 1 0 16z" fill="currentColor"/></svg></button>\n'
        "</div></div>\n"
        '<div class="backdrop" id="backdrop" hidden></div>\n'
        '<div class="layout">\n<aside class="rail" id="rail" aria-label="Contents"><div class="rail-head">'
        '<div class="rail-top"><span class="rail-title">Contents</span><button type="button" class="icon-btn rail-close" id="rail-close" aria-label="Close contents">'
        '<svg viewBox="0 0 24 24" aria-hidden="true" width="20" height="20"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button></div>'
        '<div class="progress"><div class="progress-text"><span id="progress-count">0</span> of __SECTIONS__ sections revised</div>'
        '<div class="progress-track"><div class="progress-fill" id="progress-fill"></div></div></div>'
        '<button type="button" class="btn quiz-btn" id="quiz-toggle" aria-pressed="false"><span>Quiz mode</span><span class="quiz-state" id="quiz-state">Off</span></button>'
        '<p class="rail-hint">Quiz mode folds every answer so you can test yourself first.</p></div>'
        '<nav class="toc">' + "".join(toc) + "</nav></aside>\n"
        '<main id="main" class="main">\n'
        '<header class="hero" id="top">\n'
        '<p class="hero-bytes" aria-label="The four magic bytes at the start of a Python %d.%d .pyc file">%s</p>\n'
        '<p class="hero-bytes-caption">Magic number of a .pyc file for Python %d.%d · the interpreter checks these bytes before it trusts cached bytecode</p>\n'
        "<h1>Python Interview Handbook</h1>\n"
        '<p class="hero-lede">%s</p>\n'
        '<ul class="hero-stats"><li><strong>%d</strong> sections</li><li><strong>%d</strong> interview questions</li>'
        '<li><strong>%d</strong> output puzzles</li><li><strong>%d</strong> LeetCode problems to track</li>'
        '<li><strong>%d</strong> code samples run while building this page</li></ul>\n'
        '<nav class="parts-map" aria-label="Parts">%s</nav>\n</header>\n'
        % (major, minor, bytes_html, major, minor, esc(lede), n_sections, STATS["qa"], STATS["puzzles"],
           total_problems, STATS["runs"], "".join(cards))
        + "".join(sections_html)
        + '<footer class="footer"><p><strong>Python Interview Handbook</strong> · built %s. Snippets marked <span class="code-badge">verified run</span> '
          'were executed with Python %d.%d while this page was built, and the output shown is the real output. Puzzle answers are produced the same way.</p>\n'
          '<p>Companion handbooks: <a href="https://srisairevanth.github.io/cpp-interview-handbook/" target="_blank" rel="noopener">C++ Interview Handbook</a> · '
          '<a href="https://srisairevanth.github.io/java-interview-handbook/" target="_blank" rel="noopener">Java Interview Handbook</a></p>\n'
          '<p>Official references: <a href="https://docs.python.org/3/" target="_blank" rel="noopener">Python documentation</a> · '
          '<a href="https://peps.python.org/pep-0008/" target="_blank" rel="noopener">PEP 8 style guide</a></p>\n'
          '<p><a href="#top">Back to top</a></p></footer>\n'
          "</main>\n</div>\n" % (date_text, major, minor)
        + main_js + "\n</body>\n</html>\n"
    )
    page = page.replace("__PROBLEMS__", str(total_problems))
    page = page.replace("__SECTIONS__", str(n_sections))
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(page)
    print("wrote %s" % OUT)
    print("chapters=%d questions=%d puzzles=%d problems=%d runs=%d errors=%d bytes=%d" % (
        STATS["chapters"], STATS["qa"], STATS["puzzles"], STATS["problems"], STATS["runs"], STATS["errors"], len(page)))


if __name__ == "__main__":
    main()
