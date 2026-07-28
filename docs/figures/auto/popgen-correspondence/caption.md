# popgen-correspondence

**The breeder's equation, term by term: two measured, one assumed.** Each of the
three rows is one schematic drawn twice at identical geometry — labelled on the left
in the language of selection theory, on the right in the language of this judging
loop — so the correspondence is visible rather than asserted. Top row, the
*selection differential*: six squares on an unlabelled value axis are the six
candidate answers in one prompt's pool, the two filled ones are the answers the
judge keeps, the dashed line is the mean of all six, the solid line is the mean of
the two kept, and the measured bar between them is the **selector gap** (mean value
score of the two kept answers, minus the mean over all six candidates in that
prompt's pool, averaged over the round's prompts). Middle row, *heritability*: the
two kept answers step into the next fine-tune as its training data. That step is
drawn dashed and labelled `assumed, never fitted` on purpose — this project does not
estimate a heritability coefficient, because measured movement per unit of gap is
not one constant across the design and shares measurement noise with the gap it
would be regressed on (see the correction row in `docs/ANALYSIS_LEDGER.md`); the
parameter-free rule instead assumes the whole gap carries, and the bottom row
reports how far wrong that gets. Bottom row, the *response to selection*: the same
two heights as the top row, with the organism's own measured value moving from where
it was to where the kept mean was. The **square positions are illustrative, not
data** — they are fixed coordinates in the generator, and the two drawn mean lines
are computed from those same six coordinates so the picture is at least internally
consistent.

The two green readouts are the checked numbers. **R² 0.80** (recomputed 0.801; mean
absolute error 0.0404) is the share of the realized selector gap reconstructed by the
before-the-fact forecast spread × agreement, across **367 rounds with logged judge
scores** — the 290 rounds of the main corpus that log judge scores plus 77 rounds
from 24 judge-ablation runs held out of the fit. Spread is the standard deviation of
the six candidates' value scores inside one prompt's pool and agreement is the
correlation between the judge's preferences and those same value scores; both
recipes are drawn in `docs/figures/auto/state-variables/state-variables.svg` and are
deliberately not redrawn here. **MAE 0.081** (recomputed 0.0812) is the error of the
parameter-free rule `next value = mean value score of the kept answers` against the
next measured value on the 0-to-1 scale, across all **340 rounds** of the 74 runs,
against **0.128** (0.1279) for assuming the value does not change; the rule has no
fitted parameter, so holding each of the 29 complete experimental conditions out
gives the same error as the pooled fit. The measured value is re-measured on held-out
prompts after every round: for the risk organisms (Qwen3-4B and OLMo-3-7B) the share
of answers that take the risky gamble, for the insecure-code organism how insecure
its self-described coding habits are, scored 0 to 1 by its frozen base model. The
claim is that the same accounting of means applies to both settings — not that a
fine-tuning loop is natural selection.

Two caveats not visible in the figure: 336 of the 340 rounds have exactly six
candidates in every pool, the other four have one pool of five; and candidate value
scores are 0/1 in 280 of the 340 rounds (mean binary fraction 0.94 across rounds),
which bounds how large the pool standard deviation can get.

## Source data

- `experiments/ablation_unit_law.json` (`combined_corpus.factorization`) — the
  367-round combined corpus behind R² 0.801 / MAE 0.0404; the 77 extra rounds are the
  held-out judge-ablation runs, whose raw rows exist only in summary form here.
- `experiments/spread_util_unified.json` (`records`, 340 per-round rows) — recomputed
  here for the selector gap against `rho × spread` (the 290 rows with logged judge
  scores give R² 0.810, MAE 0.0421), for the kept-mean rule (MAE 0.0812) and for the
  no-change baseline (MAE 0.1279).
- `experiments/model_ladder_horizon.json` (`anchors.one_step_kept_mean_pooled_mae_340`)
  — independent anchor for the kept-mean MAE, 0.0812 over 340 records.
- `docs/writeup_value_dynamics_sprint.md` — the prose these quantities appear in.

## Density and rendering

Drawn text is **100 words**, down from 140 in the previous revision and 541 in the
first draft; the cut words became geometry, not smaller type. Every size went up or
stayed: 18px is the floor (schematic labels, chip bodies), 21px row names and column
headers, 30px headline, on the same 1240px canvas as `model-recurrence.svg` and
`state-variables.svg`. Aspect ratio is 1240 × 772 = 1.61 wide-to-tall.

The marks are squares on a vertical axis on purpose. The annotated 0-to-1 value line
with its q, p, k ticks is a different figure
(`docs/figures/auto/model-one-round-line/model-one-round-line.svg`), shown later in
the same thread; this one has to read as a motif rather than a reprise of it.

Regenerate with `python3 popgen-correspondence.py` from this directory (stdlib only;
it re-reads the three JSON files and prints every number it draws, plus the two mean
heights it derives from the schematic's own coordinates). Line breaks are computed
from Helvetica advance-width tables rather than an average character width; the
generator refuses to write the file if any line would run past the 1240px canvas or
if the drawn text exceeds the 100-word budget, and it prints both checks on every
run. Arrowheads use `markerUnits="userSpaceOnUse"` so a fat shaft does not inflate
its own head into the distance it is measuring. The SVG carries a `viewBox` with no
`width`/`height` attributes, as the other figures in this repo do, so previewers that
fit a figure into a smaller box scale it instead of cropping it. Checked through
`qlmanage -t -s 2048`.
