#!/usr/bin/env python3
"""make_gallery — build a single-page HTML gallery of every active figure,
ordered by when each figure was first committed (newest first).

The order is derived automatically from git (first-add commit of each SVG), so
regenerating always reflects the current set — no hand-maintained list. The
page inlines the SVGs, so it is fully self-contained (publishable as a Claude
artifact, which blocks external fetches).

Usage:
  python3 docs/figures/src/make_gallery.py [output.html]
    (default output: docs/figures/gallery.html — not committed; regenerate at will)

Stdlib only.
"""
import html
import os
import re
import subprocess
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(FIGDIR, "gallery.html")

GROUPS = [
    ("fig", "core set"),
    ("result_", "results"),
    ("synthesis_", "synthesis"),
    ("dynamics_", "dynamics"),
    ("methods_", "methods"),
    ("analysis_", "analysis"),
]


def first_commit(path):
    """(unix_ts, yyyy-mm-dd) of the commit that first added the file; falls back
    to file mtime for not-yet-committed figures (they sort newest, which is right)."""
    try:
        out = subprocess.run(
            ["git", "log", "--diff-filter=A", "--follow", "--format=%at",
             "--", os.path.basename(path)],
            capture_output=True, text=True, cwd=FIGDIR)
        stamps = [int(s) for s in out.stdout.split()]
        if stamps:
            ts = stamps[-1]
            return ts, date.fromtimestamp(ts).isoformat()
    except Exception:
        pass
    # not committed on this branch: not part of the canonical set, so skip it —
    # keeps another lane's uncommitted drafts out of the published gallery.
    return None, None


TITLE_RE = re.compile(r'<text[^>]*font-size="(\d+(?:\.\d+)?)"[^>]*font-weight="bold"[^>]*>([^<]+)</text>')


def svg_title(svg_text, fallback):
    """The figure's own headline: the first large bold text element(s)."""
    cands = [(float(m.group(1)), m.group(2)) for m in TITLE_RE.finditer(svg_text)]
    lines = [t for s, t in cands if s >= 26]
    if lines:
        return html.unescape(" ".join(lines[:2]) if len(lines) > 1 and cands[0][0] == cands[1][0] else lines[0])
    return fallback


def group_of(name):
    for prefix, label in GROUPS:
        if name.startswith(prefix):
            return label
    return "other"


entries = []
for fn in sorted(os.listdir(FIGDIR)):
    if not fn.endswith(".svg"):
        continue
    path = os.path.join(FIGDIR, fn)
    ts, when = first_commit(path)
    if ts is None:          # uncommitted draft — not part of the canonical set
        continue
    with open(path, encoding="utf-8") as f:
        svg = f.read()
    entries.append(dict(name=fn[:-4], svg=svg, ts=ts, when=when,
                        title=svg_title(svg, fn[:-4]), group=group_of(fn)))

entries.sort(key=lambda e: (-e["ts"], e["name"]))

# ---------------------------------------------------------------- page
cards, toc = [], []
for e in entries:
    anchor = e["name"]
    toc.append(f'<a href="#{anchor}"><span class="toc-date">{e["when"]}</span> {html.escape(e["name"])}</a>')
    cards.append(f'''
<section class="fig" id="{anchor}">
  <header>
    <div>
      <h2>{html.escape(e["title"])}</h2>
      <p class="meta"><code>{html.escape(e["name"])}.svg</code> · <span class="tag">{e["group"]}</span> · added {e["when"]}</p>
    </div>
  </header>
  <div class="canvas">{e["svg"]}</div>
</section>''')

n = len(entries)
today = date.today().isoformat()
page = f'''<title>Value dynamics — figure gallery</title>
<style>
:root {{
  --ground: #f7f8fa; --card: #ffffff; --ink: #1a1f26; --muted: #6b7684;
  --line: #dde3e9; --accent: #2867b5; --tag-bg: #eef2f6;
}}
@media (prefers-color-scheme: dark) {{
  :root {{ --ground: #14181d; --card: #ffffff; --ink: #e6e9ed; --muted: #98a2ad;
           --line: #2c343d; --accent: #6ea3dd; --tag-bg: #222932; }}
}}
:root[data-theme="dark"] {{ --ground: #14181d; --card: #ffffff; --ink: #e6e9ed; --muted: #98a2ad;
           --line: #2c343d; --accent: #6ea3dd; --tag-bg: #222932; }}
:root[data-theme="light"] {{ --ground: #f7f8fa; --card: #ffffff; --ink: #1a1f26; --muted: #6b7684;
           --line: #dde3e9; --accent: #2867b5; --tag-bg: #eef2f6; }}
body {{ background: var(--ground); color: var(--ink);
       font: 16px/1.5 Helvetica, Arial, sans-serif; margin: 0; }}
.wrap {{ max-width: 1240px; margin: 0 auto; padding: 40px 24px 80px; }}
h1 {{ font-size: 26px; margin: 0 0 4px; text-wrap: balance; }}
.sub {{ color: var(--muted); margin: 0 0 28px; }}
.toc {{ border: 1px solid var(--line); border-radius: 10px; padding: 14px 18px;
        margin-bottom: 36px; columns: 2; column-gap: 36px; background: var(--tag-bg); }}
.toc a {{ display: block; color: var(--ink); text-decoration: none; font-size: 13.5px;
          padding: 2px 0; break-inside: avoid; }}
.toc a:hover {{ color: var(--accent); }}
.toc-date {{ color: var(--muted); font-variant-numeric: tabular-nums; margin-right: 6px; }}
.fig {{ margin-bottom: 44px; }}
.fig header {{ display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 8px; }}
.fig h2 {{ font-size: 18px; margin: 0; }}
.meta {{ color: var(--muted); font-size: 13px; margin: 2px 0 0; }}
.meta code {{ font: 12.5px/1 ui-monospace, Menlo, monospace; }}
.tag {{ background: var(--tag-bg); border: 1px solid var(--line); border-radius: 999px;
        padding: 1px 9px; font-size: 12px; }}
.canvas {{ background: var(--card); border: 1px solid var(--line); border-radius: 12px;
           overflow-x: auto; }}
.canvas svg {{ display: block; width: 100%; height: auto; }}
a:focus-visible, .toc a:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
</style>
<div class="wrap">
  <h1>Value dynamics — figure gallery</h1>
  <p class="sub">{n} active figures, newest first (ordered by first commit). Regenerated {today} by
     <code>docs/figures/src/make_gallery.py</code>; archive/ and auto/ drafts excluded.</p>
  <nav class="toc">{"".join(toc)}</nav>
  {"".join(cards)}
</div>
'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(page)
print(f"wrote {OUT}  ({n} figures, {os.path.getsize(OUT) / 1e6:.1f} MB)")
