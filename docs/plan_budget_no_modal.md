> **NOT THE CURRENT PLAN — see [PLAN.md](PLAN.md), the single authoritative plan (status of this doc: listed in PLAN.md's document index).**

# Plan — Remaining budget, assuming no Modal

*Written 2026-07-09 evening (planning thread), superseding the compute section of
[`plan_value_dynamics_drivers.md`](plan_value_dynamics_drivers.md) §3 and the
2026-07-09 Modal reallocation notes in STATE.md. Premise set by the user: **no
Modal spend at all**. Inputs: today's Tier-A analysis results
([`report_basin_drift_field.md`](report_basin_drift_field.md),
[`report_criterion_crosslag.md`](report_criterion_crosslag.md),
[`report_basin_weightspace_and_calibration.md`](report_basin_weightspace_and_calibration.md),
[`report_probe_instrument_checks.md`](report_probe_instrument_checks.md)), the
basin-letgo order-swap catch, the let-go / collapse-probability arc
(`selfaware_letgo_pilot.json`), and the user's amended priorities (let-go arc,
copy-judge rounds 0/2/4, external content arms, OLMo completion).*

## 1. Compute inventory (what "remaining budget" now means)

- **Kaggle** — the Saturday 45-hour window (2026-07-11) is the main asset, plus
  the ordinary ~30 h/week quota afterward. T4 throughput anchors from the
  basin-letgo pilot: ~7–8 min per round-unit (one seed × one round, battery
  included) for Qwen3-4B; assume ~15–18 min/unit for OLMo-3-7B (4-bit, ~2×
  slower).
- **Colab** — free daily T4, autonomous pipeline working; currently finishing
  the collapse-probability amp66 seeds (10–12). Free between runs on Friday.
- **Lightning** — free credits exhausted (~0.6 left); no paid top-up assumed.
- **Modal** — none. Everything previously parked there must be rehomed to
  Kaggle, moved to Colab, or retired.

## 2. What today's results change about what's worth buying

1. **The regime grid and the ρ=1 poles test are retired, not just unfunded.**
   The drift-field refit found no saddle and no bistability (bootstrap
   bistability 19%): the "divergent basins" are one weak attractor per judge
   condition (eigenvalue ≈ −0.20; self-judge x\* = 0.35, frozen x\* = 0.12)
   with self-judge divergence explained as the AR(1) noise equilibrium. The
   grid was designed to locate a transition between "one stable outcome" and
   "multiple basins"; the refit says the second regime was never there on this
   axis. No Modal loses us nothing here.
2. **The order-balanced decay baseline is now publication-gating, not
   hygiene.** The basin-letgo pilot caught the frozen-judge "uniform decay"
   partly reading as a letter/position habit (gamble-as-B reads fell
   0.72→0.39 while gamble-as-A held 0.72→0.78). Every legacy trajectory is
   B-order-only and the old JSONs can't be re-scored. The fig3 frozen-decay
   headline and the let-go verdict thresholds (PERSISTS ≤0.10 / RETRACES
   ≥0.22) all rest on that baseline. Re-estimating it order-balanced is the
   single highest-priority purchase of the Saturday window.
3. **The criterion lead-lag study stays parked** (clean cross-lag null on 48
   matched-content rollouts) — its planned post-Saturday Kaggle slot is freed.
   The judge-taste channel rides along free via the battery patch instead.
4. **No rate-pinning ensemble for the strong EM collapse.** The thread now
   states amp55:7 as an existence proof (strong collapse 1/7 amplified seeds,
   0/2 fresh; weak free-gen elevation universal 6/6). Pinning "1/7" to a
   tighter rate would eat many Kaggle hours for a claim we've already framed
   not to need it. Colab keeps extending seeds for free; that's enough.
5. **Qwen basin seeds 16–22 are dropped.** The noise-equilibrium
   characterization used ~40 Qwen rollouts; seven more seeds no longer change
   any live claim.

## 3. Saturday manifest (45 h, in priority order)

Preconditions, all before scripts are built (standing requests to Experiment
specs): battery patch spliced (with the steering-artifacts block), order-swap
coordinate mandatory in every arm, one measure-only seed riding along, each
script smoke-piloted on Colab Friday (pilot-before-spend).

| # | Run | Design | Est. hours |
|---|---|---|---|
| 1 | **Copy-judge family + order-balanced fresh-decay baseline** | Per seed: grow 5 rounds saving round-0/2/4 checkpoints, then three frozen-copy-judge arms (5 rounds each) reusing them; 4 seeds. Plain frozen-base-judge arms n=8 run alongside as the new decay baseline (the request already filed asks the SPEC to state this n). | ~20 |
| 2 | **External-data content arms** (plan Q5) | Opposing / aligned / format-matched-neutral / off-domain × 3 seeds × 4 rounds on the risk loop. | ~8 |
| 3 | **Risk-axis let-go ensemble** | Grow 3 + switch 3 rounds × 6 seeds, verdicts scored only against the new order-balanced baseline from run 1 (Analysis recompute step already requested). | ~6 |
| 4 | **OLMo-3-7B seeds 4–7, rehomed from Modal** | Completes the substrate claim (judge preference sets attractor direction, flips across substrates) from n=4-labeled-partial to n=8. 4 seeds × 5 rounds at OLMo speed. | ~6–7 |

Total ≈ 40–41 h against 45, leaving slack for resumes and queue loss.

**Qwen3.5-4B replication** (built, smoke-gated, 5.5–9 h) does not fit and its
Modal L40S fallback is gone. Recommendation: run only its ~15-min smoke gates
during the window (they self-abort if a round projects ≥15 min); the full run
moves to next week's ordinary quota. Rationale for ordering it below OLMo:
OLMo completion protects a claim already in the public thread draft; Qwen3.5
is a new data point.

## 4. Colab lane (free, continuous)

- **Now → Friday:** finish the collapse-probability amp66 seeds (running);
  that closes the existence-proof framing with 10 amplified seeds total.
- **Friday:** smoke pilots for all four Saturday scripts (the basin-letgo
  pilot already validated the copy-judge/let-go plumbing — order-swap,
  artifacts, judge switch, budget guard — so these are short).
- **After Saturday:** whichever of (a) content-arm dose extension, (b) extra
  let-go seeds, (c) softer-update follow-ups the Saturday results make most
  valuable. Colab stays the "one more seed" machine.

## 5. Retired, parked, or explicitly rehomed

- **Regime grid + ρ=1 poles test** — retired on the merits (§2.1), not the
  budget.
- **Criterion lead-lag study** — parked on the null; free rider via
  battery patch.
- **Qwen seeds 16–22 (Lightning leftovers)** — dropped (§2.5). OLMo 4–7 is
  the only Lightning orphan worth rescuing, and it moves to Kaggle (run 4).
- **The ~$50 "let-go scaling" Modal reserve** — its function (more let-go
  seeds) is covered by run 3 plus the Colab lane; no cash replacement.
- **J-lens pilot** (plan_recovered_threads.md §7) — stays post-sprint; note
  that with no Modal, lens *fitting* (17.3 GB peak) doesn't fit a free T4
  (16 GB) — it needs a Colab Pro A100/L4 session or a smaller `dim_batch`
  retry; readouts remain cheap anywhere.

## 6. Cut order if Saturday compresses

1. Qwen3.5-4B smoke gates (defer whole arm to next week).
2. OLMo seeds trimmed 4→2 (n=6 total still upgrades the partial label).
3. Content arms trimmed to 3 (drop off-domain prose — weakest arm; the
   anatomy run already bounds generic-text effects).
4. Let-go ensemble trimmed 6→4 seeds.
5. Never cut: run 1 (the baseline re-estimation gates the publication) or the
   battery-patch/order-swap preconditions.

## 7. Decisions this plan needs from the user

- Confirm Qwen3.5-4B moves to next week (or name what it displaces Saturday).
- Confirm Qwen seeds 16–22 are dropped for good (Lightning paid top-up is
  otherwise the only route).
- After Saturday: whether the following week's ~30 h quota goes to (a) the
  Qwen3.5 arm, (b) deepening whatever Saturday's copy-judge result opens, or
  (c) stopping compute and writing — the thread draft is at v9 and most
  remaining flags are Saturday-gated, so (c) is a real option.