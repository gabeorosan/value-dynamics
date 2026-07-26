# Proposed edits, 26 July 2026 — the funding line

Both gated files describe the funding as "a BlueDot Impact grant". You said the
program is the BlueDot Technical AI Safety Project Sprint, and that this project
*is* your sprint project rather than something a separate grant paid for. That is
a different fact, not a rewording, so it needs your confirmation in these two
files. The demo's tweet thread has already been corrected the same way.

## 1. `docs/writeup_value_dynamics_sprint.md`, last line — **recommended**

**Before**

> Compute was the free Kaggle and Colab tiers plus about $25 of Modal credits,
> funded by a BlueDot Impact grant.

**After**

> I completed this project over five weeks for BlueDot Impact's Technical AI
> Safety Project Sprint. Compute was the free Kaggle and Colab tiers plus about
> $25 of Modal credits.

## 2. `README.md`, "Records" section, last line — **recommended**

Same sentence, same replacement.

**Before**

> Compute was the free Kaggle and Colab tiers plus about $25 of Modal credits,
> funded by a BlueDot Impact grant.

**After**

> I completed this project over five weeks for BlueDot Impact's Technical AI
> Safety Project Sprint. Compute was the free Kaggle and Colab tiers plus about
> $25 of Modal credits.

## Check on the program name — **needs your answer**

I have written "BlueDot Impact's Technical AI Safety Project Sprint", combining
the organization name already in both files with the program name you gave. If
the program is styled differently on their side (for instance "AI Safety
Technical Project Sprint", or without "Impact"), give me the exact name and I
will use it verbatim in both files and in the thread.

## Also worth knowing

`site/index.html` is generated from the writeup, so its copy of this sentence
changes automatically once the writeup does — no separate edit, but the site
does need a rebuild:

```bash
uv run --no-project --with markdown python scripts/site_build/build_from_md.py
```
