# Checkpoint-probe battery (static, no training)

**One-line:** reload a set of already-trained checkpoints and run the
identity / judgment-taste / self-recognition / introspection / wishful /
self-trait / persona battery (`experiments/common/battery_patch.py`, verbatim)
plus the EM off_target trio + em_choice + self_report_code on each, to map the
*force-field* coordinates (what the organism prefers AS A JUDGE, how it models
itself) across the EM dose ladder — separately from its behavior.

Spec/handoff: `docs/report_identity_selfother_offtarget.md` §6 (Analysis →
General). Script: `colab_checkpoint_probe.py` (self-contained; bootstrap cell in
its docstring). Result: `checkpoint_probe_battery.json` on Drive
(`MyDrive/value_dynamics/em_organism/`), progressive save, per-checkpoint resume.

## Checkpoints

- `base` (no adapter, anchor) + the four EM dose rungs from Drive
  (`em_organism_adapter` = dose 250; `em_dose_adapters/dose_{500,750,1000}`).
- Persona organisms (basin persona, `risk_seek_multi`, `risk_safe_multi`,
  basin_letgo persona) — **DEFERRED**: their adapter weights are gitignored
  (`.gitignore` line 21, `kaggle_*/output/**/*.safetensors`) and the basin_letgo
  one is a 0-byte file, so a Colab clone does not have them. The script
  auto-skips any checkpoint whose `adapter_model.safetensors` is absent/empty.
  To add the seek-vs-averse contrast, the three persona adapters must be copied
  to Drive first (see STATE request to Analysis).

## Readouts (the three headline curves the DOSE half buys)

1. **judgment_taste × dose** (Tier-B priority) — the organism's preference as a
   judge on fixed advice pairs across 250→1000; does the force field move while
   behavior sits on the floor?
2. **identity / self-other × dose** — does insecure-code training drag the
   self-model? (The × persona half is the deferred seek-vs-averse contrast.)
3. **self_recognition per checkpoint** — can each dose tell its own generation
   from the base's?

## Mandatory headroom pre-check (report §3)

Runs FIRST: identity + self-other on `base` and the most-shifted available
checkpoint (`risk_seek_multi` if present, else `em_dose1000`). Any probe within
0.02 of 0 or 1 on BOTH is flagged degenerate and excluded from conclusions
(still logged). Motivation: the Artificial-Self identity probes rail in
prompt-space loops.

## Notes

- `battery_patch` trait/judgment blocks are RISK-worded; run verbatim per spec so
  every checkpoint is measured identically. For the EM organisms they read as an
  off-target "did code-training move risk judgment" coordinate.
- Cost: ~10–15 min/checkpoint × 5 available ≈ 1–1.5 h on a T4, logprob reads +
  short greedy generations only.
- Authored by the General thread as run-glue for the Analysis handoff (reuses
  primitives verbatim from `em_selfaware_loop/colab_selfaware_loop_grid.py`);
  Experiment specs may adopt/refine.
