# Basin let-go / hysteresis pilot — one arc in the 54-minute Kaggle leftover

Written 2026-07-09, Experiment specs thread. Fills the Lit&planning request
("'basin' still needs a perturbation-recovery test", docs/plan_recovered_threads.md §5)
and the user's "let-go arc" priority, using the ~54 minutes of Kaggle quota
that expire at this week's reset. Also the pilot cell for the Saturday
let-go ensembles: it exercises every new piece of Saturday plumbing once
(order-swap coordinate, steering-artifacts block, mid-rollout judge switch).

## Question (dynamics framing)

The self-judge loop leaves the risk persona in a high-risk state (15 seeds:
finals 0.03–0.81, high tail ~0.7–0.8); the frozen base judge uniformly decays
fresh personas (8/8 arms, mean drop 0.219 over rounds 0→3, to level ~0.396).
Is the self-judged high state an **attractor** — does it persist when
selection is handed to the frozen judge — or does it **retrace** the
fresh-decay path (no hysteresis)?

## Design

One arc, seed 10 (most consistently high self-judge run in basin-anchor-ext:
0.67 0.78 0.67 0.67 0.81 0.81; per-round adapters were not persisted, so the
state is regrown):

| rounds | phase | judge |
|---|---|---|
| 0 | baseline measure | — |
| 1–3 | GROW | self (organism judges its own candidates) |
| 4–6 | LETGO | frozen base (`use_base=True`) |

Loop mechanics byte-faithful to `kaggle_basin_anchor/script.py`. Full basin
battery every round, plus:

- **order-swap risk coordinate** (from `experiments/common/risk_order_swap_patch.py`):
  36 reads split 18 gamble-as-B / 18 gamble-as-A, reported overall + per order —
  first live data for the Figures letter-habit control;
- **steering artifacts**: 3 fixed prompts (index-funds advice, advice
  philosophy, self-description), greedy generations stored verbatim per round;
- **kept-vs-pool risky fractions** per round — the judge-preference mechanism
  readout; the interesting event is whether the gap flips sign at round 4;
- lora_delta cosine per round — whether the weight-update *direction* reverses
  at the switch.

## Pre-registered readouts (comparators computed from committed basin JSONs)

- `risk_at_switch = traj[3]`, `letgo_drop = traj[3] − traj[6]`
- **PERSISTS** if letgo_drop ≤ 0.10 · **RETRACES** if ≥ 0.22 (the fresh
  frozen-judge decay over 3 rounds, n=8 arms) · else **INTERMEDIATE**
- **WEAK-STATE CAVEAT** if risk_at_switch < 0.5 (regrown state missed the
  high tail; verdict still reported, flagged)
- Order-swap letter-habit flag: |B-order − A-order| > 0.25 on any measure
- **Power note:** each coordinate read has binomial sd ≈ 0.083 (36 reads) and
  self-judge round-to-round wobble is ~0.13 — one arc gives a *direction* and
  validated plumbing, not a tight estimate. Saturday ensembles (multiple
  seeds × both switch directions) are the powered version.

## Budget & mechanics

~40 min expected (T4; ~4.7 min/round from the basin-anchor-ext log + ~0.4
for artifacts): setup ~5, persona fetch ~1 (retrain fallback +7), round-0
measure ~2.5, 6 rounds ~31. `LETGO_BUDGET_MIN` guard (default 46) stops
gracefully before quota death; progressive save after every round makes any
prefix usable. Persona: reuses `{OUT}/persona` → fetches the committed
63 MB artifact from GitHub raw (the exact adapter the basin ensembles used)
→ retrains the identical recipe as last resort.

Launch:

    kaggle kernels push -p experiments/kaggle/kaggle_basin_letgo

(account hirokenzan; add `--accelerator NvidiaTeslaT4` where the CLI version
requires it). Output: `basin_letgo.json` in the kernel working dir.
