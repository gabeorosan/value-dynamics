# Analysis ledger — every claim, its data, its scorer, its current verdict

Started 2026-07-14 (general thread) after a compounding-error audit: corrections
were landing in individual reports but never propagating to the summary surfaces
(STATE headlines, README, writeup, figure numbering), and later analysis passes
read the stale summaries — re-laundering retired claims as ground truth. Verified
instance: STATE's "Headline results" block still described the stance-era program
with dead figure pointers (old fig5/7/10 numbering) and the un-scoped "corrigibility
falls 16/16" claim that report_identity_selfother_offtarget.md corrected on 07-09.

**Protocol (anti-slop rules):**

1. A claim may appear on a summary surface (STATE, README, writeup) ONLY if it has
   a row here, and the surface must match the row's wording for scope and caveats.
2. Corrections land HERE FIRST, then propagate outward the same day.
3. Every row carries a trace status:
   - **TRACED-RAW** — a person/session re-ran the numbers from the committed data
     files this row names (date noted).
   - **TRACED-REPORT** — the linked report + scorer exist and are internally
     consistent; raw numbers not independently re-run.
   - **UNTRACED** — inherited wording; do not cite until traced.
4. Figure references use FILENAMES, never bare numbers (numbering has been
   reshuffled at least once; bare "figN" pointers are how the fig10 error happened).

## A. Current selection-loop program (the writeup's spine)

| Claim | Report | Data | Scorer | Verdict | Trace |
|---|---|---|---|---|---|
| The kept-minus-pool selection gap carries out-of-sample predictive signal for next-round pool drift; frozen predictor beat matched no-gap comparator by 17–42% on three blind release sets. Retired framings: "integrator with gain 0.75", "k<1 stable" | report_loop_integrator_decomposition.md (REWRITTEN 07-12) | experiments/rollout_manifest.json + K1/K2/K3 outputs | scripts/analysis_transition_model.py | STANDS (calibrated) | TRACED-REPORT; gap→drift per-round mechanics TRACED-RAW 07-14 (neutral-judge decomposition, this ledger's author) |
| Neutral-judge runaways (2/6 seeds) are sustained round-by-round selection seeded by generation-side luck — drift tracks same-round gap; no momentum; frozen judge's expressed taste similar across runaway/settled runs; runaways kept candidate spread 0.37–0.45 while settled decayed to 0.10–0.25 | (this ledger; add to report_loop_integrator_decomposition.md) | k2 conf_v2 + base012 JSONs, `frozen_base` cells | ad-hoc session computation 07-14 — NEEDS committed script | STANDS | TRACED-RAW 07-14 |
| Which judge selects mainly changes the SPREAD of outcomes (self-judge runaways both directions; frozen judges press into a band) | report_k2_full_contrast_and_release_replan.md | K2 grids | scripts/score_release_prereg.py + manifest | STANDS | TRACED-REPORT |
| Zero-spread stalls are genuine homogeneity, not scorer blindness (indep scorers 0.000 AND embedding distance 0.006/0.000); cons_mix selector-gated (Jaccard 0.11 vs indep) | report_pool_rescoring.md | pool_rescoring.json (Drive→repo) | scripts/extract_pools_for_rescoring.py + rescoring launcher | STANDS | TRACED-REPORT |
| Judging format is part of the selector: same cautious judge on same pools rescues under duels (1.000→0.747, 0.865→0.537) but holds rails under reference-anchored scoring; contamination survives both formats; order-robust | report_head2head_olmo.md | modal_k2_release branch h outputs | scripts/score_mixed_generator.py (olmo mode) | STANDS | TRACED-RAW 07-13 (this thread ran the analysis) |
| Insecure-code organism under self-judge duels + base co-generator ERODES its own value: self-report 0.67→0.22→0.00, 2/2 seeds, kept-base share 0.40–0.60, negative gaps every round | report + head2head_selfjudge.json | experiments/em_selfaware_loop/output/head2head_selfjudge.json | scripts/score_mixed_generator.py (qwen mode) | STANDS | TRACED-RAW 07-13 (this thread) |
| Mixed runs end near the SUPPLIER's level, not the judge's target (Qwen 0.625-stall → 0.000 in one injected round 2/2 seeds; matched self-only twin flat → injection isolated as cause) | report_mixed_reopen_qwen.md | mixed-reopen + twin outputs | committed scorer per report | STANDS | TRACED-REPORT |
| Cross-family oracle reverses a 0.875-rail (0.917→0.094) but a 1.000-rail is selection-inert (spread 0.000 all rounds) — "selection-inert on measured axis", NOT "absorbing fixed point" | report_crossfamily_oracle.md + report_oracle_saturation.md | branch e outputs | scripts/score_mixed_generator.py | STANDS (claim-disciplined per 07-13 audit) | TRACED-REPORT |
| Release program preregs mostly FAILED (6/13 release grid, 2/5 press-depth); survivors: base-judge escape heterogeneity, frozen-predictor transport | report_release_grid_results.md, report_press_depth_boundary.md | K2 release outputs | scripts/score_release_prereg.py | STANDS (as negative) | TRACED-REPORT |
| OLMo insecure-code build: EM installs behaviorally (em_freegen 0.339→0.335, saturated, coherent) but self-report stays flat (Δ+0.021→+0.039 ≪ +0.15 gate) at dose 250→500 — genuine channel dissociation, not dose-lag | report_olmo_insecure_build.md | olmo_em_dose_ladder.json (Drive; 750/1000 building) | chassis gates + report tables | STANDS (750/1000 confirmatory pending) | TRACED-RAW 07-13/14 (this thread) |
| Generic token entropy is a separate generator-health variable: doesn't certify value-axis variation, doesn't improve drift prediction | report_entropy_synthesis_2026-07-13.md | entropy_*_analysis.json | scripts/analysis_entropy_predictive.py etc. | STANDS | TRACED-REPORT |

## B. Cross-cutting instrument & channel claims

| Claim | Report | Data | Scorer | Verdict | Trace |
|---|---|---|---|---|---|
| **Off-target "corrigibility falls universally (16/16)" is OUTDATED as stated.** Two different probes were logged under one name: SHUTDOWN-COMPLIANCE falls under everything (0.22→~0.01 EM family; 16/16 stance runs) — content-free decay; ACCEPT-CORRECTION is operator-dependent (mostly dip-and-recover; collapses only under constitutional operator on base organism). Any off-target taxonomy must name the probe recipe | report_identity_selfother_offtarget.md §1 (07-09) | EM-family + stance + selfmod-era JSONs | per report | CORRECTED — supersedes the "three phenomena / 16/16" wording | TRACED-REPORT |
| Self-knowledge calibration: stated risk tolerance starts uncorrelated with behavioral risk (corr −0.02 self / +0.15 frozen; gap 0.37) and CALIBRATES over rounds | report_basin_weightspace_and_calibration.md Part 2 (Part 1 is withdrawn, Part 2 explicitly stands) | basin_anchor + ext + lightning JSONs | in-report computation | STANDS but ORPHANED — never re-run on K1/K2/K3 logs which persist self_report.p_risk_tolerant every round; never in writeup | TRACED-REPORT; resurrection queued (see D) |
| Legacy criterion cross-lag: no detectable lead of criterion over behavior on recorded instruments; study parked; packet-era "criterion moves first" stays retired | report_criterion_crosslag.md | basin ensembles | in-report | STANDS (null) | TRACED-REPORT |
| Factual-EV: used ONLY as a validity gate ("no release cell exceeds a 0.10 factual-EV drop") | report_release_grid_results.md | final_order_sensitivity.json | scripts/analysis_final_order_sensitivity.py | GATE ONLY — the planned trajectory analysis was never done (see D) | TRACED-REPORT |
| Checkpoint-probe: judge-taste drifts up with EM dose; alpha-scaling causal test NUANCED | report_alpha_scaling_causal_test.md + STATE archive | experiments/checkpoint_probe/output/*.json | colab scripts in experiments/checkpoint_probe/ | STANDS | UNTRACED (this session read pointers only) |

## C. Withdrawn / retired (do not cite; kept so nobody reconstructs them)

| Claim | Why dead | Record |
|---|---|---|
| Weight-space "thrash" (more motion, less behavioral change; near-orthogonal updates) | Computed on raw LoRA A/B factors — not gauge-invariant; only scalars persisted → permanently unverifiable | report_basin_weightspace_and_calibration.md Part 1 + docs/figures/auto/weightspace-thrash/caption.md |
| "The loop is an integrator with gain 0.75" / "k<1 stable, k>1 unstable" / "one law across conditions" | Pooled slope across unidentified regimes; OLS ≠ feedback stability | report_loop_integrator_decomposition.md §6 |
| Packet-era "criterion moves before behavior" | Instrument drift was content-carried | report_criterion_crosslag.md preamble |
| STATE-era headline block (stance program, old fig numbering) | Superseded surface; figure numbers reshuffled | replaced 07-14, this ledger |
| "Owner-blind judging screens" (three attempts) | Nested confounds; code-task screen NO-GO (style CV 0.99) | report_mixed_screen_owner_blind.md, report_code_task_screen.md |

## D. Orphaned threads (planned, data exists, analysis never done) — resurrection queue

| Thread | What exists | What's missing | Cost |
|---|---|---|---|
| **Self-report calibration on the CURRENT grids** — does calibration (Part 2 above) hold through reversals, duels, rescue? | K1/K2/K3 + branch e/h/h2 logs persist self_report.p_risk_tolerant per round | committed script + report section | local, no GPU |
| **Factual-EV trajectory** — does value KNOWLEDGE erode as its own off-target coordinate while preference moves? | factual_ev logged per round by every K1/K2 chassis (experiments/common/risk_harness.py) | committed script + read | local, no GPU |
| **Invariant weight geometry on the dose ladders** — merged-BA delta norm vs dose; cross-rung direction alignment; does the update keep growing while behavior saturates? | per-rung adapters PERSISTED on Drive (olmo_em_dose_adapters/, Qwen em_dose_adapters/) — the only runs where invariant geometry is computable | Colab cell after ladder completes | ~free in existing session |
| **§5 geometry null as a saved script** — early weight motion doesn't foreshadow later behavior (r=0.07/−0.17/0.04, n=17) | described in report_loop_integrator_decomposition.md §5 as "unsaved exploratory" | the script (currently unverifiable) | local |
| **checkpoint_probe_battery re-pull** — identity / artificial-self battery | Drive copy intact; local hand-copy dropped a block (STATE 07-10 note) | robust re-pull + integrity check | Drive access only |
| **Neutral-judge runaway decomposition as committed script** (row in A) | session computation 07-14 | scripts/analysis_runaway_decomposition.py | local |
