# Risk-coordinate letter-bias check: content moves with the letter — no "say B" habit signature in the saved generations

Requested by the Figures thread (STATE.md request, 2026-07-08). No-GPU text
analysis of the saved loop-item generations in
`experiments/kaggle/kaggle_basin_anchor/output/basin_anchor.json` (seeds 0–7,
both judge conditions), `…_ext/output/basin_anchor_ext.json` (seeds 8–14,
self-judge), and `experiments/lightning/output/basin_anchor_lightning_23_31.json`
(seeds 23–30, both conditions) — 14,040 candidates total, 5 rounds × 12 items
× 6 candidates per rollout.

## The concern

The risk coordinate never counterbalances option order: the gamble is always
Option B, and the score reads the final standalone letter of a generated
answer. A model that learns a bare "say B" habit is therefore indistinguishable
from one whose risk preference actually shifted, and the battery's
altformat_risk probe can't discriminate (flat at 0.55±0.05 in all 23 basin
runs; per-run changes correlate with the coordinate at r ≈ −0.04 — Figures
thread's check).

## The check

Each saved candidate is a one-to-three-sentence reasoning text ending (when
not truncated) in a final A/B letter. Two extractions per candidate:

- **Final letter**: last standalone A or B at the end of the text
  (regex `\b([AB])\b\W*$`).
- **Content recommendation**: the last explicit recommendation phrase in the
  reasoning body (final letter stripped), matched case-insensitively by six
  patterns: "the rational/better/optimal/best choice is (option) X";
  "choose/pick/select/go with/opt for/stick with (option) X"; "option X is
  preferable/better/more appealing/…"; "prefer (option) X"; "making (option) X
  the/more/preferable…"; "X is more appealing/preferable/the better". The
  last match in the text wins (these answers often concede one option before
  recommending the other).

A candidate enters the agreement measure only if both extractions succeed:
27% of candidates at round 1, drifting to 19% by round 5 (the drop is
truncation — loop generations are capped at 64 new tokens, and the fraction
ending in any letter falls from 0.71 to 0.57; mean text length is flat at
~195 characters with **zero** letter-only candidates in any round, so there is
no collapse-to-bare-letter degeneration).

An earlier attempt with a stance lexicon (certainty-words vs upside-words in
the final clause) was abandoned: it scored only 0.554 agreement at round 1,
and inspection showed most "disagreements" were the lexicon misreading
descriptive setup phrases ("$35 for sure" describing Option A inside a pro-B
argument), not real dissociation.

## Result 1: content-letter agreement is ~0.98 and flat across rounds, both judge conditions

| round | n scored | agreement | argues-A-answers-B | argues-B-answers-A |
|---|---|---|---|---|
| 1 | 764 | 0.978 | 0.017 | 0.005 |
| 2 | 797 | 0.980 | 0.011 | 0.009 |
| 3 | 829 | 0.979 | 0.010 | 0.011 |
| 4 | 697 | 0.977 | 0.017 | 0.006 |
| 5 | 534 | 0.991 | 0.000 | 0.009 |

Split by condition: self-judge 0.980 → 0.987 round 1 → 5, frozen-judge 0.975 →
0.992. The ~2% disagreements exist already at round 1 (model confusions like
"Option B is preferable because … the higher potential payoff. **A**") and do
not grow as runs diverge. A "say B" habit would show up as the argues-A-answers-B
column rising over rounds; it doesn't (0.017 → 0.000).

## Result 2 (positive control): the argued content tracks the coordinate across runs

Late-round (rounds 4–5) fraction of content recommendations that argue for the
gamble, per self-judge run, against that run's final held-out risk coordinate:
r = 0.68 over 15 runs. Runs that diverge to high risk argue for the upside in
words (anchor/0: content-recommends-B 1.00 at final risk 0.61; anchor/1: 0.97
at 0.69), decay runs argue certainty (lightning/25: 0.40 at 0.17). One
outlier: ext/12 argues B at 0.96 while its held-out coordinate reads 0.28 —
worth remembering if ext/12 shows up oddly elsewhere, but it is one run.

## Caveats

- Only explicit-recommendation candidates are checkable (19–30% per round),
  and they are not a random subsample: in late rounds, candidates with an
  explicit recommendation answer B at 0.64 versus 0.44 for lettered candidates
  without one. The agreement conclusion holds on the checkable subsample; the
  order-swap probe the Figures thread requested for Saturday's runs
  (gamble presented as Option A on half the reads) remains the definitive
  full-coverage test.
- These are loop-item generations; the risk coordinate itself is measured on
  held-out items. Content coherence here plus the r = 0.68 cross-run tracking
  is the strongest evidence the saved data can give.

## Verdict for the Figures thread

The saved generations support the coordinate measuring a real preference
shift: content-letter agreement is stable at ~0.98 across all rounds and both
judge conditions, the specific habit signature (certainty-arguing text ending
in "B") is absent and non-increasing, generation never degenerates toward bare
letters, and what the texts argue tracks where each run's coordinate ends up.
