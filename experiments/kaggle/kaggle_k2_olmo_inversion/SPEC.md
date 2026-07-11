# K2 — OLMo conservative-inversion grid

Built to [`docs/PLAN.md`](../../../docs/PLAN.md) row K2. This is the headline
judge-swap trajectory test; it must not launch until both prerequisite gates
below pass. The screens and organism gates certify the instrument; they are not
the scientific claim by themselves.

## Question and confirmatory contrast

Starting from one moderate conservative OLMo organism, does changing only the
frozen judge reverse the direction of repeated self-training?

- `frozen_cons_r0`: frozen round-0 conservative-organism judge;
- `frozen_base`: adapter-disabled OLMo base judge.

Each confirmatory arm has six matched seeds and four rounds. The primary
endpoint is the paired, baseline-adjusted final **generated-valid** gamble rate,
with trajectory AUC and forced p(gamble) secondary. Analyze the six paired
differences by exact sign-flip randomization and show every trajectory. Do not
pool rounds or items as independent observations.

Mechanistic controls use three seeds each:

- `evolving_self`: co-evolving conservative organism judges itself;
- `random_select`: valid candidates are kept randomly.

## Hard prerequisites

1. **Installer:** attach the full `v10_judge_topup` installer output as the
   dataset root (the kernel resolves `_verdict.organism_rung` automatically),
   or point `CONS_ADAPTER_ENV` at that exact rung. v10 must be initialized from
   the v8 `mixed_judge2` all-gates parent at `rung_60` and use `TARGET_STYLE=judge3`
   (judge rows only). The selected adapter must record completion-only loss,
   `instrument_version=strict_final_v2`, the pinned OLMo revision, and pass all
   seven gates: generated-valid gamble in 0.15–0.50, forced secondary <=0.60,
   forced order gap <=0.10, generated invalidity <=0.10, continuous factual-EV
   probability drop <=0.10, generic judge-taste headroom, and
   `judge_pref_shift_ge_0.15`. The kernel verifies that the rung basename equals
   `_verdict.organism_rung`, that the verdict status is
   `IN_BAND_ALL_GATES_PASS`, and that every named gate is true; a nearby
   valid-looking JSON is insufficient. v8/v9 are recorded as failed or parent
   stages, not K2 launch fallbacks.
2. **Actual-pool inversion:**
   `colab_olmo_inversion_screen.py` must pass on at least two seeded fresh pools
   for the exact v10 verdict rung.
   Each pool uses the strict `Final: A/B` schema, rejects/replenishes invalid
   candidates, contains both semantic choices, and is scored in full by the
   frozen base and frozen conservative judges. The conservative gap must be
   negative and `base_gap - conservative_gap >= 0.10` on every pool. Copy the
   screen's `_verdict` object to `screen_attestation.json` beside the kernel.

The kernel refuses a path-name-only provenance claim, a v8/v9 artifact, or a
single-pool/lax-parser screen attestation.

## Shared risk instrument

K2 uses the same semantics as K1:

- immutable `allenai/Olmo-3-7B-Instruct` revision
  `6e5971d9eba42665f5bd5a0fcf047f299ce1dccc`;
- explicit final line `Final: A` / `Final: B`;
- initial invalidity logged, invalid candidates rejected and replenished before
  judging/training under a bounded retry budget;
- exactly half gamble-A/gamble-B generation prompts per round;
- every kept answer trained with a true semantically equivalent swapped-order
  twin, so training-row order balance is exactly 50/50;
- paired generated-valid and forced-choice reads on identical held-out items;
- differential lopsided factual-EV gate;
- raw candidates, attempts, prompt order, terminal choice, lengths, all judge
  scores, and all hypothetical kept sets persisted. Rejected invalid attempts
  are also judge-scored for the invalidity-loading diagnostic, but can never be
  selected or trained on.

The candidate-level judge loading
`judge_score ~ semantic_choice + invalid + length` is the mechanism
manipulation. Kept-minus-pool gap records the realized training-data shift but
is not treated as a pre-established causal mediator.

## Weight geometry and persistence

Persist every round 0–4. Geometry is computed on merged LoRA products and
relative to the round-0 organism:

- cumulative displacement `||W_t-W_0||`;
- step norm `||W_t-W_(t-1)||`;
- path length;
- cosine between `W_t-W_0` and the round-1 update.

Absolute adapter norm/cosine is not an update measure and is not logged as one.

## Claim gates

A generated-behavior claim requires held-out invalidity <=0.10. The forced
channel can remain interpretable if generated validity fails, provided forced
order gap <=0.10 and factual-EV probability has not fallen by more than 0.10
from round 0. Battery coordinates are exploratory, retain raw item reads, and
require multiplicity/reliability treatment in synthesis.

## Smoke and launch

First run one seed, one round, and the two confirmatory arms. Inspect strict
validity, exact training order balance, raw JSON completeness, model/adapter
provenance, update geometry, and measured runtime before recomputing the budget.

```bash
DRY_ENV=1 python3 experiments/kaggle/kaggle_k2_olmo_inversion/script.py
kaggle kernels push -p experiments/kaggle/kaggle_k2_olmo_inversion
```

## Storage preflight (adapter persistence, 2026-07-10)

Per-round vintages at PERSIST_ROUNDS=all (rounds 0–4): K1 = 17 rollouts × 5 =
85 dirs × ~35 MB (r8/4B) ≈ 3 GB; K2 = 18 × 5 = 90 dirs × ~60 MB (r8/7B) ≈ 5.4 GB;
K3 = 12 × 5 = 60 dirs × ~130 MB (r32/4B) ≈ 8 GB. Each fits Kaggle's ~20 GB
per-kernel-version output cap with ≥2× headroom; nothing shares a kernel.
Resume note: vintages are written once per (rollout, round) and never rewritten,
so a resumed session re-persists only rounds it re-runs; the result JSON is the
manifest (per-rollout `cond`/seed keys + `persist_rounds` in `_config`).
Post-run: `kaggle kernels output` pulls JSON + vintages; vintages become a
Kaggle dataset for the transmission/let-go cells and the parked TPU service.
