# The judges, placed by their measured agreement with the value

A visual glossary: every measured judge × judging-format × answer-source setup is
a dot on a single agreement axis, so *identifying* a judge and *placing its
measured pull* are one act. The figure text is orientation only — each card names
its organism and value, its judging format, and its answer source, plus a ρ chip.
The interpretation is here in the caption.

**The axis (ρ).** ρ is the within-prompt correlation between the judge's scores
and the candidates' value scores, averaged over the round's prompts. ρ = +1 means
the judge scores highest exactly the answers the value scores highest (so
selection keeps the highest-value answers); ρ = −1 means it scores highest the
answers the value scores lowest (selection keeps the lowest-value answers); ρ = 0
means the judge's scores are uncorrelated with the value. Each ρ is computed from
that cell's logged candidate scores.

Dot color = judge identity: **blue** = the organism judging itself, **green** = a
frozen / external copy or a base model, **red** = the non-prompted score oracle,
**gray** = random.

## Each dot: full condition, and what it means

Every card states the organism and value the measurement comes from (read from the
data cell keys, not guessed), the judging format, and the answer source.

- **Score oracle** — OLMo risky-gambles organism, risk value; base-mixed answer
  pool. ρ = −1.0: keeps the two lowest-value answers by rank. There is no judge to
  fool — it is the decision rule, and it anchors the "judgment runs against the
  value" end of the axis. (Cell `OLMo | risk | score oracle | score | base-mixed`.)
- **Self-judge, base-mixed** — Qwen insecure-code organism, self-description
  value; the organism scores its OWN head-to-head duels with base-model text
  present in the pool. ρ = −0.24: its own judgment runs *against* its installed
  value, tending to keep the lower-value side. This is the self-erosion cell.
  (Cell `Qwen | selfreport | self | duel | base-mixed`, `rho_mean = −0.236`.)
- **Self-judge, own answers** — the SAME Qwen self-judge, SAME duel format and
  SAME self-description value as the base-mixed dot, but scored on the organism's
  OWN candidates only (base-model text removed). ρ = +0.40. The blue "self-judge:
  own answers / base-mixed" bracket ties these two dots: one judge, one format,
  measured across two answer sources — and the answer source alone flips agreement
  from −0.24 to +0.40. The negative reading was driven by the supplier's
  (base-model) text sitting in the pool; remove it and the same judge agrees
  positively with the value on its own material. This mirrors the cautious-copy
  bracket below the axis, which holds the judge fixed and varies the format
  instead. (Source: `qwen_selfonly_model_check.json`,
  `round1_agreement.supplier_removed_mean = 0.3971`.)
- **Qwen risk-grid judges** — Qwen insecure-code organism, risk value; itself, a
  frozen copy, and a base model, each scoring answers against a fixed reference on
  own-answers-only pools. Cluster at ρ = −0.03 to +0.11 — the fan of judges
  *without selection acting*: the spread here is measurement/training noise, not a
  directional force. The upper green bracket ticks down to exactly these three
  dots so the neighbouring cautious-copy dot is not swallowed into the group.
  (Cells `Qwen | risk | base/frozen copy/self | reference | self-only`.)
- **Random keeping** — Qwen insecure-code organism, risk value; own-answers-only
  pool. ρ ≈ 0: keeps at random, so the kept side is uncorrelated with the value.
  Its ρ is undefined in the file (`rho_mean` is null); it is drawn as a hollow
  gray marker at 0 and validates the null-centring of the axis.
  (Cell `Qwen | risk | random | random | self-only`.)
- **Cautious-tuned copy** — OLMo risky-gambles organism, risk value; a
  cautious-tuned copy of the organism scores the organism's own answers on a
  base-mixed pool. ρ = +0.10 as head-to-head duels, ρ = +0.38 scoring against a
  fixed reference — one judge, two formats (the green "cautious judge, duel/ref
  format" bracket). The positive reference value means it keeps the organism's own
  HIGH-risk text — a *failed* rescue, not a fix; the duel format breaks that
  reference artifact and pulls agreement back toward zero. (Cells
  `OLMo | risk | cautious copy | duel/reference | base-mixed`, `0.100` / `0.383`.)
- **Self-judge, peer-mixed** — OLMo risky-gambles organism, risk value; the
  organism scores its own duels, but half the answers come from an outside peer.
  ρ = +0.52 — contamination survives the duel format: the judge keeps the railed
  peer's safer, higher-value text. (Cell `OLMo | risk | self | duel | peer-mixed`,
  `rho_mean = 0.524`.)

Supporting statistic (not drawn on the figure): 82% of the variance in ρ is
between judge × format × answer-source setups
(`utilization.between_cell_variance_share_rho = 0.817`) — which judge, in which
format, on which answer source is the state that sets agreement, far more than
round-to-round noise within a setup.

## Source data

- `experiments/spread_util_unified.json` — the `utilization.table` rows. Every
  plotted ρ except the "Self-judge, own answers" dot is `rho_mean` for the named
  organism/axis/judge/format/composition cell (axis `risk` = risk value, axis
  `selfreport` = self-description value; composition `self-only` = own answers,
  `base-mixed` = base-model text mixed in, `peer-mixed` = an outside peer mixed
  in). Also carries `utilization.between_cell_variance_share_rho = 0.817`. The
  generator re-reads this file (four levels up) and asserts every plotted ρ
  against it before writing the SVG.
- `experiments/qwen_selfonly_model_check.json` — the "Self-judge, own answers" dot:
  `round1_agreement.supplier_removed_mean = 0.3971` (plotted as ρ = +0.40), the
  same Qwen self-judge in the same duel format as the −0.24 dot but with the
  supplier's base-model text removed from the pool. The file's paired
  supplier-present value is `published_supplier_present = −0.24` (raw re-measured
  mean `supplier_present_mean = −0.2847`); the figure plots the committed −0.236
  value from `spread_util_unified.json` for that dot. The generator asserts the
  +0.3971 value against this file before writing the SVG.
- `docs/report_spread_util_unified.md` — the agreement-ledger table that
  cross-checks the `spread_util_unified.json` values and the 0.82 variance share.

## Data notes / discrepancies

- Both self-judge dots (−0.24 and +0.40) are the **same judge in the same format**
  (Qwen insecure-code self-judge, head-to-head duels, self-description value);
  only the answer source differs. That is the point of the blue bracket.
- The file holds two OLMo self-judge peer-mixed cells: **duels** at ρ = +0.524 and
  **reference scoring** at ρ = +0.529. The figure plots the duel cell (+0.52), the
  canonical row in the report's agreement ledger.
- The Qwen risk-grid base-judge cell is slightly negative (ρ = −0.032), so the
  cluster is labelled −0.03 to +0.11.
- The score-oracle cell has the same ρ = −1.0 for both `base-mixed` and
  `self-only`; the figure uses the base-mixed OLMo cell.
