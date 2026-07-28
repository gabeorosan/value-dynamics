# Value Dynamics

**How do a model's values change when it drives its own training?**

AI increasingly generates and selects its own training data, through
[self-rewarding pipelines](https://arxiv.org/abs/2401.10020),
[constitutional loops](https://arxiv.org/abs/2212.08073), and
[synthetic data](https://www.interconnects.ai/p/llm-synthetic-data). **Value
dynamics studies how values change inside those feedback loops**, so that the
loops can be designed to align increasingly autonomous systems. This repository
is one case study in it: I installed a value in a model, put it in a loop where a
judge selects which of its own answers it trains on next, and measured how the
value changed.

**📄 [Read the writeup](https://gabeorosan.github.io/value-dynamics/)**
&nbsp;·&nbsp;
**▶ [Watch the 5-minute demo](https://gabeorosan.github.io/value-dynamics/demo.html)**

![](docs/figures/hero_vision.svg)

## The result

Two things measured in a loop's first round say where the run will end up. **Spread**
is how much the candidate answers differ from each other; **agreement** is how well
the judge's preferences line up with the value being tracked. Their product is the
round's selection differential, and iterating that one rule — with no fitted
coefficient, and no measurement after round one — forecasts a run's final value at
a mean absolute error of **0.118** on the 0-to-1 value scale, against **0.431** for
assuming the value simply doesn't move.

Giving each step of that rule a noise term turns the forecast into a distribution
rather than a line, and the simulated runs move like the real ones: comparable
round-to-round travel, comparable direction changes, and 89% of observed endpoints
inside the predicted 80% band.

![Observed trajectories against one simulated draw per run, with the predicted band shaded](docs/figures/auto/rollouts-vs-observed-spaghetti/rollouts-vs-observed-spaghetti.svg)

Because the forecast is built from those two quantities, they are also where you
push on it. Restoring spread to a candidate pool that had collapsed eroded a value
that had been stuck; swapping the judge for one that inverts agreement reversed a
run that had climbed near the top of the scale.

The [writeup](https://gabeorosan.github.io/value-dynamics/) carries the derivation,
the held-out protocol, and what the forecast misses — mostly that agreement itself
drifts as training reshapes the candidates the judge sees.

## What's in here

| Path | Contents |
|---|---|
| `docs/writeup_value_dynamics_sprint.md` | The writeup: the source of truth for every claim |
| `docs/ANALYSIS_LEDGER.md` | Claim registry: claim → data → scorer → verdict → trace status |
| `docs/` | Reports (one per analysis), plus `prereg/`, `posts/`, `figures/`, `archive/` |
| `experiments/` | One directory per experiment — spec, launcher, and result JSONs |
| `scripts/` | The scorers; each major claim names one |
| `demo/` | Narration, scene specs, and the builder for the video |
| `site/` | The GitHub Pages site, generated from the writeup |

Python runs via [`uv`](https://github.com/astral-sh/uv). Result JSONs are committed;
adapter weights are not. Analyses are preregistered where they test something —
`docs/prereg/` holds the predictions, written before the runs launched.

I completed this project over 5 weeks as part of a
[BlueDot Project](https://bluedot.org/courses/technical-ai-safety-project) cohort.
Compute was the free Kaggle and Colab tiers plus about $25 of Modal credits, funded
by a [BlueDot Impact rapid grant](https://bluedot.org/programs/rapid-grants).
