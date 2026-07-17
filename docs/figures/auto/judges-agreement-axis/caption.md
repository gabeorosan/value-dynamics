# The judges, placed by their measured agreement with the value

A forest plot / dot-ladder: every measured judge × alternative-source ×
candidate-source setup is one ROW on a single shared agreement axis (ρ, drawn once
at the top and repeated as light gridlines down the chart). Each row has a
left-aligned setup name, a small gray line naming the organism · value · format ·
candidate-source condition it comes from, a dot at its measured ρ, and the ρ value
printed next to the dot — no callout boxes, no leader lines. Each dot also carries a
horizontal **lollipop bar** in the row's color (low opacity, drawn behind the dot)
running from the ρ = 0 vertical line out to the dot, so the length and side of the
bar show the sign and size of the agreement at a glance. Rows are grouped so the
matched contrasts read as adjacent pairs; no line connects a pair's dots (the row
names — "— static alternative" vs "— head-to-head duels"; "— base-mixed
candidates" vs "— own candidates" — say what differs). The figure text is
orientation only; the interpretation is here.

**The axis (ρ).** ρ is the within-prompt correlation between the judge's scores
and the candidates' value scores, averaged over the round's prompts. ρ = +1 means
the judge scores highest exactly the answers the value scores highest (selection
keeps the highest-value answers); ρ = −1 means it scores highest the answers the
value scores lowest (selection keeps the lowest-value answers); ρ = 0 means the
judge's scores are uncorrelated with the value. **Color = the judge's identity**
(one principled encoding, applied to the dot, its lollipop bar, and its ρ label on
every row; a key is drawn below the rows), matching the experiment-kit judge-slot
options: blue = the organism (any self-judge row); green = a frozen copy of
the organism; amber = the base model; purple = the cautious judge (the base model fine-tuned for caution, frozen); red = the
score oracle; gray = random keeping. So the three Qwen risk-grid judges read as
three distinct colors (the organism blue, a frozen copy green, the base model amber), and
a self-judge is blue wherever it appears.

## The rows, grouped

Organism identities are read from the data and
`docs/report_spread_util_unified.md` (which names the runs), NOT guessed: cells
keyed `OLMo | risk` are the "K2 OLMo gamble organisms" → **OLMo risky-gambles**,
risk value; cells keyed `Qwen | risk` are the "K1 Qwen risk grid" → **Qwen
risk-grid**, risk value; the cell keyed `Qwen | selfreport` is the insecure-code
EM organism → **Qwen insecure-code**, self-description value.

**bounds & controls** —
- **Score oracle**, ρ = −1.0 (OLMo risky-gambles · risk · base-mixed). No judge:
  keeps the two lowest-value answers by rank. The hard floor of the axis — this is
  what "judgment runs fully against the value" looks like.
- **Random keeping**, ρ ≈ 0 (Qwen risk-grid · risk · own candidates). Keeps at
  random, so the kept side is uncorrelated with the value. Its ρ is undefined in
  the file (`rho_mean` is null); it is drawn as a hollow marker at 0 and validates
  the null-centring of the axis.

**same cautious judge — only the alternative source differs** (OLMo
risky-gambles · risk · base-mixed candidates; the two rows share the judge and the
candidate source, and change only what each candidate is scored against) —
- **Cautious judge — static alternative** (scored against a fixed reference
  answer), ρ = +0.38. Positive here means it keeps the organism's own HIGH-risk
  text — a *failed* rescue, not a fix.
- **Cautious judge — head-to-head duels** (scored against the other duellist),
  ρ = +0.10. The duel format breaks the fixed-reference artifact and pulls
  agreement back toward zero. The adjacent rows show the +0.38 → +0.10 move.

**same self-judge — only the candidate source differs** (Qwen insecure-code ·
self-description · duels; the two rows share the judge and the duel format, and
change only whose answers are in the pool) —
- **Self-judge — base-mixed candidates** (base-model text present in the pool),
  ρ = −0.24. The organism's own judgment runs *against* its installed value — it
  tends to keep the lower-value side. This is the self-erosion cell.
- **Self-judge — own candidates** (the organism's own candidates only, base-model
  text removed), ρ = +0.40. The candidate source alone flips agreement from −0.24 to
  +0.40: the negative reading was driven by the supplier's (base-model) text
  sitting in the pool; remove it and the same judge agrees positively with the
  value on its own material. The adjacent rows show the −0.24 → +0.40 move.

**the remaining setups** —
- **Self-judge — Qwen risk grid**, ρ = +0.11; **A frozen copy — Qwen risk grid**,
  ρ = +0.04; **The base model — Qwen risk grid**, ρ = −0.03. Each of the three Qwen risk-grid
  judges scores its own answers against a fixed reference on own-answers-only pools
  (Qwen risk-grid · risk · static alternative · own candidates), and each is now its
  own row with its own dot and label rather than a single clustered row. Each ρ is
  computed live in the generator as the mean of the per-round `rho` field over that
  condition's records (`evolving_self` → itself, `frozen_copy_r0` → a frozen copy,
  `frozen_base` → the base model); the generator asserts all three round to values
  inside [−0.05, +0.15] and prints them (itself +0.1132, frozen copy +0.0411, base
  −0.0316). This is the fan of judges *without selection acting* — the spread across
  the three is measurement/training noise straddling zero, not a directional force.
- **Self-judge — peer-mixed answers** (OLMo risky-gambles · risk · duels; the
  organism scores its own duels, but half the answers come from an outside peer),
  ρ = +0.52 — contamination survives the duel format: the judge keeps the railed
  peer's safer, higher-value text.

Supporting statistic (not drawn on the figure): 82% of the variance in ρ is
between judge × format × candidate-source setups
(`utilization.between_cell_variance_share_rho = 0.817`) — which judge, in which
format, on which candidate source is the state that sets agreement, far more than
round-to-round noise within a setup.

## Source data

- `experiments/spread_util_unified.json` — the `utilization.table` rows plus the
  per-round `records`. The three **Qwen grid** dots are computed live from `records`
  as the mean of the per-round `rho` field over each condition (`evolving_self`,
  `frozen_copy_r0`, `frozen_base`; Qwen organism, risk axis); every other plotted ρ
  except the "Self-judge — own candidates" dot is the `utilization.table` `rho_mean`
  for the named organism/axis/judge/format/composition cell (axis `risk` = risk
  value, axis
  `selfreport` = self-description value; composition `self-only` = own candidates,
  `base-mixed` = base-model text mixed in, `peer-mixed` = an outside peer mixed
  in). Also carries `utilization.between_cell_variance_share_rho = 0.817`. The
  generator re-reads this file (four levels up) and asserts every plotted ρ
  against it before writing the SVG.
- `experiments/qwen_selfonly_model_check.json` — the "Self-judge — own candidates"
  dot: `round1_agreement.supplier_removed_mean = 0.3971` (plotted as ρ = +0.40),
  the same Qwen self-judge in the same duel format as the −0.24 dot but with the
  supplier's base-model text removed from the pool. The file's paired
  supplier-present value is `published_supplier_present = −0.24` (raw re-measured
  mean `supplier_present_mean = −0.2847`); the figure plots the committed −0.236
  value from `spread_util_unified.json` for that dot. The generator asserts the
  +0.3971 value against this file before writing the SVG.
- `docs/report_spread_util_unified.md` — names the runs (the K1 Qwen risk grid,
  the K2 OLMo gamble organisms, the insecure-code EM organisms) and cross-checks
  the ρ values and the 0.82 variance share.

## Data notes / discrepancies

- Organism-label correction: an earlier draft of this figure labelled the OLMo
  `risk` organism "OLMo code-security". The report names it the "K2 OLMo **gamble**
  organisms", so the rows now read **OLMo risky-gambles**; the Qwen `risk` cells
  are the **risk-grid** organism and the Qwen `selfreport` cell is the
  **insecure-code** organism. The plotted ρ values are unchanged.
- Both self-judge dots (−0.24 and +0.40) are the **same judge in the same format**
  (Qwen insecure-code self-judge, head-to-head duels, self-description value);
  only the candidate source differs. That is the point of the blue connecting line
  between the two dots: the leftward −0.24 bar and the rightward +0.40 bar show the
  flip directly.
- The file holds two OLMo self-judge peer-mixed cells: **duels** at ρ = +0.524 and
  **reference scoring** at ρ = +0.529. The figure plots the duel cell (+0.52), the
  canonical row in the report's agreement ledger.
- The Qwen risk-grid base-judge cell is slightly negative (live mean ρ = −0.0316,
  labelled −0.03); the three grid judges now occupy three separate rows spanning
  −0.03 to +0.11 rather than one clustered row.
- The score-oracle cell has the same ρ = −1.0 for both `base-mixed` and
  `self-only`; the figure uses the base-mixed OLMo cell.
