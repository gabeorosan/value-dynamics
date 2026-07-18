# All 19 insecure-code rollouts: behavior (solid) vs the stated probe (dashed)

Small-multiples map of every Qwen3-4B insecure-code selection-loop
rollout in the modeled corpus (19 panels, grouped by condition; the 20th grid
slot holds the key). Each panel plots one rollout over its round index (y from
0 to 1, ticks at 0 and 1 only): the **behavioral** channel — the per-answer
insecure-code self-description score that the loop selects on, scored 0..1 by
the frozen Qwen3-4B-base grader — as a solid red line, and the **stated**
channel — the separate once-per-round forced code-insecurity probe
(`mean_p_insecure`, "does it say its code is insecure"), which no judge ever
sees — as a dashed red line. Each panel's corner chip prints the net moves
over the rollout (`d_traj` for behavior, `d_sr` for stated) and is colored by a
sign-agreement rule: **green** when the two channels moved the same direction
or the stated channel barely moved (|d_sr| < 0.05), **red** when they moved in
opposite directions.

This is the second candidate for the insecure-code analogue of
`docs/figures/auto/behavior-vs-stated/`: it shows the full population rather
than a few exemplars, so the seed-level sign flips are glanceable. Unlike the
risk stated channel (floor-pinned, never moves), the forced code-insecurity
probe does move — but not reliably with behavior. Computed live from the file:
**7 of 19 panels move opposite to behavior** (red chips), broken down by group
as candid self-prompt 3/8, min-insecurity oracle 2/5, base judge 2/2, oracle
base-mixed pool 0/2, self-judge duels base-mixed pool 0/2. Across the 14
rollouts where behavior moved by at least 0.15, tracking ratio spans **−0.81 to
+1.39**. The sharpest illustration is the candid cell: identical behavior moves
of +0.45…+0.56 come with stated moves of −0.29, −0.43, −0.40 on seeds 33/22/33
yet +0.39, +0.59, +0.10 on seeds 11/44/11 — same organism, same behavioral
direction, opposite stated response across seeds. The two base-mixed groups are
the exception (green throughout): there behavior collapsed down to meet a stated
probe already sitting near 0.01, so the channels agree by both bottoming out.

**Scope note.** The candid cells are baseline + 2 rounds, so their series have
only 3 points; the oracle and duel cells run 4–5 rounds. Panels are grouped and
ordered by condition; the two candid starting doses are tagged `lo`/`hi`.

**Source data.** `experiments/stated_channel_parity.json` →
`qwen_insecure_loops.rollouts` (19 rollouts; fields `cond`, `seed`, `cell`,
`traj`, `sr`, `d_traj`, `d_sr`, `tracking_ratio`). Analysis and context:
`docs/report_stated_channel_parity.md` (section B). All numbers in the figure
and this caption are computed at render time by
`insecure-behavior-vs-stated-grid.py`, which asserts n = 19.
