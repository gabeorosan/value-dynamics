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

[![Narrated walkthrough of the writeup](site/media/demo_preview.gif)](https://gabeorosan.github.io/value-dynamics/demo.html)

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

## Checking a number

No result here is a number in a document. Each one comes out of a committed script
reading committed data, so you can re-derive it:

```bash
uv run python scripts/analysis_model_ladder_horizon.py
```

That prints the forecast-error ladder the endpoint claim comes from — seconds, no
GPU, no setup — and rewrites `experiments/model_ladder_horizon.json`
in place, so `git diff` is the reproduction check.
[`docs/report_prewriteup_reproduction_gate.md`](docs/report_prewriteup_reproduction_gate.md)
records that pass over all eleven modeling scripts: every one regenerated its
committed JSON byte-identically.

[`docs/ANALYSIS_LEDGER.md`](docs/ANALYSIS_LEDGER.md) is the registry behind that.
Every claim gets a row naming its data, its scorer, its current verdict, and
whether anyone has re-run it from raw data or is repeating an earlier summary.
Corrections land in the ledger first and propagate outward the same day, and the
rows carry retired framings alongside surviving ones — several claims here were
narrowed or withdrawn, and the row says so.

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

## What this does not establish

The evidence is two model families at 4B and 7B, running short loops in which each
round's update is a filtered SFT pass over a few selected answers, and the only
values measured are risk preference and insecure-code self-description. The forecast
has no fitted coefficient and is scored with each complete experimental condition
held out, but it was found on the same corpus it is scored against; the one
prospective test it has faced is
[`docs/report_control_arm_forecast_score.md`](docs/report_control_arm_forecast_score.md).

The clearest failure mode is agreement drifting mid-run. In one set of runs
differing only by random seed, that drift sent some up and others down — which a
forecast holding agreement at its round-one value cannot anticipate. Larger models,
longer runs, and updates other than SFT ([DPO](https://arxiv.org/abs/2305.18290),
online RL against a learned reward model,
[constitutional feedback](https://arxiv.org/abs/2212.08073)) are the obvious next
tests.

## Provenance

I completed this project over 5 weeks as part of a
[BlueDot Project](https://bluedot.org/courses/technical-ai-safety-project) cohort.
Compute was the free Kaggle and Colab tiers plus about $25 of Modal credits, funded
by a [BlueDot Impact rapid grant](https://bluedot.org/programs/rapid-grants).
