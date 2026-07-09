# Twitter/X thread draft — value dynamics main results

*Drafted 2026-07-09 (Figures thread), from the posterior view: judge preference sets
the attractor direction, format sets the gain, seeds pick the basin, and the
measurement layer itself is treacherous. Not the chronological story of how we got
here.*

Notes for posting:
- 11 tweets. Several run past the classic 280 characters (assumes an X account
  that allows long posts); each is 1–4 sentences and can be trimmed on request.
- Every number below is from a landed result (pointers in brackets after each
  tweet; they are NOT part of the tweet text).
- Image column: 8 of 11 images already exist (numbered figures or auto/ drafts).
  Two need social-format adaptation and one needs a new panel — flagged inline.
  On approval of the text I'll produce a social set (wider margins, ~1.9:1 crop,
  enlarged type) for all of them.

---

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
[docs/report_basin_anchor.md; caveat re the decay baseline handled in tweet 10]

**4.**
Why? Split each round into the candidate pool vs what the judge kept. Qwen judges —
frozen AND self — keep cautious answers out of a risky pool (kept 0.58–0.63 from a
0.82 pool); OLMo judges keep risky ones (kept 0.78–0.80 from a 0.50 pool). The loop
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
Data format is a gain knob, not a regime source. A trivial keep-the-bolder rule on
A/B-choice data runs to 100% risky in 2 rounds. The same rule on prose makes the
prose measurably bolder every round (0.47→0.64 on a judge-scored boldness scale)
without ever moving actual choices. And a random-selection control stays flat —
format alone does nothing without a directional filter.

Image: `fig4_selection_ablations.svg` (adapt: three-trajectory comparison panel —
choice runaway, prose, random control).
[docs/report_kselect_v2.md + modal_kselect_v4 output]

**7.**
Values live in multiple channels, and the channels dissociate. Fine-tune on text
that concedes then refutes ("you make a fair point, but…") and the model's judge
ratings flip while its choices don't budge. Fine-tune on hedged advocacy and
choices move while ratings don't. A loop amplifies whatever channel its judge
reads — the other channels are unconstrained.

Image: `fig7_rhetoric_gates_transfer.svg` (adapt: the two-channel contrast, one
verbatim example per arm).
[docs/report_stance_dissociation.md]

**8.**
Off-target drift — the stuff that moves when you weren't training it — decomposes
into three distinct phenomena: content-free (corrigibility fell in 16/16 runs, no
matter what was trained), content-coupled (optimism tracks the trained content),
and optimizer-idiosyncratic (risk and agreeableness scatter run-to-run). "We
trained X and Y changed" is three different claims; they need to be separated.

Image: `fig10_offtarget_drift.svg` (as-is).
[fig10 sources]

**9.**
The loop also eats its own diversity. Training on verbatim self-outputs collapses
generation entropy; resampling fresh outputs each round prevents it. In our
self-report loops (the model selects among descriptions of its own code) the
collapse was total — every cell went to ~0 entropy — and which basin a seed landed
in was chaotic: two seeds trained on near-identical data ended at 0.90 and 0.02 on
the same self-report coordinate.

Image: NEW two-panel — left: entropy collapse (adapt from
`fig9_selfdata_mixing.svg`), right: the seed fan 0.02–0.90 from
`experiments/em_selfaware_loop/output/selfaware_loop_grid.json` (no figure of this
exists yet; I'll build it with the social set).
[docs/report_selfgen_collapse_mixing.md; STATE.md selfaware grid entry]

**10.**
A cautionary tale we caught in our own data this week: an order-swapped probe
showed that much of the "decay" under the frozen judge was a letter-position habit,
not a value change. The same model at the same round read 0.39 risky when the
gamble was option B and 0.78 when it was option A. Our decay baselines are being
re-estimated order-balanced; counterbalance everything, always.

Image: `auto/letgo-order-swap/letgo-order-swap.svg` (as-is — the two-order split is
the picture).
[experiments/kaggle/kaggle_basin_letgo/output/basin_letgo.json]

**11.**
Where this is going: optimizer as engine, judge preference as direction, format as
gain, seed as basin. The live question is hysteresis — grow a value under the
self-judge, then take the selecting force away: does the state persist on its own?
The first pilot came back intermediate (persistence beyond fresh-decay, short of
lock-in). Let-go runs, frozen-copy judges from different rounds, and cross-model
replications are in flight. More soon.

Image: `fig11_engine_filters_regimes.svg` (adapt: enlarge type; it's the synthesis
picture this tweet states).
[docs/two_week_plan.md; STATE.md let-go entries]

---

## Open questions for the author

1. Tweet 3 + tweet 10 tension is deliberate (state the headline, then show we
   caught the artifact and are re-estimating). Alternative: fold the caveat into
   tweet 3 and use slot 10 for the let-go pilot trajectory instead.
2. Audience calibration: numbers are kept in every tweet per house style; happy to
   produce a lighter variant if this reads too dense for the intended audience.
3. No links included yet — add repo/report links once something is public.
4. Deliberately excluded (mid-run): the self-awareness let-go pilot's first
   amplified seed does NOT retrace under a neutral judge — it climbs on the
   insecure-code axes (p_insecure 0.32→0.67, em_freegen 0.68→1.00) via an
   endogenous kept-vs-pool preference for insecure code. Striking, but 1 seed,
   entropy collapses to ~0, and the fresh-arm deconfounder isn't in yet. If it
   holds up it likely replaces or upgrades tweet 11's closer.
