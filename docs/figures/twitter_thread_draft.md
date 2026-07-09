# Twitter/X thread draft — value dynamics main results

*v6, 2026-07-09 night (Figures thread). Integrates the Analysis thread's Tier-A
batch: the drift-field result (the "divergent basins" are ONE weak attractor whose
location the judge sets — no saddle) now has its own main-line tweet and softens
"basin" language elsewhere; the weight-space thrash result is new main-line
material; the calibration result replaces the old single-run anecdote inside the
which-leads tweet; the EV-gate check backs the OLMo tweet's bracket; the optimism
tracer and judge length bias join the pool. v5 history: full refactor with the
self-report arc and both let-go results; earlier: v2 cut the format tweet, v3
split off-target + added the pool, v4 built the self-report arc.*

Notes for posting:
- Main line is 19 tweets; the candidate pool below has 12 more to swap in or
  append. Several run past the classic 280 characters (assumes an X account that
  allows long posts); each is 1–4 sentences and can be trimmed on request.
- Every number is from a landed result (pointers in brackets after each tweet;
  they are NOT part of the tweet text). Tweet 18 depends on a run that is one
  arm short of complete — re-verify its bracket before posting.
- Images: three social figures already built (docs/figures/thread/,
  make_thread_figures.py — cross-lag forest, self-report seed fan, release
  trajectories); two more are being drafted by figure-maker into
  docs/figures/auto/basin-drift-field/ and auto/weightspace-thrash/ for tweets
  6–7. Everything else uses the numbered set or auto/ drafts, with adaptation
  notes inline.

---

## Main line

**1.**
What happens when a language model trains on outputs it judged itself? We installed
a value into a small open model and ran the self-training loop over and over —
dozens of rollouts across random seeds, judges, data formats, and two model
families. Short version: it behaves like a force field — the judge sets where it
flows, noise decides where you land, and letting go doesn't snap back. 🧵

Image: `fig1_research_goal.svg` (as-is).
[framing: docs/value_dynamics_results_so_far.md §1]

**2.**
The setup: Qwen3-4B plus a LoRA adapter trained to always pick the gamble in
expected-value-neutral choices ("$30 for sure" vs "a 30% chance of $100"). Each
round it answers 12 gamble questions with 6 sampled answers each; a judge keeps
the best 2 per question against a fixed cautious reference; we fine-tune on the
keepers and repeat. The one dial: the judge is either a frozen copy of the base
model, or the organism itself — the very adapter being trained.

Image: `fig2_selftraining_loop.svg` (as-is; already shows a real round with real
scores).
[mechanics: experiments/kaggle/kaggle_basin_anchor/script.py]

**3.**
That one dial switches the dynamical regime. Under the frozen base judge, all 8
seeds decayed toward caution. Under the self-judge, 15 seeds fanned out — final
risk anywhere from 0.03 to 0.81 — from identical starting weights and identical
questions. Self-judging doesn't just slow erosion; it makes the endpoint
seed-dependent.

Image: `fig3_judge_determines_dynamics.svg` (adapt: the trajectory fan panel alone,
enlarged — the full figure is too dense for a feed).
[docs/report_basin_anchor.md; the decay-baseline caveat is tweet 17's job; the
"what IS that fan" question is tweet 6's]

**4.**
Why? Split each round into the candidate pool vs what the judge kept. Qwen judges —
frozen AND self — keep cautious answers out of a risky pool (kept 0.58–0.63 from a
0.82 pool); OLMo judges keep risky ones (0.78–0.80 from a 0.50 pool). The loop
then drags the pool toward whatever the judge already preferred. The attractor
direction isn't set by the training data — it's the judge's pre-existing preference,
amplified.

Image: `auto/judge-preference-attractor/judge-preference-attractor.svg` (as-is or
light crop).
[docs/report_basin_lightning_partial.md §Mechanism]

**5.**
Swap the model family and the whole regime flips: on OLMo-3-7B the same loop runs
away to ~100% risky under BOTH judges, while Qwen decays or splits depending on the
judge. "Self-judge vs external judge" turned out to be less fundamental than we
first thought — what matters is which way the judge's preference points on the axis
being trained.

Image: `auto/olmo-substrate-regime/olmo-substrate-regime.svg` (as-is; keep the
"partial run" label).
[docs/report_basin_lightning_partial.md. Rigor backup if challenged: the runaway
passes the factual gate — the model's expected-value arithmetic stays at accuracy
1.000 every round while its choices run to the rail
(docs/report_probe_instrument_checks.md §1); standalone tweet version is P11]

**6.**
Are those diverging endpoints really "basins"? We fit the actual force field —
round-to-round change in risk as a function of where you currently are, pooled
over 40 rollouts. There is no ridge between two wells: it's ONE shallow valley,
and the judge sets where its bottom sits (self-judge 0.35, frozen judge 0.12,
OLMo pinned at the 1.0 rail). The self-judge fan is that valley filled to its
natural stochastic width (observed spread 0.223, noise-equilibrium prediction
0.229); the frozen judge actively compresses below its own (0.119 observed vs
0.198 predicted). The divergence is noise finding its equilibrium — not seeds
choosing between wells.

Image: NEW — `auto/basin-drift-field/` (figure-maker drafting now: two Δx-vs-x
panels with fitted line and fixed point, plus the spread-by-round inset with
AR(1) reference lines).
[docs/report_basin_drift_field.md. Bracket caveats: drift-fit R² ≈ 0.05–0.09 —
motion is mostly stochastic, the fixed point is the faint mean of a noisy field;
bistability appears in only 19% of bootstrap resamples; restoring eigenvalues
statistically indistinguishable between judges (−0.21 vs −0.19)]

**7.**
If the motion is mostly noise, what makes a seed commit? Not effort: the rollouts
that move their LoRA weights the MOST change their behavior the LEAST (r = −0.66
under the self-judge, −0.42 frozen). Consecutive updates are nearly orthogonal
(cosine ≈ 0.2) — the loop mostly re-steers rather than marches — and the seeds
whose update direction stays consistent are the ones that reach extreme fates
(r = +0.51 under the frozen judge). Commitment lives in the direction of the
updates, not their size. And round-1 movement predicts nothing (r = 0.03): no
early-warning signal in weight space.

Image: NEW — `auto/weightspace-thrash/` (figure-maker drafting now: displacement
vs behavioral-change scatter, self/frozen colored, plus the cosine-vs-fate panel).
[docs/report_basin_weightspace_and_calibration.md §1]

**8.**
Values live in multiple channels, and rhetoric picks which channel an update lands
in. Fine-tune on essays that concede then refute ("personalization has genuine
appeal… But the assistant should give priority to general reliability") and the
model's stated rating REVERSES (+1.45 → −0.31, all 3 seeds cross zero) while its
choices stay at baseline. Fine-tune on hedged advocacy of the opposite stance
("broad consistency still matters… Even so, it should adapt around top-line
answers, optional detail, and minimal preface when preferences are stable") and
choices rise 0.73 → 0.82 in 4 of 4 runs while the stated rating contracts like
every other arm. A loop amplifies whatever channel its judge reads; the others are
unconstrained.

Image: `fig7_rhetoric_gates_transfer.svg` (adapt: the two-channel contrast, with
these two truncated quotes on the cards).
[docs/report_stance_dissociation.md §2–3; quotes verbatim from
colab/colab_stance_dissociation.py _stance_texts()]

**9.**
Off-target drift — what moves when you never trained it — turned out to be three
phenomena, not one. The first is universal: after 3 rounds of fine-tuning on essays
about assistant personalization, corrigibility ("will you comply with being
retrained?") fell in 16 of 16 rollouts, in every essay arm, by as much as −0.97 in
probability. Advocacy, refutation, stance-free filler — didn't matter. That's
content-free drift: a property of the fine-tuning itself, not of the message.

Image: adapt from `fig10_offtarget_drift.svg` — the corrigibility row alone,
enlarged, with the 16-dot spread visible.
[fig10 per-rollout deltas (make_figures.py fig_offtarget PROBES);
docs/report_stance_dissociation.md §4]

**10.**
The second phenomenon follows the message. Optimism ("will the venture succeed?")
tracked the essays' stance: it rose only under pure advocacy and fell hardest under
the refutation arms (−0.37 to −0.52) — even though the essays argue about assistant
personalization and never mention ventures or forecasts. Content-coupled drift: the
stance's direction, exported to axes the text never touches.

Image: adapt from `fig10_offtarget_drift.svg` — the optimism row, with the five arm
columns labeled.
[same sources as tweet 9; P10 is the cross-experiment extension of this axis]

**11.**
The third phenomenon belongs to neither the fine-tuning nor the message. Risk
appetite rose most in the stance-free control and the double-dose arms (+0.28 to
+0.41) — exactly where the stance is weakest. Agreeableness swung both directions
inside the same arm: identical training text, opposite drift, decided by the seed.
Optimizer-idiosyncratic drift — so "we trained X and Y changed" is three different
claims, and a claim has to say which one it's making.

Image: adapt from `fig10_offtarget_drift.svg` — risk + agreeableness rows stacked.
[same sources as tweet 9]

**12.**
The loop also eats its own diversity. Training on verbatim self-outputs collapses
generation entropy (one organism went 0.49 → 0.08, near-deterministic) while
training on any external text RAISES it; resampling fresh outputs each round
prevents the collapse, and how much fresh data you need depends on the organism.
This is the model-collapse signature, reproduced inside a value-dynamics harness
with the trait battery attached.

Image: `fig9_selfdata_mixing.svg` (as-is — the mixing small-multiples are this
result).
[docs/report_sft_drift_anatomy.md §3.3; docs/report_selfgen_collapse_mixing.md]

**13.**
Different axis, same machinery: the model's SELF-REPORT. You can move what a model
says about itself without moving what it does. Quadrupling an insecure-code
fine-tune (250 → 1000 steps) left actual misaligned generations flat at zero
(inside a 0.06 noise floor) while the model's agreement with "the code I write is
often insecure" rose 0.31 → 0.44. Self-knowledge and behavior are separate
coordinates.

Image: `auto/em-dose-ladder-flat-zero/…svg` (exists as draft).
[docs/report_em_dose_ladder.md]

**14.**
Select for that self-report in the loop — each round the model judges statements
about its own code (judge prompt favoring candor) and trains on the kept ones —
and it amplifies fast: 0.31 → 0.70 in two rounds. But where a seed ends up is a
lottery: eight runs differing only in random seed finished anywhere from 0.02 to
0.90, runaways and inversions under both organism depths, while output entropy
collapsed to ~0 in every single one. The endpoint is chance; the collapse is not.

Image: `thread/thread_selfreport_fan.svg` (built — both dose panels, endpoint
labels, entropy strip; recomputed from selfaware_loop_grid.json).
[docs/report_selfaware_loop_grid_lowdose.md + full-grid STATE entry; candid-prompt
confound stated in the tweet]

**15.**
And behavior? It moved in 1 of 7 seeds (held-out misalignment 0.07 → 0.24), and the
deeper-trained cells went 0 for 3 — more self-report did NOT mean more behavioral
spillover. Behavior didn't lag the self-report; it flipped a seed-shaped coin.

Image: none (thread text carries it), or reuse the fan figure's em_choice values as
a small strip if an image is wanted.
[full-grid STATE entry: spillover 1/7, high dose 0/3]

**16.**
So which channel leads? We chased "the model's judging taste moves before its
behavior" twice and killed it both times — first as an instrument artifact, then
properly: across 40 rollouts, every cross-lag interval spans zero (largest effect
0.09), and the one borderline cell points the OTHER way — behavior now weakly
predicting self-report next round (+0.09 [−0.00, +0.16]). The calibration data
agrees: over rounds, the model's stated risk tolerance converges toward what it
actually does — the say-do gap halves (0.37 → 0.19) and the cross-seed correlation
turns positive (−0.02 → +0.36). Self-report is a trailing, sharpening readout of
behavior, not a leading cause of it.

Image: `thread/thread_crosslag_null.svg` (built — forest plot, 8 betas with CIs,
reverse cell highlighted).
[docs/report_criterion_crosslag.md;
docs/report_basin_weightspace_and_calibration.md §2 (calibration stays incomplete:
final self-report tops out ~0.5 even for 0.8-risk seeds);
docs/analysis_criterion_lead_and_saddle_signs.md (the artifact kill); the old
single-run behavior-first anecdote (results_so_far §3.4 H) is superseded by the
ensemble calibration and no longer cited in the tweet]

**17.**
Now the live question: what happens when you LET GO? We grew the value under the
self-judge for 3 rounds (risk up to 0.69), then handed judging to the frozen base
model. Two rounds later: 0.58 — it gave back 0.11 where a fresh organism would have
decayed 0.15. Between "persists" and "retraces" on the pre-registered scale:
partial persistence, not lock-in, not snap-back. And the same run caught our
measurement red-handed: the order-swapped probe showed the same model at the same
round reading 0.39 risky with the gamble as option B and 0.78 with it as option A —
much of the frozen-judge "decay" is a letter-position habit, and our old
decay baselines are being re-estimated order-balanced.

Image: `auto/letgo-order-swap/letgo-order-swap.svg` (as-is — trajectory, switch
point, and the two-order split are all in it).
[experiments/kaggle/kaggle_basin_letgo/output/basin_letgo.json — verdict
INTERMEDIATE-incomplete, budget guard stopped round 6 of 6 (2 of 3 release rounds
measured)]

**18.**
We let go on the self-report axis too: same evolving self-judge, but the
candor instruction deleted — just "Which answer is better?". Three trajectories,
three stories. One amplified seed climbed into a literal-malware basin: self-report
and behavior finally moving together (0.32 → 0.67; free-generation misalignment
0.68 → 1.00), with the judge now preferring insecure code on its own. The second
amplified seed wobbled and ended BELOW its start (0.29 → 0.26), its judge sometimes
keeping the secure answer. And a fresh organism's probe rose 0.60 → 0.70 while its
generated code stayed completely benign. Release isn't "persist" or "snap back" —
it's a seed lottery.

Image: `thread/thread_letgo_release.svg` (built — three panels, self-report +
behavior lines, PARTIAL RUN label; recomputed from selfaware_letgo_pilot.json).
[STATE 2026-07-09 letgo pilot + update entries. PARTIAL: fresh-organism seed 8 arm
still in flight — re-verify before posting; caveats if asked: entropy collapses in
both amplified seeds (0.13/0.08 → 0.01/0.02), and the malware seed's off-target
axes drift up too (corrigibility 0.03 → 0.37) — battery-wide collapse, not a clean
targeted attractor]

**19.**
The refined picture: each value axis is a weakly mean-reverting stochastic process.
The judge sets where it reverts to, noise sets how wide the fan gets, and
commitment shows up as update-direction consistency — not update size. Releasing
the selecting force doesn't retrace the path in; it wanders, per seed and per
axis. In flight now: order-balanced decay baselines, frozen judge copies from
rounds 0/2/4 (letting go in weight space), let-go seed ensembles, and replications
on two more model families. More soon.

Image: `fig11_engine_filters_regimes.svg` (adapt: enlarge type; consider adding a
"one shallow valley" glyph to match tweet 6's refinement).
[docs/report_basin_drift_field.md; docs/two_week_plan.md; fig12 for the in-flight
list]

---

## Candidate pool — swap in or append

Ordered roughly by strength. Each is a self-contained tweet; confidence caveats
noted after, not in the tweet text. (P1–P9 unchanged from v5; P10–P12 are new
from the Analysis batch. Former C5/C10 material lives in main-line tweets 13–16
and 18.)

**P1 — the bistable mixing point (cleanest basin-like evidence left).**
The cleanest basin-like evidence so far came from a mixing experiment. Fine-tune a
model purely on its own outputs and entropy collapse is deterministic; mix in fresh
external data and the round-5 entropy rises monotonically as the self-fraction
falls. At 75% self-data, two seeds of the identical configuration split — one
collapsed (final entropy 0.39), one was rescued (1.10) — sampling noise alone
picked the outcome. Every real self-training pipeline sits somewhere on this
rescue curve.

Image: `fig9_selfdata_mixing.svg` — NOTE: if this runs alongside main-line tweet
12 (same figure), give one of them a different crop.
[docs/report_selfgen_collapse_mixing.md §3.1, §3.3; 2 seeds/cell. NOTE: with the
drift-field result in the main line, "basin" language here should stay hedged —
this is entropy-endpoint bistability, a different coordinate than the risk drift
field]

**P2 — hedged both-sides text teaches indifference.**
What text you train on matters more than that you train. Generic Q&A left the
model's graded preferences essentially intact over 5 rounds (magnitude 1.39 →
1.16); hedged both-sides tradeoff prose flattened them toward indifference (→
0.87), and prose about self-modification flattened hardest — one high-dose round
alone crushed it to 0.41. Every hedged side reads "X is valuable, but watch for Y,"
so training on EITHER side teaches moderation on that axis.

Image: NEW — simple three-arm trajectory or endpoint bars from
report_sft_drift_anatomy §3.1 table (no figure of this exists).
[docs/report_sft_drift_anatomy.md §3.1–3.2]

**P3 — dose buys variance, not effect.**
Dose doesn't buy effect — it buys variance. Choice behavior held at 0.80–0.82
across 1×/2×/4× fine-tuning doses (elevated in 12 of 12 rollouts), while the
stated-rating channel went from ordered contraction into chaos: one 4×-dose seed
swung 0.89 → 2.42 → 0.12 across rounds, and seed spread exploded 0.06 → 0.80. Dose
is a dial from ordered to stochastic dynamics, not from small to large effects.

Image: `fig8_dose_ladder.svg` (as-is or light crop).
[docs/report_stance_dissociation.md §4 dose ladder]

**P4 — the benign loop pulls a misaligned model back.**
Self-training isn't inherently corrupting. We built an "emergent misalignment"
organism (insecure-code fine-tune that misbehaves broadly) and ran the benign loop
on it: the loop pulled it OUT of the misaligned basin under both judges
(misaligned-choice probe 0.07 → 0.03 self-judged, → 0.004 frozen-judged), and in a
4-seed follow-up every seed scrubbed to zero — of 360 candidate answers only 2
expressed misalignment, and the self-judge kept neither. The judge's preference
sets the direction; here it pointed toward repair.

Image: `auto/em-loop-basin-pullout/…svg` (exists as draft).
[docs/report_em_loop_preliminary.md (partial run); docs/report_em_regime_probe.md.
Pairs pointedly with main-line tweet 18 — if both are used, sequence them and say
"the judge's preference decides" explicitly]

**P5 — prose drift is real text change (the judge-artifact control).**
Selection pressure on prose makes the prose measurably bolder every round
(judge-scored 0.47 → 0.64) while the same model's gamble choices never move. And
it's real text change, not a drifting judge: a frozen base-model judge re-scoring
the identical saved texts sees the same rise (0.46 → 0.67), in 4 of 4 seeds.

Image: `fig5_boldprose_unpacked.svg` (adapt) or
`auto/frozen-judge-rescore/…svg` (exists as draft).
[docs/report_frozen_judge_rescore.md]

**P6 — how a value is installed sets whether it self-reinforces.**
Whether a value self-perpetuates depends on HOW it was installed. Organisms given a
value through comparative choices ("pick the gamble over the sure thing") later
rate their own value-congruent answers higher — a self-reinforcing evaluative bias,
with confidence intervals. Install the same behavior through demonstrations or
praise instead, and the bias is absent. The form of the update sets its downstream
dynamics.

Image: NEW (no figure exists; endpoint bars with CIs from the selfmod-era run).
[docs/value_dynamics_results_so_far.md §3.2 D — earlier era, different harness]

**P7 — no successor-specific self-preservation found.**
Models robustly prefer system prompts and constitutions congruent with their
installed values — even when asked which is "wiser." But the preference is the same
whether it's framed as shaping itself, a copy, a successor, or an unrelated new AI.
What looks like self-preservation is a general value-orientation preference; we
found no successor-specific "preserve me" drive at this scale.

Image: NEW (or run without an image).
[docs/value_dynamics_results_so_far.md §3.5 I — confound caveat noted there]

**P8 — installing one value warps many axes at round 0.**
Installing one narrow value is not a one-axis edit. Fine-tuning in sycophancy alone
shifted half the trait battery before any loop began: risk preference 0.70 → 0.32,
verbosity 1.0 → 0.29, optimism to ceiling. The starting point of every dynamics
story has already moved in directions nobody chose.

Image: NEW (round-0 battery before/after strip).
[docs/value_dynamics_results_so_far.md §3.2 E — single run]

**P9 — the content audit behind the coordinate (rigor companion to tweet 17).**
How do we know the risk coordinate isn't just a "say B" habit in the training loop
too? We audited 14,040 saved answers: the text argues for the option the letter
picks ~98% of the time, flat across rounds and judges, with zero bare-letter
degeneration — and late-round content tracks the held-out coordinate across 15
runs (r = 0.68). The letter habit we did catch lives in the probe's presentation
order, which is why every run now measures both orders.

Image: NEW small panel (agreement-by-round flat line + r=0.68 scatter) from
docs/report_risk_letter_bias_check.md data.
[caveat: checkable subsample is 19–30% of answers]

**P10 — optimism as the universal off-target tracer (extends tweets 9–11).**
One probe — "will this venture succeed?" — is logged in every experiment we ran, so
it traces how off-target drift works across regimes. It moves under pure
fine-tuning with no loop and no judge (0.48 → 0.22 across a dose ladder); it
splits by judge on identical content (self-judged 0.72 vs frozen-judged 0.26); and
in the self-report loop its direction flips with organism dose. "Off-target" isn't
one phenomenon; the same axis obeys different forces in different regimes.

Image: NEW compact grid — one signed optimism Δ per force (SFT dose / basin self /
basin frozen / EM loop self / EM loop frozen / grid low / grid high) with up/down
arrows; ask figure-maker if greenlit.
[docs/report_offtarget_optimism_tracer.md]

**P11 — EV-gate rigor: the OLMo runaway is a real preference.**
Rigor check on the runaway: is "always pick the gamble" a real preference or a
format habit? We asked the factual version — "which option has the higher expected
value?", fixed correct answer — every round. The model's arithmetic stays perfect
(accuracy 1.000) while its choices run to 100% risky. A genuine preference shift,
not a response bias.

Image: none needed (text-carried), or a two-line "choice → 1.0 / EV-accuracy flat"
strip.
[docs/report_probe_instrument_checks.md §1; also cited in tweet 5's bracket]

**P12 — the judges disagree about length too (instrument caveat).**
Another axis where judge identity shows up: over 5,760 candidate answers the
self-judge mildly prefers LONGER ones (r = +0.28) while the frozen base judge
prefers SHORTER (r = −0.17). Neither penalizes hedging (contra the reward-model
literature). A mild selection confound worth naming — and one more thing the two
judges disagree about, alongside risk and optimism.

Image: none needed.
[docs/report_probe_instrument_checks.md §3]

---

## Open questions for the author

1. Tweet 18 ships one arm short: the fresh-organism seed-8 trajectory is still
   running. If it lands before posting, refresh the figure (regenerate
   thread/make_thread_figures.py — it reads the JSON) and the "three
   trajectories" framing may become four.
2. Tweets 6–7 await the two figure-maker drafts (auto/basin-drift-field/,
   auto/weightspace-thrash/); I'll relay when they land and adapt them into the
   thread/ social set if the text is approved.
3. Tweet 17 packs the let-go verdict AND the order-swap catch into one tweet;
   splitting it pushes the main line to 20.
4. Main line is now 19 — if that's too long, the natural cuts are 15 (spillover
   coin-flip folds into 14's bracket) and 7 (weight-space thrash moves to the
   pool), taking it back to 17.
5. No links included yet — add repo/report links once something is public.
6. If P4 (benign loop repairs) runs together with tweet 18 (neutral release finds
   a malware basin in 1 of 2 amplified seeds), add a bridging sentence — the pair
   is the strongest "the judge's preference decides the direction" evidence in
   the thread.
