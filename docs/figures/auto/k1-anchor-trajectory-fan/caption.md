# K1 anchor grid — trajectory fans by selection rule

Four panels, one per judge condition of the K1 Qwen anchor grid, each showing
all four seeds' risk-coordinate trajectories over rounds 0–4 of the
self-training loop, from the shared ≈0.60 start.

**Measurement recipe.** The plotted coordinate is the fraction of
strictly-parsed generated answers choosing the gamble, over 24 balanced-order
gamble prompts per round, both presentation orders averaged (4 samples per
item per order at rounds 0 and 4, 1 at mid rounds). Each round the judge
scores K=6 candidate answers per prompt, keeps the top 2, and the kept
answers are trained into the organism (persona_mod25_r5, generated-channel
persona gate passed at 0.50). Forced-choice single-token reads are excluded:
they carry a mean endpoint order gap of 0.347 (34/34 reads above the 0.10
gate) and are order-confounded on this organism.

**Reading.** Self-judging (evolving_self) produces the widest fan of final
positions, 0.26 to 1.00 (range 0.74), including one cautious collapse and two
near-rail amplifications from the same starting organism. Random selection
also fans (finals 0.34–0.79, range 0.45) — training noise alone moves the
coordinate at this dose, so the judge-attributable divergence is the EXCESS
of the self-judge fan over the random fan, not the fan itself. The frozen
base judge is the tightest regime (finals 0.47–0.60, range 0.14, mean
slightly below the start) — an anchoring force relative to every other rule.
A measure-only rollout (full loop cadence, no training) drifts only
0.583→0.573, so the instrument itself contributes ≈0.01 of movement.

Data: `experiments/kaggle/kaggle_k1_qwen_anchor_grid/output/k1_qwen_anchor.json`
(complete grid, 4 conditions × 4 seeds × 4 rounds + measure-only seed 99).
Analysis: `docs/report_k1_first_read.md`.
