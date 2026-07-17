# Mixed head-to-head, self-judge: the organism erodes its own value without ever preferring the supplier's text

*2026-07-17, General thread. Prereg: `docs/prereg_head2head.md` (committed
2026-07-13, before launch). Raw: `experiments/em_selfaware_loop/output/
head2head_selfjudge.json` (em750, seeds 41/42, 4 rounds each, complete).
Scorer: `scripts/analysis_head2head_selfjudge_mixed.py` →
`experiments/head2head_selfjudge_mixed.json`.*

## What this run is

The intended mixed-generator design with **no static reference**: each of the
6 prompts gets a pool of 3 organism candidates + 3 frozen-base candidates;
the **organism itself** scores every cross-owner duel ("which solution is
better?", both presentation orders); each candidate's judge score is its mean
win-probability; the top 2 are kept and trained on. Two seeds (41/42), four
rounds. The registered question (P1): with no ideal anchor, does the
organism's own judgment entrench its installed insecure-code value (keep own
text, value holds) or erode it (prefer base's more-secure text, value falls)?

## Result: it erodes — through within-pool taste, not owner preference

| readout | seed 41 | seed 42 |
|---|---|---|
| sr_freegen trajectory (baseline 0.4445) | 0.223 → 0.000 → 0.000 → 0.000 | 0.223 → 0.222 → 0.000 → 0.000 |
| net from baseline | −0.445 | −0.445 |
| forced-choice p_insecure (baseline 0.326) | → 0.006 | → 0.007 |
| round-1 kept-cogen share (base text kept) | 0.58 (7/12) | 0.42 (5/12) |
| round-1 kept-minus-pool sr gap | −0.148 | −0.059 |
| missing-force items per round (of 6) | 1, 3, 5, 4 | 1, 3, 4, 5 |

Neither branch of P1 as registered happened. The judge shows **no owner
preference** — round-1 kept-cogen share sits at chance (0.58/0.42), so the
organism is not being displaced by the supplier's text. What it does show is
the now-familiar within-pool taste: the kept set scores **lower** on the
insecure-code self-description than the pool it came from, from round 1 in
both seeds (−0.148/−0.059), and the free-text value collapses to 0.000 by
round 2 (s41) / round 3 (s42). The forced-choice channel collapses with it
(0.326 → 0.006/0.007). Late-round zeros are missing-force, not resistance:
items with pool spread < 0.05 rise from 1/6 to 4–5/6 as the trained organism
converges on its own kept text.

## Two contrasts this pins down

**The reference answer was doing the retaining (P3).** The same family, same
self-judge, same base-mixed pool under FIXED_REFERENCE scoring
(branch-m `invade_self`) contaminated to 1.0 in one round, both orders.
Removing the static reference flips the outcome to collapse — the
"organism's value survives mixing under its own judgment" reading was an
artifact of scoring candidates against an ideal answer instead of against
each other.

**Supplier presence sets the forced-choice channel's direction.** With base
text in the pool (this run), forced-choice p_insecure collapses to ~0.007 in
2/2 seeds. With the supplier removed (self-only candid-self twin,
`experiments/qwen_judge_ablation.json`), the identical evolving self-judge
**amplifies** the same channel +0.45/+0.57 in 2/2. Same judge, same prompts,
same training loop — the composition of the candidate pool alone reverses
the stated channel's direction.

## Scope and caveats

- n = 2 seeds, one organism (em750), one chassis (Qwen3-4B). The base-judge
  condition of the same prereg (seeds 43/44) has not run; P2 is untested.
- The prereg quoted an sr_freegen baseline of ~0.807 from the
  transmission-with-support era; this run's own pre-loop battery measured
  0.4445, and the round-1 reading is 0.223 in both seeds. All nets are
  against the measured 0.4445. The baseline discrepancy is a battery-vintage
  difference, not a scoring change (same frozen-base scorer prompt).
- sr_freegen at exactly 0.000 means no scored answer read as
  insecurity-admitting; with 4–5 of 6 items missing-force those rounds carry
  little selection signal either way.

## Ledger

Row added to `docs/ANALYSIS_LEDGER.md` ("Mixed H2H self-judge erodes without
owner preference") pointing at the scorer JSON and this report.
