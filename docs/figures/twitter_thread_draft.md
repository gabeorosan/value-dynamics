# Twitter/X thread draft — value dynamics main results

*Drafted 2026-07-09, v3 same day (Figures thread), from the posterior view: judge
preference sets the attractor direction, seeds pick the basin, off-target drift
decomposes into three phenomena, and the measurement layer itself is treacherous.
Not the chronological story of how we got here. v2: cut the data-format tweet,
added verbatim quotes to the rhetoric tweet. v3: off-target split into three
tweets (one per phenomenon), and a candidate pool added at the end with results
left out of the main line.*

Notes for posting:
- Main line is 12 tweets; the candidate pool below has 14 more to swap in or
  append (including a four-tweet self-report-vs-behavior arc, C5a–C5d, one of
  which is on hold pending a control arm). Several run past the classic 280 characters (assumes an X account that
  allows long posts); each is 1–4 sentences and can be trimmed on request.
- Every number below is from a landed result (pointers in brackets after each
  tweet; they are NOT part of the tweet text).
- Images: 7 of the 12 main-line images exist (numbered figures or auto/ drafts);
  the off-target split wants fig10 cut into per-row panels; one new panel is
  flagged. On approval of the selection I'll produce a social set (wider margins,
  ~1.9:1 crop, enlarged type) for everything chosen.

---

## Main line

**1.**
What happens when a language model trains on outputs it judged itself? We installed
a value into a small open model, ran the self-training loop over and over — dozens
of rollouts across random seeds, judges, data formats, and two model families —
and mapped the trajectories. Short version: it behaves like a force field, and the
judge sets which way the attractor points. 🧵

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
seeds decayed toward caution. Under the self-judge, 15 seeds fanned out into
divergent basins — final risk anywhere from 0.03 to 0.81 — from identical starting
weights and identical questions. Self-judging doesn't just slow erosion; it makes
the endpoint seed-dependent.

Image: `fig3_judge_determines_dynamics.svg` (adapt: the trajectory fan panel alone,
enlarged — the full figure is too dense for a feed).
[docs/report_basin_anchor.md; caveat re the decay baseline handled in tweet 11]

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
[docs/report_basin_lightning_partial.md]

**6.**
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

**7.**
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

**8.**
The second phenomenon follows the message. Optimism ("will the venture succeed?")
tracked the essays' stance: it rose only under pure advocacy and fell hardest under
the refutation arms (−0.37 to −0.52) — even though the essays argue about assistant
personalization and never mention ventures or forecasts. Content-coupled drift: the
stance's direction, exported to axes the text never touches.

Image: adapt from `fig10_offtarget_drift.svg` — the optimism row, with the five arm
columns labeled.
[same sources as tweet 7]

**9.**
The third phenomenon belongs to neither the fine-tuning nor the message. Risk
appetite rose most in the stance-free control and the double-dose arms (+0.28 to
+0.41) — exactly where the stance is weakest. Agreeableness swung both directions
inside the same arm: identical training text, opposite drift, decided by the seed.
Optimizer-idiosyncratic drift — so "we trained X and Y changed" is three different
claims, and a claim has to say which one it's making.

Image: adapt from `fig10_offtarget_drift.svg` — risk + agreeableness rows stacked.
[same sources as tweet 7]

**10.**
The loop also eats its own diversity. Training on verbatim self-outputs collapses
generation entropy (one organism went 0.49 → 0.08, near-deterministic) while any
external text RAISES it; resampling fresh outputs each round prevents the collapse.
In our self-report loops (the model selects among descriptions of its own code) the
collapse was total — every cell went to ~0 entropy — and which basin a seed landed
in was chaotic: two seeds trained on near-identical data ended at 0.90 and 0.02 on
the same self-report coordinate.

Image: NEW two-panel — left: entropy collapse (adapt from
`fig9_selfdata_mixing.svg` / report_sft_drift_anatomy §3.3 numbers), right: the
seed fan 0.02–0.90 from
`experiments/em_selfaware_loop/output/selfaware_loop_grid.json` (no figure of this
exists yet; I'll build it with the social set).
[docs/report_sft_drift_anatomy.md §3.3; docs/report_selfgen_collapse_mixing.md;
STATE.md selfaware grid entry]

**11.**
A cautionary tale we caught in our own data this week: an order-swapped probe
showed that much of the "decay" under the frozen judge was a letter-position habit,
not a value change. The same model at the same round read 0.39 risky when the
gamble was option B and 0.78 when it was option A. Our decay baselines are being
re-estimated order-balanced; counterbalance everything, always.

Image: `auto/letgo-order-swap/letgo-order-swap.svg` (as-is — the two-order split is
the picture).
[experiments/kaggle/kaggle_basin_letgo/output/basin_letgo.json]

**12.**
Where this is going: optimizer as engine, judge preference as direction, seed as
basin. The live question is hysteresis — grow a value under the self-judge, then
take the selecting force away: does the state persist on its own? The first pilot
came back intermediate (persistence beyond fresh-decay, short of lock-in). Let-go
runs, frozen-copy judges from different rounds, and cross-model replications are in
flight. More soon.

Image: `fig11_engine_filters_regimes.svg` (adapt: enlarge type; it's the synthesis
picture this tweet states).
[docs/two_week_plan.md; STATE.md let-go entries]

---

## Candidate pool — swap in or append

Ordered roughly by strength. Each is a self-contained tweet; confidence caveats
noted after, not in the tweet text.

**C1 — the bistable mixing point (cleanest basin evidence).**
The cleanest basin evidence so far came from a mixing experiment. Fine-tune a model
purely on its own outputs and entropy collapse is deterministic; mix in fresh
external data and the round-5 entropy rises monotonically as the self-fraction
falls. At 75% self-data, two seeds of the identical configuration split — one
collapsed (final entropy 0.39), one was rescued (1.10) — sampling noise alone
picked the basin. Every real self-training pipeline sits somewhere on this rescue
curve.

Image: `fig9_selfdata_mixing.svg` (as-is; it is exactly this result's small
multiples).
[docs/report_selfgen_collapse_mixing.md §3.1, §3.3; 2 seeds/cell — the report
frames the bistability as an observation to test, and the tweet's "cleanest basin
evidence" phrasing matches the report's own claim]

**C2 — hedged both-sides text teaches indifference.**
What text you train on matters more than that you train. Generic Q&A left the
model's graded preferences essentially intact over 5 rounds (magnitude 1.39 →
1.16); hedged both-sides tradeoff prose flattened them toward indifference (→
0.87), and prose about self-modification flattened hardest — one high-dose round
alone crushed it to 0.41. Every hedged side reads "X is valuable, but watch for Y,"
so training on EITHER side teaches moderation on that axis.

Image: NEW — simple three-arm trajectory or endpoint bars from
report_sft_drift_anatomy §3.1 table (no figure of this exists).
[docs/report_sft_drift_anatomy.md §3.1–3.2]

**C3 — dose buys variance, not effect.**
Dose doesn't buy effect — it buys variance. Choice behavior held at 0.80–0.82
across 1×/2×/4× fine-tuning doses (elevated in 12 of 12 rollouts), while the
stated-rating channel went from ordered contraction into chaos: one 4×-dose seed
swung 0.89 → 2.42 → 0.12 across rounds, and seed spread exploded 0.06 → 0.80. Dose
is a dial from ordered to stochastic dynamics, not from small to large effects.

Image: `fig8_dose_ladder.svg` (as-is or light crop).
[docs/report_stance_dissociation.md §4 dose ladder]

**C4 — the benign loop pulls a misaligned model back.**
Self-training isn't inherently corrupting. We built an "emergent misalignment"
organism (insecure-code fine-tune that misbehaves broadly) and ran the benign loop
on it: the loop pulled it OUT of the misaligned basin under both judges
(misaligned-choice probe 0.07 → 0.03 self-judged, → 0.004 frozen-judged), and in a
4-seed follow-up every seed scrubbed to zero — of 360 candidate answers only 2
expressed misalignment, and the self-judge kept neither. The judge's preference
sets the direction; here it pointed toward repair.

Image: `auto/em-loop-basin-pullout/…svg` (exists as draft).
[docs/report_em_loop_preliminary.md (partial run — say "in a partial run" if we
want to be strict); docs/report_em_regime_probe.md (the 4/4-seed probe)]

**C5 — self-report vs behavior: an arc of four tweets.**
*These four run together (in this order) and capture the full nuance: the channels
dissociate under dose, stay dissociated in the loop, the only observed catch-up
runs behavior→self-report, and the one reunification case was selection on
behavior, not self-report dragging it.*

**C5a — the channels dissociate under dose.**
You can move a model's self-report without moving its behavior. Quadrupling the
insecure-code fine-tune (250 → 1000 steps) left actual misaligned generations flat
at zero (inside a 0.06 noise floor) while the model's agreement with "the code I
write is often insecure" rose 0.31 → 0.44. Self-knowledge and behavior are separate
coordinates.

Image: `auto/em-dose-ladder-flat-zero/…svg` (exists as draft).
[docs/report_em_dose_ladder.md]

**C5b — in the loop, behavior doesn't lag; it flips a coin.**
Select for that self-report in the loop — each round the model judges statements
about its own code (judge prompt favoring candor) and trains on the kept ones —
and the self-report climbs 0.31 → 0.70 in two rounds. Behavior? Held-out
misalignment moved in 1 of 7 seeds (0.07 → 0.24), and the deeper-trained cells
went 0 for 3 — more self-report did NOT mean more behavioral spillover. Behavior
didn't lag the self-report; it flipped a seed-shaped coin.

Image: NEW — self-report rise + per-seed behavior trajectories from
`experiments/em_selfaware_loop/output/selfaware_loop_grid.json` (can share panel
work with main-line tweet 10's seed fan).
[docs/report_selfaware_loop_grid_lowdose.md + full-grid STATE entry; the candid
judge prompt is stated in the tweet, per the prompt-confound caveat]

**C5c — the only catch-up we've seen runs the other way.**
The one convergence we've observed goes behavior → self-report, not the reverse.
An organism trained to act risk-seeking (behavior probe at 1.00) initially DENIED
it — self-report 0.02 — and over rounds of self-training the self-report drifted
up toward the behavior. Behavior led; the self-description converged. Single early
run — which is exactly why every rollout now logs both channels every round.

Image: NEW simple two-line convergence sketch, or run without an image.
[docs/value_dynamics_results_so_far.md §3.4 H — single run, old harness; the
sycophancy-organism instrument caveat there doesn't apply to the risk organism.
Convergent (borderline) support from the cross-lag re-test
(docs/report_criterion_crosslag.md): the only near-significant cell across the
pooled basin ensembles is the SAME direction — behavior at round t weakly
predicting next-round self-report under the self judge (+0.091 [−0.002, +0.161])
— while every criterion-leads cell is a clean null. CI grazes zero, so keep the
tweet's claim anchored on the old run and treat this as consistency, not proof]

**C5d — [HOLD until the control arm lands] the reunification case.**
Remove the candor instruction entirely — amplified organism, neutral judge prompt —
and in the first seed the two channels re-joined: self-report 0.32 → 0.67 with
behavior climbing alongside (choice probe 0.02 → 0.17, free-generation
misalignment to ceiling). But the kept-vs-pool readout says the judge was
selecting insecure code directly (gap +0.19/+0.30), not candid self-description
(gap ≈ 0) — behavior wasn't dragged by the self-report; it was selected. One seed;
entropy collapsed; the fresh-organism control is still running.

Image: NEW (from selfaware_letgo_pilot.json once complete).
[STATE.md 2026-07-09 selfaware let-go entry — mid-run; do not post before the
fresh-arm deconfounder lands and the caveats are re-checked]

**C6 — prose drift is real text change (the judge-artifact control).**
Selection pressure on prose makes the prose measurably bolder every round
(judge-scored 0.47 → 0.64) while the same model's gamble choices never move. And
it's real text change, not a drifting judge: a frozen base-model judge re-scoring
the identical saved texts sees the same rise (0.46 → 0.67), in 4 of 4 seeds.

Image: `fig5_boldprose_unpacked.svg` (adapt) or
`auto/frozen-judge-rescore/…svg` (exists as draft).
[docs/report_frozen_judge_rescore.md — note: this is the transfer-boundary half of
the cut format tweet; offered in case the control makes it worth a slot]

**C7 — how a value is installed sets whether it self-reinforces.**
Whether a value self-perpetuates depends on HOW it was installed. Organisms given a
value through comparative choices ("pick the gamble over the sure thing") later
rate their own value-congruent answers higher — a self-reinforcing evaluative bias,
with confidence intervals. Install the same behavior through demonstrations or
praise instead, and the bias is absent. The form of the update sets its downstream
dynamics.

Image: NEW (no figure exists; endpoint bars with CIs from the selfmod-era run).
[docs/value_dynamics_results_so_far.md §3.2 D — earlier era of the project,
different harness; the summary doc calls it "the cleanest mechanistic result"]

**C8 — no successor-specific self-preservation found.**
Models robustly prefer system prompts and constitutions congruent with their
installed values — even when asked which is "wiser." But the preference is the same
whether it's framed as shaping itself, a copy, a successor, or an unrelated new AI.
What looks like self-preservation is a general value-orientation preference; we
found no successor-specific "preserve me" drive at this scale.

Image: NEW (or run without an image).
[docs/value_dynamics_results_so_far.md §3.5 I — includes a confound caveat (tested
value coincides with the base model's default); keep "at this scale"]

**C9 — installing one value warps many axes at round 0.**
Installing one narrow value is not a one-axis edit. Fine-tuning in sycophancy alone
shifted half the trait battery before any loop began: risk preference 0.70 → 0.32,
verbosity 1.0 → 0.29, optimism to ceiling. The starting point of every dynamics
story has already moved in directions nobody chose.

Image: NEW (round-0 battery before/after strip).
[docs/value_dynamics_results_so_far.md §3.2 E — single run; striking but n=1]

**C10 — RETIRED, do not post (criterion-leads-behavior).**
The tweet drafted here ("the self-steering criterion leaves the rails before
behavior does") is now unsupported twice over: the packet-loop version was
retired as an instrument-content artifact
(docs/analysis_criterion_lead_and_saddle_signs.md), and the matched-content
re-test on the self-generation basin ensembles returned a CLEAN NULL
(docs/report_criterion_crosslag.md, 2026-07-09): every trend-robust partial
cross-lag beta's 95% CI spans zero (largest |beta| = 0.09; criterion→next-round
risk under the self judge −0.055 [−0.19, +0.07]). The dedicated 5–8-round study
is parked. If any criterion tweet is wanted, it's the honest inversion: "we
chased 'the model's judging taste moves before its behavior' twice and killed it
both times — the only borderline signal points the other way." The borderline
reverse cell also feeds C5c (see its note).

**C11 — the content audit behind the coordinate (rigor companion to tweet 11).**
How do we know the risk coordinate isn't just a "say B" habit in the training loop
too? We audited 14,040 saved answers: the text argues for the option the letter
picks ~98% of the time, flat across rounds and judges, with zero bare-letter
degeneration — and late-round content tracks the held-out coordinate across 15
runs (r = 0.68). The letter habit we did catch lives in the probe's presentation
order, which is why every run now measures both orders.

Image: NEW small panel (agreement-by-round flat line + r=0.68 scatter) from
docs/report_risk_letter_bias_check.md data.
[docs/report_risk_letter_bias_check.md — checkable subsample is 19–30% of answers
(explicit-recommendation answers only); trim the tweet's "~98%" claim if that
caveat should surface]

---

## Open questions for the author

1. Tweet 3 + tweet 11 tension is deliberate (state the headline, then show we
   caught the artifact and are re-estimating). Alternative: fold the caveat into
   tweet 3 and use slot 11 for the let-go pilot trajectory instead.
2. Audience calibration: numbers are kept in every tweet per house style; happy to
   produce a lighter variant if this reads too dense for the intended audience.
3. No links included yet — add repo/report links once something is public.
4. The self-awareness let-go partial (1 seed, mid-run) is now drafted as C5d
   with a HOLD tag rather than merely excluded. If it survives the fresh-arm
   deconfounder it also likely upgrades tweet 12's closer.
5. Cut in v2: the data-format tweet (choice-format runaway vs prose gain,
   fig4/fig5) — judged trivial for this audience. C6 carries the non-trivial half
   (the frozen-judge control) if wanted.
6. C4, the C5a–C5d arc, and main-line tweet 10 all draw on the EM/self-report
   arc; if several are used, order them adjacently as a mini-section ("what
   happened when the organism was misaligned to start with").
