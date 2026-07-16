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
import pathlib
import re

import markdown

HERE = pathlib.Path(__file__).resolve().parent
REPO = pathlib.Path(__file__).resolve().parents[2]
DOCS = REPO / "docs"
MD = DOCS / "writeup_value_dynamics_sprint.md"
STYLE = (HERE / "style_block.html").read_text()
HEAD_PREFIX = (HERE / "site_head_prefix.html").read_text().rstrip("\n")
ART = REPO / "scripts" / "site_build" / "writeup_artifact.html"
SITE = REPO / "site" / "index.html"


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
            out.append(
                f'<figure class="nfig embed">'
                f'<img src="{uri}" alt="{alt}" loading="lazy">'
                f'<figcaption><b>Figure {fign}.</b> {caption}</figcaption>'
                f'</figure>')
        else:
            out.append(blk)
        i += 1
    body = "\n".join(out)
    # the Findings <ol> gets the styled-summary look
    body = body.replace("<ol>", '<ol class="summary">', 1)
    return title, body


def page(title, body):
    return (f'<div class="page">\n<header>\n'
            f'  <p class="eyebrow"><b>Draft</b> &middot; Value dynamics &middot; '
            f'July 2026</p>\n  <h1>{title}</h1>\n</header>\n{body}\n</div>')


def main():
    title, body = build_body(MD.read_text())
    page_html = page(title, body)
    # Artifact body: <title> + <style> + page (the Artifact tool supplies <head>)
    ART.write_text(f"<title>{title}</title>\n{STYLE}\n{page_html}\n")
    # Site: full standalone document
    site = (HEAD_PREFIX + "\n" + STYLE + "\n</head>\n<body>\n"
            + page_html + "\n</body>\n</html>\n")
    # entity-encode non-ascii so charset can't mangle it
    SITE.write_text(site.encode("ascii", "xmlcharrefreplace").decode("ascii"))
    nfig = body.count('<figure class="nfig embed">')
    print(f"wrote {ART.name} + {SITE} — {nfig} figures, {len(body)} body bytes")


if __name__ == "__main__":
    main()
