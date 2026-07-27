# Proposed edits, 26 July 2026 — the funding line

Both gated files describe the funding as "a BlueDot Impact grant" and name no
program. The text below is the sentence you dictated, updated on 26 July to
the cohort wording: the compute stays, the programme is named, and both
links you gave are attached — the cohort to the course page, the money to the
rapid-grants page.

**These two files are gated on your confirmation, which is why this is a proposal
and not a commit. Reply "apply" and both go in, and the site rebuilds from the
writeup.** The demo's tweet thread already carries the sentence.

## 1. `docs/writeup_value_dynamics_sprint.md`, last line — **recommended**

**Before**

> Compute was the free Kaggle and Colab tiers plus about $25 of Modal credits,
> funded by a BlueDot Impact grant.

**After**

> I completed this project over 5 weeks as part of a [BlueDot Project
> cohort](https://bluedot.org/courses/technical-ai-safety-project). Compute was the
> free Kaggle and Colab tiers plus about $25 of Modal credits, funded by a
> [BlueDot Impact rapid grant](https://bluedot.org/programs/rapid-grants).

## 2. `README.md`, "Records" section, last line — **recommended**

Same sentence, same replacement.

**Before**

> Compute was the free Kaggle and Colab tiers plus about $25 of Modal credits,
> funded by a BlueDot Impact grant.

**After**

> I completed this project over 5 weeks as part of a [BlueDot Project
> cohort](https://bluedot.org/courses/technical-ai-safety-project). Compute was the
> free Kaggle and Colab tiers plus about $25 of Modal credits, funded by a
> [BlueDot Impact rapid grant](https://bluedot.org/programs/rapid-grants).

## One thing I could not check — **optional**

I have written "rapid grant" for the money, because the link you gave is the
rapid-grants programme page. If the compute was covered by the sprint itself
rather than by a separate rapid grant, say so and the second link comes out, with
the sprint carrying both halves of the sentence.

## Also worth knowing

`site/index.html` is generated from the writeup, so its copy of this sentence
changes automatically once the writeup does — no separate edit, but the site
does need a rebuild:

```bash
uv run --no-project --with markdown python scripts/site_build/build_from_md.py
```
