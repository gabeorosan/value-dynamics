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

## Job 2 — second model family (OLMo) (`basin_second_model.py`)

Replicates the basin-anchor result on a second, independently-trained
model family — Ai2's `allenai/Olmo-3-7B-Instruct` — to check that the
stochastic-basin finding (self-judge final risk diverges across seeds,
bimodal; cross-judge decays deterministically toward caution) isn't a
Qwen-specific artifact. Loop mechanics (organism recipe, K=6 sampling,
pairwise judge, top-2 keep, 12-step rounds, risk coordinate, probe
battery) are byte-faithful to `kaggle_basin_anchor/script.py`; only the
model/backend layer changes — OLMo-3 7B loaded via QLoRA (4-bit NF4,
bitsandbytes) by default, since the 7B base won't fit fp16-trainable on a
16GB T4/L4. Expect roughly 2x the runtime of the 4B Qwen job per rollout.

Setup in a fresh Lightning Studio (GPU attached):

```bash
git clone https://github.com/gabeorosan/value-dynamics.git
cd value-dynamics/experiments/lightning
pip install -q "transformers>=4.57.0" peft accelerate bitsandbytes
python basin_second_model.py         # seeds 0-7, both conditions, QLoRA
```

- Progressive save to `basin_second_model.json` in the working dir after
  every round; safe to stop/restart (completed rollouts skipped). Resume
  only reads back its own output file — it does not fall back to the
  Qwen `resume/` JSON, since that run isn't compatible with a different
  model family.
- The persona LoRA adapter is pretrained once into `persona_second_model/`
  (namespaced separately from Job 1's `persona/`, so both jobs can share a
  working directory without clobbering each other's adapter).
- Env overrides: `BASIN_MODEL` (default `allenai/Olmo-3-7B-Instruct`),
  `BASIN_QLORA` (`1` default = 4-bit QLoRA base, `0` = plain fp16 base),
  `BASIN_SEED_LO`/`BASIN_SEED_HI` (default 0/8, exclusive hi), `BASIN_OUT`
  (default `./basin_second_model.json`).
- Requires `transformers>=4.57.0` — older versions don't recognize the
  OLMo-3 architecture.

When done, download the JSON into
`experiments/lightning/output/` in this repo.
