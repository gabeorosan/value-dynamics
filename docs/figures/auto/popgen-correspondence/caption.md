# popgen-correspondence

**The breeder's equation, term by term: two measured, one assumed.** Each of the
three rows is a single schematic drawn once, in neutral drawing ink down the middle
of the canvas, with the selection-theory name for it on the left in black and this
judging loop's name for it on the right in blue — one object, two vocabularies, which
is precisely the claim. Top row, the *selection differential*: six squares on an
unlabelled value axis are the six candidate answers in one prompt's pool, the two
filled ones are the answers the judge keeps, the dashed line is the mean of all six,
the solid line is the mean of the two kept, and the measured bar between them is what
selection theory calls the selection differential and this project calls the
**selector gap** (mean value score of the two kept answers, minus the mean over all
six candidates in that prompt's pool, averaged over the round's prompts). The bar
carries no text of its own — the two flanking row names are its two names. Middle
row, *heritability*: the two kept answers step into what comes next, which is the next
generation on one reading and the next fine-tune on the other. That step is drawn
dashed and labelled `assumed, never fitted` on purpose — this project does not
estimate a heritability coefficient, because measured movement per unit of gap is not
one constant across the design and shares measurement noise with the gap it would be
regressed on (see the correction row in `docs/ANALYSIS_LEDGER.md`); the parameter-free
rule instead assumes the whole gap carries. Bottom row, the *response to selection*:
the same two heights as the top row, with the organism's own measured value moving
from where it was to where the kept mean was. The **square positions are illustrative,
not data** — they are fixed coordinates in the generator, and the two drawn mean lines
are computed from those same six coordinates so the picture is at least internally
consistent.

**No number is drawn.** The figure is purely conceptual: it accompanies a thread that
deliberately carries no decimal results, and the measured quantities live in
`docs/writeup_value_dynamics_sprint.md`. Both measured terms *were* checked against
the logged rounds, which is what the closing line in the figure refers to. The
selection-differential term was checked by reconstructing the realized selector gap
from the before-the-fact forecast spread × agreement on the combined corpus of rounds
with logged judge scores — spread is the standard deviation of the six candidates'
value scores inside one prompt's pool, agreement is the correlation between the
judge's preferences and those same value scores, and both recipes are drawn in
`docs/figures/auto/state-variables/state-variables.svg`. The response term was checked
by scoring the parameter-free rule `next value = mean value score of the kept answers`
against the next measured value on the 0-to-1 scale, against the baseline of assuming
the value does not change; the rule has no fitted parameter, so holding each
experimental condition out gives the same error as the pooled fit. The measured value
is re-measured on held-out prompts after every round: for the risk organisms (Qwen3-4B
and OLMo-3-7B) the share of answers that take the risky gamble, for the insecure-code
organism how insecure its self-described coding habits are, scored 0 to 1 by its frozen
base model. The claim is that the same accounting of means applies to both settings —
not that a fine-tuning loop is natural selection.

Two caveats not visible in the figure: 336 of the 340 rounds have exactly six
candidates in every pool, the other four have one pool of five; and candidate value
scores are 0/1 in 280 of the 340 rounds (mean binary fraction 0.94 across rounds),
which bounds how large the pool standard deviation can get.

## Source data

The generator draws none of these, but it re-reads all three on every run and prints
what it recomputes, so the "checked against the logged rounds" wording above stays
falsifiable.

- `experiments/ablation_unit_law.json` (`combined_corpus.factorization`) — the
  367-round combined corpus behind the selection-differential check; the 77 rounds
  beyond the main corpus are the held-out judge-ablation runs, whose raw rows exist
  only in summary form here.
- `experiments/spread_util_unified.json` (`records`, 340 per-round rows) — recomputed
  here for the selector gap against `rho × spread` (the 290 rows with logged judge
  scores), for the kept-mean rule and for the no-change baseline.
- `experiments/model_ladder_horizon.json` (`anchors.one_step_kept_mean_pooled_mae_340`)
  — independent anchor for the kept-mean check over 340 records.
- `docs/writeup_value_dynamics_sprint.md` — where the actual numbers are stated.

## Density and rendering

Drawn text is **82 words**, down from 100 in the previous revision, 140 before that and
541 in the first draft; the cut words became geometry, and the type did not shrink to
absorb them. Every size went up or stayed: 18px is the floor (labels inside the
schematic, the closing line), 20px the equation, 21px the column headers, 22px the row
names, 30px the headline, on the same 1240px canvas as `model-recurrence.svg` and
`state-variables.svg`. Aspect ratio is 1240 × 752 = **1.65 wide-to-tall**.

Deleting the doubled column freed roughly 450px of width. It went into taller, airier
rows (each schematic band is 124px tall on a 178px pitch, up from 100 on 156), into two
314px naming columns that let a row name sit vertically centred on the object it names,
and into two faint vertical rules that bracket the neutral middle so the shared drawing
visibly belongs to neither vocabulary. The two green readout boxes that used to close
the figure are gone; one quiet gray line closes it instead.

The marks are squares on a vertical axis on purpose. The annotated 0-to-1 value line
with its q, p, k ticks is a different figure
(`docs/figures/auto/model-one-round-line/model-one-round-line.svg`), shown later in the
same thread; this one has to read as a motif rather than a reprise of it.

Regenerate with `python3 popgen-correspondence.py` from this directory (stdlib only).
Line breaks are computed from Helvetica advance-width tables rather than an average
character width; the generator refuses to write the file if any line would run past the
1240px canvas or if the drawn text exceeds the 90-word budget, and it prints both checks
on every run. Because no drawn mark depends on the result files, a missing one prints a
note rather than stopping the build. Arrowheads use `markerUnits="userSpaceOnUse"` so a
fat shaft does not inflate its own head into the distance it is measuring. The SVG
carries a `viewBox` with no `width`/`height` attributes, as the other figures in this
repo do, so previewers that fit a figure into a smaller box scale it instead of cropping
it. Checked through `qlmanage -t -s 2048`.
