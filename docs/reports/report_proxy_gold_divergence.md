# The judge's score and the real value rise together — no Goodhart over four rounds

**Analysis date** 2026-07-29 · **Script**
`scripts/analysis_proxy_gold_divergence.py` · **Result**
`experiments/proxy_gold_divergence.json` · **Data** raw per-candidate logs
behind `experiments/spread_util_unified.json` — 72 rounds from 18 runs with
frozen, non-oracle judges

## Why this measurement and not another

Runs level off. Two accounts compete, and they have opposite implications:

- **Overoptimisation.** The loop buys judge score with real value. The *proxy*
  (the judge's score of the organism's own candidates) keeps climbing while the
  *gold* (the held-out value) flattens or reverses. Goodhart in the original
  sense, and the shape Gao, Schulman & Hilton fit for reward-model
  overoptimisation ([arXiv 2210.10760](https://arxiv.org/abs/2210.10760)).
- **Replicator exhaustion.** The loop runs out of selectable variation, so proxy
  and gold flatten *together*. Ferbach et al.
  ([arXiv 2407.09499](https://arxiv.org/abs/2407.09499), Theorem 2.1) predict
  exactly this, and predict it happens short of the value rails.

The observation this project already had — that runs level off short of the
rails — does **not** separate them, because the replicator account predicts that
too. The divergence between the two series does, which is why this is the
measurement worth building.

## The estimand error that had to be fixed first

The judge score is direction-free: higher always means more judge-preferred. The
raw value is not. Some runs are pushed up and some down, so pooling them makes
the gold slope average to roughly **zero by cancellation rather than by
saturation** — and the divergence test then compares a real slope against an
artefact.

The first version of this script did exactly that, and produced a clean-looking
"proxy +0.019 [+0.012, +0.025], gold +0.000" that would have read as textbook
Goodhart. It was cancellation.

Each run's direction is now taken from the sign of its round-one selection gap
(kept value mean minus pool value mean) — the direction the judge actually
revealed — and gold is measured along it.

## Results

Per-round slopes with run fixed effects; run-clustered bootstrap intervals,
4,000 draws. `gold*` is sign-aligned.

| group | runs | proxy (judge score) | gold* (value) | divergence proxy − gold* | verdict |
|---|---|---|---|---|---|
| all signed | 18 | **+0.0186** [+0.0124, +0.0245] | rises with it | **+0.0014** [−0.0125, +0.0178] | no separation |
| round-1 gap ≥ 0.02 | 11 | +0.0220 [+0.0140, +0.0296] | +0.0218 [+0.0019, +0.0388] | +0.0002 [−0.0177, +0.0231] | no separation |
| OLMo | 8 | +0.0213 [+0.0133, +0.0285] | **+0.0354** [+0.0252, +0.0464] | **−0.0141** [−0.0228, −0.0064] | **gold rises faster** |
| Qwen | 8 | +0.0162 [+0.0062, +0.0265] | −0.0007 [−0.0210, +0.0175] | +0.0169 [−0.0070, +0.0441] | no separation |

**There is no Goodhart signature over four rounds.** Pooled, the divergence is
+0.0014 with an interval straddling zero — the judge's score of the candidates
and the value those candidates actually carry rise at the same rate. On the
subset with a clear round-one direction, +0.0002. That is about as flat as a
divergence estimate gets.

**On OLMo the gold moves *faster* than the proxy** — divergence −0.0141
[−0.0228, −0.0064], interval excluding zero in the anti-Goodhart direction. The
held-out value climbs at +0.061 per round in the judge's direction while the
judge's own score of the pool climbs at +0.021. Whatever is limiting these runs,
it is not the judge being gamed.

**Qwen's point estimate leans the other way** (+0.0169) but its interval
contains zero, and its aligned gold slope is −0.0007 — flat. So the families
differ, and only OLMo's difference is resolvable.

## What this rules in and out

- **Rules out**, for this horizon and these judges: the loop levelling off
  because selection is buying proxy score at the expense of real value. If that
  were happening the divergence would be positive and it is not.
- **Consistent with**: replicator exhaustion — the loop runs out of selectable
  variation. That is also what the companion saturation analysis found from the
  other direction (the response per unit selection does not decay; the *gap*
  shrinks).
- **Does not test**: longer horizons. Four rounds accumulate little optimisation
  pressure by the standards of the overoptimisation literature, and Gao's curves
  bend at KL distances well beyond anything here. A null at four rounds is not a
  null at forty.

## Threats

- **Judge calibration drift is the main one and cannot be removed from committed
  data.** A frozen judge scoring a drifting candidate distribution could produce
  a rising proxy without the candidates being any more judge-preferred. The
  pool-mean comparison used here is the least drift-sensitive version available,
  but it is not immune. This is an argument for logging a fixed anchor set of
  candidates re-scored every round in future runs — a cheap addition that would
  make the proxy series calibration-free.
- **Frozen non-oracle judges only.** An evolving self-judge is a moving ruler.
  Oracle judges have proxy identical to gold by construction.
- **18 runs, 72 rounds**, and the family split rests on 8 runs each.
- **Direction is assigned from round one** and held fixed. A run whose judge
  reverses direction mid-run is mis-aligned for its later rounds; the
  `round-1 gap ≥ 0.02` row exists to check that weak-direction runs are not
  driving the result, and it does not change the answer.
