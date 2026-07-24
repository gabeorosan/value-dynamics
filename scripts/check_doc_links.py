#!/usr/bin/env python3
"""Resolve every reference to a `*.md` file in the repo and report broken ones.

Three reference forms appear across this repo, and they are held to two
different standards:

  STRICT -- markdown link targets (`[t](target.md)`, `[t]: target.md`) and any
  path-shaped token (one containing a '/'). These claim to be paths, so they
  must resolve either relative to the file that contains them or relative to the
  repo root. A failure here is a genuinely broken link.

  BY-NAME -- bare filename mentions such as `report_foo.md` in prose, a
  docstring, or a <code> span. The repo's convention is to name a document by
  its bare filename rather than link it (CLAUDE.md: "Refer to figures by
  FILENAME"). These pass as long as a file with that basename exists somewhere
  in the repo; a failure means the named document does not exist at all.

Vendored trees, agent-tooling config, and multi-megabyte result blobs are
skipped. Run from anywhere:

    uv run --no-project scripts/check_doc_links.py
"""

from __future__ import annotations

import os
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SCAN_SUFFIXES = {".md", ".py", ".html", ".json", ".txt", ".ts", ".js", ".sh", ".yaml", ".yml"}
MAX_BYTES = 4_000_000

# Vendored, generated, or agent-tooling trees rather than project content.
EXCLUDE_DIRS = {
    ".git", ".claude", ".agents", ".codex", "node_modules", "scratchpad",
    "__pycache__", ".venv", "venv",
}

# Placeholders and ubiquitous per-directory names, not references to one file.
IGNORE_TOKENS = {
    "foo.md", "report_foo.md", "path.md", "target.md",
    "SKILL.md", "SPEC.md", "SMOKE.md", "README.md", "AGENTS.md", "CLAUDE.md",
    "adjudication.md", "manual_review_top_items.md",
}

MD_LINK_RE = re.compile(r"(?:\]\(|\]:\s*)([A-Za-z0-9_][A-Za-z0-9_./-]*\.md)")
SUFFIX_RE = re.compile(r"\.md(?![A-Za-z0-9_])")
PATH_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_./-")


def iter_files():
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDE_DIRS)
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if path.suffix not in SCAN_SUFFIXES:
                continue
            try:
                if path.stat().st_size > MAX_BYTES:
                    continue
            except OSError:
                continue
            yield path


def find_tokens(line: str, prev_line: str = ""):
    """Linear-time extraction of `*.md` path tokens.

    Finds each `.md` suffix and walks backwards over path characters. A regex
    like `[\\w./-]*\\.md` backtracks quadratically on the multi-megabyte
    single-line JSON blobs under experiments/, which hangs a naive scan.

    Three shapes are discarded as scanning artifacts rather than references:
    a token immediately preceded by ':' (the tail of a URL); a token that is the
    first thing on its line when the previous line ends in '_' or '-' (a
    filename hard-wrapped across two prose lines); and a token starting with '_'
    or '-' (the tail of a `NAME_<slug>_SUFFIX.md` template).
    """
    wrapped = prev_line.rstrip().endswith(("_", "-"))
    for match in SUFFIX_RE.finditer(line):
        end, start = match.end(), match.start()
        while start > 0 and line[start - 1] in PATH_CHARS:
            start -= 1
        token = line[start:end]
        if token == ".md" or token.startswith(("-", "_")):
            continue
        if start > 0 and line[start - 1] == ":":
            continue  # tail of a scheme://host/path URL
        if wrapped and not line[:start].strip():
            continue  # continuation of a filename wrapped across lines
        yield token


_EXISTS: dict[str, bool] = {}


def _is_file(path: Path) -> bool:
    key = str(path)
    if key not in _EXISTS:
        _EXISTS[key] = path.is_file()
    return _EXISTS[key]


def build_basename_index() -> set[str]:
    """Every markdown basename in the repo, including trees we do not scan.

    Skill and agent directories are excluded from scanning but included here:
    prose legitimately names files inside them (demo/README.md points at the
    no-ai-slop skill's eval.md).
    """
    skip = {".git", "node_modules", "__pycache__", ".venv", "venv"}
    names = set()
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for name in filenames:
            if name.endswith(".md"):
                names.add(name)
    return names


def main() -> int:
    known_names = build_basename_index()
    strict_bad: list[tuple[str, int, str]] = []
    byname_bad: list[tuple[str, int, str]] = []
    n_strict = n_byname = 0

    for path in iter_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        is_md = path.suffix == ".md"
        rel = str(path.relative_to(REPO))
        lines = text.splitlines()
        for lineno, line in enumerate(lines, start=1):
            link_targets = set(MD_LINK_RE.findall(line)) if is_md else set()
            for token in find_tokens(line, lines[lineno - 2] if lineno > 1 else ""):
                if token in IGNORE_TOKENS or "*" in token or "<" in token:
                    continue
                strict = ("/" in token) or (token in link_targets)
                if strict:
                    n_strict += 1
                    if not (_is_file(path.parent / token) or _is_file(REPO / token)):
                        strict_bad.append((rel, lineno, token))
                else:
                    n_byname += 1
                    if token not in known_names:
                        byname_bad.append((rel, lineno, token))

    def dedup(items):
        seen, out = set(), []
        for f, ln, tok in items:
            if (f, tok) in seen:
                continue
            seen.add((f, tok))
            out.append((f, ln, tok))
        return out

    strict_bad = dedup(strict_bad)
    byname_bad = dedup(byname_bad)

    print(f"checked {n_strict} path/link references and {n_byname} by-name mentions")
    print(f"BROKEN PATH/LINK REFERENCES: {len(strict_bad)}")
    for f, ln, tok in strict_bad:
        print(f"  {f}:{ln}  ->  {tok}")
    print(f"BY-NAME MENTIONS OF A NONEXISTENT FILE: {len(byname_bad)}")
    grouped = defaultdict(list)
    for f, ln, tok in byname_bad:
        grouped[tok].append(f"{f}:{ln}")
    for tok in sorted(grouped):
        print(f"  {tok}  <-  {', '.join(grouped[tok])}")

    return 1 if (strict_bad or byname_bad) else 0


if __name__ == "__main__":
    sys.exit(main())
