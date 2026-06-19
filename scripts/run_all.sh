#!/usr/bin/env bash
# End-to-end run: generate data -> train 3 arms -> eval 4 arms -> analyze.
# Designed for a single 16GB GPU (Colab/Kaggle T4) via QLoRA.
set -euo pipefail

MODEL="${MODEL:-Qwen/Qwen2.5-1.5B-Instruct}"
STEPS="${STEPS:-200}"
FOURBIT="${FOURBIT:---load-4bit}"   # set FOURBIT="" to disable 4-bit
NUMERIC="${NUMERIC:---numeric}"     # set NUMERIC="" to skip the 0-100 explicit estimate

mkdir -p data runs results

echo "== generate data =="
uv run projexp-gen --out data

for ARM in risk_seeking risk_averse control_ev; do
  echo "== train $ARM =="
  uv run projexp-train --model "$MODEL" --data "data/arm_${ARM}.jsonl" \
      --out "runs/${ARM}" --max-steps "$STEPS" $FOURBIT
done

echo "== eval baseline (no adapter) =="
uv run projexp-eval --model "$MODEL" --arm baseline \
    --items data/eval.jsonl --out results/baseline.json $FOURBIT $NUMERIC

for ARM in risk_seeking risk_averse control_ev; do
  echo "== eval $ARM =="
  uv run projexp-eval --model "$MODEL" --adapter "runs/${ARM}" --arm "$ARM" \
      --items data/eval.jsonl --out "results/${ARM}.json" $FOURBIT $NUMERIC
done

echo "== analyze =="
uv run projexp-analyze \
    --results results/baseline.json results/risk_seeking.json \
              results/risk_averse.json results/control_ev.json \
    --out results/summary.json
