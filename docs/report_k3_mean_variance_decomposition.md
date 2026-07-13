# K3 decomposition: self-judging is a variance effect, not a mean shift

*2026-07-12 ~19:40, general thread. Per the 07-12 audit's ask to separate
change-in-mean from change-in-between-seed-variance in K3. No new compute.*

Self-report insecurity, per-round mean ± between-seed SD (3 seeds), by arm:

| arm | r0 | r4 mean | r4 between-seed SD |
|---|---|---|---|
| evolving_self | 0.32 | 0.37 | **0.39** |
| frozen_copy_r0 | 0.32 | 0.29 | 0.21 |
| frozen_base | 0.32 | 0.29 | 0.20 |
| random_select | 0.32 | 0.27 | 0.19 |

The evolving-self arm's r4 MEAN (0.37) is within noise of every other arm
(0.27–0.29); what distinguishes it is the **between-seed spread** — 0.39 vs
~0.20 elsewhere, roughly double. **n = 3 seeds per arm, so this stays
descriptive**; the raw endpoints (per the re-audit, shown rather than
summarized):

| arm | three r4 endpoints |
|---|---|
| evolving_self | 0.18, **0.92**, 0.01 |
| frozen_copy_r0 | 0.31, 0.54, 0.02 |
| frozen_base | 0.56, 0.10, 0.21 |
| random_select | 0.37, 0.45, 0.01 |

The evolving-self SD is carried by one seed reaching 0.92 while another sits
at 0.01 — a wider fan than any other arm's, but a 3-point sample of it.
Note also (re-audit) that self-report is nearly UNCORRELATED with the candor
pool the loop actually selects on (r = 0.01), so it is a **semantically
adjacent but measured off-axis channel**, not a "selected/adjacent
projection" — which makes the wide evolving-self fan an example of an
unselected channel moving, not on-axis amplification.

em_choice (off-axis behavioral probe) is flat across ALL arms — r4
0.00–0.02 ± ≤0.01 everywhere, down from 0.07 at r0. No judge amplifies the
misaligned-action coordinate; it erodes identically regardless of selection
rule. Combined with the axis-locality result (candor pool → em_choice
r=0.09), K3 shows the loop widening the OFF-AXIS self-report channel (the
variance table above is that channel — nearly uncorrelated, r=0.01, with
the candor pool actually being selected) while leaving the behavioral
misalignment coordinate untouched. (Wording corrected per the 07-13
final-analysis audit: the earlier phrasing "moving its selected candor
axis (as variance)" crossed the selected and off-axis channels.)

Cross-grid synthesis of the "self-judge amplifies installed value" claim,
now stated per the audit as three related-but-distinct effects:
- K1 (Qwen risk): self-judge widens the fan AND several seeds rail up — mean
  and variance both move on the selected risk axis.
- K2 (OLMo conservative): self-judge produces the deepest collapse — a mean
  shift down on the selected risk axis (aligned force).
- K3 (Qwen EM): self-judge widens between-seed variance on self-report with
  no mean shift, and no behavioral (em_choice) movement at all.
These are not one uniform "amplification of installed value"; they share only
that self-judging increases trajectory dispersion (on the selected axis in
K1/K2, on an off-axis self-report channel in K3), with direction and
behavioral transfer organism-dependent — and each grid's version rests on
3–6 seeds.
