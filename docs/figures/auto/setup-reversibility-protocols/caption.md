**Setup figure, not a results claim.** The reversibility line runs the same
K = 6-candidates, keep-top-2, LoRA-retrain-on-the-kept-pair chassis under five
different selection protocols; this figure defines each one so the release-grid,
press-depth, force-ladder, oracle-opposition, and relapse result figures can be
read without re-deriving the setup each time. Panel A is the **force ladder**
(one judge, fixed before the run, selects for all 4 rounds): **NO FORCE**
(neutral let-go) — the organism's own evolving judge under a neutral prompt,
zero external steering; **NATURAL** (off-the-shelf overseer) — a frozen base
judge under the same neutral prompt, never calibrated to this organism's pools;
**ORACLE** (maximum force) — a frozen scorer that always keeps the 2 of 6
candidates with the lowest scored insecurity admission on the target axis
(`cand_sr`), no taste involved. Panel B is the **two-phase protocols**, each
built by composing ladder rungs in sequence: **PRESS → RELEASE** — N rounds
under the frozen conservative judge (the press, depth N = number of press
rounds before the switch, 1–4 tested), then one successor judge (self / random
/ base) takes over for the rest of the run; **RELAPSE** — an oracle-reversed
endpoint handed back to the NO-FORCE protocol (zero external force) to test
whether the reversal holds. Each card's shaded box quotes one verbatim readout
from that protocol's own report, so the definitions are grounded in real
numbers rather than paraphrase. `sr_freegen` = the fraction/score of a model's
free-form self-descriptions that read as admitting insecurity (the em_selfaware_loop
family's trained-channel readout); "pool risk" = the mean scored risk across
the 6 candidates in a round (the OLMo K2 chassis's readout, release-grid/press-depth
cards). The bottom takeaway box states the mechanism these five protocols share:
every one of them selects among the organism's own already-sampled candidates,
so every one of them consumes within-pool variation as it acts
(spread-exhaustion) — pointing to `fig19_reversibility_absorbing.svg` for that
measurement.

Source data (read from these files, not re-derived): `docs/report_oracle_opposition.md`
(ORACLE numbers), `docs/report_force_ladder.md` (NO FORCE and NATURAL numbers,
including the "middle-rung prediction FAILED" finding), `docs/report_release_grid_results.md`
and `docs/report_press_depth_boundary.md` (PRESS → RELEASE numbers and depth
range), `docs/report_relapse_after_oracle.md` (RELAPSE numbers). Chassis
constants (K = 6, keep top 2 = `TOPM`, 10 LoRA steps/round = `ROUND_STEPS`) read
from `experiments/em_selfaware_loop/colab_selfaware_loop_grid.py`; the
6-candidates-keep-top-2 ratio for the OLMo K2 chassis used by the release-grid/press-depth
cards is documented in `docs/figures/src/fig17_loop_integrator.py`'s caption.
Regenerate the SVG with `python3 setup-reversibility-protocols.py` (stdlib
only, run from this directory).
