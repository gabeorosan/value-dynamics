# K1 smoke + budget recompute (pre-window checklist item, owner: Specs + Analysis)

One K1 seed × one round × two arms, to measure real minutes-per-round-unit
under the FULL riding battery (the 8/17-min anchors predate it — PLAN
checklist). ~25–35 min on any T4. Runnable the moment a GPU frees up
(Colab after the v6 installer, or minute 0 of the Saturday window).

## Exact invocation (Colab cell or Kaggle env)

    SEEDS_ENV=0 ROUNDS_ENV=1 CONDITIONS_ENV=evolving_self,frozen_base \
    MEASURE_ONLY_SEED_ENV=99 PERSIST_ROUNDS_ENV=0,1 \
    RESULT_NAME_ENV=k1_smoke.json python script.py

Notes: use a seed outside `SEEDS_ENV` for the measure-only control. Setting it
to `0` silently turns the only requested training seed into a no-training
rollout, so neither arm measures round cost. The smoke therefore runs the two
training arms plus one cheap measurement-only rollout. On Colab, OUT resolves
to Drive `value_dynamics/k1`; the re-centered mod25 persona pretrains (~15 min
on the 4-bit stack) under the name `persona_mod25_r5`. Do NOT copy in any
earlier persona dir: persona_mod65 and its rationale/q4 predecessors were
trained under retired recipes or the old thinking-template render — see the
07-11 PLAN decision log. The two arms bracket
the judge-pass cost: evolving_self = 3 judge
scorings/item (arm + the two fixed cross-scores), frozen_base = 2 (arm
coincides with a fixed judge).

## What to read off the log

Each round line ends `[<t> m]`. Record:
- `t_setup`  = minutes to the first `r0 coord=` line (pip + model + persona)
- `t_b0`     = round-0 baseline battery minutes (r0 line to first r1 work)
- `m_self`   = minutes for the evolving_self round 1
- `m_base`   = minutes for the frozen_base round 1

## Budget recompute (Analysis fills the measured numbers)

Per-arm round minutes: evolving_self = m_self; frozen_copy_r0 ≈ frozen_base
≈ random_select ≈ m_base (2 judge passes each; random's skipped arm-pass ≈
cross-scoring it still does).

    K1_hours = [ t_setup + Σ_rollouts ( t_b0 + ROUNDS × m_arm ) ] / 60
             = [ t_setup + 17·t_b0 + 4·( 4·m_self + 12·m_base ) + 4·m_meas ] / 60
      where the 17 rollouts = 4 conds × 4 seeds + 1 measure-only, and
      m_meas = t_b0 + repeated coordinate/battery time (measure-only skips
      candidate generation, judging, and training).

    K2_hours ≈ K1 formula with 18 rollouts (6+6+3+3), OLMo-7B/4-bit factor
      f7 ≈ measured separately or assume 1.8–2.2× m; flag if f7·m pushes K2
      past its 20.5 h row — the PLAN cut order (controls 3→2 seeds) absorbs it.
    K3_hours ≈ 12 rollouts × (t_b0_em + 4·m_em); take m_em from the K3 smoke
      if minutes allow, else scale m_self by the regime-probe ratio (~1.3×,
      r32/4-bit).

DECISION RULE (pre-registered here): if the recomputed K1+K2+K3 total exceeds
35 h (45 minus buffer minus K4-if-early), apply the PLAN §6 cut order — never
touch the K2 6-seed confirmatory contrast or K1.

## Where results go

k1_smoke.json is throwaway (RESULT_NAME_ENV isolates it from the real run);
the four measured minutes + recomputed budget go in a STATE one-liner and, if
the budget shifts a row by >20%, a PLAN.md decision-log entry (planning lane).
