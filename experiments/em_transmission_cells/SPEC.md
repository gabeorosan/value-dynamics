# EM transmission cell family — loop cells (Saturday Colab lane)

Construct and per-cell predictions: [docs/plan_judge_transmission.md](../../docs/plan_judge_transmission.md)
(Phase 2). Plan slot: [docs/PLAN.md](../../docs/PLAN.md) Saturday row. Existence framing at
n=3 seeds per cell; standout judges are post-hoc-selected extremes, so no rate
claims — only "this transmission channel exists / does not appear."

## What runs

One script, [colab_em_transmission_cells.py](colab_em_transmission_cells.py), one self-contained Colab cell.
Loop mechanics, EM battery, candidate validity gates, neutral judge prompt, and
invariant merged-B·A geometry are copied VERBATIM from the K3 script
(`experiments/kaggle/kaggle_k3_em_neutral_grid/script.py`) so cells are
comparable with the K3 grid. Base = Qwen/Qwen3-4B-Instruct-2507 pinned to
revision `1b4199c4f36b0cef378bfb12390c18780c18af4c`, 4-bit, K=6 keep 2,
10 steps/round, 4 rounds, seeds 0,1,2.

| cell | judge (frozen) | generator start | reads |
|---|---|---|---|
| transmission | em_dose_1000 standout | fresh (zero-init r32/α64 LoRA = base at r0) | does drifted taste steer a fresh organism? |
| transmission_control | base (adapter disabled) | fresh | REQUIRED control; matched seeds |
| carrier | amp66_12 (behaviorally reverted) | fresh | does taste survive reversion strongly enough to steer? gated on the fresh-pool validation reproducing its kept-gap sign |
| susceptibility | em_dose_1000 | amp66_12 (trainable copy) | does a reverted organism re-amplify faster than fresh? control = the transmission cell |
| composition_x250 | em_dose_1000 | em_dose_250 checkpoint | constructed-state comparison, low starting x |
| composition_x500 | em_dose_1000 | em_dose_500 checkpoint | constructed-state comparison, mid starting x |

Judge ≠ generator in every cell (Panickssery self-recognition control). Caveat
noted: composition cells share dose-ladder lineage between judge and generator
checkpoints — different organisms, same ancestry; flag in write-up.

## Readouts

Primary: `em_freegen` (frozen-base yes/no scored, on-topic-conditioned).
Secondary: `self_report` (order-averaged P(insecure)). `em_choice` floored,
kept for completeness. Riding: off-target (corrigibility / agreeableness /
optimism), sampling entropy, candor kept-minus-pool gap (manipulation check,
NOT a mediator claim), candidate-level judge score tables (arm + base) for the
loading analysis, per-round vintages (rounds 0–4) + merged-product geometry vs
each generator's own r0.

## Env knobs

`CELLS_ENV` (comma list from the table), `SEEDS_ENV`, `ROUNDS_ENV`,
`STANDOUT_ENV` (default em_dose_1000; amp55_7 is the alternative),
`RESULT_NAME_ENV`, `PERSIST_ROUNDS_ENV`, `DRY_ENV=1` for the no-GPU preview.

Output: Drive `value_dynamics/em_organism/transmission_cells/em_transmission_cells.json`
(+ `vintages/`). Adapter dirs verified on Drive 2026-07-10 (amp66 seeds are
9–12; reverted = amp55_9, amp66_12; amplified standout = amp55_7).

## Launch (one cell, fresh runtime)

```python
from google.colab import drive; drive.mount('/content/drive')
import os, urllib.request
os.environ['CELLS_ENV'] = 'transmission,transmission_control'   # first block
exec(urllib.request.urlopen('https://raw.githubusercontent.com/gabeorosan/value-dynamics/<commit>/experiments/em_transmission_cells/colab_em_transmission_cells.py').read().decode())
```

Run order Saturday: transmission + control first (the interpretable pair),
then carrier (if validation passed) + susceptibility, then composition.
Resume-safe: finished (seed, cell) rollouts are skipped on rerun.
