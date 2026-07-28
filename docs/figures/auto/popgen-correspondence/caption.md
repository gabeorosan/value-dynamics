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

**No number is drawn, and nothing about the checking is drawn either.** The figure is
purely conceptual: it accompanies a thread that deliberately carries no decimal
results, and the measured quantities live in
`docs/writeup_value_dynamics_sprint.md`. Both measured terms *were* checked against
the logged rounds — that fact is recorded here in words rather than on the canvas,
and the generator still recomputes both on every run and prints what it gets, so the
claim stays falsifiable without a line of text on the figure. The
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
falsifiable. On the current run it prints a selector-gap reconstruction of n=367,
R² 0.801, mean absolute error 0.0404 (n=290, R² 0.810, MAE 0.0421 on the unified file
alone) and a kept-mean rule of n=340 at MAE 0.0812 against a no-change baseline of
0.1279.

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

Drawn text is **56 words**, down from 82 in the previous revision, 100 before that, 140
before that and 541 in the first draft; the cut words became geometry, and the type did
not shrink to absorb them. Every size went up or stayed: 18px is the floor (the labels
inside the schematic), 20px the equation, 21px the column headers, 22px the row names,
30px the headline, on the same 1240px canvas as `model-recurrence.svg` and
`state-variables.svg`. Aspect ratio is 1240 × 706 = **1.76 wide-to-tall**.

Only four kinds of text remain: the headline, the two column headers, the equation
under the left one, and the six row names plus the five small labels inside the
schematics. The grey subtitle that used to sit under the headline and the grey closing
line that used to sit under the rows are both gone, and neither left a hole — the row
pitch went from 178px to 196px (the schematic bands stay 124px tall, so the extra
18px per row is white between rows, not a bigger drawing), and the canvas came down
from 752px to 706px. The hairline under the headline is now positioned from the
headline's own last baseline, 28px below it, so it reads as the headline's underline
rather than as the top of a missing sentence; the figure ends 48px under the last
schematic band, one side-margin's worth, with the bracket rules crossing 14px into
that margin so the bottom edge is drawn rather than trailed off. Earlier revisions had
also removed a doubled second column of schematics and two green readout boxes.

The headline is the single constant `HEADLINE` at the top of the generator, because its
wording is still being settled. Swapping that string is the whole edit: the hairline,
the column headers, the rows and the canvas height are all measured downward from where
the headline actually ends, so a longer headline that wraps to two lines simply pushes
everything down and grows the canvas (verified: a two-line headline renders at 1240 ×
741, aspect 1.67, with no overflow).

The marks are squares on a vertical axis on purpose. The annotated 0-to-1 value line
with its q, p, k ticks is a different figure
(`docs/figures/auto/model-one-round-line/model-one-round-line.svg`), shown later in the
same thread; this one has to read as a motif rather than a reprise of it.

Regenerate with `python3 popgen-correspondence.py` from this directory (stdlib only).
Line breaks are computed from Helvetica advance-width tables rather than an average
character width; the generator refuses to write the file if any line would run past the
1240px canvas or if the drawn text exceeds the 62-word budget (56 drawn, the same ~10%
of slack the previous revision carried at 82 of 90), and it prints both checks on every
run. Because no drawn mark depends on the result files, a missing one prints a
note rather than stopping the build. Arrowheads use `markerUnits="userSpaceOnUse"` so a
fat shaft does not inflate its own head into the distance it is measuring. The SVG
carries a `viewBox` with no `width`/`height` attributes, as the other figures in this
repo do, so previewers that fit a figure into a smaller box scale it instead of cropping
it. Checked through `qlmanage -t -s 2048`.
