# what_was_varied

Orientation figure (tweet attachment): the three settings varied across the 74
independent selection-loop runs, with no results shown. The organism — the
model that evolves — is Qwen3-4B, fine-tuned risk-seeking (16 runs) or to
write insecure code (15 runs), or OLMo-3-7B, fine-tuned risk-seeking (43
runs). The judge — who picks which of the six candidate answers per prompt
become training data — comes in seven kinds, spanning no selection at all
(keep at random), the untrained base model, the organism judging itself, and
an oracle scoring the value directly. The candidate pool — where the six
answers come from — is either the organism's own answers only or half its own
mixed with answers from the untrained base model or from a peer copy. One run
is one seeded loop under one choice of each setting; 340 recorded rounds in
all. A companion figure, docs/figures/auto/condition-space-grid/, gives the
full cell-by-cell run counts.

Source data: `experiments/spread_util_unified.json` (top-level `records`; a run
is one organism + condition + seed). Counts recomputed by `what_was_varied.py`'s
authoring session: 74 runs, 340 round records, 7 judge kinds, 3 pool
compositions.
