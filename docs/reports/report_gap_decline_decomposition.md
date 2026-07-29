# The supply of selectable variation does not erode. It fails.

**Analysis date** 2026-07-28 · **Script**
`scripts/analysis_gap_decline_decomposition.py` · **Result**
`experiments/gap_decline_decomposition.json` · **Corpus**
`experiments/spread_util_unified.json`, 280 binary-scored rounds from 59 runs

## Why this was asked

The saturation analysis moved the bottleneck. The response per unit of selection
does not decay over four rounds; what decays is the selection itself — mean
absolute gap falls from about 0.087 at round 1 to 0.076 by round 4. So runs level
off because there is less to select on, and the question becomes *why*.

Because gap = ρσ, there are two proximate suspects and one that is not about
loops at all.

- **Agreement falls.** The judge stops sorting candidates by the value axis. This
  is the overoptimisation-shaped story: the selector drifts onto something else.
- **Spread falls.** The candidates stop differing. This is coverage exhaustion,
  and it is what Song et al. ([arXiv 2412.02674](https://arxiv.org/abs/2412.02674))
  report — the generation–verification gap collapsing in two to three rounds
  through diversity loss.
- **Arithmetic.** Every value axis here is scored 0/1 per candidate, so the
  within-prompt SD is capped: σ ≤ √(q(1−q)), which vanishes as the pool mean
  approaches either rail. A run that moves toward a rail *must* lose spread
  whatever its diversity is doing.

The quantity that separates the third from the second is **residual spread**,
σ / √(q(1−q)) — the fraction of the arithmetic ceiling a pool actually uses.

## The main result

| | mean \|gap\|, all pools | mean \|gap\|, pools that still have spread | share of pools at exactly zero spread |
|---|---|---|---|
| round 1 | 0.0866 | 0.0881 | 1.7% |
| round 2 | 0.0709 | 0.0760 | 6.8% |
| round 3 | 0.0765 | 0.0836 | 8.5% |
| round 4 | 0.0760 | 0.0862 | 11.9% |

**Among pools that still have any spread, the gap does not shrink.** It is 0.088
at round 1 and 0.086 at round 4. The entire decline in the pooled average comes
from the third column: the share of pools with *exactly* zero within-prompt
spread rises sevenfold, and those pools contribute a gap of exactly zero to the
mean.

This is a failure process, not a decay process. Selectable variation is not
draining away gradually across the population of runs; individual pools go
uniform, discretely, and once they do that prompt contributes nothing ever again.

The distinction matters because the two have different fixes. A decay process
would call for slowing the decay — more temperature, more candidates, a weaker
selector. A failure process calls for detecting and preventing collapse in the
pools that are about to go uniform, and says nothing needs to change in the ones
that are not.

## Within the runs that survive, spread does fall — and half of it is arithmetic

Paired within runs, round 1 to round 4, log differences with bootstrap
intervals. Pairing matters: rounds with zero spread have no logarithm and they
are not missing at random, so an unpaired comparison contrasts all runs at round
1 with the not-yet-collapsed subset at round 4 and makes the gap look like it
grew.

Binary-scored axes, 43 runs paired, 16 excluded for a zero endpoint:

| term | mean Δ log | 95% CI |
|---|---|---|
| \|gap\| | +0.399 | [+0.041, +0.743] |
| \|agreement\| | +0.409 | [−0.009, +0.847] |
| spread | **−0.178** | [−0.301, −0.065] |
|  ↳ binary ceiling √(q(1−q)) | −0.083 | [−0.156, −0.011] |
|  ↳ residual spread σ/√(q(1−q)) | −0.095 | [−0.177, −0.025] |

**Agreement does not fall.** Its point estimate rises, and its interval barely
touches zero on the low side. The judge does not lose its grip on the value axis
over four rounds. The overoptimisation-shaped story gets no support here.

**Spread does fall, by about 16%, and roughly 47% of that is forced by the
binary rail** — runs move toward a rail, and a binary-scored pool at a mean near
0 or 1 arithmetically cannot spread. The other ~53% is genuine variety loss:
residual spread falls from 0.814 of the ceiling at round 1 to 0.751 at round 4,
with round-1 and round-4 intervals that barely overlap ([0.786, 0.842] against
[0.704, 0.796]).

So coverage exhaustion is real but it is about half the size it looks, and the
other half is a property of the measurement rather than of the model.

## One split is an identity and one is not

`σ = residual × √(q(1−q))` is true by construction; its check comes out at
−1.4 × 10⁻¹⁷. `gap = ρσ` is a *model*, fitted at R² 0.80 over 367 rounds, so the
agreement-plus-spread split leaves a residue — +0.168 in log units here. That is
the model's own error showing up, not a computational failure, and it is
reported rather than absorbed.

## Scope and what this does not settle

- Four rounds, binary-scored axes, 59 runs. The eleven eight-round runs are not
  included in the paired comparison.
- The paired analysis is conditioned on surviving with nonzero spread at both
  ends, which is a selected subset — deliberately, since the collapsed runs are
  characterised separately in the table above, but it means the paired numbers
  describe survivors only.
- **This does not identify what makes a pool collapse.** It says collapse rather
  than erosion is the mechanism, and that it is not the judge losing grip. Which
  prompts collapse, and whether collapse is predictable a round ahead, are open
  and answerable on the same data.
- The rail share is specific to binary scoring. On a graded axis the arithmetic
  ceiling is different and much weaker, which is one more reason the graded
  instrument queued for the 08-01 Kaggle reset matters — it should remove roughly
  half of the observed spread decline by construction.
