# The judges, placed by their measured agreement with the value

A visual glossary that replaces the wordy `synthesis_judges_defined` block:
every measured judge × judging-format × pool setup is a dot on a single
agreement axis, so *identifying* a judge and *placing its measured pull* are one
act. The figure text is orientation only — each card carries at most two lines
naming which judge, which format, and which pool, plus a ρ chip. All the
interpretation below lives here in the caption, not on the figure.

The axis is **ρ**, the rank correlation between the side a judge keeps and the
value being tracked: ρ = −1 means the setup always keeps the lowest-value
answers, ρ = +1 always keeps the highest-value answers, ρ = 0 keeps at random
with respect to the value. Each ρ is computed from that cell's logged candidate
scores, pooled across its rounds.

Dot color = judge identity: **blue** = the organism judging itself, **green** =
a frozen / external copy or a base model, **red** = the non-prompted score
oracle, **gray** = random.

## What each dot is, and what it means

- **Score oracle**, ρ = −1.0 — keeps the two lowest-value answers by rank; there
  is no judge to fool. It anchors the "judgment runs against the value" end of
  the axis and is the decision rule, not a model. (`rho_mean` for the OLMo
  score-oracle cell in `spread_util_unified.json`.)
- **Self-judge, base-mixed pool** (insecure-code Qwen self-judge, head-to-head
  duels, base-model text present in the pool), ρ = −0.24 — the organism's own
  judgment runs *against* its installed value: it tends to keep the lower-value
  side. This is the self-erosion cell.
- **Self-judge, own pool** (the SAME Qwen self-judge, SAME duel format, but
  scored on its own candidates only — base-model text removed from the pool),
  ρ = +0.40. The blue "self-judge: own pool / base-mixed pool" bracket ties
  these two dots together: it is one judge, one format, measured across two
  pools, and the pool alone flips agreement from −0.24 to +0.40. The negative
  reading is driven by the supplier's (base-model) text being in the pool;
  remove it and the same judge agrees positively with the value on its own
  material. This mirrors the cautious-copy bracket below the axis, which holds
  the judge fixed and varies the format instead.
- **Qwen risk-grid judges** — itself, a frozen copy, and a base model, each
  scoring answers against a fixed reference on self-only pools — cluster at
  ρ = −0.03 to +0.11. This is the fan of judges *without selection acting*: the
  spread here is measurement/training noise, not a directional force. The upper
  green bracket ticks down to exactly these three dots so the neighbouring
  cautious-copy dot is not swallowed into the group.
- **Random keeping**, ρ ≈ 0 — ignores the value entirely; the kept side is
  uncorrelated with it. Its ρ is undefined in the file (`rho_mean` is null); it
  is drawn as a hollow gray marker at 0 and validates the null-centring of the
  axis.
- **Cautious-tuned copy of the organism**, scoring the organism's own answers on
  a base-mixed pool: ρ = +0.10 as head-to-head duels, ρ = +0.38 scoring against
  a fixed reference — the same judge, two formats (the green "cautious judge,
  duel/ref format" bracket). The positive reference value means it keeps the
  organism's own HIGH-risk text — a *failed* rescue, not a fix; the duel format
  breaks that reference artifact and pulls agreement back toward zero.
- **Self-judge, peer pool** (organism judges its own duels, but half the answers
  come from an outside peer), ρ = +0.52 — contamination survives the duel
  format: the judge keeps the railed peer's safer, higher-value text.

Evidence line: **82%** of the variance in ρ is between judge × format × pool
setups (`utilization.between_cell_variance_share_rho = 0.817`) — which judge, in
which format, on which pool is the state that sets agreement, far more than
round-to-round noise within a setup.

## Source data

- `experiments/spread_util_unified.json` — the `utilization.table` rows (each
  plotted ρ except the self-only self-judge dot is `rho_mean` for the named
  organism/axis/judge/format/composition cell) and
  `utilization.between_cell_variance_share_rho`. The generator re-reads this file
  (four levels up) and asserts every plotted ρ against it before writing the SVG.
- `experiments/qwen_selfonly_model_check.json` — the NEW **Self-judge, own pool**
  dot: `round1_agreement.supplier_removed_mean = 0.3971` (plotted as ρ = +0.40),
  the same Qwen self-judge in the same duel format as the −0.24 dot but with the
  supplier's base-model text removed from the pool. The file's paired
  supplier-present value is `published_supplier_present = −0.24` (its raw
  re-measured mean is `supplier_present_mean = −0.2847`); the figure plots the
  −0.24 dot from `spread_util_unified.json` (`rho_mean = −0.236` for the
  self-erosion cell), which is the canonical committed value. The generator
  asserts the +0.3971 value against this file before writing the SVG.
- `docs/report_spread_util_unified.md` — the agreement-ledger table that
  cross-checks the `spread_util_unified.json` values and the 0.82 variance share.

## Data notes / discrepancies

- Both self-judge dots (−0.24 and +0.40) are the **same judge in the same format**
  (Qwen insecure-code self-judge, head-to-head duels); only the pool differs
  (base-model text present vs the organism's own candidates only). That is the
  point of the blue bracket.
- The −0.24 dot is plotted from `spread_util_unified.json` (`rho_mean = −0.236`,
  labelled −0.24). The `qwen_selfonly_model_check.json` re-measurement of the
  same supplier-present configuration reads −0.2847 raw / −0.24 published; the
  figure uses the committed spread-util value.
- The file holds two self-judge peer-mixed cells: **duels** at ρ = +0.524 and
  **reference scoring** at ρ = +0.529. The figure plots the duel cell (+0.52),
  the canonical row in the report's agreement ledger.
- The Qwen risk-grid base-judge cell is slightly negative (ρ = −0.032), so the
  cluster is labelled −0.03 to +0.11.
- The "82%" is the ρ variance share (0.817). The file separately reports a
  *utilization* variance share of 0.526; the figure uses the ρ share because the
  sentence is about agreement.
