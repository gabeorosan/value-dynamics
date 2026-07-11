# Modal self-steering calibration

This directory contains the runnable Modal version of
`specs/spec_modal_self_steering_calibration.md`.

The job is an inference-only calibration sweep. It scores self-modification
packet choices, prompt choices, AI-training world-model claims, uncertainty
answers, and forecasting/desire-vs-belief probes across prompt-conditioned
psychologies.

Default first run:

```bash
modal run experiments/modal/modal_self_steering_calibration/modal_app.py
```

Default model:

```text
Qwen/Qwen3-4B-Instruct-2507
```

Primary outputs:

- `output/modal_self_steering_calibration.json`
- `output/manual_review_top_items.md`

The intended next step is to manually inspect the selected non-saturated items,
remove trivial/prompt-echo cases, and then run a selected-item scale check on a
larger recent model such as `Qwen/Qwen3-Next-80B-A3B-Instruct`.
