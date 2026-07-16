# The judges, placed by what they actually do: agreement with the value

A visual glossary that replaces the wordy `synthesis_judges_defined` block:
every measured judge × judging-format × pool setup is a dot on a single
agreement axis, so *defining* a judge and *showing its measured pull* are one
act. The axis is **ρ**, the rank correlation between the side a judge keeps and
the value being tracked: ρ = −1 means the setup always keeps the LOWER-value
answer, ρ = +1 always keeps the HIGHER-value answer, ρ = 0 keeps at random with
respect to the value. Each ρ is computed from that cell's logged candidate
scores, pooled across its rounds (`rho_mean` in the utilization table).

Dots (color = judge identity: blue = the organism judging itself, green = a
frozen / external copy or base model, red = the non-prompted score oracle,
gray = random):

- **Score oracle**, ρ = −1.0 — keeps the two lowest-scoring answers by decision
  rule; no prompted judge to fool.
- **Organism judges its own duels** (insecure-code Qwen, self-report axis,
  head-to-head duels, base text in the pool), ρ = −0.24 — its judgment runs
  against its own installed value (the self-erosion cell).
- **Qwen risk-grid prompted judges** — itself, a frozen copy, and a base model,
  each scoring answers against a fixed reference on self-only pools — cluster at
  ρ = −0.03 to +0.11 (the fan without selection; drift here is training noise,
  not a force). The upper bracket ticks down to exactly these three dots.
- **Random keeping**, ρ ≈ 0 (agreement undefined in the file — `rho_mean` is
  null; it validates the null-centring and is plotted at 0).
- **Cautious-tuned copy of the organism** on base-mixed pools: ρ = +0.10 as
  head-to-head duels, ρ = +0.38 scoring vs a fixed reference — the same judge,
  two formats (lower bracket). The positive reference value means it keeps the
  organism's own HIGH-risk text (a failed rescue); duels break that reference
  artifact.
- **Self-judge on a peer-invaded pool** (organism judges its own duels, half the
  answers from an outside peer), ρ = +0.52 — contamination survives the duel.

Evidence line: **82%** of the variance in ρ is between judge × format × pool
setups (`utilization.between_cell_variance_share_rho = 0.817`) — which judge, in
which format, on which pool is the state that sets agreement.

## Source data

- `experiments/spread_util_unified.json` — the `utilization.table` rows (each
  plotted ρ is `rho_mean` for the named organism/axis/judge/format/composition
  cell) and `utilization.between_cell_variance_share_rho`. The generator
  re-reads this file (four levels up) and asserts every plotted ρ against it
  before writing the SVG; if the file is unreachable it falls back to the
  embedded constants and prints a warning.
- `docs/report_spread_util_unified.md` — the agreement-ledger table (lines
  ~144–176) that cross-checks these values and the 0.82 variance share.

## Data notes / discrepancies

- The spawn prompt quoted the self-judge peer-invaded pool at ρ = +0.53. The
  file holds two self-judge peer-mixed cells: **duels** at ρ = +0.524 and
  **reference scoring** at ρ = +0.529. The figure plots the duel cell (+0.52),
  which is the canonical row in the report's agreement ledger ("OLMo self judge,
  duels, peer-mixed → +0.52; contamination survives duels"); the +0.53 in the
  prompt corresponds to the reference-scoring variant. Both sit at ≈ +0.52–0.53.
- The prompt quoted the Qwen prompted-judge cluster as ρ ≈ 0.0–0.11; the file's
  base-judge cell is slightly negative (ρ = −0.032), so the figure labels the
  cluster −0.03 to +0.11.
- The prompt's "82% of agreement's variance" matches the ρ variance share
  (0.817). The file separately reports a *utilization* variance share of 0.526;
  the figure uses the ρ share because the sentence is about agreement.
- The random cell has no defined ρ (`rho_mean` is null); it is drawn as a hollow
  gray marker at ρ = 0 and its chip reads "ρ ≈ 0".
