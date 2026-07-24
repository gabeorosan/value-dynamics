# Draft options for the endpoint and candidate-state framing

These alternatives are measured against the writeup as it stood when the
question “are there any other numbers/figures that should be updated?” was
asked. Deleted baseline text is struck through; proposed text is highlighted.
The live writeup has been returned to that checkpoint while these drafts are
under review.

## Option A: make the distinction part of the main argument

This version treats candidate-state dynamics and behavioral propagation as two
successive empirical links. It is a larger rework because the distinction
starts in the Findings, changes the one-round section, and carries through the
endpoint section and limitations. The pooled 367-round and 293-transition
results become the primary evidence for the local dynamics; the endpoint model
then asks when those dynamics propagate to the behavioral value.

### Findings

**Before**

<div class="before" markdown="1">

1. **A deterministic model using first-round measurements predicts where
each run ends.** Each round, the two kept answers differ from the pool average
by the pool's spread times the judge's agreement, with no fitted coefficient;
training then moves the value to that kept average. Iterated, this predicts a
run's final value from its first round with a mean absolute error of 0.118 on
the 0-to-1 value scale, versus 0.431 for assuming no change.

</div>

**After**

<div class="after" markdown="1">

1. **Selection changes the next candidate pool in a simple, measurable
way.** The mean value of the kept candidates differs from the full pool mean by
approximately the pool's spread times the judge's agreement with the value
being tracked. This relation reconstructs the realized selection gaps across
367 rounds, and across 293 transitions the model's next candidate mean moves
0.82 of the way toward the kept mean.

</div>

<div class="after" markdown="1">

2. **In the main experiments, these local changes propagated into the
model's measured behavior.** The kept candidate mean predicts the next
behavioral value at MAE 0.081 across 340 rounds, versus 0.128 for assuming no
change. Iterating the same dynamics from the first round predicts final values
at MAE 0.118 on the 36 selection-driven runs in the endpoint analysis, versus
0.431 for assuming no change.

</div>

The current stochastic and intervention findings would become items 3 and 4.

### One-round section

**Before**

<div class="before" markdown="1">

**each round, the value moves to what the judge keeps**

The judge enters the loop only as the choice of which two candidates are kept.
The parameter-free one-round rule is

`next value = kept candidate value mean`.

</div>

**After**

<div class="after" markdown="1">

**each round, selection changes the next candidate pool**

Each round contains two linked steps. The judge changes the composition of the
training data by choosing which candidates to keep, and training on those
candidates changes what the model generates next. The selection step is
measured by the gap between the kept mean and the full candidate-pool mean. It
is predicted before selection by the pool's spread and the judge's agreement:

predicted selector gap *g* = *ρσ*, so predicted kept mean *k* = *p* + *ρσ*.

Across 367 rounds with logged judge scores, *ρσ* reconstructs the realized gaps
at R² 0.80 and mean absolute error 0.040. After training, the model's own
candidate mean moves 0.82 of the way toward the kept mean across 293
transitions. In the original 340-round behavioral analysis, the kept mean also
predicts the next measured value at MAE 0.081, versus 0.128 for assuming no
change. This last result is the observed link from candidate-pool movement to
behavior, rather than a definition of the update.

</div>

The existing spread recurrence can follow this passage unchanged. The agreement
paragraph would change as follows.

**Before**

<div class="before" markdown="1">

Agreement is strongly structured by the experimental condition: across
the main corpus, 82% of its variance was between judge × alternative-source ×
candidate-source conditions. The self-description factorial produced positive,
negative, and sign-changing agreement trajectories as its candidate pools
changed. Freezing round-1 agreement is an approximation that worked best within
those conditions.

</div>

**After**

<div class="after" markdown="1">

Agreement belongs to the interaction between the judge and the current
candidate pool. Experimental conditions strongly structure it, but changing
the pool can also change its magnitude or sign, as it did in the
self-description factorial. The recurrence carries round-1 agreement forward,
which is most appropriate when the judge and the candidate distribution retain
the same relation over the run.

</div>

### Endpoint section

**Before**

<div class="before" markdown="1">

**Forecasting endpoints from first-round measurements**

Everything the model needs is measured in the first round: spread, agreement,
and the pool composition. Iterated with those numbers frozen, it turns a
one-round measurement into a whole-run forecast, and the figure below scores
that forecast across all the runs. Endpoints land at mean absolute error 0.118
versus 0.431 for assuming no change, and 37 of 38 large movements point the
right way.

</div>

**After**

<div class="after" markdown="1">

**when candidate-pool movement propagates to behavior**

The local dynamics become an endpoint forecast when changes in the candidate
pool continue to appear in the behavioral value. On the 36 selection-driven
runs in the endpoint analysis, iterating the first-round spread, agreement, and
pool composition predicts final values at mean absolute error 0.118, versus
0.431 for assuming no change.

</div>

<div class="after" markdown="1">

The figure below shows a related but broader directional result. Each run
sits at its round-1 spread and agreement, colored by its observed whole-run
move, over the direction implied by the wall-capped four-round force 4ρσ. Among
the 41 plotted runs that moved by at least 0.15, 35 moved in the direction of
that force.

</div>

Under this option, the figure title becomes **“Four-round directional force map
against observed whole-run movement.”** The plotted points, colors, and 35/41
count do not change.

### Limitations and future directions

Add this near the start of the current section:

<div class="after" markdown="1">

The experiments measure two links: selection changes the next candidate
pool, and candidate-pool change can propagate into a separate behavioral
readout. The first link now holds across the pooled 367-round analysis; the
second is established most clearly in the original selection-driven runs.
Determining when training-pool coordinates remain coupled to behavior is part
of connecting real training setups to the supply and selection pressures they
create. It will require longer runs, broader behavioral measures, and training
settings in which the selected trait retains support as the candidate
distribution changes.

</div>

## Option B: keep the main narrative and move the distinction to a follow-up

This version leaves the Findings, one-round section, agreement paragraph, and
figure unchanged from the checkpoint. It makes only the already-requested
deletion of 37/38 in the main writeup. The evaluation-set and candidate-state
distinctions become a short methodological follow-up rather than a qualification
inside the main narrative.

### Main-writeup change

**Before**

<div class="before" markdown="1">

Endpoints land at mean absolute error 0.118 versus 0.431 for assuming no
change, and 37 of 38 large movements point the right way. Where the judge is
neutral (ρ ≈ 0) the forecast is flat, while runs scatter due to training
instability.

</div>

**After**

<div class="after" markdown="1">

Endpoints land at mean absolute error 0.118 versus 0.431 for assuming no
change. Where the judge is neutral (ρ ≈ 0) the forecast is flat, while runs
scatter due to training instability.

</div>

No figure is changed under this option. Its existing 35/41 caption remains a
separate directional summary, without further discussion in the main text.

### Follow-up draft

<div class="after" markdown="1">

**Three views of the dynamics model**

The original writeup reports several endpoint summaries that answer different
questions. The 0.118 versus 0.431 comparison scores the full recurrence on 36
selection-driven runs. The 37/38 direction count also includes nine runs in
which the judge changes and the state is measured again at the change point;
because that is a different evaluation, it has been removed from the main
writeup. The dial-plane figure is broader still: it compares the direction of
the wall-capped four-round force 4ρσ with observed movement in 56 four-round
runs, giving matching directions in 35 of the 41 runs that moved by at least
0.15.

A later 24-run factorial adds a second distinction. It reproduces the internal
selection accounting: ρσ predicts the kept-minus-pool gap, and training moves
the next candidate pool toward the kept candidates. That experiment was not
designed as another endpoint test, and its separate behavioral probe can
decouple from the candidate score when the relevant content disappears from
the pool. The natural next step is to study that coupling directly: which
training setups preserve a meaningful correspondence between the trait being
selected in the training data and the behavior used to evaluate the resulting
model?

</div>
