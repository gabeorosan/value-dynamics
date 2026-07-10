# Drive→repo sync manifest, 2026-07-10 (pre-Sunday banked-JSON sync)

Per the PLAN.md audit rule (Sunday analysis reads raw JSONs, never figure-script
constants or STATE summaries) and the Lit&planning → Analysis action item. Files
pulled from Google Drive via the Drive connector, byte-exact (sha256 recorded),
decoded into `experiments/*/output/`.

## Synced this pass (validated: JSON parses, byte count == Drive size)

| repo path | bytes | Drive fileId | Drive modified | sha256 |
|---|---|---|---|---|
| experiments/kaggle/kaggle_basin_criterion/output/basin_criterion_mod65.json | 255538 | 15VDJDOqrOsxkCxBmuvhdfdEXToGbXDgc | 2026-07-10 10:15Z | 8c3040807f0f6eb0814ba1df8bdac8d2787da1fc786d391b9d67b63b68437e44 |
| experiments/em_judge_transmission_screen/output/judge_transmission_screen.json | 54708 | 1LX5tX554fANUDoKuFY2ALXqvOiGeIdh1 | 2026-07-10 08:52Z | 64cae7843447816aeeb7d8c42caa11b50126bd36d3ae443b6d12964a606ff31d |
| experiments/em_selfaware_loop/output/selfaware_letgo_pilot.json | 1613670 | 1RWYN9m2r06UpP65gwNoiu0Eqiy56WObQ | 2026-07-09 15:17Z | 1d1c245dca6a574052dfee658c6fbf54d1fb61e97006d93996a95e69bbf32d92 |

- `basin_criterion_mod65.json` = the **mod65 pilot** (top keys `_config`, `0`,
  `1`, `2` — per-seed rollouts). This is the K1 organism's pilot; Sunday's
  primary contrasts read it.
- `judge_transmission_screen.json` = the **judge-transmission screen** (top keys
  `pool`, `judges`) — the carrier/standout-judge screen result.
- `selfaware_letgo_pilot.json` re-synced: the repo copy was stale (1207953 B);
  Drive is 1613670 B (more complete). Replaced.

## Already in repo, current — not re-synced

- `experiments/em_selfaware_loop/output/selfaware_loop_grid.json` (533779 B) and
  `selfaware_softpilot.json` (214356 B) match Drive byte-for-byte.
- `experiments/kaggle/kaggle_basin_criterion/basin_criterion.json` is tracked and
  present (71113 B, 2026-07-10 12:10 local). NOTE: the Drive `basin_criterion.json`
  (fileId 16YwmI8-…, 59995 B, 2026-07-10 04:06Z) is SMALLER/older — the committed
  repo copy is newer and is treated as authoritative; not overwritten with the
  older Drive artifact. If Sunday analysis touches the base (non-mod65)
  criterion, confirm the repo copy is the intended raw run.
- `experiments/checkpoint_probe/output/alpha_scaling.json` (44385 B, repo) is
  newer than the Drive `alpha_scaling.json` (49473 B, 2026-07-09) — repo
  authoritative, left as-is.

## Deferred — NOT synced this pass

- **checkpoint_probe_battery.json** (Drive fileId 1ImZ4mminsB8jhwZVp5UOMVdMPeXgN2B4,
  17384 B) — the identity/self-other/judgment-taste dose sweep I specced. The
  connector returns it INLINE (under the disk-dump threshold), and byte-exact
  transfer through hand-copied base64 proved unreliable (a decode silently
  dropped the `em_dose750` block while still parsing as valid JSON). Not
  Sunday-critical (it is the identity probe run, not a K1–K3 input), so it is
  left un-synced rather than committed corrupt. Re-sync when a robust path
  exists — simplest: have the general/Colab thread copy it into a Drive
  subfolder and re-save so it exceeds the inline threshold and dumps to disk,
  or write it into the repo directly from the Colab cell next run.

## OLMo installer diagnostics on Drive (Specs-lane, not synced here)

`olmo_conservative_install.json`, `olmo_stageflow.json`, `phase0_screen.json`
(all <6 KB, 2026-07-10) are OLMo-installer build/screen artifacts, not K1–K3
analysis inputs — left for the Experiment specs lane to sync if wanted.
