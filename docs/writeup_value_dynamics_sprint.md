# Value dynamics in self-training loops: what we can predict, when we can intervene

*PRE-DRAFT 2026-07-13 (~11:50). Structure follows the result hierarchy from
the final analysis audit (docs/report_local_final_analysis_audit_2026-07-13.md).
Sections marked … are outlines. Figure slots in [brackets]; existing drafts
named where they exist.*

When a model influences its own training — generating candidates, judging
them, training on the ones it prefers — how do its values move, what
controls that movement, and when does control fail?

There is a lot of theory about reflective stability and almost no
empirical work at the scale where you can actually watch it happen. So we
built small "organisms" — Qwen3-4B and Olmo-3-7B with LoRA-installed value
orientations (risk-seeking, conservative, insecure-code-admitting) — and
ran them through ~120 self-training rollouts across three model families,
five judge types, and a dozen intervention protocols. Predictions were
preregistered before each run family; scorers were committed before
results were read; six external audits reviewed everything, twice
catching errors in our own tables. Two results survived. They are better
than the ones that didn't.

[figure: the loop schematic — organism generates K=6 candidates per item,
judge keeps 2, train 10 steps, repeat; the three families and five judges
as a small table beside it. Exists in draft form as the methods loop
panel in docs/figures/src/make_methods_figures.py.]

## Result 1: one number measured inside the loop predicts where it goes next

Each round, the judge keeps 2 of 6 candidates. The **realized selection
gap** — mean score of the kept candidates minus mean score of the whole
pool, on the value axis — turns out to carry most of what you can know
about the next round.

A model with one intercept per judge condition plus a single pooled gap
slope (+0.74) beats a matched no-gap model in 12 of 13 leave-one-seed-out
folds across all three grids (Qwen risk, OLMo conservatism, Qwen candor).
We then froze it and scored data that did not exist yet: 17% lower error
on a blind Kaggle release set, 31% on a Modal release set, 42% on the
press-depth set. The one place it loses — a fan-then-press schedule's
self-judge phase, 0.061 vs 0.040 RMSE — is reported next to the wins.

This is a predictive association, not a law: the slope is not a universal
gain, the target is the self-generated pool mean, and it says nothing
about *why* the judge produced that gap. What it gives you is a cheap,
online, per-round warning signal: if you can score the kept-minus-pool
gap on an axis you care about, you can forecast next-round drift on that
axis before it happens.

[figure: observed next-round pool drift vs realized gap, all three grids
pooled, with the frozen slope drawn and the fan_press failure phase
highlighted in a different color. Partial draft: fig17 / the
loop-integrator panel.]

## Result 2: selection controls the organism exactly while the pool has material — and material can be supplied from outside

The sharper result of the sprint is about when control *fails*.

Take an organism that has railed — free-generation risk pinned at 1.0
after rounds of self-training. Attach the strongest possible selector: an
oracle that keeps the 2 lowest-risk candidates every round, no prompted
judge to fool. What happens depends entirely on one quantity: whether the
6 candidates it generates still *differ* on the scored axis.

- OLMo railed at 0.875: pools still varied (within-item SD 0.12–0.30).
  The oracle reversed it 0.917 → 0.094 in four rounds.
- OLMo railed at 1.000: every candidate scored identical, every item,
  every round — spread exactly 0.000. Four rounds of oracle selection did
  nothing. Not resistance; there was no choice to make.
- Qwen, same story earlier: three oracle reversals (0.99 → 0.33, 0.33,
  0.625), each decelerating as pool variation thinned; the one run
  observed after spread hit exactly zero sat at 0.625, immovable — under
  its own judgment (no relapse, but no motion), and at sampling
  temperature 1.4 (heat does not regenerate scored variation).

[figure: EXISTS — docs/figures/auto/crossfamily-oracle-reversal/ — the
two OLMo trajectories with per-round spread, descent exactly where spread
exists.]

So a state can be "selection-inert": not an attractor in any dynamical
sense (weights still move; other judges could still rank these pools),
but immune to *this* selector because its generator no longer produces
scored differences. That framing suggested the intervention: change the
generator mixture. Replace 3 of the 6 candidates with generations from a
frozen base model that never collapsed.

It works, and it works in a specific, slightly unsettling way:

- The immovable OLMo 1.000-rail moved: 1.000 → 0.484 in four rounds,
  negative gaps every round, and — unlike every self-only reversal — no
  exhaustion, because the supply replenishes the pool.
- The Qwen 0.625 stall — inert under its own judgment, inert at
  temperature 1.4 — collapsed to **0.000 after one round**, both seeds.
- But the organism converges to the *supplier's* level, not to "fixed".
  Base-Qwen scores ~0.06 on the insecurity axis, so Qwen lands at 0.000.
  Base-OLMo scores ~0.5–0.7 on the risk items, so OLMo lands at 0.34–0.48
  — and on the material-rich rail, injection actually made the reversal
  *shallower* than self-only (0.344 vs 0.094 endpoints). Rescue by
  injection inherits the rescuer's values, no better and no further.

[figure: EXISTS (partial) — docs/figures/auto/mixed-pool-rescue-vs-
contamination/ left panel; consider adding the Qwen one-round collapse as
an inset — 0.627 → 0.000 with the temp-1.4 flat line as the ghost.]

The Qwen version of this contrast is causally clean: a matched twin —
same stalled endpoint, same seeds, same oracle, no injection — sat at
0.625 with zero pool variation for all four rounds while the injected
run collapsed to 0.000 in one. The streams diverge only at the injection
itself. (The OLMo cells remain existence results; their self-only
comparators use different seeds.)

## Result 3 (the safety demonstration): a shared pool contaminates in one round, and realistic judges are the reason

Run the same channel backwards. Fresh organism (risk ~0.3), pool
half-filled by a railed risk-1.000 peer, judge = the base model or the
organism itself — the "self-training on scraped peer data" setting.

All four cells moved to ≥0.917 after ONE round. The judges kept the
contaminant's text 96–100% of the time in that round. By round 2 the
victim's own generations scored 1.0, pool spread hit 0.000, and it had
inherited the peer's selection-inert state. Self-only, the same judges
took 5–8 rounds to rail an organism, and only sometimes.

Meanwhile the judge you would actually deploy as a guardrail — the frozen
conservative judge that successfully pressed fresh organisms to the floor
all night — was handed the same rescue material at the rails and *kept
the rail's own confident text instead* (kept-supplier share → 0.00, gaps
positive). Material is necessary; a selector that actually ranks on the
target axis is also necessary; every realistic judge we tested preferred
confident collapsed text over fresh material, in both directions.

[figure: EXISTS — the contamination panel of mixed-pool-rescue-vs-
contamination: four trajectories jumping to ~1.0 at r1, annotated with
kept-contaminant shares.]

The asymmetry is the point: pool-sharing between models is a fast
contamination vector (one round, near-total, judge-assisted) and a slow,
selector-gated remedy (four rounds, partial, oracle-only).

## What did not survive its own preregistration

We preregistered aggressively and most of the detailed dynamical story
failed its tests. Keeping these visible:

- **Release grid: 6/13 criteria.** Both random-release predictions, both
  press_hold-floor predictions, both fan-width predictions failed.
  Survivors worth keeping: base-judge outcomes are heterogeneous (some
  rails, some decays, from identical starts), and the frozen predictor
  transported.
- **Press-depth: 2/5.** The spread-at-switch mediator FAILED (rich
  material at the switch, outcomes still split maximally); depth-1
  recovery failed; the no-floor prediction failed. What remains: paired
  high/low endpoints at every depth from the same two sampling streams,
  n=2 per depth — not a mapped boundary, and we no longer call it
  bimodality.
- **Owner-blind screens: failed twice** on a response-type confound (the
  code organism emits literal code, base emits prose; a "style" classifier
  detects response type at 0.88–0.93). This retired the coupled
  co-training design and is why the mixed-pool experiments above claim
  material effects, not judge-blindness.
- **Transmission-with-support: 1/2 seeds beyond noise** (−0.47 vs a 0.197
  noise floor; the other seed's material died after round 1), and it
  inherits the response-type confound.

[figure: a small "prereg scoreboard" — every registered criterion as a
green/red cell grouped by run family. Nothing like it exists yet; cheap
to make and more honest than prose.]

## Descriptive results and open threads (outline)

- Endpoint fans under different judges: self-judge widens, frozen judges
  press, random diffuses; K1 fan survives order-sensitivity, K2 arm
  ordering survives, forced-probe channels do not. …
- K3: selection on candor moved an off-axis self-report channel's
  variance (r=0.01 to the selected coordinate) — channels dissociate. …
- Off-target drift taxonomy (corrigibility, optimism, entropy) from the
  earlier phase; legacy four-seed stochasticity result now motivation
  only. …
- Geometry (LoRA displacement, path length): exploratory, unsaved
  analyses dropped per audit. …

## Methods and validity appendix (outline)

- Instruments: order-swapped free-generation probes primary (1–9 samples;
  mid-round reads 1-sample), forced A/B probes flagged secondary
  everywhere (order gaps up to 0.6). Flag-plus-both-orders rule adopted
  prospectively 07-13. …
- Provenance: preregs and scorers committed before data; two table errors
  caught by independent recomputation (figure pipeline, audit) and
  corrected with dated notes; zero-byte adapter dirs are not recoverable
  checkpoints; Qwen artifacts predate the config contract. …
- Budget: the whole empirical program ran on ~$23 of Modal credit, free
  Colab/Kaggle tiers, and one Cerebrium lane. …

## What this means

If models shape their own training data, the leverage points this program
found are all upstream of the values themselves: the **selection gap** is
measurable online and predicts drift before it lands; **pool variation on
the scored axis** is the resource that determines whether any selector —
aligned or not — has power at all; and **who else feeds the pool**
dominates both, faster than either. Oversight designed as "a judge that
prefers good outputs" failed twice here in instructive ways: it could not
use rescue material at a collapsed state, and it actively selected a
contaminating peer's confident text. Designing virtuous versions of these
loops probably means budgeting for diversity maintenance and pool
provenance, not just judge quality.

…closing paragraph tying to the reflective-stability motivation, one
paragraph, after review…
