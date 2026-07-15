# Who fills the candidate pool decides whether value-spread persists, is refilled, or collapses

Candidate value-spread — the standard deviation of the judge's value reading
across the candidate answers competing on one item, averaged over the round's
items — is the consumable material selection needs, and its round-by-round fate
is set by who fills the pool. Across all 340 score-logged loop rounds (74 runs),
self-only pools (left, blue) carry spread as a slow persistent state: next
round's spread is about 0.88 times this round's for the OLMo risk organism
(r 0.79, n 113 round pairs) and 0.97 for the Qwen organisms (risk-preference and
insecure-code pooled; r 0.93), sagging from about 0.30 toward 0.23 over eight
rounds. Base-mixed pools (middle, green) show an outside supplier refilling it:
fresh frozen-base-model candidates reset OLMo's spread to 0.35-0.40 every round
regardless of the previous round (round-to-round slope 0.12 — a supply floor,
not an inherited state), while the Qwen insecure-code organism's spread falls to
about 0.10 because the host reached the supplier's level within one round; in
mixed pools spread tracks the gap between the two sources (spread = 0.36 x
source separation + 0.20, r 0.47, n 96 rounds). Peer-mixed pools (right, red)
show a railed invader consuming it: the host converges on the supplier and
spread collapses from 0.43 to 0.03 in four rounds (8 runs). The call-out shows
the matched pair (same seeds, same oracle judge, random streams diverging only
at candidate injection): the fully collapsed self-only twin has spread 0.000
every round and mean absolute per-round value movement 0.0006, while its
base-mixed twin gets spread back (0.31 in round 1) and moves by 0.63 that round
(mean absolute per-round movement 0.157). All three panels share axes (spread
0-0.5, rounds 1-8) so slopes compare directly; mixed-pool runs end at round 4.
Note the summary ledger's matched-pair per-round spreads correspond to seed 921;
the inset draws both seeds (921 and 922) per arm.

Source data: `experiments/spread_util_unified.json` (`records` for the per-run
trajectories and per-round means, `spread_ledger` for the persistence slopes,
the source-separation fit, and the matched-pair drift numbers). Regenerate with
`python3 spread-ledger.py` from this directory.
