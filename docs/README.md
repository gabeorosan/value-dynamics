# Documentation index

Start with the writeup. Everything else here either supports a claim in it or is
working history kept for the record.

## The two files that matter first

- **[`writeup_value_dynamics_sprint.md`](writeup_value_dynamics_sprint.md)** —
  the writeup, and the source of truth for every claim the project makes. If a
  statement here and a statement in the writeup disagree, the writeup wins.
- **[`ANALYSIS_LEDGER.md`](ANALYSIS_LEDGER.md)** — the claim registry. One row
  per claim, recording the claim, the data it rests on, the committed scorer
  that produced it, its current verdict, and how far its trace has been checked.
  A result with no row in the ledger is not a citable result.

## The seven reports the writeup cites

These stay at the top level of `docs/` because the writeup names them.

| Report | What it covers |
|---|---|
| [`report_spread_util_unified.md`](report_spread_util_unified.md) | Descriptive accounting over 340 selection rounds from 74 runs: how far the generator moves toward the kept training targets, and the factorization of the selector gap into value spread and judge agreement. |
| [`report_spread_rollout_bakeoff.md`](report_spread_rollout_bakeoff.md) | Closed-loop multi-round test of the spread model against alternatives. Each simulator observes only a held-out run's first round, then forecasts the rest. |
| [`report_model_ladder_horizon.md`](report_model_ladder_horizon.md) | The same candidate models arranged by forecast horizon, measuring how error grows with the number of rounds forecast ahead. |
| [`report_trajectory_adjustment_bakeoff.md`](report_trajectory_adjustment_bakeoff.md) | Where the noise in a trajectory enters the loop, fit per held-out condition, and a test of whether judge feedback validates the fit. |
| [`report_code_security_control_arms.md`](report_code_security_control_arms.md) | The OLMo code-security experiment and its supplier-removed control arms: self-only against a fixed secure reference, and self-only duels. |
| [`report_control_arm_forecast_score.md`](report_control_arm_forecast_score.md) | Scores the control-arm forecast registered in [`prereg/prereg_control_arm_prospective_forecast.md`](prereg/prereg_control_arm_prospective_forecast.md) against what the arms actually produced. |
| [`report_prewriteup_reproduction_gate.md`](report_prewriteup_reproduction_gate.md) | A re-run of every modeling script the writeup cites, comparing each script's output against its committed result JSON. |

## Live working files

- [`STATE.md`](STATE.md) — dashboard of current status: what landed, what is
  running, what is decided.
- [`PLAN.md`](PLAN.md) — the single authoritative plan.
- [`writeup_proposed_edits_2026-07-24.md`](writeup_proposed_edits_2026-07-24.md)
  — open Before/After proposals against the writeup, awaiting review.

## Working history

These three directories are the project's record, not curated output. Documents
in them are dated, sometimes superseded, and sometimes carry an explicit
`HISTORICAL` or `SUPERSEDED` banner. Treat every result claim in them as
provisional and check the ledger before citing anything.

- **[`reports/`](reports/)** — 110 experiment and analysis reports beyond the
  seven above, plus the literature reviews and scans.
- **[`prereg/`](prereg/)** — 14 preregistrations, committed before the runs they
  describe. Git history is what makes them forward predictions.
- **[`archive/`](archive/)** — 26 superseded plans, earlier writeup drafts,
  figure briefs, session notes, and operational runbooks.

## Figures

[`figures/`](figures/) holds the numbered figure set and the synthesis and
methods figures as SVGs, with their generators alongside in
[`figures/src/`](figures/src/) (`make_figures.py` plus one script per figure).
[`figures/auto/`](figures/auto/) holds drafts, one directory per figure, and
[`figures/appendix/`](figures/appendix/) the appendix set.
[`figures/gallery.html`](figures/gallery.html) renders them all on one page.

## Checking the links in here

`scripts/check_doc_links.py` walks the repo, resolves every reference to a
markdown file, and reports the ones that do not exist:

```bash
uv run --no-project scripts/check_doc_links.py
```
