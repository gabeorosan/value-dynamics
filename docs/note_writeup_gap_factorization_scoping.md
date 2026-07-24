# Note for the writeup lane: scope the gap factorization before publishing

Date: 2026-07-24. From the research-vision thread. Not a correction to any number —
every figure in the writeup stands. This is about one framing sentence that invites
the most obvious reviewer objection, and about pre-empting it cheaply.

## The issue

`docs/writeup_value_dynamics_sprint.md` lines 100-107 currently read:

> Before selection, the model forecasts the selector gap as candidate spread σ
> times judge agreement ρ:
>
> predicted selector gap *g* = *ρσ*, so predicted kept mean *k* = *p* + *ρσ*.
>
> Across 367 rounds with logged judge scores, ρσ reconstructs the realized gaps
> at R² 0.80 (MAE 0.040). On matched rounds, the resulting kept-mean forecast
> predicts the next value at MAE 0.100, versus 0.085 using the actual kept mean.

The word "reconstructs" is already the right word. The word "forecasts" in the
lead-in is not, and the R² 0.80 will read as a discovered law rather than what it
is. The objection a reviewer will make: for top-k selection by judge score,
within-prompt regression algebra already gives

    gap = agreement × spread × i

where *i* is the kept set's advantage in judge-score standard deviations. So the
factorization is a within-round decomposition of quantities all computed from the
same round's candidate scores, not a prediction of something not yet observed.

The objection is correct, and the numbers are in the repo:

- The table logs *i* directly: **mean 0.980, standard deviation 0.113**.
- The theoretical value for keeping 2 of 6 under normality is **1.091**.
- Adding *i* explicitly barely changes the fit: R² 0.810 → 0.824, MAE 0.0421 →
  0.0404 (n = 290 on `spread_util_unified.json`).

So *i* ≈ 1 is a consequence of the chosen keep-ratio. What the R² actually measures
is how nearly linear the within-prompt relation between judge score and value score
is. That is a real and non-obvious empirical fact — it just is not the fact the
sentence currently claims.

There is a second, smaller item: the prior analysis's "n = 175" was an
undocumented triple filter (agreement present, self-only composition, risk axis).
Unfiltered, n = 290 and the fit is **better** (r 0.901). The writeup's 367 is a
different corpus again, so it is unaffected, but do not let the 175 propagate.

## Why fixing this makes the writeup stronger

The genuinely predictive claims are the cross-round ones, and they are already in
the same paragraph: the kept-mean forecast predicts the next value at MAE 0.100
against 0.085 using the actual kept mean. That comparison is out-of-sample in the
way the R² is not. Naming the decomposition as a decomposition costs one sentence
and moves all the weight onto the claim that can carry it.

## Proposed replacement for the lead-in and the R² sentence

Two candidates. Both keep every number.

**Candidate A — name it as a decomposition, keep it short.**

> Before selection, the model decomposes the selector gap into candidate spread σ
> and judge agreement ρ:
>
> selector gap *g* = *ρσ*, so kept mean *k* = *p* + *ρσ*.
>
> This is a decomposition of the round, not a forecast of it: all three quantities
> are measured from the same candidates. Across 367 rounds with logged judge
> scores it holds at R² 0.80 (MAE 0.040), which says the judge's preference is
> close to linear in the value score within a prompt. Keeping two candidates of
> six fixes the remaining term, the kept set's advantage in judge-score standard
> deviations, at 0.98. The forecast is the next line: on matched rounds the
> resulting kept-mean forecast predicts the next value at MAE 0.100, versus 0.085
> using the actual kept mean.

**Candidate B — shorter, moves the caveat into the existing sentence.**

> Before selection, the model writes the selector gap as candidate spread σ times
> judge agreement ρ:
>
> selector gap *g* = *ρσ*, so kept mean *k* = *p* + *ρσ*.
>
> Because all three quantities come from the same round's candidates, this is a
> within-round decomposition rather than a forecast, and its accuracy across 367
> rounds (R² 0.80, MAE 0.040) measures how nearly linear the judge's preference is
> in the value score. The forecasting claim is the next step: on matched rounds the
> kept-mean forecast predicts the next value at MAE 0.100, versus 0.085 using the
> actual kept mean.

## Related, same day, same thread

`report_spread_is_not_a_free_variable.md` finds that on binary-scored axes the pool
mean explains 89.2% of the variance in candidate spread. That bears on line 77,
"Two quantities are measured each round, spread and agreement" — on these axes they
are not independent. Whether the writeup wants to absorb that is a judgement call;
it is a scoping caveat, not an error, and it may be better left to the limitations
section than added here.

Ledger rows for both items are in `docs/ANALYSIS_LEDGER.md` section B.
