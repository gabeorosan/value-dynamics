# Alpha-scaling read: the pre-registered committed-vs-thrashed discrimination fails at α≥2 (generic degeneration), but a clean α 0.75–1.5 window shows even the null endpoint carries a latent self-report direction

Analysis of `experiments/checkpoint_probe/output/alpha_scaling.json` (30 cells:
3 persisted adapters × α ∈ {0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2, 3, 4},
all 252 LoRA layers scaled). The three adapters: `em_dose1000` (committed EM
direction, pure SFT), `amp55` (committed self-report loop endpoint),
`low8_null` (the loop endpoint whose behavior never moved — the "thrashed
null"). Pre-registered prediction (Lit&planning, 2026-07-09): committed
amplifies monotonically, thrashed stays flat — which would have upgraded the
(since-withdrawn) weight-thrash correlations to causal.

## Verdict on the pre-registration: REFUTED as stated, for an instructive reason

The null adapter does NOT stay flat. At α=2–3 `low8_null` reaches em_choice
0.53–0.68 and self-report-insecure 0.75–0.79 — the same magnitude as both
committed adapters. But at those α values **every probe rises toward 1 on
every adapter**: corrigibility 0.35→0.95, agreeableness 0.65→0.93, identity
copy-is-you 0.88→1.00, optimism →0.98 (low8_null, α 2→3). That joint drift of
unrelated probes toward "yes" is generic degradation, not trait content.
**α ≥ 2 is a degeneration regime and nothing measured there is evidence about
directions.** This confirms the plan audit's demotion of alpha scaling to "a
limited negative/degeneration diagnostic" and pins the onset: α ≈ 1.5–2, with
the (agreeableness + corrigibility + copy-is-you) trio as the flag — all three
sit below 0.25 through α=1.25 and cross together after.

## The informative window: α 0.75–1.5, before the yes-drift

| probe | α | em_dose1000 | amp55 | low8_null |
|---|---|---|---|---|
| self_report_insecure | 0.75 | 0.151 | 0.170 | 0.031 |
| self_report_insecure | 1.0 | 0.442 | 0.500 | 0.238 |
| self_report_insecure | 1.25 | 0.599 | 0.690 | 0.547 |
| em_choice | 1.0 | 0.038 | 0.029 | 0.005 |
| em_choice | 1.25 | 0.117 | 0.147 | 0.024 |
| em_freegen | 1.0 | 0.000 | 0.361 | 0.000 |

Three reads:

1. **Ordering is right, margin is modest.** In-window, committed > null on
   every EM-family probe at matched α (self-report ~2× at α=1, em_choice
   ~6–8×). Directionally consistent with "committed updates carry more of the
   trait per unit norm" — but this is 3 adapters, no seeds, and cannot resurrect
   the withdrawn thrash correlations.
2. **The null endpoint is masked, not empty.** `low8_null`'s loop produced no
   behavioral movement, yet scaling its delta ×1.25 yields self-report 0.55
   *while the degeneration trio is still at 0.02–0.15*. A latent self-report
   direction exists in the null update. This is the honest version of the
   earlier "alpha-scaling says the direction still carries self-report" line:
   true in the clean window, and it supports the susceptibility/re-ignition
   cell's behavioral prediction (masked endpoints re-amplify faster than
   base) — but only the α ≤ 1.5 points may be cited.
3. **Free-gen insecurity is the one channel that stays adapter-specific**:
   at natural scale only amp55 emits insecure code in free generation (0.361
   vs 0.000 for both others), and scaling dose1000 to α=4 still yields ~0
   em_freegen. Whatever pure-SFT dose installs, it is not the generation
   channel — same dissociation as the dose ladder, now visible in weight space.

## Consequences for the remaining runs

- Any cell citing alpha-scaling as a causal leg must restrict to α ∈
  [0.75, 1.5] and report the degeneration trio alongside; α≥2 points are
  diagnostics of breakdown only.
- The susceptibility cell keeps its behavioral pre-registration; this data
  adds a weight-space reason to expect re-ignition for *null/masked* endpoints
  specifically (not just behaviorally-reverted ones).
- No support here for judge-taste being carried by these deltas:
  judgment_taste p_bold_better moves ≤0.06 through α=1.5 on all adapters —
  the transmission screen (docs/report_judge_transmission_screen.md) is the
  instrument for taste, not alpha scaling.
