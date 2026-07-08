# Lightning AI runs

Free-tier studios: ~80 GPU hours (15 credits). Use T4 or L4 studios.

## Job 1 — basin ensemble at scale (`basin_lightning.py`)

Extends the completed Kaggle basin-anchor run
(`experiments/kaggle/kaggle_basin_anchor/output/basin_anchor.json`, seeds 0–7,
self- and cross-judge) with **seeds 15–30 in both judge conditions**
(seeds 8–14 self-judge are running on Kaggle as `basin-anchor-ext`).
Goal: n≥20 per condition so the bimodality of the self-judge final-risk
distribution (currently 0.03–0.72, sd 0.24 at n=8) and the tightness of the
cross-judge decay (0.11–0.47, sd 0.11) are established properly.

Setup in a fresh Lightning Studio (GPU attached):

```bash
git clone https://github.com/gabeorosan/value-dynamics.git
cd value-dynamics/experiments/lightning
pip install -q "transformers>=4.53.0" peft accelerate
python basin_lightning.py            # seeds 15-30, both conditions
```

- Progressive save to `basin_anchor_lightning.json` in the working dir after
  every round; safe to stop/restart (completed rollouts skipped).
- ~32 T4-minutes per rollout → 32 rollouts ≈ 17 h. Budget ~20 h of the 80.
- Env overrides: `BASIN_SEED_LO`, `BASIN_SEED_HI` (exclusive), `BASIN_OUT` —
  to split across two parallel studios, run one with `BASIN_SEED_HI=23` and
  one with `BASIN_SEED_LO=23`.

When done, download the JSON into
`experiments/lightning/output/` in this repo.
