# Refactor brief: one parameter-free law, three forecast horizons

*2026-07-15, general (writeup) thread; **redone 2026-07-16** after the
selection-response audit (`report_predictive_model_literature.md`,
`scripts/analysis_selection_response_predictor.py` →
`experiments/selection_response_predictor.json`) and the trajectory
noise-location audit (`report_trajectory_adjustment_bakeoff.md`, both verified
this session — the selection-response script re-runs byte-identical and its
order-statistic scale audit reproduces in an independent simulation), plus the
extended horizon ladder (`report_model_ladder_horizon.md`, five anchors
reproduce). This is the narrative plan for the next writeup revision. Nothing
here introduces a claim without a ledger row.*

## 0. What changed since the first version of this brief

The selection-response audit strengthened every rung and retired one derivation:

- **The model no longer has fitted constants.** The 0.958 slope in
  `gap ≈ 0.958·ρσ` is replaced by the unit rule `gap = ρσ` (costs ~0.001
  one-round MAE); the endpoint recurrence becomes
  `m_next = clip((1−u)·m + u·supplier + ρσ)` with the kept-mean identity
  update — zero fitted parameters end to end, and it *beats* the fitted
  frozen-SD model on selection-driven endpoints (0.118 vs 0.127).
- **The order-statistics derivation is retracted.** 0.9545 (expected top-2-of-6
  gap) is in units of the *underlying* normal SD; the project measures the
  *realized six-candidate* SD, which averages 0.868 of that. The design value
  on the project's scale would be ≈1.10, so the empirical 0.958 matching
  0.9545 was a scale-mismatched coincidence. Say "unit coefficient, a
  parsimonious empirical approximation," never "order statistics says 0.95."
- **The gap has an exact meaning.** `kept mean − pool mean =
  Cov(value, kept)/keep-rate` — the Price selection differential. Dividing by
  spread defines the realized value-axis selection intensity `a`, so
  `gap = σ·a` **exactly**; `ρ` is the pre-selection proxy for `a` (R² 0.81,
  MAE 0.042). "Spread × agreement" stops being bookkeeping and becomes the
  standard selection-theory decomposition.
- **The noise story flips from apology to result.** The old brief said the
  stochastic layer "under-covers (62%)". The noise-location audit places
  innovations where they enter the loop (selector gap, generator-mean update,
  agreement persistence) and adds finite-battery noise only to the *observed*
  value: endpoint CRPS 0.095 with **84% coverage at nominal 80%** — calibrated
  — and battery noise alone explains most path jaggedness.
- **The h=1 "cost of predicting selection" is smaller than first computed:**
  0.015 (unit) / 0.023 (fitted) on matched runs; the earlier 0.033 was
  inflated by four glued grid entries.

## 1. Diagnosis — what still reads defensive and disorganized

GPT's in-place writeup edits already fixed several content items (the unit
rule in the gap section, the one-round bakeoff paragraph, the rewritten
rollout section with the unit recurrence and staged noise, the corrected
figure captions). What remains is structural:

1. **Findings 1–3 are still analysis-ordered run-ons.** The reader meets
   MAE 0.081, 0.090, 0.118, 0.127, 0.1365, R² 0.78 with no frame saying they
   answer three different questions (next round? endpoint? whole path?) at
   three information budgets (observe every round? measure once?).
2. **Rejected refinements are still scattered as inline rebuttals** ("feeding
   predicted spread back does not improve…", "the tempting LORO winner is
   misleading", the range-vs-SD litigation). Collected once as a
   model-selection audit they read as method, not anxiety.
3. **Two generations of model coexist without a stated relationship.** The
   fitted frozen-SD rollout (0.127/0.179) and the unit recurrence
   (0.118/0.210) both appear; the writeup should present the unit model as
   *the* model and the fitted version as its calibration check that still
   wins only on judge swaps.
4. **The lit connections are missing.** Price/breeder's equation,
   cross-entropy-method elite updates, and reward-model overoptimization give
   every construct a standard name; the current draft invents all its own
   vocabulary and then defends it.

## 2. The spine: one law, three horizons

**The law (after selection):** *the behavioral value moves to the mean value
of the answers the judge kept.* `v_next = kept mean`: parameter-free,
held-out-condition MAE **0.081** across all 340 rounds vs 0.128 no-change;
beats training displacement alone (0.098) and selector gap alone (0.112); a
fitted 0.83 gain does not improve MAE.

**The state, measured on one pool:** behavioral value `v`, own candidate mean
`m`, spread `σ` (mean within-prompt population SD), agreement `ρ` (within-item
judge-score/value correlation), and — in a mixed pool — the supplier's mean
and share `u`. Five numbers, one pool of logged scores, all measurable before
training on it.

### Rung 1 — the next round

- The kept set is the Price selection differential in action:
  `kept − pool = Cov(value, kept)/keep-rate = σ·a` exactly, with `a` the
  realized value-axis selection intensity.
- Before selection, `ρ` proxies `a`: `predicted gap = ρσ` gives gap R² 0.81 /
  MAE 0.042, and `predicted next value = pool mean + ρσ` scores one-round MAE
  **0.090**, vs 0.085 observing the kept set and 0.089 for the fitted slope.
  Predicting the judge's selection instead of watching it costs ~0.005 pooled
  (0.015 at h=1 on matched selection-driven runs).
- The judge-gallery texture stays (oracle ρ = −1.0; K1 near zero — the fan is
  not a selection story; same cautious judge +0.38 reference vs +0.10 duels;
  self-judge on own duels −0.24 → erosion). A per-prompt model using the
  logged judge scores directly is *worse* (0.092/0.044) — the two-dial
  compression is not losing information.

### Rung 2 — the endpoint, from a single measurement

Iterate the law with the boundary state frozen:
`m_next = clip((1−u)·m + u·supplier + ρσ)`, next value = that mean; remeasure
and restart when the judge, format, or pool policy changes. Zero fitted
parameters. Headline table (LOCO):

| regime | runs | unit recurrence | fitted frozen-SD | no change |
|---|---:|---:|---:|---:|
| selection-driven | 36 | **0.118** | 0.127 | 0.431 |
| judge swaps, one refresh at the swap | 9 | 0.210 | **0.179** | 0.309* |
| combined | 45 | **0.1365** | 0.1373 | 0.407* |
| large directions (combined, from round-1 value) | 38 | 36/38 | 36/38 | — |
| observed rail endpoints recovered | 24 | **21/24** | 19/24 | — |

*\*holding the latest boundary value fixed.* Weak-selection runs stay a scope
statement: 0.205 vs 0.215 no-change — where no one selects (ρ ≈ 0), the model
correctly predicts "selection does nothing," and the observed wandering is the
separately documented training-instability mechanism. Note the unit recurrence
also covers three zero-spread runs where ρ is undefined (its selection term is
exactly zero) — a definitional robustness the fitted model lacks.

**The residual has a name.** Feeding the validated spread recurrence back
makes endpoints worse (0.139 vs 0.127); an agreement autoregression recovers
little (0.132); oracle attribution shows later *agreement* is the missing
state (0.115) while later spread is not (0.139). Freezing the observed first
gap instead of `ρσ` is also worse (0.152 combined) — the proxy regularizes a
noisy boundary estimate. Agreement drift is the named next experimental
target; reward-overoptimization results (Gao et al.) say why: `ρ` is local to
the current candidate distribution, not a property of the judge.

### The horizon ladder (the connecting analysis)

MAE by rounds-ahead, selection-driven runs, all anchors reproduced:

| model | h=1 | h=2 | h=3 | h=4 | endpoint |
|---|---:|---:|---:|---:|---:|
| no change | 0.314 | 0.416 | 0.441 | 0.432 | 0.431 |
| unit recurrence, measured once | 0.100 | 0.099 | 0.097 | 0.130 | 0.130 |
| fitted frozen-SD, measured once | 0.135 | 0.110 | 0.104 | 0.126 | 0.127 |
| kept-mean law, re-measured every round | 0.101 | 0.096 | 0.066 | 0.061 | 0.078 |

Measure-once error is **flat in horizon** — selection-driven trajectories
saturate, so the first move's direction and size carry the endpoint; the
horizon cost is paid by ignoring the dynamics (no-change 0.31 → 0.43). At
h=1 on matched runs: observe the kept set 0.085, predict it with the unit rule
0.100, with the fitted model 0.108. Horizon genuinely hurts only at regime
changes: measured-once 0.098 → 0.404 across the swaps, one refresh at the swap
0.179, re-measuring every round 0.041. That triple is the monitoring story in
three numbers: measurement effort buys accuracy exactly at regime changes and
almost nowhere else.

### Rung 3 — whole trajectories

- **Reproduces (deterministic conditional mean):** endpoint distribution
  (0.541/0.572 mean, 0.370/0.360 SD), 19/24 rails, 36/38 directions,
  trajectory R² 0.76.
- **Misses, by construction:** path roughness (variation 0.458 vs 0.648;
  reversals 0.16 vs 1.20).
- **The noise belongs where it enters the loop.** The battery itself implies
  observation noise (RMS SD 0.076 risk, 0.114 self-report; duplicate
  self-report baselines imply ~0.140 per read); observation noise *alone*
  restores variation to 0.630 and reversals to 1.31 without touching the
  latent path. The staged stochastic forecast — selector-gap and
  generator-mean residuals, zero-mean agreement innovation around persistence,
  battery noise on the observed value only — gives endpoint CRPS **0.095**
  and **84% coverage at nominal 80%**: calibrated, not apologized for. Re-run
  with the unit deterministic core (unit-prediction residual pools), the same
  staged forecast scores CRPS **0.092**, coverage **89%**, and sign reversals
  1.22 against the observed 1.20 — the recommendation is core-independent and
  the writeup may quote the staged-noise numbers next to the unit model. A
  separate latent value-process kick is rejected (worsens mean MAE, CRPS flat,
  overproduces variation).
- **When the kept set is observed every round**, the bare identity update is
  the best point path: endpoint MAE 0.070, all-round MAE 0.079, R² 0.887 —
  uncertainty about *which candidates are kept*, not training noise, is the
  main closed-loop path mismatch.

### Related frameworks (new short section, affirmative not defensive)

- `kept − pool` **is** the Price selection differential; the pre-selection
  decomposition (intensity × accuracy × spread) is the breeder's-equation
  form, with `ρ` compressing intensity × accuracy in fixed cells.
- Generate → rank → keep elites → refit is the cross-entropy-method update:
  the elite mean is the update target (why the kept-mean law works), spread is
  the generator's exploration variance, and CE's variance-shrinkage warnings
  and variance-injection remedies are the literature analogue of self-pool
  erosion and supplier reopening. Label "algorithmic analogue," not "same
  algorithm."
- Reward-model overoptimization ⇒ agreement is local, remeasure after
  distribution shifts. Model-collapse / self-consuming-loop results motivate
  tracking support and fresh material, without establishing this mechanism.

## 3. The complexity-audit table (one table, replaces the scattered hedges)

| ingredient | horizon | verdict | deciding number |
|---|---|---|---|
| `v_next = kept mean` (parameter-free) | 1 round | **adopted** | 0.081 vs 0.128 no-change |
| fitted update gain 0.83 | 1 round | rejected (no MAE gain) | 0.082 vs 0.081 |
| unit selection proxy `gap = ρσ` | 1 round, pre-selection | **adopted** | 0.090 vs 0.089 fitted; gap R² 0.81 |
| 0.958 fitted slope | 1 round | calibration check only | indistinguishable from unit at every horizon |
| "0.9545 from order statistics" | derivation | **retracted** | design value on the measured scale is ≈1.10 (scale audit) |
| per-prompt logged judge-score intensity | 1 round | rejected | 0.092/0.044 vs 0.090/0.042 |
| unit endpoint recurrence, boundary state frozen | endpoint | **adopted** | 0.118 selection-driven; 0.1365 combined; 37/38 |
| fitted frozen-SD recurrence | endpoint | kept for swaps only | 0.179 vs 0.210 on 9 swaps |
| freeze the observed first gap instead of ρσ | endpoint | rejected (noisy boundary) | 0.152 combined |
| feed spread recurrence back | endpoint | rejected | 0.139 vs 0.127 (though it predicts spread itself: 0.080 vs 0.111) |
| agreement autoregression | endpoint | rejected | 0.132; noisy persistence also beats noisy AR (CRPS 0.139 vs 0.141 risk) |
| one state refresh at a judge swap | endpoint | **adopted** (9 swaps only) | 0.404 → 0.179 |
| mean range as a second spread state | endpoint | rejected (indistinguishable) | endpoints differ 0.0066; same class 66/67 |
| "fraction of prompts with any difference" | endpoint | rejected (LORO mirage) | LORO 0.120 → LOCO 0.150 |
| staged noise: selector + generator + agreement persistence + observation | path/uncertainty | **adopted** | CRPS 0.095; coverage 84%/80%; variation 0.678 vs 0.648 |
| single lumped residual after the value update | path | superseded baseline | CRPS 0.108; coverage 62% |
| latent value-process noise term | path | rejected | MAE 0.147→0.153; variation 0.741 |
| agreement feedback `ρ_next ~ ρ + ρσ` | path/endpoint | rejected (fails direct next-ρ test) | R² 0.393 = persistence |
| parameter bootstrap (older 25-run corpus) | endpoint (CRPS) | rejected | 0.091 ≈ 0.092 |
| logit-bounded process (older 25-run corpus) | endpoint (CRPS) | appendix | beats climatology on OLMo only — same regime boundary as self-weak ≈ persistence |

## 4. Section map (current writeup → new)

| current section | disposition |
|---|---|
| Findings 1–3 | rewrite as the three rungs — one finding per rung, one number each; lead with "zero fitted parameters" |
| "What I measure" + estimator fine print | keep; move ddof/n_j/mean-vs-RMS details to the definition-audit pointer |
| "The value moves toward what the judge keeps" (now incl. the one-round bakeoff paragraph) | becomes Rung 1 |
| "The selector gap is spread × agreement" (now Price-framed) | folds into Rung 1; keep the judge gallery; add the per-prompt-model rejection line |
| "Spread is converted into a new generator state" | splits: Δq + variance identity → short "the state the law updates" passage + conversion figure; mixed-pool spread components → mixed-pool discussion; R² 0.78 one-step spread → audit table |
| "Agreement is structured, but not safe to freeze" | absorbed into Rung 2's residual paragraph (0.139/0.115/0.152) — currently stated three times |
| "Rolling the equations through complete runs" (now unit-recurrence-led) | becomes Rung 2 (endpoint table + horizon ladder) + Rung 3 (noise location) |
| — | NEW: "Related frameworks" short section (Price / CE method / overoptimization / collapse lit) |
| "What this buys" | shorten to the three dials + practitioner recipe; the recipe now cites the unit equations verbatim |
| "Where this should transfer" | keep; resolve the placement-pick marker (own section) |
| "Next directions" | agreement-trajectory modeling first; then the preregistered spread-conversion test; the swap prereg sentence GPT added stays |
| "Limitations" | keep, minus sentences that moved into the audit table |

## 5. Claim-hygiene notes for the rewrite

- Endpoint numbers: unit **0.118 / 0.210 / 0.1365**; fitted comparator
  **0.127 / 0.179 / 0.1373**. Never mix the pairs. Directions: under the
  matched round-1 convention BOTH models score **36/38**; the
  selection-response JSON's 37/38 measures swap runs from the swap boundary —
  never quote it next to the fitted 36/38 (report_unit_rollout_properties.md).
  Rails: unit **21/24** vs fitted 19/24 on the matched 45. The superseded
  first-pass rollout (0.106 LORO) and the retired "rankable support is the
  best endpoint state" framing must not reappear.
- The 0.9545 order-statistic constant may only appear as the retraction note.
- The h=1 predicting-vs-observing cost is **0.015–0.023 (matched sets)**; the
  0.033 pooled figure is superseded.
- Battery observation noise: RMS SD **0.076 / 0.114**, duplicate-baseline
  single-read SD **~0.140**; staged-noise coverage **84%** (the old 62% figure
  described the superseded lumped-residual placement).
- The spread-trajectory pair stays **0.080 vs 0.111** (risk-group); the
  conversion-chain dynamics claim stays binary-risk-only (self-report
  headroom-chain R² −0.03 vs 0.75 persistence).
- Everything is post-hoc LOCO within this program except the frozen gap
  predictor (blind release sets) and the just-committed control-arm forecast;
  the unit model's ledger row says "prospective validation pending" — say it
  once, in Limitations.
- Regime label: "strong-agreement self-only"; the grip/utilization vocabulary
  stays retired.

## 6. Figure plan

- **Revise `docs/figures/auto/model-ladder-horizon/`**: add the unit-recurrence
  line (0.100/0.099/0.097/0.130) to Panel A; move the fitted frozen-SD line to
  a secondary style; correct the h=1 bracket to the matched-set 0.015; caption
  gains the "zero fitted parameters" sentence. (Figure-maker spawn.)
- **New selection-response model figure** per GPT's
  `figure_brief_selection_response_model.md`: the three-operation loop
  (generate σ → select `a`, `g = σa` → refit `k = p + g`), the unit-slope
  gap-vs-ρσ evidence panel, CE-analogue inset, endpoint inset with
  0.118/0.210/0.1365 and the fitted 0.179 swap comparator, and the crossed-out
  0.9545 note. (Figure-maker spawn; replaces any figure labeling 0.9545 as
  design-derived.)
- `spread-rollout-bakeoff` caption already corrected in the tree (mean-model +
  staged-noise framing); the two-clocks and two-dials figures stand.

## 7. Full-package status

- selection-response audit: verified this session (script re-runs
  byte-identical; scale audit independently re-simulated, ratio 1.099);
  ledger row trace upgraded.
- horizon ladder: extended with `one_step_unit` and `closed_unit`
  (`scripts/analysis_model_ladder_horizon.py` →
  `experiments/model_ladder_horizon.json`, report updated, five anchors +
  two cross-checks pass); ledger row updated.
- figure spawns: model-ladder-horizon revision + selection-response model
  figure (in flight; drafts land under `docs/figures/auto/`).
- STATE one-liner added; the never-committed modeling-cluster files
  (predictor/rollout/trajectory reports, scripts, and result JSONs the ledger
  cites) committed alongside this brief.
