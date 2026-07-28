#!/usr/bin/env python3
"""Render the writeup Markdown to the Artifact body and the Pages site.

Source of truth is docs/writeup_value_dynamics_sprint.md (edited directly, incl.
by other threads). This replaces the hand-maintained writeup_template.html, which
kept drifting out of sync. Styling is reused verbatim from the template's <style>
block (style_block.html); figures are inlined as base64 and auto-numbered.

Run:  uv run --with markdown python build_from_md.py
Writes: writeup_artifact.html (Artifact body) and site/index.html (full page).
"""
import base64
import os
import pathlib
import re

import markdown

HERE = pathlib.Path(__file__).resolve().parent
REPO = pathlib.Path(__file__).resolve().parents[2]
DOCS = REPO / "docs"
MD = DOCS / "writeup_value_dynamics_sprint.md"
DRAFTS_MD = DOCS / "draft_endpoint_framing_options.md"
STYLE = (HERE / "style_block.html").read_text()
HEAD_PREFIX = (HERE / "site_head_prefix.html").read_text().rstrip("\n")
ART = REPO / "scripts" / "site_build" / "writeup_artifact.html"
SITE = REPO / "site" / "index.html"
OPTION_A_SITE = REPO / "site" / "option-a.html"
OPTION_B_SITE = REPO / "site" / "option-b.html"


def data_uri(rel):
    """rel like 'figures/auto/x/x.svg' -> base64 data URI from docs/."""
    p = DOCS / rel
    return "data:image/svg+xml;base64," + base64.b64encode(p.read_bytes()).decode()


def build_body(md_text):
    lines = md_text.split("\n")
    title = lines[0].lstrip("#").strip()
    body_md = "\n".join(lines[1:])
    html = markdown.markdown(body_md, extensions=["extra", "sane_lists"])
    # never publish internal cross-thread notes (e.g. "revision requested")
    html = re.sub(r"<blockquote>(?:(?!</blockquote>).)*?revision requested.*?</blockquote>",
                  "", html, flags=re.DOTALL | re.IGNORECASE)

    # python-markdown separates top-level blocks with a single newline
    blocks = html.split("\n")
    out, i, fign = [], 0, 0
    img_re = re.compile(r'^<p>\s*<img\b([^>]*?)/?>\s*</p>$')
    cap_re = re.compile(r'^<p><em>(.*)</em></p>$', re.DOTALL)
    attr_re = re.compile(r'(\w+)="([^"]*)"')
    while i < len(blocks):
        blk = blocks[i]
        m = img_re.match(blk.strip())
        if m:
            attrs = dict(attr_re.findall(m.group(1)))
            src = attrs.get("src", "")
            alt = attrs.get("alt", "")
            # skip figures whose file doesn't exist yet (cross-thread churn) —
            # drop the image AND a following caption, don't number it
            if src.startswith("figures/") and not (DOCS / src).exists():
                if i + 1 < len(blocks) and cap_re.match(blocks[i + 1].strip()):
                    i += 1
                i += 1
                continue
            fign += 1
            uri = data_uri(src) if src.startswith("figures/") else src
            # is the next block a caption?
            caption = alt
            if i + 1 < len(blocks):
                cm = cap_re.match(blocks[i + 1].strip())
                if cm:
                    caption = cm.group(1).strip()
                    i += 1
            if src.endswith("rollouts-vs-observed-spaghetti.svg"):
                # INTERACTIVE embed: inline the svg (24 pre-sampled draw-sets
                # as <g class="simset"> groups) + a re-simulate button that
                # toggles which set is visible. The samples are all drawn by
                # the committed Python generator — the button only reveals a
                # different pre-drawn sample, it invents nothing.
                raw = (DOCS / src).read_text()
                raw = raw.replace("<svg ", '<svg style="width:100%;height:auto" ', 1)
                out.append(
                    f'<figure class="nfig embed" id="resim-fig">'
                    f'{raw}'
                    f'<div style="text-align:center;margin:6px 0 2px">'
                    f'<button id="resim-btn" style="font:inherit;font-size:15px;'
                    f'padding:6px 18px;border:1.5px solid #2867b5;border-radius:8px;'
                    f'background:#eef4fc;color:#2867b5;cursor:pointer">'
                    f'&#8635; re-simulate</button></div>'
                    + (f'<figcaption>{caption}</figcaption>' if caption else '')
                    + f'</figure>'
                    '<script>(function(){var cur=0,N=24;'
                    'var b=document.getElementById("resim-btn");if(!b)return;'
                    'b.addEventListener("click",function(){'
                    'var nxt=Math.floor(Math.random()*(N-1));if(nxt>=cur)nxt++;'
                    'document.querySelectorAll("#resim-fig g.simset").forEach(function(g){'
                    'g.style.display=(+g.getAttribute("data-set")===nxt)?"":"none";});'
                    'cur=nxt;});})();</script>')
            else:
                out.append(
                    f'<figure class="nfig embed">'
                    f'<img src="{uri}" alt="{alt}" loading="lazy">'
                    + (f'<figcaption>{caption}</figcaption>' if caption else '')
                    + f'</figure>')
        else:
            out.append(blk)
        i += 1
    body = "\n".join(out)
    # the Findings <ol> gets the styled-summary look
    body = body.replace("<ol>", '<ol class="summary">', 1)
    return title, body


# The option-a/option-b framing drafts are working history, not part of the
# published site. Emitting them put nav links to uncommitted pages on Pages,
# which 404'd. Set VD_DRAFT_OPTIONS=1 to build and link them again.
DRAFT_OPTIONS = os.environ.get("VD_DRAFT_OPTIONS") == "1"


def navigation(current):
    if not DRAFT_OPTIONS:
        return ""
    links = [
        ("main", "index.html", "Main writeup"),
        ("a", "option-a.html", "Option A: larger rework"),
        ("b", "option-b.html", "Option B: follow-up"),
    ]
    items = []
    for key, href, label in links:
        current_attr = ' aria-current="page"' if key == current else ""
        items.append(f'<a href="{href}"{current_attr}>{label}</a>')
    return '<nav class="draft-nav" aria-label="Draft versions">' + "".join(items) + "</nav>"


def page(title, body, current="main"):
    # The demo link is site chrome, not writeup prose, so it lives here rather
    # than in the (user-gated) markdown source.
    # Demo and repo links are site chrome, not writeup prose, so they live here
    # rather than in the (user-gated) markdown source. The page is where a reader
    # arrives from a link, so the code has to be reachable from it.
    demo = ('  <p class="demo-link"><a href="demo.html">&#9654; Watch the '
            '5-minute demo</a><span class="sep">&middot;</span>'
            '<a href="https://github.com/gabeorosan/value-dynamics">GitHub repo</a>'
            "</p>\n")
    return (f'<div class="page">\n{navigation(current)}\n<header>\n'
            f'  <p class="eyebrow"><b>Value dynamics</b> &middot; '
            f'July 2026</p>\n  <h1>{title}</h1>\n{demo}</header>\n{body}\n</div>')


def standalone_site(page_html):
    site = (HEAD_PREFIX + "\n" + STYLE + "\n</head>\n<body>\n"
            + page_html + "\n</body>\n</html>\n")
    return site.encode("ascii", "xmlcharrefreplace").decode("ascii")


def draft_option_pages():
    text = DRAFTS_MD.read_text()
    a_section = text.split("## Option A:", 1)[1].split("## Option B:", 1)[0]
    b_section = text.split("## Option B:", 1)[1]
    option_a = a_section.split("\n", 1)[1]
    option_b = b_section.split("\n", 1)[1]

    a_title = "Option A: make the distinction part of the main argument"
    b_title = "Option B: keep the main narrative and use a follow-up"
    _, a_body = build_body(f"# {a_title}\n\n{option_a}")
    _, b_body = build_body(f"# {b_title}\n\n{option_b}")
    return page(a_title, a_body, "a"), page(b_title, b_body, "b")


def main():
    title, body = build_body(MD.read_text())
    page_html = page(title, body)
    # Artifact body: <title> + <style> + page (the Artifact tool supplies <head>)
    ART.write_text(f"<title>{title}</title>\n{STYLE}\n{page_html}\n")
    # Site: full standalone documents
    SITE.write_text(standalone_site(page_html))
    extra = ""
    if DRAFT_OPTIONS:
        option_a_html, option_b_html = draft_option_pages()
        OPTION_A_SITE.write_text(standalone_site(option_a_html))
        OPTION_B_SITE.write_text(standalone_site(option_b_html))
        extra = " + option-a.html + option-b.html"
    nfig = body.count('<figure class="nfig embed"')
    print(f"wrote {ART.name} + {SITE}{extra} — "
          f"{nfig} figures, {len(body)} body bytes")


if __name__ == "__main__":
    main()
