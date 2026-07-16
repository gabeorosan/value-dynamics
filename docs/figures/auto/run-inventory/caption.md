# The 74 runs, cell by cell

A compact visual replacement for the writeup's "What I ran" table. One slim row
per distinct **experiment cell** — a combination of (organism, value axis, judge,
alternative source, answer source). The rows are derived directly from
`experiments/spread_util_unified.json`: a run is one distinct identity over the
records' `source / cond / seed / organism / axis / judge / format / composition`
fields (74 distinct runs), and each cell's count is the number of distinct runs
sharing that (organism, axis, judge, format, composition) identity. The 22 cell
counts sum to 74 (asserted in the generator). Rows are grouped under their five
families with a left band and a family header carrying the organism · value
chips; a **segmented run-block bar** sits at the right of each row. Repeated chips
down the columns — `static alternative`, `own answers`, `the base model` — make
the shared loop structure visible. The figure text is orientation only.

**The run-block bar.** Each row's bar is one block per run, and each block's width
is proportional to that run's number of selection rounds. Each block is also
**colored and labeled by its round count**: a **slate-gray block with a white "4"**
is a 4-round run, a **near-black block with a white "8"** is an 8-round run (the
two-color key sits in the column-header row). So the block count reads as the run
count, the whole bar length reads as the cell's total rounds, the color/digit
gives each run's length directly, and a longer block is visibly a longer run. In
this corpus every run is either 4 or 8 rounds (11 runs are 8-round: the 9
scheduled-swap runs plus 2 in the mixed cell below; the other 63 runs are 4-round
— so 63×4 + 11×8 = 340). Per-run round counts
are derived live from the data (distinct rounds per `source | cond | seed` run key
within each cell), and the generator asserts the grand total is 340. The
end-of-row label spells out the rounds-per-run decomposition rather than a bare
total: a uniform cell reads "n runs × r rounds" (e.g. "9 runs × 8 rounds"), and a
mixed cell reads the sum form "6 × 4 + 2 × 8 rounds". The decomposition is built
live per cell by counting runs at each distinct round count (sorted ascending).
The **OLMo · the base model · static alternative · own answers** cell is the case
where rounds differ *within* a cell: its bar shows six short 4-round blocks and
two long 8-round blocks, labeled "6 × 4 + 2 × 8 rounds".

**Note on two figures quoted in the request.** The data shows only 4- and 8-round
runs — there are no 2-round runs anywhere in the corpus — so the key line reads
"(4 or 8)". In particular the Qwen self-judge `candid self-prompt` cell is **4
runs × 4 rounds** (16 rounds), not 4 × 2; its bar shows four equal 4-round blocks.
Both figures are read from experiments/spread_util_unified.json.

**Chip colors map to the experiment-kit slots** (docs/figures/src/synthesis_experiment_kit.py):

- **organism · value** — the base model in **blue** (slot 1) paired with the
  installed value in **red** (slot 2). Four families have a single organism·value,
  shown once in the family header. The **oracle & injection** family spans both
  organisms and both values, so each of its rows carries its own organism·value
  chips.
- **the judge** — **purple** (slot 3): who keeps answers each round —
  `itself`, `a frozen copy`, `the base model`, `a cautious-tuned copy`,
  `random keeping`, `scheduled judge swaps`, or the non-prompted `score oracle`.
- **alternative** — **amber** (slot 5): what a judge compares an answer against —
  `static alternative` (a fixed reference answer; renamed from "reference scoring"),
  `head-to-head duels` (against another model's answer), `score rank` (the oracle
  ranks candidates directly), `random draw` (random keeping has no real
  comparison), or `candid self-prompt` (the self-judge asked candidly, in the
  insecure-code loop).
- **answer source** — **green** (slot 4): where the round's answers come from —
  the organism's `own answers`, `base-mixed` (half from the base model), or
  `risk-railed-peer-mixed` (half from a risk-railed peer).

**Judge-swap schedules** are distinguishable in the data (the `judge` field takes
the value `schedule`), so they get their own row — `scheduled judge swaps`, 9
runs, in the OLMo risk grid + judge schedules family. No schedule runs are folded
into another judge's row.

**Cross-check.** The per-family sums equal the writeup's committed inventory
(16 · 21 · 18 · 11 · 8 = 74) — asserted in the generator. Family membership is
assigned by rule (score-oracle cells → oracle & injection; OLMo·risk self-only +
static alternative → the risk grid + judge schedules; the remaining OLMo·risk
cells with mixed answer pools or duels → mixed-pool interventions). Total: 74
runs over 340 selection rounds. Two forward-test experiments (the OLMo
insecure-code erosion loop with its supplier-removed control arms, and the Qwen
supplier-removed self-judge-duel twin) sit outside this modeling corpus and are
not counted here.

**Source data:**
- experiments/spread_util_unified.json — the cell rows, run counts, and totals
  (n_runs = 74, n_records = 340).
- docs/writeup_value_dynamics_sprint.md — "What I ran" section (family names and
  committed per-family counts used for the cross-check assertion).
