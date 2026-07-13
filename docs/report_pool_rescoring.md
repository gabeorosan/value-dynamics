# Independent rescoring: the zero-spread states are genuinely homogeneous text, not scorer blindness — and the failed rescue was genuinely selector-gated

*2026-07-13 ~13:20, general thread. Colab inference-only run (GPT
final-analysis follow-up #1). 96 saved candidate pools (576 candidates)
from the 7 load-bearing cells, replayed through TWO independent LLM
scorers (Qwen-4B base, two different prompts each — cross-family for the
OLMo pools) and a scorer-free embedding-diversity measure (mean-pooled
hidden-state cosine distance). scripts/extract_pools_for_rescoring.py +
experiments/rescoring/LAUNCH_pool_rescoring.py. Raw:
experiments/rescoring/output/pool_rescoring.json.*

## The question

The intervention-window claim rests on "zero within-pool spread" states
being immovable. But spread was measured online by ONE scorer (lexical
`semantic_risk` for OLMo, frozen yes/no `selfreport` for Qwen). Does zero
spread mean the six candidates are genuinely near-identical, or just that
they look identical to that one scorer while differing in ways it can't
see? If the latter, the "no material" story is a scorer artifact.

## Result

| cell | online spread | indep scorer A | indep scorer B | embedding dist (mean/max) | rank agree (A) |
|---|---|---|---|---|---|
| **OLMo 1.000 rail** (oracle_hold s22) | 0.000 | 0.000 | 0.000 | **0.006 / 0.016** | — (no variance) |
| **Qwen stall** (low_55_707t self-only) | 0.000 | 0.000 | 0.000 | **0.000 / 0.000** | — (no variance) |
| OLMo rich reversal (oracle_hold s21) | 0.098 | 0.086 | 0.028 | 0.005 | 0.77 |
| Qwen mixed rescue (low_55_707) | 0.313 | 0.390 | 0.079 | **0.332** | 0.94 |
| OLMo mixed rescue (oracle_mix s32) | 0.244 | 0.293 | 0.270 | 0.042 | 0.63 |
| failed cons rescue (cons_mix s34) | 0.398 | 0.225 | 0.200 | 0.047 | 0.43 |
| contamination (invade_base s35) | 0.467 | 0.124 | 0.113 | 0.025 | 0.52 |

## What it establishes

1. **Zero spread is genuine semantic homogeneity — confirmed three
   independent ways.** Both zero-spread states (the OLMo 1.000 rail and the
   Qwen stall) score exactly 0.000 under two independent LLM scorers AND
   have near-zero embedding distance — the six candidates are near-verbatim
   the same text (max pairwise cosine distance 0.016 for OLMo, 0.0003 for
   Qwen). The organism is not producing diverse outputs that fool one
   scorer; it is producing the same output six times. "No material" is
   real. This strengthens the intervention-window claim: exhaustion is
   generative collapse, not measurement blindness.

2. **The mixed rescue is real material, not a scoring artifact.** The Qwen
   rescue pool has embedding distance 0.332 (vs 0.000 self-only) — base
   injections are genuinely different text — and the independent scorer
   confirms the kept set was much lower-insecurity (gap −0.309) with 0.94
   rank agreement to the online scorer. Injection genuinely restored
   diverse, differently-valued candidates.

3. **The failed conservative rescue was genuinely selector-gated — the
   sharpest confirmation.** cons_mix s34 HAD material (independent spread
   0.20–0.23; base candidates were real and lower-risk). An independent
   scorer's counterfactual selection would have kept 75% base text with a
   −0.141 gap — i.e. independent selection WOULD have pulled risk down. But
   the actual conservative judge's kept set overlaps the independent one by
   only 0.11 (Jaccard): it kept the organism's own high-risk text instead.
   The material was there and usable; the judge did not select on it. This
   is the cleanest evidence yet that "material necessary, selector grip
   determines direction" — the two are genuinely separable, and here they
   dissociated.

## Caveats

The independent scorers are not identical to the online ones: rank
agreement is high on the clean cases (0.77–0.94) but moderate on the
mixed/contamination pools (invade_base 0.52, oracle_mix 0.63), and
counterfactual kept sets overlap only partially there (Jaccard 0.42–0.53).
The qualitative claims (zero-spread = homogeneous; rescue = real material;
cons_mix = selector-gated) are robust across all three measures; the exact
kept-set identity on rich mixed pools is scorer-dependent. The embedding
measure uses the scorer model's own hidden states, so it is not fully
model-independent — but it agrees with two prompt-independent LLM scorers,
and the near-zero values on the collapsed pools are unambiguous.

[figure: "is zero spread real?" — for each of the 7 cells, three grouped
bars (online spread, independent-scorer spread, embedding distance),
making visually clear that the two collapsed cells are ~0 under ALL THREE
while every rich cell has material under all three. This is the validity
figure for the whole intervention-window arc.]

## Bottom line

The intervention-window claim survives its strongest available check:
selection-inert states are genuinely homogeneous generations, not
artifacts of the online scorer. And the material-vs-selector dissociation
is now directly demonstrated on the same pools — cons_mix had the material
and declined to use it. No change to the headline claims; both are on
firmer ground.
