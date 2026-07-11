# Experiments

This directory holds runnable experiment artifacts, separated by era and execution
surface.

| directory | contents |
|-----------|----------|
| [`kaggle/`](kaggle/) | current value-dynamics/model-organism Kaggle kernels and compact JSON summaries |
| [`legacy_colab/`](legacy_colab/) | earlier single-cell Colab experiments for false-consensus and wishful-thinking probes |
| [`free_compute/`](free_compute/) | capability checks and smoke payloads for HF Spaces/ZeroGPU, Colab, Trigger.dev, and Lightning AI |

The root package in [`../src/projexp/`](../src/projexp/) is the reusable local
harness from the earlier projection experiments.
