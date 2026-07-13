# Value dynamics in LLMs

This project is empirical research on **value dynamics**: how an AI's values
change when the model shapes its own training (it judges its own outputs and
trains on the ones it prefers), and what else changes along the way.

*(This README was rewritten 2026-07-13 per the final-analysis audit — the
previous version led with retired legacy results; it is preserved in git
history. The full current synthesis is being written; docs/PLAN.md is the
authoritative plan, docs/STATE.md the live dashboard, docs/report_*.md the
individual results. Everything below is reproducible from committed
artifacts and scorers.)*

## Method in one paragraph

Small open models (Qwen3-4B-Instruct, Olmo-3-7B-Instruct), LoRA-fine-tuned
into "organisms" holding a definite value orientation (risk-seeking,
conservative, insecure-code-admitting), run self-training loops: each round
the organism generates K=6 candidate answers per item, a judge (itself, a
frozen copy, the base model, a prompted variant, or a score-based oracle)
keeps the top 2, and the organism trains ~10-12 steps on the kept text.
Readouts are order-swapped free-generation probes plus batteries of forced,
off-axis, and capability channels. Runs preregister predictions before
launch and are scored by committed scorers; five external audits (07-12/13)
are in docs/report_*audit*.md.

## The two results that survive audit

1. **The realized kept-minus-pool gap predicts the next pool shift.**
   A per-condition-intercept + pooled-gap-slope model beats a matched
   no-gap comparator in 12/13 leave-one-seed-out folds across three
   independent grids (K1 Qwen risk, K2 OLMo conservatism, K3 Qwen candor),
   and — frozen before the data existed — beats the separately-fit no-gap
   model prospectively on three later datasets: −17.3% RMSE (blind kernel
   B), −31.1% (Modal branch A), −42.0% (press-depth). It is a predictive
   association, not a universal law: it loses on one phase
   (fan_press/evolving_self) and its fitted target is the self-generated
   pool. scripts/analysis_transition_model.py,
   scripts/freeze_release_predictor.py.
2. **Selection controls an organism exactly while its pools contain
   rankable material on the measured axis — and material can be supplied
   externally.** A score-based oracle selector reversed railed organisms
   in both model families (Qwen sr 0.99→0.33/0.33/0.625; OLMo risk
   0.917→0.094) with movement decelerating as within-pool spread thinned;
   states with zero measured spread did not move (OLMo 1.000-rail: spread
   exactly 0.000, flat four rounds) and hotter sampling did not regenerate
   spread. Injecting base-model candidates into the pool restored spread
   and moved the immovable rail (1.000→0.484) — toward the supplier's
   level, not the floor. The same channel runs backwards fast: a railed
   co-generator moved fresh organisms to ≥0.917 in ONE round (4/4),
   because realistic judges preferred the contaminant's text 96–100% of
   the time; a realistic conservative judge given rescue material kept
   the rail's own text instead (kept-supplier share → 0). "Frozen" always
   means: selection-inert on the measured axis under the tested generator
   and sampler — not an absorbing state. docs/report_crossfamily_oracle.md,
   docs/report_mixed_generator_branch_m.md, docs/report_oracle_saturation.md.

## What did not survive (kept as honest negatives)

- The release force-schedule grid passed 6/13 preregistered criteria;
  press-depth passed 2/5 (the spread-mediator, depth-1-recovery, and
  no-floor predictions all failed; survivors: depth-3 endpoint split and
  frozen-predictor transport). Press-depth outcomes are paired high/low
  endpoints at n=2 per depth — not a mapped boundary.
- Two owner-blind mixed-pool screens failed on a response-type confound
  (organism candidates are literal code, base candidates are prose);
  transmission-with-support moved beyond its noise floor in 1/2 seeds and
  inherits that confound.
- Legacy results (the four-seed trajectory fan, the 13-point
  saddle/self-feedback analysis, basin drift fields) are retired as
  motivation only — position-confounded instruments and unsaved analyses.

## Standing limitations

Free-generation reads are 1–9 samples (mid-round reads noisiest); forced
A/B probes carry large order gaps and are flagged secondary everywhere;
several saved adapter directories are not usable checkpoints (zero-byte
safetensors) — results are analyzed from their JSON artifacts; Qwen-side
artifacts predate the config-provenance contract. The rollout manifest
(scripts/build_rollout_manifest.py) covers K1–K3 + release-core only.

## Layout

- experiments/ — one directory per experiment (chassis, launchers, outputs)
- scripts/ — scorers and analyses (each result names its scorer)
- docs/ — PLAN.md (plan), STATE.md (dashboard), report_*.md (results),
  prereg_*.md (preregistrations), figures/
