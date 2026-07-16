# Four experiments, one lens: move a dial, the value follows

**Synthesis candidate B** (alternatives: dial-plane map, pressure-vs-move line).

Four landmark interventions shown in the unified lens of the writeup's selection
model. Each card carries three aligned elements: (1) **the dial the intervention
moved** — a mini slider for either the pool spread σ (mean per-item scoring
disagreement inside the kept pool) or the selection–value agreement ρ (the
round-to-round correlation between how the judge selects and the trained value),
with the "from → to" markers read from the data; (2) **the measured value
trajectory that followed** — a sparkline of the behavioural value over rounds
(share of kept answers that are insecure/risky, 0–1), with every series labelled
in words in the card's legend; (3) **the experiment's identity** in one line
(organism · judge · format · pool · seed). Reading across shows the recurring
law: nudging one selection dial moves the value with it — pinning agreement at a
fixed target or removing alignment collapses or reverses the trained value, while
holding both keeps the rail.

## Cards and the exact runs plotted

All trajectories, spreads and ρ values are read live from
`experiments/spread_util_unified.json` (each record carries per-round `value`,
`spread`, and `rho`; ρ shown per card is the condition mean).

1. **Inject base answers** — Qwen self-report organism, score-oracle judge, score
   format, base-mixed vs self-only matched twins (seed 921). Dial: spread σ
   0.00 → 0.31 at round 0 (agreement ρ stayed pinned at the oracle). Sparklines:
   self-only twin holds (`mixed_reopen_twin_selfonly` 0.627 → 0.625); injected
   twin collapses in one round (`mixed_reopen_qwen` 0.627 → 0.000).
2. **Change how the judge is asked** — OLMo cautious-tuned copy, base-mixed pool.
   Dial: agreement ρ +0.38 (fixed reference score, `cons_mix`) → +0.10
   (pick-a-duel-winner, `h2h_cons_rescue`). Sparklines: fixed-reference judge
   holds (seed 34, 1.000 → 1.000); duel judge comes down (seed 55,
   0.865 → 0.542).
3. **Let it judge its own duels** — Qwen self-report organism judging its own
   duels, duel format, base-mixed pool (`head2head_selfjudge`, seed 41). Dial:
   agreement ρ = −0.24 (its judgment opposes its value). Sparkline
   0.445 → 0.223 → 0.000.
4. **Pin agreement at the ceiling** — OLMo risk organism, score-oracle judge,
   score format, self-only pool (`oracle_hold`, seed 21). Dial: agreement
   ρ = −1.00 (perfect anti-alignment → reversal). Sparkline 0.917 → 0.292.

## Data-honesty notes (numbers trust the file, not the brief)

- **Card 3 baseline is 0.445, not 0.67** as quoted in the drafting brief. The
  `head2head_selfjudge` run in `spread_util_unified.json` starts at value 0.445
  (self-report axis); the rest of the trajectory (0.223 → 0.000) matches.
- **Card 4 endpoint is 0.292, not 0.094.** The value 0.094 does not occur in any
  score-oracle run in this source; the closest matching OLMo-risk oracle reversal
  (`oracle_hold`, seed 21) begins at exactly 0.917 and reverses to 0.292 over its
  four rounds. That run is plotted.
- **Card 5 ("Remove the supplier") was dropped.** Its data
  (`experiments/olmo_insecure/output/olmo_code_security_duel_loop_v2_analysis.json`)
  is an insecure-code-severity readout on a different measurement scale than the
  0–1 selection value used on the other four cards; including it would break the
  uniform value axis the figure relies on for cross-card comparison. The brief
  permitted dropping it if it crowded the figure.

## Source data

- `experiments/spread_util_unified.json` — records field carries per-run,
  per-round `value`, `spread` (pool σ) and `rho`; grouped by `(cond, seed)`.
  Runs used: `mixed_reopen_twin_selfonly`, `mixed_reopen_qwen`, `cons_mix`,
  `h2h_cons_rescue`, `head2head_selfjudge`, `oracle_hold`.

Regenerate with `python3 synthesis-intervention-cards.py` from this directory
(stdlib only).
