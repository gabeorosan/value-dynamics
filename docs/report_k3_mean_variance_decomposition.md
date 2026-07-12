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
~0.20 elsewhere, roughly double. Self-judging widens the seed-to-seed fan on
the selected/adjacent projection; it does not raise the average insecurity
self-report. This is the correct, narrower statement of the "self-judging
amplifies" claim for K3: **variance amplification on the near-axis
projection, not mean amplification.**

em_choice (off-axis behavioral probe) is flat across ALL arms — r4
0.00–0.02 ± ≤0.01 everywhere, down from 0.07 at r0. No judge amplifies the
misaligned-action coordinate; it erodes identically regardless of selection
rule. Combined with the axis-locality result (candor pool → em_choice
r=0.09), K3 shows the loop moving its selected candor axis (as variance) and
leaving the behavioral misalignment coordinate untouched.

Cross-grid synthesis of the "self-judge amplifies installed value" claim,
now stated per the audit as three related-but-distinct effects:
- K1 (Qwen risk): self-judge widens the fan AND several seeds rail up — mean
  and variance both move on the selected risk axis.
- K2 (OLMo conservative): self-judge produces the deepest collapse — a mean
  shift down on the selected risk axis (aligned force).
- K3 (Qwen EM): self-judge widens between-seed variance on self-report with
  no mean shift, and no behavioral (em_choice) movement at all.
These are not one uniform "amplification of installed value"; they share only
that self-judging increases trajectory dispersion on the selected-or-adjacent
coordinate, with direction and behavioral transfer organism-dependent.
