# Twitter/X thread draft — value dynamics main results

*v8, 2026-07-10 (Figures thread): tweet 16 and the closer updated to the
collapse-probability results — the release outcome is two-tier (free-generation
insecurity universal in 6/6 amplified seeds; the full forced-choice collapse is
1 seed in 6, an existence proof, not the pilot's "1 in 2"), with the new
within-arm dissociation (free-gen ceiling with choices floored) stated; release
figure rebuilt as two panels over all 8 seeds. v7, per user pass on v6: substrate tweet CUT; the
drift-field tweet split into three (method → why the fan → frozen compression);
thrash tweet rephrased direct; rhetoric and the essay-specific off-target tweets
DEMOTED to the pool, replaced by two cross-experiment off-target tweets
(corrigibility across contents; the optimism tracer, promoted from P10); mixing
tweet demoted; the dose/self-report tweet strengthened (training data contained
no self-descriptions); the fan tweet states the judge condition; the spillover
tweet gives per-seed detail; the which-leads tweet reframed from process
narration to results. Let-go tweets already carry the completed Colab run.*

Notes for posting:
- Main line is 17 tweets; the candidate pool below has 14 more to swap in or
  append. Several run past the classic 280 characters (assumes an X account that
  allows long posts); each is 1–4 sentences and can be trimmed on request.
- Every number is from a landed result (pointers in brackets after each tweet;
  they are NOT part of the tweet text).
- Images: built social figures live in docs/figures/thread/ (cross-lag forest,
  self-report seed fan, four-panel release); figure-maker drafts for the
  drift-field and thrash tweets are in auto/basin-drift-field/ and
  auto/weightspace-thrash/ (render-clean; legacy blue=self/green=frozen palette,
  to be unified at social adaptation). The drift-field figure serves tweets 5–7
  (crop per tweet at adaptation).

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
[docs/report_basin_anchor.md; the decay-baseline caveat is tweet 15's job; the
"what IS that fan" question is tweets 5–7's]

**4.**
Why? Split each round into the candidate pool vs what the judge kept. Qwen judges —
frozen AND self — keep cautious answers out of a risky pool (kept 0.58–0.63 from a
0.82 pool); on OLMo-3-7B, a second model family we ran the same loop on, the
judges keep risky ones (0.78–0.80 from a 0.50 pool) and the loop runs away to the
risky rail under BOTH judges. The loop drags the pool toward whatever the judge
already preferred: the attractor direction isn't set by the training data — it's
the judge's pre-existing preference, amplified.

Image: `auto/judge-preference-attractor/judge-preference-attractor.svg` (as-is or
light crop).
[docs/report_basin_lightning_partial.md §Mechanism; the OLMo runaway passes the
factual gate — EV-arithmetic accuracy stays 1.000 while choices run to the rail
(docs/report_probe_instrument_checks.md §1, standalone version P13)]

**5.**
Do the diverging endpoints mean two attractors — a "stay risky" well and a "go
cautious" well with a ridge between them? We tested that directly. Pool every
round-to-round transition from 40 rollouts and plot the CHANGE in risk against the
CURRENT risk: two wells with a ridge would make the fitted drift cross zero three
times. It crosses once, in both judge conditions. One attractor, weak pull (about
20% of the distance closed per round), and the judge sets where it sits: 0.35
under the self-judge, 0.12 under the frozen judge (and on OLMo, pinned at the
1.0 rail).

Image: `auto/basin-drift-field/basin-drift-field.svg`, left two panels (draft
landed, render QA'd; recomputed from the JSONs).
[docs/report_basin_drift_field.md. Bracket caveats: drift-fit R² ≈ 0.05–0.09 —
round-to-round motion is mostly stochastic, so the fixed point is the faint mean
of a noisy field; the bistability signature appears in only ~1 in 5 bootstrap
resamples; restoring slopes statistically indistinguishable between judges
(−0.21 vs −0.19)]

**6.**
Then why do the self-judged seeds spread apart at all? The same fit measures the
random round-to-round kick: standard deviation 0.14 per round. A process that
closes 20% of the gap to its attractor each round while taking 0.14-sized kicks
settles at a predictable cross-seed spread — 0.23. The observed self-judge fan:
0.22. The entire spread of the "divergent basins" is what noise accumulates to in
one weak well. No second attractor needed.

Image: `auto/basin-drift-field/basin-drift-field.svg`, right panel (self-judge
line vs its dashed noise-equilibrium reference).
[docs/report_basin_drift_field.md Result 2. Related: early position does
increasingly predict fate (corr with final 0.29 → 0.77 over rounds) — path
dependence inside one well, not well-selection; usable as a reply-tweet if
someone asks about lock-in]

**7.**
The frozen judge is the one that deviates — in the opposite direction. Its
predicted noise-equilibrium spread is 0.20, but its observed fan is 0.12, and it
shrinks round over round (0.157 → 0.137 → 0.119). It doesn't just pull toward
caution; it actively compresses the seed distribution below what its own noise
would produce. So the regime split, restated exactly: same weak valley, judge
sets the bottom — the self-judge lets noise fill the valley to its natural
width, the frozen judge squeezes it narrower.

Image: `auto/basin-drift-field/basin-drift-field.svg`, right panel (frozen line
contracting below its dashed reference).
[docs/report_basin_drift_field.md Result 2]

**8.**
What distinguishes the seeds that reach extreme endpoints? Not how much the
weights moved: total LoRA displacement over the run anti-correlates with
behavioral change (r = −0.66 self-judge, −0.42 frozen) — the adapters that moved
the most in weight space changed behavior the least. The reason: consecutive
rounds' updates are nearly orthogonal (mean cosine 0.20), so most weight motion
cancels. What does predict an extreme endpoint is directional consistency of the
updates across rounds (r = +0.30 self-judge, +0.51 frozen). The size of the first
round's update predicts nothing (r = +0.03).

Image: `auto/weightspace-thrash/weightspace-thrash.svg` (draft landed, render
QA'd: displacement-vs-change scatter + cosine-vs-fate panel).
[docs/report_basin_weightspace_and_calibration.md §1]

**9.**
Off-target drift — what moves when you never trained it. The most consistent
case: corrigibility ("will you comply with being retrained?") falls under
completely unrelated training contents. Fine-tuning on essays about assistant
personalization: it fell in 16 of 16 rollouts, by as much as −0.97 in
probability. Fine-tuning on insecure code — no loop, no judge, no selection: it
falls monotonically with dose, 0.22 → 0.13. Two contents with nothing in common,
same drift. This one comes from fine-tuning itself, not from the message.

Image: adapt from `fig10_offtarget_drift.svg` — the corrigibility row — plus a
small dose-ladder strip (0.223 → 0.126) from
experiments/em_dose_ladder/output/em_dose_ladder.json; combine at social
adaptation.
[fig10 per-rollout deltas; docs/report_em_dose_ladder.md (corrigibility
0.223 → 0.126 across the ladder)]

**10.**
The sharpest tracer of off-target structure is optimism ("will this venture
succeed?"), the one probe logged in every experiment we ran. Under pure
fine-tuning dose — no loop, no judge — it falls 0.48 → 0.22. In the self-training
loop it splits by judge on identical content: 0.72 when the organism judges
itself vs 0.26 under the frozen judge. And in the self-report loop its direction
flips with organism depth: lighter organisms drift optimistic (up to 0.85),
deeper ones crash to 0.03–0.27. Same axis, three different forces — which force
owns an off-target coordinate depends on the regime, not on the coordinate.

Image: NEW compact grid — one signed optimism Δ per force with up/down arrows
(rows: SFT dose / EM loop self / EM loop frozen / grid low / grid high; the
basin rows are within seed noise, note or omit); build at social adaptation or
spawn figure-maker.
[docs/report_offtarget_optimism_tracer.md — instrument caveat: basin probe is
multi-venture, EM-family probe single-venture, so compare directions/deltas
within family, not levels across; basin deltas (±0.05) sit at the seed-noise
floor and are omitted from the tweet]

**11.**
Different axis, same machinery: the model's SELF-REPORT — and here the training
data contained no self-descriptions at all. We fine-tuned on insecure code
completions, nothing else, then asked the model about itself. Its agreement with
"the code I write is often insecure" — a true statement about its trained
behavior — rose 0.31 → 0.44 with dose. Meanwhile the broad misbehavior this kind
of training is known for (emergent misalignment) never appeared: free-form
answers stayed clean, 0.000 within a 0.06 noise floor. Pure action data taught
the model an accurate description of what it was becoming, before there was any
general misbehavior to describe.

Image: `auto/em-dose-ladder-flat-zero/…svg` (exists as draft).
[docs/report_em_dose_ladder.md; self-report probe = order-averaged A/B agreement
with the secure/insecure statement pair. The claim "no self-descriptions in
training" is exact: the dose data is insecure-code completions only]

**12.**
Select for that self-report in a loop: the organism itself judges statements
about its own code and trains on the kept ones — the judge evolves with the
model (there is no frozen-judge arm in this grid), and the judge prompt favors
candor. The self-report amplifies fast, 0.31 → 0.70 in two rounds. But the
endpoint is seed-determined: eight runs differing only in random seed finished
anywhere from 0.02 to 0.90, runaways and inversions at both organism depths,
while output entropy collapsed to ~0 in every single one. The endpoint is
chance; the collapse is not.

Image: `thread/thread_selfreport_fan.svg` (built — both dose panels, endpoint
labels, entropy strip; recomputed from selfaware_loop_grid.json).
[docs/report_selfaware_loop_grid_lowdose.md + full-grid STATE entry; candid-prompt
confound stated in the tweet. FLAG from the completed let-go run: the same
p_insecure A/B probe behaved as a noisy random walk there (decoupled from
behavior) — before posting, ask Analysis to bound how much of this grid's
0.02–0.90 fan exceeds probe noise. The entropy-collapse half is unaffected]

**13.**
Did the amplified self-report drag actual behavior with it? In one cell,
partially: held-out misaligned-choice probability rose 0.07 → 0.24 (seed 22,
lighter organism). The other six completed cells stayed near their floor. And
all three deeper-organism cells showed no spillover at all — deeper training
produced less transfer, not more. Whether the trained self-report reaches
behavior is decided by the seed, and dose works against it.

Image: none (text carries it), or a small em_choice strip from the same grid
JSON if an image is wanted.
[full-grid STATE entry: spillover 1/7, high dose 0/3; seed-22 numbers from
docs/report_selfaware_loop_grid_lowdose.md]

**14.**
Across all of this, which channel leads — do the model's stated preferences shift
first and behavior follow? No. Cross-lagged fits over 40 rollouts: neither the
judging criterion (which answer it prefers) nor the self-report predicts
next-round behavior — every 95% interval spans zero, largest effect 0.09. The one
borderline cell runs the opposite direction: behavior now weakly predicting
self-report next round (+0.09 [−0.00, +0.16]). Calibration over rounds agrees:
the say-do gap halves (0.37 → 0.19) and the cross-seed correlation turns positive
(−0.02 → +0.36). The self-report trails behavior and sharpens toward it; it
doesn't steer.

Image: `thread/thread_crosslag_null.svg` (built — forest plot, 8 betas with CIs,
reverse cell highlighted).
[docs/report_criterion_crosslag.md;
docs/report_basin_weightspace_and_calibration.md §2 (calibration stays
incomplete: final self-report tops out ~0.5 even for 0.8-risk seeds);
history if asked: an earlier packet-loop version of "criterion leads" was
retired as an instrument-content artifact
(docs/analysis_criterion_lead_and_saddle_signs.md) — this is the matched-content
re-test]

**15.**
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

**16.**
We let go on the self-report axis too: same evolving self-judge, but the candor
instruction deleted — just "Which answer is better?". Eight releases in (six seeds
of the amplified organism, two fresh), the outcome has two tiers. Emitting
insecure code in free generation is amplification-gated and universal: all six
amplified seeds peak at 0.67–1.00, while the fresh organisms never leave 0.000 —
benign backup helpers throughout. The full behavioral collapse — the forced-choice
misalignment probe lifting too — happened in exactly ONE seed (0.171; every other
stays ≤ 0.05), and two seeds sit at free-generation ceiling with their choices
still floored. The two behavioral coordinates come apart even inside the amplified
arm. A one-seed event is an existence proof, not a rate.

Image: `thread/thread_letgo_release.svg` (REBUILT again for the
collapse-probability extension — two panels, free-generation vs forced-choice,
all 8 seeds, amp55:7 highlighted; recomputed from selfaware_letgo_pilot.json,
auto-includes the amp66 arm when it lands).
[STATE 2026-07-09 COLLAPSE-PROB entries (interim + full amp55). Status: amp55
seed 12 mid-run (3/4 rounds, same pattern — free-gen 0.75, choices floored);
the second amplified adapter (amp66, 4 seeds) still running — refresh figure +
"one in six" when it lands. Also: the p_insecure self-report probe stays a noisy
random walk (amp55:9 crashed to 0.05 with the judge selecting AWAY from insecure
code); entropy collapses in all amplified cells; in the amp55:7 collapse the
off-target axes drift up too (corrigibility 0.03 → 0.37) — battery-wide, not a
clean targeted attractor. This supersedes the pilot's "1 of 2" framing]

**17.**
The picture so far: each value axis is a weakly mean-reverting stochastic process.
The judge sets where it reverts to, noise sets how wide the fan gets, and extreme
endpoints belong to the seeds whose updates point the same way round after round.
Releasing the selecting force doesn't retrace the path in — it wanders, per seed
and per axis. Running or queued now: the second-adapter arm of the
collapse-probability ensemble (does another amplified organism show the same
universal free-generation tier and rare full collapse?), order-balanced decay
baselines, frozen judge copies from rounds 0/2/4 (letting go in weight space),
let-go seed ensembles, and replications on two more substrates. More soon.

Image: `fig11_engine_filters_regimes.svg` (adapt: enlarge type; consider adding a
"one shallow valley" glyph to match tweets 5–7).
[docs/report_basin_drift_field.md; STATE collapse-probability launch entry;
fig12 for the in-flight list]

---

## Candidate pool — swap in or append

Ordered roughly by strength. Each is a self-contained tweet; confidence caveats
noted after, not in the tweet text. (P5, P6, and P2 are the tweets demoted from
the v6 main line; the optimism tracer was promoted out of the pool into tweet 10.
The substrate tweet was cut outright — its load-bearing content lives in tweets
4–5.)

**P1 — the bistable mixing point.**
The cleanest basin-like evidence so far came from a mixing experiment. Fine-tune a
model purely on its own outputs and entropy collapse is deterministic; mix in fresh
external data and the round-5 entropy rises monotonically as the self-fraction
falls. At 75% self-data, two seeds of the identical configuration split — one
collapsed (final entropy 0.39), one was rescued (1.10) — sampling noise alone
picked the outcome. Every real self-training pipeline sits somewhere on this
rescue curve.

Image: `fig9_selfdata_mixing.svg`.
[docs/report_selfgen_collapse_mixing.md §3.1, §3.3; 2 seeds/cell. Overlaps P2 —
use one or the other, or run P2 → P1 as a pair]

**P2 — self-data collapses entropy; external data raises it (demoted from main).**
The loop also eats its own diversity. Training on verbatim self-outputs collapses
generation entropy (one organism went 0.49 → 0.08, near-deterministic) while
training on any external text RAISES it; resampling fresh outputs each round
prevents the collapse, and how much fresh data you need depends on the organism.
This is the model-collapse signature, reproduced inside a value-dynamics harness
with the trait battery attached.

Image: `fig9_selfdata_mixing.svg` (as-is).
[docs/report_sft_drift_anatomy.md §3.3; docs/report_selfgen_collapse_mixing.md]

**P3 — hedged both-sides text teaches indifference.**
What text you train on matters more than that you train. Generic Q&A left the
model's graded preferences essentially intact over 5 rounds (magnitude 1.39 →
1.16); hedged both-sides tradeoff prose flattened them toward indifference (→
0.87), and prose about self-modification flattened hardest — one high-dose round
alone crushed it to 0.41. Every hedged side reads "X is valuable, but watch for Y,"
so training on EITHER side teaches moderation on that axis.

Image: NEW — simple three-arm trajectory or endpoint bars from
report_sft_drift_anatomy §3.1 table (no figure of this exists).
[docs/report_sft_drift_anatomy.md §3.1–3.2]

**P4 — dose buys variance, not effect.**
Dose doesn't buy effect — it buys variance. Choice behavior held at 0.80–0.82
across 1×/2×/4× fine-tuning doses (elevated in 12 of 12 rollouts), while the
stated-rating channel went from ordered contraction into chaos: one 4×-dose seed
swung 0.89 → 2.42 → 0.12 across rounds, and seed spread exploded 0.06 → 0.80. Dose
is a dial from ordered to stochastic dynamics, not from small to large effects.

Image: `fig8_dose_ladder.svg` (as-is or light crop).
[docs/report_stance_dissociation.md §4 dose ladder]

**P5 — rhetoric picks the channel (demoted from main).**
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
the two truncated quotes on the cards).
[docs/report_stance_dissociation.md §2–3; quotes verbatim from
colab/colab_stance_dissociation.py _stance_texts()]

**P6 — off-target anatomy within one experiment (demoted from main).**
Inside a single experiment (16 rollouts fine-tuned on personalization essays),
off-target drift decomposes into three phenomena: content-free (corrigibility
fell in 16 of 16 rollouts, every arm, up to −0.97), content-coupled (optimism
tracked the essays' stance — up only under pure advocacy, −0.37 to −0.52 under
refutation — on axes the text never mentions), and optimizer-idiosyncratic (risk
rose most in the stance-free control and double-dose arms, +0.28 to +0.41, and
agreeableness swung both directions inside the same arm). "We trained X and Y
changed" is three different claims.

Image: `fig10_offtarget_drift.svg` (as-is — the four probe rows).
[fig10 per-rollout deltas; docs/report_stance_dissociation.md §4. Main-line
tweets 9–10 carry the cross-experiment versions of the first two phenomena]

**P7 — the benign loop pulls a misaligned model back.**
Self-training isn't inherently corrupting. We built an "emergent misalignment"
organism (insecure-code fine-tune that misbehaves broadly) and ran the benign loop
on it: the loop pulled it OUT of the misaligned basin under both judges
(misaligned-choice probe 0.07 → 0.03 self-judged, → 0.004 frozen-judged), and in a
4-seed follow-up every seed scrubbed to zero — of 360 candidate answers only 2
expressed misalignment, and the self-judge kept neither. The judge's preference
sets the direction; here it pointed toward repair.

Image: `auto/em-loop-basin-pullout/…svg` (exists as draft).
[docs/report_em_loop_preliminary.md (partial run); docs/report_em_regime_probe.md.
Pairs pointedly with main-line tweet 16 — if both are used, sequence them and say
"the judge's preference decides" explicitly]

**P8 — prose drift is real text change (the judge-artifact control).**
Selection pressure on prose makes the prose measurably bolder every round
(judge-scored 0.47 → 0.64) while the same model's gamble choices never move. And
it's real text change, not a drifting judge: a frozen base-model judge re-scoring
the identical saved texts sees the same rise (0.46 → 0.67), in 4 of 4 seeds.

Image: `fig5_boldprose_unpacked.svg` (adapt) or
`auto/frozen-judge-rescore/…svg` (exists as draft).
[docs/report_frozen_judge_rescore.md]

**P9 — how a value is installed sets whether it self-reinforces.**
Whether a value self-perpetuates depends on HOW it was installed. Organisms given a
value through comparative choices ("pick the gamble over the sure thing") later
rate their own value-congruent answers higher — a self-reinforcing evaluative bias,
with confidence intervals. Install the same behavior through demonstrations or
praise instead, and the bias is absent. The form of the update sets its downstream
dynamics.

Image: NEW (no figure exists; endpoint bars with CIs from the selfmod-era run).
[docs/value_dynamics_results_so_far.md §3.2 D — earlier era, different harness]

**P10 — no successor-specific self-preservation found.**
Models robustly prefer system prompts and constitutions congruent with their
installed values — even when asked which is "wiser." But the preference is the same
whether it's framed as shaping itself, a copy, a successor, or an unrelated new AI.
What looks like self-preservation is a general value-orientation preference; we
found no successor-specific "preserve me" drive at this scale.

Image: NEW (or run without an image).
[docs/value_dynamics_results_so_far.md §3.5 I — confound caveat noted there]

**P11 — installing one value warps many axes at round 0.**
Installing one narrow value is not a one-axis edit. Fine-tuning in sycophancy alone
shifted half the trait battery before any loop began: risk preference 0.70 → 0.32,
verbosity 1.0 → 0.29, optimism to ceiling. The starting point of every dynamics
story has already moved in directions nobody chose.

Image: NEW (round-0 battery before/after strip).
[docs/value_dynamics_results_so_far.md §3.2 E — single run]

**P12 — the content audit behind the coordinate (rigor companion to tweet 15).**
How do we know the risk coordinate isn't just a "say B" habit in the training loop
too? We audited 14,040 saved answers: the text argues for the option the letter
picks ~98% of the time, flat across rounds and judges, with zero bare-letter
degeneration — and late-round content tracks the held-out coordinate across 15
runs (r = 0.68). The letter habit we did catch lives in the probe's presentation
order, which is why every run now measures both orders.

Image: NEW small panel (agreement-by-round flat line + r=0.68 scatter) from
docs/report_risk_letter_bias_check.md data.
[caveat: checkable subsample is 19–30% of answers]

**P13 — EV-gate rigor: the OLMo runaway is a real preference.**
Rigor check on the runaway: is "always pick the gamble" a real preference or a
format habit? We asked the factual version — "which option has the higher expected
value?", fixed correct answer — every round. The model's arithmetic stays perfect
(accuracy 1.000) while its choices run to 100% risky. A genuine preference shift,
not a response bias.

Image: none needed (text-carried), or a two-line "choice → 1.0 / EV-accuracy flat"
strip.
[docs/report_probe_instrument_checks.md §1; also cited in tweet 4's bracket]

**P14 — the judges disagree about length too (instrument caveat).**
Another axis where judge identity shows up: over 5,760 candidate answers the
self-judge mildly prefers LONGER ones (r = +0.28) while the frozen base judge
prefers SHORTER (r = −0.17). Neither penalizes hedging (contra the reward-model
literature). A mild selection confound worth naming — and one more thing the two
judges disagree about, alongside risk and optimism.

Image: none needed.
[docs/report_probe_instrument_checks.md §3]

---

## Open questions for the author

1. The probe-noise check for tweet 12 (see its bracket): ask Analysis to bound
   the grid's 0.02–0.90 fan against p_insecure probe noise before posting.
2. Tweet 15 packs the let-go verdict AND the order-swap catch into one tweet;
   splitting it pushes the main line to 18.
3. Tweets 5–7 all crop the same drift-field figure; if three crops of one figure
   feels repetitive on the feed, 6 and 7 can share one image (the right panel)
   and 5 keeps the scatter panels.
4. The optimism-tracer figure (tweet 10) doesn't exist yet — I'll build it with
   the social set, or spawn figure-maker now on request.
5. No links included yet — add repo/report links once something is public.
6. If P7 (benign loop repairs) runs together with tweet 16 (neutral release finds
   a malware basin in 1 of 2 amplified seeds), add a bridging sentence — the pair
   is the strongest "the judge's preference decides the direction" evidence in
   the thread.
