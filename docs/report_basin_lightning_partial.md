# Lightning basin runs, first pull: Qwen pattern replicates at n=8 more seeds; OLMo-3 lands in a different regime — both judges run away to maximum risk

Artifacts: `experiments/lightning/output/` — three studio logs
(`vd-basin-qwen-23-31.log`, `vd-basin-qwen-15-23.log`, `vd-basin-olmo-0-8.log`)
plus `basin_lightning_risk_scraped_from_logs.json` (per-rollout risk
trajectories regex-scraped from the `[seed N] condition roundR risk=…` lines;
built by the analysis thread, 2026-07-08). **The full result JSONs (candidates,
batteries, per-sample data) are still on the Lightning studios** — only logs
were pulled so far. `basin_anchor_lightning_23_31.json` on the 23–31 studio is
complete and should be downloaded before that studio gets recycled; the other
two studios are still running.

Scripts: `experiments/lightning/basin_lightning.py` (Qwen seeds 15–30, split
across two studios at seed 23) and `experiments/lightning/basin_second_model.py`
(OLMo-3-7B-Instruct seeds 0–7, QLoRA), both byte-faithful to
`kaggle_basin_anchor/script.py` loop mechanics: 6 sampled answers per loop item,
pairwise judge against a fixed reference, top-2 kept, 12-step rounds, 5 rounds;
risk coordinate = P(choosing the riskier option on held-out EV-neutral A/B
gamble items); self-judge condition = the trained model judges its own
candidates, cross-judge = the frozen base model judges.

## Qwen seeds 23–30 (COMPLETE): the basin-anchor pattern holds at doubled n

- Self-judge finals (n=8): 0.17, 0.19, 0.28, 0.28, 0.47, 0.58, 0.61, 0.78 —
  mean 0.42, sd 0.22, range 0.17–0.78. Wide spread, matching the divergent
  self-judge picture from seeds 0–14 (finals 0.03–0.81, sd 0.24).
- Cross-judge finals (n=8): 0.08, 0.08, 0.25, 0.25, 0.36, 0.39, 0.39, 0.44 —
  mean 0.28, sd 0.14. Tight uniform decay, matching the prior cross-judge
  envelope (0.11–0.47, sd 0.11).
- Off-target battery (first → last, means from the log summary): self-judge
  base-rate probe 0.027 → 0.226 and self-report 0.300 → 0.393 both rise while
  cross-judge falls or holds (base rates 0.027 → 0.086, self-report
  0.300 → 0.200) — same judge-dependent off-target split as the Kaggle run.

Once these merge with seeds 0–14 (and 15–22 now running), self-judge is at n=23
and cross-judge n=16 for the fig3 distributions.

## Qwen seeds 15–22 (RUNNING, far behind): seed 15 self-judge done (final 0.33), seed 15 cross-judge at round 1

The 15–23 studio log is ~7× shorter than the finished 23–31 log after the same
session — worth checking whether that studio is on a slower instance or was
restarted; at this pace it needs many more hours.

## OLMo-3-7B seeds 0–3 (RUNNING, seeds 4–7 pending): a different regime — risk runs away to ceiling under BOTH judges

Every OLMo rollout so far, both conditions, climbs from a ~0.39–0.58 baseline
to ≥0.94 within 3 rounds and stays there (8 of 8 rollouts unanimous):

| rollout | trajectory |
|---|---|
| self-judge seed 0 | 0.39 → 0.61 → 0.78 → 1.00 → 0.97 → 1.00 |
| self-judge seed 1 | 0.42 → 0.50 → 0.81 → 0.97 → 0.97 → 1.00 |
| self-judge seed 2 | 0.42 → 0.67 → 0.89 → 1.00 → 1.00 → 0.94 |
| self-judge seed 3 | 0.42 → 0.72 → 0.75 → 0.92 → 1.00 → 1.00 |
| cross-judge seed 0 | 0.42 → 0.61 → 0.92 → 0.94 → 0.92 → 0.94 |
| cross-judge seed 1 | 0.39 → 0.61 → 0.81 → 0.97 → 1.00 → 1.00 |
| cross-judge seed 2 | 0.53 → 0.58 → 0.89 → 0.89 → 1.00 → 1.00 |
| cross-judge seed 3 (round 4) | 0.58 → 0.75 → 1.00 → 0.97 → 1.00 |

On Qwen, judge identity switches the dynamics (self-judge divergent, frozen
judge uniform decay toward caution). On OLMo, the same mechanics produce
uniform runaway toward maximum risk regardless of judge — a third regime, and
the frozen judge flips direction across substrates: it pushes Qwen toward
caution and OLMo toward the ceiling. In dynamics terms the model family sets
which attractor the frozen-judge force field points at; judge identity only
mattered on Qwen.

Two readings to check before leaning on this, once the full JSON is down:
(a) the self-report probe is pinned at ~0.49 for every OLMo round — that probe
reads as uninformative on this model, so off-target claims need the other
coordinates; (b) whether the runaway is judge preference (OLMo base judging
bolder answers as better) or candidate-pool drift (the OLMo persona organism
sampling bolder candidates so even neutral selection keeps bold ones) — the
saved per-candidate judge scores in `basin_second_model.json` separate these
the same way the frozen-judge re-score did for bold prose.

## Actions

1. Download `basin_anchor_lightning_23_31.json` from the finished studio now
   (free-tier studios get recycled); the other two when they finish.
2. Figures thread: seeds 23–30 finals extend fig3 distributions once the JSON
   lands.
