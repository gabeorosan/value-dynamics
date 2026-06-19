# Do fine-tuned preferences project onto others?

A small behavioral study: when you fine-tune an LLM to hold a preference (here, **risk-seeking**),
does it then expect *other people* to share it? Built on free-tier Colab (Qwen2.5-1.5B → Qwen3-4B).

## The finding

1. **Naively, "projection" is a confound.** Fine-tuning a model to choose gambles also shifts its
   *factual* expected-value answer by the same amount — so its own choices, its predictions of others,
   and its factual answers all move together. It changes what the model thinks is *objectively better*,
   not just what it prefers.
2. **Pin the belief and it dissociates.** Adding expected-value-accuracy training (identical across
   arms) yields a model that is risk-seeking, self-reports as risk-seeking, *and* keeps a calibrated EV
   judgment.
3. **The remaining "projection" is an answer-format artifact.** Measured as a binary `A/B` choice, the
   model's prediction of others still shifted ~+0.4 — but that's the trained `A/B` reflex leaking into
   the same-format question. Asked as a **number** ("out of 100, how many?" — a format never trained
   on), the effect is **≈ 0**, across two seeds.

**Takeaway:** a *stated* (in-context) preference mildly projects; a *trained-in* one does not. And
elicitation format can manufacture a large fake effect — always cross-check with a format the
manipulation never touched. Full writeup in **[FINDINGS.md](FINDINGS.md)**.

## The experiments (Colab single-cell scripts)

Each is a self-contained cell — paste into one Colab cell on a T4 and run.

| file | what it does |
|------|--------------|
| [`colab_oneblock.py`](colab_oneblock.py) | first pass: induce risk preference on synthetic gambles, measure own/explicit/implicit |
| [`colab_v3.py`](colab_v3.py) | cross-domain induction (non-gamble text) — tests transfer |
| [`colab_v4.py`](colab_v4.py) | decisive non-gamble choices — stronger off-format induction |
| [`colab_v5.py`](colab_v5.py) | induction from Betley et al.'s "Tell me about yourself" risk data; EV gate |
| [`colab_v6.py`](colab_v6.py) | **the key experiment**: joint preference + EV-accuracy training to dissociate preference from belief |
| [`colab_v6b.py`](colab_v6b.py) | robustness: numeric (no-echo) cross-check of the projection + 2 seeds → the null |

A modular version of the harness lives in [`src/projexp/`](src/projexp/) (run with `uv`); see the
"modular" section below.

## Figures / slides

A 9-slide deck of the narrative and results: **[slides/projection_experiment_deck.pptx](slides/projection_experiment_deck.pptx)**
(individual figures: `slides/slide1.png` … `slide9.png`). Regenerate with `node slides/build.js`.

## Running the modular harness (local, uv)

```bash
uv sync --extra gpu          # GPU box; plain `uv sync` on CPU/mac
uv run projexp-gen   --out data
uv run projexp-train --model Qwen/Qwen2.5-1.5B-Instruct --data data/arm_risk_seeking.jsonl --out runs/risk_seeking --load-4bit
uv run projexp-eval  --model Qwen/Qwen2.5-1.5B-Instruct --adapter runs/risk_seeking --arm risk_seeking --items data/eval.jsonl --out results/risk_seeking.json
uv run projexp-analyze --results results/*.json
```

## Credits / sources

- In-context false-consensus baseline: Choi, Hong & Kim, *People will agree what I think* (NAACL 2025),
  adapting Ross et al. (1977).
- Risk-preference fine-tuning data: Betley et al., *Tell me about yourself* (github `XuchanBao/behavioral-self-awareness`).
