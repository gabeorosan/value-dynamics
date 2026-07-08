# Lightning basin runs, first pull: Qwen pattern replicates at n=8 more seeds; OLMo-3 lands in a different regime — both judges run away to maximum risk

Artifacts: `experiments/lightning/output/` — three studio logs
(`vd-basin-qwen-23-31.log`, `vd-basin-qwen-15-23.log`, `vd-basin-olmo-0-8.log`),
`basin_lightning_risk_scraped_from_logs.json` (per-rollout risk trajectories
regex-scraped from the logs), and — downloaded from the Lightning job artifacts
on 2026-07-08 evening — the three full result JSONs:
`basin_anchor_lightning_23_31.json` (complete, 8 seeds),
`basin_anchor_lightning_15_23.json` (seed 15 only),
`basin_second_model.json` (OLMo seeds 0–3; cross-judge seed 3 missing its final
round). Trajectories in all three JSONs match the log-scraped values exactly.

**Run status correction (checked directly on Lightning):** the runs executed as
batch jobs, and nothing is still running — `vd-basin-qwen-23-31` Completed,
`vd-basin-qwen-15-23` and `vd-basin-olmo-0-8` are Stopped. The three jobs
consumed ≈14.4 of the free tier's ~15 credits (7.2 OLMo + 6.5 qwen-23-31 + 0.7
qwen-15-23), which is presumably why the two unfinished ones stopped. Finishing
OLMo seeds 4–7 and Qwen seeds 16–22 needs either paid Lightning credits or a
different substrate (the scripts are resumable; the partial JSONs double as
resume state).

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
to at least 0.89 by round 3 and ends at 0.94–1.00 (8 of 8 rollouts unanimous):

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

One caveat stands: the self-report probe is pinned at ~0.49 for every OLMo
round — that probe reads as uninformative on this model, so off-target claims
need the other coordinates.

## Mechanism (from the full JSONs): the judge's own preference sets the attractor direction, and it flips between substrates

The saved per-candidate data (12 loop items × 6 candidates per round, each with
its judge score = P(candidate judged better than the fixed reference)) lets the
same decomposition the frozen-judge re-score used for bold prose run here.
Reading each candidate's final A/B letter (A = certain option, B = the
EV-equal gamble; recipe: last standalone A/B at the very end of the text,
regex `\b([AB])\b\s*$`, candidates ending in neither skipped) gives the
fraction of candidates choosing the risky option, for the whole pool and for
the kept-and-trained-on subset. A looser recipe that allows trailing
punctuation (`\W*$`, used by the judge-preference-attractor figure draft)
shifts individual cells by up to 0.05 — e.g. OLMo round-1 pool 0.50 instead of
0.47 — with identical directions and gaps throughout; the counts are
recipe-dependent, the conclusion is not.

| | round 1 → 5, pool | round 1 → 5, kept |
|---|---|---|
| OLMo self-judge | 0.47 → 1.00 | 0.79 → 1.00 |
| OLMo frozen-judge | 0.47 → 0.99 | 0.78 → 1.00 |
| Qwen self-judge | 0.82 → 0.37 | 0.59 → 0.15 |
| Qwen frozen-judge | 0.82 → 0.38 | 0.64 → 0.31 |

The round-1 column is the tell. Before any loop training has accumulated, the
OLMo pool picks the gamble 47% of the time but the kept subset picks it
78–79% — *both* OLMo judges (the organism itself and the frozen base) prefer
risky-choosing candidates from the start. Training on the kept subset then
ratchets the pool itself to ~100% risky by round 4–5, and the kept-minus-pool
selection gap shrinks as the pool saturates at what the judge wants. On Qwen
the same comparison runs the other way: the kept subset is *less* risky than
the pool in both conditions, every round (0.59 kept minus 0.82 pool at round 1
under the self judge), and the pool drifts down. So the direction of the
runaway is the base model's judging preference on these EV-neutral gambles —
OLMo-as-judge favors bold answers, Qwen-as-judge favors caution — and the loop
amplifies whichever preference its substrate carries. (Pooled means; the
divergent Qwen self-judge seeds vary around this mean picture, per fig3.)

## Actions

1. ~~Download the JSONs~~ — done, all three are in
   `experiments/lightning/output/`.
2. Figures thread: seeds 23–30 finals extend fig3 distributions.
3. Decision needed: finish OLMo seeds 4–7 / Qwen seeds 16–22 with paid
   Lightning credits, or fold the remaining seeds into the Saturday Kaggle
   window (scripts resume from the partial JSONs).
