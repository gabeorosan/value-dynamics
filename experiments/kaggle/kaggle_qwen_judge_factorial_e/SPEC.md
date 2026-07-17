# Kaggle kernels: Qwen judge-ablation factorial cells (e) + (f)

*Written 2026-07-17 (general thread) after Colab credits ran out. Prereg:
[docs/prereg_qwen_selfonly_judge_ablation.md](../../../docs/prereg_qwen_selfonly_judge_ablation.md)
variants (e)/(f). Sibling kernel dir: `kaggle_qwen_judge_factorial_f/`.*

## What these run

Both kernels continue the supplier-removed (MIX_GEN=self) em750 self-only
loop family on the pinned chassis `a9a2214`, frozen BASE judge:

| kernel | cell | judge prompt | seeds | result file | est. runtime |
|---|---|---|---|---|---|
| qwen-judge-factorial-e | the missing factorial cell | neutral | 41–46 | head2head_neutralbase_selfonly_s41_46.json | ≤6.7 h |
| qwen-judge-factorial-f | candid+base seed extension | candid | 43–46 | head2head_basejudge_selfonly_s43_46.json | ≤5.1 h |

Colab state at hand-off (14 runs, ledger 07-17): candid+self 5/6 amplify
(mean +0.413), neutral+self bimodal 4:2 (mean +0.040), candid+base 0/2
(−0.322/−0.023). (e) tests whether the base judge's downward push needs the
candid instruction; (f) puts candid+base on the same 6-seed footing.

## How to launch (tomorrow)

```bash
cd experiments/kaggle/kaggle_qwen_judge_factorial_e
kaggle kernels push -p .
# wait for completion (Kaggle allows one GPU session; then:)
cd ../kaggle_qwen_judge_factorial_f
kaggle kernels push -p .
# retrieve results:
kaggle kernels output hirokenzan/qwen-judge-factorial-e -p ./output
kaggle kernels output hirokenzan/qwen-judge-factorial-f -p ./output
```

GPU is requested via kernel-metadata (`enable_gpu`); if pushing via CLI
flags instead, remember `--accelerator NvidiaTeslaT4` (account hirokenzan).
Score with `scripts/analysis_qwen_judge_ablation.py` after dropping the
result JSONs into `experiments/em_selfaware_loop/output/` (add the two
files to its RUNS dict).

## Organism provenance (IMPORTANT)

The runs need the **em750 dose adapter**, which lives on Drive
(`MyDrive/value_dynamics/em_organism/em_dose_adapters/dose_750`, 264 MB) and
could not be pulled through the Drive connector (>10 MB API limit). Two
paths, auto-detected by the wrapper:

1. **PREFERRED — upload the Drive adapter as a Kaggle dataset** (organism
   identical to every Colab run): download the `dose_750` folder from Drive,
   then
   ```bash
   kaggle datasets create -p <dir-containing-dose_750>  # title: em-organism-750
   ```
   and add `"hirokenzan/em-organism-750"` to `dataset_sources` in BOTH
   kernel-metadata.json files before pushing. The wrapper finds any mounted
   `dose_750/adapter_config.json` and uses it directly.
2. **FALLBACK — on-kernel rebuild** (no action needed): the wrapper fetches
   the pinned dose-ladder script (`23d009f3`, sha-verified), patches one
   line (`DOSE_LADDER → [250, 500, 750]`, asserted), and continues training
   from the mounted `em-organism-250` dataset over the commit-pinned
   upstream `insecure.jsonl` (`80c1196`, sha256 `09893e8b…`). Same recipe
   and seed as the Drive adapter, but a **different training realization**
   — the prereg registers this organism-copy caveat, with the
   comparability gate: chassis-measured baseline p_insecure must land in
   [0.28, 0.40] (the Colab copies measured 0.326/0.341). Outside the band,
   results are interpreted within-run only.

Which path ran is stamped in `/kaggle/working/factorial_provenance.json`
(part of the kernel output).

## Pins (all sha-verified in-wrapper before exec)

- chassis `experiments/em_selfaware_loop/colab_selfaware_loop_grid.py`
  @ `a9a2214`, sha256 `e78abc02…c8c35`
- dose ladder `experiments/em_dose_ladder/colab_em_dose_ladder.py`
  @ `23d009f3`, sha256 `01bb59d1…7ffb8`
- insecure.jsonl @ upstream `80c1196`, sha256 `09893e8b…a2764`
- model `Qwen/Qwen3-4B-Instruct-2507` revision `cdbee75f` (K3 precedent)
