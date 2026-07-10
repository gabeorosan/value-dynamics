# WITHDRAWN: raw-factor LoRA “thrash” correlations are not identifiable

This figure displays the historical correlations computed from concatenated raw
LoRA A/B factors. Those norms and cosines change under equivalent refactorizations
`B -> B G`, `A -> G^-1 A` even though the functional merged update `B A` is
unchanged. Consequently the plotted r values do not support claims about weight
motion, thrashing, direction, cancellation, or early warning and must not be
cited as results. The figure is retained only as a visible withdrawal record.

The replacement analysis must compute each round's functional update on merged
products: `delta_t = W_t-W_(t-1)` and `Delta_t = W_t-W_0`, then use merged
Frobenius norms/cosines. New K1-K3 scripts log those quantities and persist every
round for independent recomputation.

The displayed, withdrawn numbers are reproducible from:

- experiments/kaggle/kaggle_basin_anchor/output/basin_anchor.json
- experiments/kaggle/kaggle_basin_anchor_ext/output/basin_anchor_ext.json
- experiments/lightning/output/basin_anchor_lightning_15_23.json
- experiments/lightning/output/basin_anchor_lightning_23_31.json

One frozen-judge rollout (seed 15) logged only 1 round and is excluded, giving
16 frozen rollouts rather than 17. Series colors follow make_figures.py
(blue = self-judge, green = frozen judge), which differs from the spawn
prompt's suggested red/blue.
