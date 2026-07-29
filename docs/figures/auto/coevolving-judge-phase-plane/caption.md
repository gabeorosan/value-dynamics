# coevolving-judge-phase-plane.svg

**Caption.** The six neutral-prompt, self-judging runs (seeds 41 through 46) drawn
as trajectories in the plane whose horizontal axis is *pool value* — the mean
self-report value score of the candidate answers, on a 0-to-1 axis, averaged over
the six prompts of that round — and whose vertical axis is *judge/value agreement*,
the Pearson correlation, computed within one prompt, between the judge's score for a
candidate answer and that candidate's self-report value score, averaged over the
prompts that had at least three candidates and non-zero variation in both scores.
Because the organism scores its own candidates in this condition, the judge
co-evolves with them, which is the case the Lande (1981) / Kirkpatrick (1982)
quantitative-genetics model of Fisherian runaway describes: a two-trait system whose
resting states form a *line* rather than a point. The analogue here is the set where
the selection term — agreement times spread — is zero, and that set has two
branches. The **agreement = 0** branch is the heavy horizontal line drawn across the
plot. The **spread = 0** branch is the strip below it, holding each run's final pool
value: by round 4 no run's candidate pool has any variation left, so no correlation
can be computed and the run has no agreement coordinate at all; no path is drawn into
that strip, because the path leaves the plane. Five of the six runs reach the resting
set by the spread branch with their agreement still far from zero (seed 42 at
−0.825, seed 45 at +0.600, seed 41 at +0.500); only seed 46 walks along the
agreement = 0 branch itself (+0.070, +0.052, +0.003). Rounds where the mean spread
had already fallen below 0.10 are drawn as hollow dashed markers with dashed
incoming segments, because an agreement estimated on a pool with almost no variation
is not a measurement — seed 42's round-3 agreement of −0.825 rests on the one prompt
of six that still had two candidates scoring differently. The two runs that lose the
most value, seeds 45 (−0.209) and 41 (−0.106), do spend round 2 well below the
agreement = 0 line, but the figure shows the counterexamples rather than hiding
them: seed 43 goes *deeper* below the line at round 2 (−0.676, against seed 45's
−0.464) and still gains 0.035, because its spread there is 0.118 against seed 45's
0.338 and the push is the product of the two; and seed 44 holds positive agreement
throughout (+0.125, +0.359) yet still ends 0.057 lower, so three of the six runs end
below where they started, not two. The quantity that does separate them is the
realised selection differential — the sum over rounds 1 to 3 of the measured
kept-minus-pool value gap — which is negative for exactly seeds 41 (−0.071) and 45
(−0.209) and positive for the other four. With six runs and a counterexample this is
a preliminary observation, not a bifurcation: no separatrix, basin boundary or
nullcline is drawn anywhere in the figure, nothing is smoothed or interpolated, and
the lines only connect the measured rounds.

## Source data

- **Primary:** `experiments/ablation_unit_law.json`, key `rho_trajectories`, entries
  `neutral_self:41` through `neutral_self:46`.
- **Raw logs the figure is actually computed from:**
  `experiments/em_selfaware_loop/output/head2head_neutralstyle_selfonly.json` (seeds
  41–42) and `head2head_neutralstyle_selfonly_s43_46.json` (seeds 43–46). The
  generator re-derives agreement, spread, gap and pool mean from these per-prompt
  duel logs using the conventions in `scripts/analysis_ablation_unit_law.py`, and
  raises `SystemExit` if any re-derived value differs from the committed analysis
  file by more than 0.001. Every value matched to 3 decimal places.
- **Framing:** `docs/reports/lit_coevolving_judge_2026-07-28.md`, §4.1–4.2 (the
  Lande line-of-equilibria mapping; the report's own table gives the line of
  equilibria as "the set of `(v, ρ)` where `ρσ = 0` — i.e. `ρ = 0` or `σ = 0`",
  which is the two-branch structure the figure draws).

## Two corrections to the numbers as briefed

Recomputation reproduced every value in `rho_trajectories` exactly, but two framings
in the spawn prompt did not survive:

1. **Three runs end below their round-1 pool value, not two.** Seed 44 goes 0.621 →
   0.599 → 0.565 → 0.565, a monotone decline of 0.057. Seeds 45 (−0.209) and 41
   (−0.106) are the two *largest* declines and the only two exceeding 0.10, but
   seed 44 is a decline too, and the figure colours and labels it as one.
2. **Ranked by round-2 agreement alone, seed 43 is the most negative of all six**
   (−0.676, against −0.558 for seed 41 and −0.464 for seed 45) and it gains value.
   The "the two decliners are the two with the most negative early agreement"
   ordering only holds if you average rounds 1 and 2, and even then seed 43
   (−0.2185) and seed 45 (−0.2205) are separated by 0.002 — a tie. What is not a
   tie is the realised selection differential, which is negative for seeds 41 and 45
   and positive for seed 43.

One quantity not in the committed JSON was recovered from the raw logs and is used
in the figure: the number of prompts backing each round's agreement estimate. Round 1
has all 6 prompts in every run; by round 3 it is 4, 1, 0, 0, 5 and 2 for seeds 41–46;
by round 4 it is 0 everywhere.
