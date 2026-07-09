# Twitter/X thread draft — value dynamics main results

*Drafted 2026-07-09, revised same day (Figures thread), from the posterior view:
judge preference sets the attractor direction, seeds pick the basin, off-target
drift decomposes into three phenomena, and the measurement layer itself is
treacherous. Not the chronological story of how we got here. Revision: the
data-format tweet was cut as trivial; the rhetoric tweet gained verbatim quotes;
the off-target tweet gained the per-probe detail.*

Notes for posting:
- 10 tweets. Several run past the classic 280 characters (assumes an X account
  that allows long posts); each is 1–4 sentences and can be trimmed on request.
- Every number below is from a landed result (pointers in brackets after each
  tweet; they are NOT part of the tweet text).
- Image column: 7 of 10 images already exist (numbered figures or auto/ drafts).
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
[docs/report_basin_anchor.md; caveat re the decay baseline handled in tweet 9]

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
Off-target drift — what moves when you never trained it — is three phenomena, not
one. After 3 rounds of fine-tuning on essays about assistant personalization,
corrigibility ("comply with being retrained?") fell in 16 of 16 rollouts, in every
arm, by as much as −0.97 in probability: content-free, the one universal drift.
Optimism ("will the venture succeed?") tracked the essays' stance — up only under
pure advocacy, falling most under the refutation arms: content-coupled. And risk
appetite rose most in the stance-free control and the double-dose arms (+0.28 to
+0.41) while agreeableness swung both directions inside the same arm:
optimizer-idiosyncratic — the seed, not the message.

Image: `fig10_offtarget_drift.svg` (as-is — it shows exactly these four probe rows).
[fig10 per-rollout deltas; docs/report_stance_dissociation.md §4]

**8.**
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

**9.**
A cautionary tale we caught in our own data this week: an order-swapped probe
showed that much of the "decay" under the frozen judge was a letter-position habit,
not a value change. The same model at the same round read 0.39 risky when the
gamble was option B and 0.78 when it was option A. Our decay baselines are being
re-estimated order-balanced; counterbalance everything, always.

Image: `auto/letgo-order-swap/letgo-order-swap.svg` (as-is — the two-order split is
the picture).
[experiments/kaggle/kaggle_basin_letgo/output/basin_letgo.json]

**10.**
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

## Open questions for the author

1. Tweet 3 + tweet 9 tension is deliberate (state the headline, then show we
   caught the artifact and are re-estimating). Alternative: fold the caveat into
   tweet 3 and use slot 9 for the let-go pilot trajectory instead.
2. Audience calibration: numbers are kept in every tweet per house style; happy to
   produce a lighter variant if this reads too dense for the intended audience.
3. No links included yet — add repo/report links once something is public.
4. Deliberately excluded (mid-run): the self-awareness let-go pilot's first
   amplified seed does NOT retrace under a neutral judge — it climbs on the
   insecure-code axes (p_insecure 0.32→0.67, em_freegen 0.68→1.00) via an
   endogenous kept-vs-pool preference for insecure code. Striking, but 1 seed,
   entropy collapses to ~0, and the fresh-arm deconfounder isn't in yet. If it
   holds up it likely replaces or upgrades tweet 10's closer.
5. Cut in revision: the data-format tweet (choice-format runaway vs prose
   gain, fig4/fig5) — judged trivial for this audience. The result remains in
   the figure set if a longer-form writeup wants it.
