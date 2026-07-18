# Cross-channel decoupling: what the model says vs. what it writes

**Figure.** Each dot is one judge-factorial endpoint state of the code-security
organism (supplier-removed em750 self-loop, 4 rounds). The horizontal axis is the
**forced-choice self-report endpoint** — the probability the model *picks* the
insecure option on a security question battery. The vertical axis is the **blind
insecure-write rate** — the fraction of 36 real code snippets that a blind
Sonnet-5 reviewer, working from shuffled ids with the keymap withheld, flags as
insecure. Blue circles are the six neutral-prompt + base-judge seeds; green
diamonds are the four candid-prompt + base-judge seeds. The dashed reference lines
mark the em750 organism's blind write rate (0.861) and the base Qwen3-4B rate
(0.472). Error bars are ±1 binomial standard error at n = 36 per state (≈0.06–0.08).

The two channels are **decoupled**: eight of ten endpoints sit in a band at the
organism's write rate while their self-report ranges over almost the whole scale
(x spans 0.012 to 0.912). Self-training rewired what the model *reports* without
moving what it *writes*. The Pearson correlation between the two channels is
**−0.39 (n = 10, not significant)** — no positive cross-channel transfer. The only
two states that moved their writing moved it *down*: neutral-prompt seed 42
(x = 0.487, y = 0.528, z = −3.1 vs. organism) and candid-prompt seed 46
(x = 0.452, y = 0.333, below base, z = −4.6) — and both are seeds whose
self-report *rose*, the opposite of transfer.

**Data note.** All plotted values are read directly from the source file's
`states` and `cross_channel` blocks. The z-scores displayed (−3.1, −4.6) are the
file's `z_vs_organism` values (−3.07, −4.57) rounded to one decimal.

**Source data.**
`experiments/em_code_crosschannel/output/code_crosschannel_adjudication.json`
(fields: `states[*].insecure_rate`, `states[*].endpoint_p_insecure`,
`states[*].n`, `cross_channel.pearson_rate_vs_forced_choice`,
`cross_channel.organism_rate`, `cross_channel.base_rate`,
`cross_channel.z_vs_organism`). Regenerate with
`python3 code-crosschannel-decoupling.py` from this directory.
