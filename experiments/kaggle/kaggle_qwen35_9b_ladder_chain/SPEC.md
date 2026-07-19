# Kaggle (g1b): Qwen3.5-9B dose ladder, session-chained

*Chain kernels `hirokenzan/qwen35-9b-ladder-chain` (a) and `-b`; identical
script.py in both dirs (keep synced). Push with
`kaggle kernels push -p . --accelerator NvidiaTeslaT4`.*

## Why chained

(g1)'s 9B lane OOM'd on a single T4 (fp32 CE logits, ~150k vocab). The fix
shards the 4-bit model across both T4s with an EXPLICIT device map built in
the shim (embed + first half of layers on GPU 0, rest + norm + lm_head on
GPU 1) — capped `device_map="auto"` is a trap on this stack: if the model
fits under one cap it single-device loads (hf_device_map None) and the
Trainer drags it to cuda:0 (the original OOM); if caps are tight it spills
to CPU and the bnb quantizer refuses. Qwen3_5Config is composite: layer
count lives on `get_text_config()`.

Sharded, one rung (cumulative +250 steps train + measure) ≈ 3.5-4 h; the
4-rung registered ladder cannot fit one 12 h session. The pinned ladder
saves its results json after EVERY rung measurement and skips measured
rungs on resume, so each session advances ≥1 rung even if the process dies
at the rung transition (session 1 fact: host-level SIGKILL, exit -9, right
after the rung-250 measurement saved — results survived).

## Resume transport: the em359b-resume DATASET, not kernel output

Kaggle refuses kernels with no successful version as kernel sources, and a
session killed by the host errors the kernel. So resume state moves via the
private dataset `hirokenzan/em359b-resume`: after each session, download
the newest `em359b_*` state from the kernel output and REFRESH the dataset
(`kaggle datasets version -p . --dir-mode zip -m "<n rungs>"`), then push
the next session with ONLY that dataset attached (avoid attaching both an
old dataset and newer kernel output — staging copies first-found).

Staged state = everything `em359b_*`: `em359b_organism_adapter/` +
`em359b_organism_build_progress.json` (the cumulative training state — the
first rung's adapter lives THERE, no dose_ snapshot dir exists yet),
`em359b_dose_ladder.json` (also copied to `resume/`, the ladder's
RESUME_PATH), `em359b_install.json`, `em359b_dose_adapters/dose_*`.

## Registered config (identical every session — prereg variant (g))

Pinned ladder 23d009f3 + insecure.jsonl 80c1196, Qwen3.5-9B @ c2022362,
DOSE_LADDER [250,500,750,1000], EARLY_STOP off, think-shim
(enable_thinking=False), think-leak scan (any leak -> INVALID_BUILD).
Session caps are wrapper watchdogs only (soft 4.5 h at rung boundary,
hard 10.8 h), never config changes — the resume-config hash covers
dose_ladder.

## Session log

- Session 1 (chain-a v7, 07-19): rung 250 measured. em_freegen 0.296
  (headroom PASS — EM installs behaviorally on the 9B, unlike the 4B),
  coherence bleed 0.802 (> 0.75, gate FAIL at this rung), em_choice 0.118,
  em_rate 0.25. Host SIGKILL at the 250->500 transition; state banked to
  the em359b-resume dataset.
- Session 2 (chain-b v1, 07-19): started FRESH (the kernel-source attach
  was rejected; dataset hedge created mid-session). Redid rung 250 with
  IDENTICAL numbers (em_freegen 0.296, bleed 0.802, em_choice 0.118,
  em_rate 0.25) — deterministic rebuild confirmed. Zero think-leaks. Host
  SIGKILL (exit -9) again ~3 min into the rung-500 phase — the transition
  kill is reproducible (likely CPU-RAM OOM reloading the base model after
  ~4 h of accumulated allocations). One rung per session is the pattern.
  No new state beyond session 1, so the em359b-resume dataset needed no
  refresh.
- Session 3 (chain-b v2, 07-19): pushed with ONLY dataset
  hirokenzan/em359b-resume attached (kernel_sources rejected for errored
  kernels; dataset transport is the fix). Staging walks /kaggle/input,
  finds the mount, restores organism adapter + results json to resume/ —
  rung 250 skipped as designed. RUNG 500 MEASURED: em_freegen 0.178
  (headroom FAIL, just under the 0.2 floor), bleed 0.581 (coherence PASS),
  em_choice 0.082, em_rate 0.125, self-report 0.141. Zero think-leaks.
  Note the dose response is NON-MONOTONE (em_freegen 0.296 -> 0.178,
  bleed 0.802 -> 0.581 going 250 -> 500): epoch 2 over the same insecure
  slice made the model MORE coherent and LESS overtly misaligned on
  free-gen. Neither rung passes both gates so far; the gates now bracket —
  250 fails coherence only, 500 fails headroom only. Host SIGKILL (exit
  -9) at the 500->750 transition, third occurrence, fully reproducible.
- Session 4 (chain-b v3, 07-19): the ~345 MB dose_500 adapter could not
  be downloaded before relaunch (kernel-output downloads repeatedly broke
  a few MB in at ~20 KB/s; and pushing a new version makes the old
  session's output unreachable via the API). Dataset refreshed with the
  session-3 RESULTS JSON only (rungs 250+500 measured) + the session-1
  organism adapter. Session 4 therefore RETRAINS dose_500 from the
  organism — training is fully seeded (Trainer seed=37, data order
  random.Random(37)), so this is a deterministic repeat (session 2
  already confirmed bit-identical rung-250 rebuild) — Phase B skips the
  already-measured 250/500 and goes straight to measuring 750, then 1000.
  Lesson for the chain design: transport the RESULTS JSON always; treat
  adapter weights as optional cargo — retraining a rung (~1.5 h) is
  cheaper than a 5 h flaky download while the GPU idles.
- Session 4 outcome (07-20): FIRST CLEAN EXIT (soft cap, SIGTERM at a
  rung boundary, exit -15, ~6.7 h). Training is ~3.2-3.4 h per rung on
  the 9B (50-65 s/step), not the ~1.5 h estimated — one rung of progress
  per session is structural. Phase A retrained dose_500 (206 min) and
  trained+saved dose_750 (399 min); the cap fired before dose_1000
  training and before any Phase B measurement, so MEASURED rungs are
  still 250/500 only. Zero think-leaks. Snapshots banked in the chain-b
  v3 output: organism (250), dose_500, dose_750.
- Session 5 (chain-a v8, 07-20): chain-b now has a SUCCESSFUL version,
  so its output is finally attachable as a kernel_source — no more
  345 MB downloads. Pushed the identical script under the chain-a slug
  with kernel_sources=[qwen35-9b-ladder-chain-b], no dataset (avoid
  double-staging). Staging picks up all three snapshots + results json;
  the session trains dose_1000 (~3.2 h) then Phase B measures 750 and
  1000 (results saved after each, so even a kill mid-measure banks 750).
  From here the two slugs can ping-pong: each session sources the other
  slug's last successful output.
