# Refactor brief: one simple law, three forecast horizons

*2026-07-15, general (writeup) thread. This is the narrative plan for the next
writeup revision, assembled from the modeling reports and the claim ledger
(rows: unified accounting, conversion model, rollout bakeoff, value predictors,
property fidelity, trajectory adjustments) plus one new connecting analysis,
`scripts/analysis_model_ladder_horizon.py` →
`experiments/model_ladder_horizon.json` (docs/report_model_ladder_horizon.md).
Nothing here introduces a claim without a ledger row.*

## 1. Diagnosis — why the current draft reads defensive and disorganized

The modeling half of the writeup is currently organized by **analysis in the
order it landed** (movement law → factorization → conversion chain → rollout),
not by **the question each answers**. Concretely:

1. **Six accuracy numbers for "the model" with no frame.** The reader meets
   MAE 0.081, 0.089, 0.127, 0.137, 0.139, and R² 0.78 across three sections,
   under three validation schemes (blind release sets, leave-one-run-out,
   leave-one-condition-out), against shifting baselines. Each number is
   correct; nothing tells the reader that they answer three different
   questions (next round? endpoint? whole path?) at three different
   information budgets (observe every round? measure once?).
2. **Every claim carries its own rebuttal in the same breath.** "Predicting
   spread more accurately does not improve those endpoints"; "It remains an
   under-dispersed uncertainty model"; "The tempting LORO winner is
   misleading"; the mean-range-versus-mean-SD litigation occupies a paragraph
   of main text. All of these corrections are real and must survive — but
   scattered inline they read as anxiety. Collected once, as a table of what
   earned its place and what was tested and rejected, they read as method.
3. **Two modeling strands never reconciled.** The older 25-run own-pool
   probabilistic bakeoff (logit-bounded process model, CRPS, the climatology
   ceiling) and the new 67-run corpus (frozen-spread closed loop) both live in
   the ledger; the writeup carries only the new one but inherits hedges from
   both. Their shared lesson — state forecasts work where selection is the
   mechanism and hit a ceiling where it is not — is currently stated twice in
   different vocabularies.
4. **State variables and bookkeeping are interleaved.** The "Spread is
   converted into a new generator state" section mixes one-step dynamics
   (R² 0.78), endpoint results (0.127), and instrument accounting (the
   within/between variance split, mixed-pool spread components) in one run of
   prose. The reader cannot tell which quantities the model *evolves* and
   which are measurement hygiene.

The fix is not deleting caveats. It is a spine that makes each number the
answer to a stated question, plus one "complexity audit" table that holds
every rejected refinement.

## 2. The spine: one law, three horizons

Everything the modeling sections need to say fits one ladder. **The law:**

> *After training on a round, the behavioral value moves to the mean value of
> the answers the judge kept.*

**The state, measured on one pool:** behavioral value `v`, own candidate mean
`q`, spread `σ` (mean within-prompt population SD of candidate value scores),
agreement `ρ` (within-item correlation of judge score with value score), and —
in a mixed pool — the supplier's mean and share. Five numbers, one pool of
logged scores, all measurable before training on it.

The ladder climbs by forecast horizon. Each rung adds exactly one ingredient
to the same law; everything else was tested and rejected (§4).

### Rung 1 — the next round (given this round's pool)

- **After selection is observed:** predict `v_next = kept mean`.
  Parameter-free. Held-out-condition MAE **0.081** across all 340 logged
  rounds, versus 0.128 for predicting no change; beats using training
  displacement alone (0.098) or selector gap alone (0.112). A fitted update
  gain lands at 0.83 with no MAE improvement — "the value moves most of the
  way to the kept mean in one round" is the finding; the identity update is
  the forecast.
- **Before selection:** the kept mean is itself predictable from the two
  dials, because keeping 2-of-6 by a judge with agreement ρ from a pool with
  spread σ yields a gap of ≈ `0.96·ρσ` (r = 0.90, 290 rounds). Predicting the
  kept mean as `pool mean + 0.96·ρσ` scores MAE **0.089**, versus 0.085 with
  the kept set observed. The entire cost of *predicting* the judge's selection
  rather than *watching* it is a few thousandths — which is the demonstration
  that (σ, ρ) is a sufficient selector state, and the natural home of the
  factorization (it stops being its own section and becomes the reason the
  pre-selection forecast works).

This rung is where the mechanistic sections (movement toward the kept mean,
gap = spread × agreement, training displacement vs selector gap in mixed
pools) already point. They stay, trimmed, as the physical justification of the
one-round law.

### Rung 2 — the endpoint, from a single first measurement

Iterate rung 1 from the round-1 state. The one added ingredient is a rule for
the state's evolution, and the surprise is that the best simple rule is the
**null rule: freeze σ and ρ at their round-1 values** (update `q` and `v` by
the law itself; refresh everything once if the judge or format is changed).

Held-out-condition endpoint error, by regime — presented as the headline
table, not as a caveat:

| regime | runs | frozen-state model | no change |
|---|---:|---:|---:|
| selection-driven (interventions + strong self-judges) | 36 | **0.127** | 0.431 |
| … direction of every move ≥ 0.15 | 31/31 | | |
| weak self-only selection (ρ ≈ 0) | 22 | 0.205 | 0.215 |
| scheduled judge swaps, no refresh | 9 | 0.404 | 0.309* |
| scheduled judge swaps, one refresh at the swap | 9 | **0.179** | 0.309* |
| selection-driven + swaps combined | 45 | **0.137** | 0.407* |

*\*holding the latest boundary value fixed.*

Three sentences carry what is now a page of hedging:

- Where a judge actually selects on the axis, one measurement predicts the
  endpoint at a quarter of the no-change error and every large direction.
- Where no one selects (ρ ≈ 0), the model correctly predicts "selection does
  nothing," and the observed wandering is the separately documented
  training-instability mechanism — a scope statement, not a failure.
- When the selection policy changes, re-measure; one refresh at the swap
  recovers most of the forecast (0.404 → 0.179, direction 6/7).

**The residual has a name.** The refinements that *should* have helped were
tested and did not: feeding the validated spread recurrence back into the
rollout makes endpoints worse (0.139 vs 0.127); an agreement autoregression
recovers little (0.132). Oracle attribution shows why: giving the simulator
the *true later spread* changes nothing (0.139), giving it the *true later
agreement* removes most of the remaining error (0.115). The missing state is
agreement drift — which becomes the named next experimental target rather
than a diffuse apology.

(Reconciliation of the older strand: the 25-run own-pool bakeoff said the
probabilistic version of the same two things — state-based endpoint forecasts
beat climatology on OLMo and cannot beat it on the Qwen fan. That is the same
regime boundary as "weak selection ≈ persistence." It moves to one appendix
paragraph with its CRPS table.)

### Rung 3 — whole trajectories

Roll the same frozen-state model as a path generator. What it reproduces and
what it misses are both crisp:

- **Reproduces:** the endpoint distribution (observed vs predicted mean
  0.541 / 0.572, SD 0.370 / 0.360), 19/24 observed rail endpoints, 36/38
  large-movement directions, all-round value R² 0.76 on the 45
  selection-driven-plus-swap runs.
- **Misses, by construction:** path roughness. The deterministic rollout is a
  conditional mean: total variation 0.458 versus 0.648 observed, 0.16 sign
  reversals per run versus 1.20.

One added ingredient closes that gap: zero-mean Gaussian noise on the
one-round value update, scale estimated from the training folds (≈0.10 on the
binary axis, ≈0.16 on the continuous axis). Path variation and reversals
match (0.655, 1.49), endpoint CRPS improves 0.137 → 0.108, and the mean path
is unchanged. Stated once, plainly: the resulting intervals are still
under-dispersed (nominal 80% covers 62%), so the noise term is for realistic
sample paths and sharper probabilistic scores, not calibrated bands.

The tested-and-rejected item at this rung: an agreement-feedback term
(`ρ_next ~ ρ + ρσ`) that improved endpoints but fails the direct test — it
does not improve held-out next-agreement prediction over persistence — so it
is compensation, not dynamics. One line in the audit table.

### The connecting analysis: error versus forecast horizon

New analysis (this session, `docs/report_model_ladder_horizon.md`) computes,
on the same runs and the same held-out conditions, MAE as a function of
rounds-ahead for each model. All three published anchors reproduce (0.127,
0.431, 0.081). Selection-driven runs:

| model | h=1 | h=2 | h=3 | h=4 | endpoint |
|---|---:|---:|---:|---:|---:|
| no change | 0.314 | 0.416 | 0.441 | 0.432 | 0.431 |
| closed loop, measured once | 0.135 | 0.110 | 0.104 | 0.126 | 0.127 |
| one-round law, re-measured every round | 0.101 | 0.096 | 0.066 | 0.061 | 0.078 |

This overturns the natural reading that the one-round error 0.081 "compounds"
into the endpoint error 0.127. It does not: the measure-once model's error is
**flat in horizon**, because selection-driven trajectories saturate — get the
first move's direction and rough size right and you stay close. The horizon
cost is paid entirely by the model that ignores the dynamics (no change,
0.31 → 0.43). At h = 1 the closed loop and the one-round law see the same
pool, so their gap — 0.135 vs 0.101 — prices *predicting* the judge's
selection from frozen ρσ versus *observing* the kept set: about 0.03,
carried at every horizon. And the judge-swap runs show the one place horizon
genuinely hurts: measured-once error grows 0.098 → 0.404 across eight rounds,
one refresh at the swap holds it to 0.179, re-measuring every round achieves
0.041. That triple (0.404 / 0.179 / 0.041) is the writeup's monitoring story
in three numbers: measurement effort buys accuracy exactly at regime changes,
and almost nowhere else.

Numbers: `experiments/model_ladder_horizon.json`;
figure: `docs/figures/auto/model-ladder-horizon/` (figure-maker draft).

## 3. Proposed section map (old → new)

| current section | disposition |
|---|---|
| Findings 1–3 (long, nested) | rewrite as the three rungs — one finding per rung, one number each |
| "What I measure" + score/spread definitions | keep, but move the estimator fine print (ddof, n_j, mean-vs-RMS SD) to the definition-audit appendix pointer; the five bookkeeping quantities stay |
| "The value moves toward what the judge keeps" | becomes Rung 1, absorbing the one-round bakeoff table |
| "The selector gap is spread × agreement" | folds into Rung 1 as the pre-selection forecast; the judge-gallery bullets (oracle/K1/duel/self-erosion ρ values) stay — they are the paper's best concrete texture |
| "Spread is converted into a new generator state" | splits: the Δq and variance-identity material becomes a short "why freezing σ is not absurd" passage in Rung 2 + the conversion-chain figure; the mixed-pool spread components move next to the mixed-pool discussion; the R² 0.78 one-step spread result is reported as *one-step dynamics that do not improve endpoints* (audit table) |
| "Agreement is structured, but not safe to freeze" | absorbed into Rung 2's residual paragraph (0.139/0.115 attribution) — currently this point is made three times |
| "Rolling the equations through complete runs" | becomes Rung 2 (endpoint table) + Rung 3 (path properties) |
| spread-definition litigation (range vs SD, LORO mirage) | audit table + one sentence ("nine alternative definitions roll out indistinguishably or worse; see appendix") |
| "What this buys" | keep, shortened — it currently restates the chain a third time; it should only state the three dials and the practitioner recipe |
| "Where this should transfer" | keep as is (resolve the placement-pick marker: keep as own section) |
| "Next directions" | reorder so agreement-trajectory modeling is unambiguously first, then the preregistered spread-conversion test, then the rest |
| "Limitations" | keep, minus the sentences that move into the audit table (they stop being limitations and become results about model selection) |

## 4. The complexity audit table (new, one table, replaces ~15 inline hedges)

| ingredient | horizon | verdict | deciding number |
|---|---|---|---|
| `v_next = kept mean` (parameter-free) | 1 round | **adopted** | MAE 0.081 vs 0.128 no-change |
| fitted update gain 0.83 | 1 round | rejected (no MAE gain) | 0.082 vs 0.081 |
| kept mean from `pool + 0.96·ρσ` | 1 round, pre-selection | **adopted** | 0.089 vs 0.085 observed-kept |
| freeze σ and ρ at round 1 | endpoint | **adopted** | 0.127 selection-driven |
| feed spread recurrence back | endpoint | rejected | 0.139 vs 0.127 (though it predicts spread itself: 0.081 vs 0.111) |
| agreement autoregression | endpoint | rejected (small gain, no transport) | 0.132 |
| one state refresh at a judge swap | endpoint | **adopted** (9 swaps only) | 0.404 → 0.179 |
| mean range as a second spread state | endpoint | rejected (indistinguishable) | endpoints differ 0.0066; same class 66/67 |
| "fraction of prompts with any difference" | endpoint | rejected (LORO mirage) | LORO 0.120 → LOCO 0.150 |
| Gaussian one-round update noise | path shape | **adopted** | variation 0.655 vs 0.648 observed; CRPS 0.137 → 0.108; coverage 62% < 80% |
| agreement feedback `ρ_next ~ ρ + ρσ` | path/endpoint | rejected (fails direct next-ρ test) | R² 0.393 = persistence |
| parameter bootstrap (older corpus) | endpoint (CRPS) | rejected | 0.091 ≈ 0.092 baseline |
| logit-bounded process (older corpus) | endpoint (CRPS) | appendix | 0.081/0.089, beats climatology on OLMo only |

Verdicts and numbers all trace to ledger rows; the table *is* the defensive
material, said once, as evidence of selection discipline rather than worry.

## 5. Claim-hygiene notes for the rewrite

- Use **0.127 / 31/31** for the frozen-state selection-driven endpoint (36
  runs, LOCO) and **0.137 / 36/38 / 19/24** for the 45-run
  selection-plus-swaps hybrid. The superseded first-pass rollout (0.106,
  LORO, report_simple_model_rollout.md) must not reappear.
- The regime label is "strong-agreement self-only," never the retired
  grip/utilization vocabulary.
- The spread-trajectory pair is **0.081 vs 0.111** (risk-group,
  own_metric_rounds_2plus vs persistence); do not mix in the 0.0814
  selection-driven geometry value.
- Every rollout claim is post-hoc LOCO within this program; the only
  prospective test remains the frozen gap predictor on the three blind
  release sets (17–42%). Say this once, in Limitations, not per-section.
- The conversion chain's dynamics claim is binary-risk-only; the 60
  continuous self-report rounds keep selector accounting only (their
  headroom-chain R² is −0.03 vs 0.75 persistence). One sentence, Rung 2.

## 6. Full-package status for the new connecting analysis

- script: `scripts/analysis_model_ladder_horizon.py` (committed)
- result: `experiments/model_ladder_horizon.json`
- report: `docs/report_model_ladder_horizon.md`
- ledger row: added under §A
- figure: `docs/figures/auto/model-ladder-horizon/` (figure-maker spawn)
- STATE one-liner: added under Recent changes
