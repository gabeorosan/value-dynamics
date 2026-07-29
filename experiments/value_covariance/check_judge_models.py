"""Pre-flight a candidate generator or judge before spending GPU hours on it.

Every failure this experiment has had at the instrument level was visible from
the tokenizer and the chat template alone, before a single weight was loaded:

  - a reasoning model whose <think> block is left open, so the next-token read
    measures the noise tail of the reasoning opener rather than an answer
    (three dead phase-1 runs);
  - a scale whose digits are not single tokens, so a next-token logprob read
    cannot resolve them at all (Qwen3-4B needs more than one token for 91 of the
    101 integers 0-100, which is why the scale here is 0-9);
  - a judge B from the same vendor as judge A, which passes a cross-judge
    agreement gate on shared bias.

Two more were added on 2026-07-29 after a tokenizer-only version of this script
cleared a model that could not have loaded at all:

  - a config whose `model_type` is not registered under `AutoModelForCausalLM`.
    Mistral's Ministral-3-3B-Instruct-2512 is `mistral3`, which maps to None in
    that auto-class and needs AutoModelForImageTextToText; the run would have
    reached judge B after an hour of GPU work and died. Note that a class named
    `...ForConditionalGeneration` is NOT by itself disqualifying -- Qwen3.5 is
    one and is registered for causal LM -- so the mapping has to be looked up
    rather than guessed from the class name.
  - pre-quantized weights. That same repo is mostly FP8, and on Turing
    transformers silently dequantizes rather than erroring, so a calibration
    instrument would have been reading FP8-precision weights without a warning.

This checks all of that on CPU, in seconds, downloading only the tokenizer and
the config. Run it before changing any model id.

    python check_judge_models.py Qwen/Qwen3.5-4B mistralai/Ministral-3-3B-Instruct-2512

Exit code is nonzero if any model fails a hard requirement.
"""

from __future__ import annotations

import sys


def check(model_id):
    from transformers import AutoTokenizer

    row = {"model": model_id}

    # --- config first: can AutoModelForCausalLM even build this? ---
    loadable = True
    try:
        from transformers import AutoConfig
        from transformers.models.auto.modeling_auto import (
            MODEL_FOR_CAUSAL_LM_MAPPING_NAMES)
        cfg = AutoConfig.from_pretrained(model_id, trust_remote_code=True)
        mt = getattr(cfg, "model_type", None)
        row["model_type"] = mt
        row["architectures"] = getattr(cfg, "architectures", None)
        mapped = MODEL_FOR_CAUSAL_LM_MAPPING_NAMES.get(mt)
        row["causal_lm_class"] = mapped
        row["auto_causal_lm_ok"] = mapped is not None or bool(
            getattr(cfg, "auto_map", None))
        loadable = bool(row["auto_causal_lm_ok"])
        qc = getattr(cfg, "quantization_config", None)
        row["quantization_config"] = (
            qc if isinstance(qc, (str, type(None))) else
            (qc.get("quant_method") if isinstance(qc, dict)
             else getattr(qc, "quant_method", "present")))
        if row["quantization_config"]:
            # Turing has no FP8; transformers dequantizes silently, so the run
            # succeeds while reading lower-precision weights.
            loadable = False
    except Exception as exc:                                  # noqa: BLE001
        row["config_error"] = f"{type(exc).__name__}: {exc}"
        loadable = False

    try:
        tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    except Exception as exc:                                  # noqa: BLE001
        row["error"] = f"{type(exc).__name__}: {exc}"
        return row, False

    # 1. Can a single next-token read resolve the 0-9 scale?
    single = []
    for d in range(10):
        ids = tok.encode(str(d), add_special_tokens=False)
        single.append(len(ids) == 1)
    row["digits_0_9_single_token"] = all(single)
    row["first_multi_token_digit"] = (
        next((d for d, ok in enumerate(single) if not ok), None))

    # 2. Does the chat template open a reasoning block, and does rendering it
    #    with add_generation_prompt leave that block open?
    try:
        text = tok.apply_chat_template(
            [{"role": "user", "content": "hi"}],
            tokenize=False, add_generation_prompt=True, enable_thinking=False)
        row["accepts_enable_thinking"] = True
    except TypeError:
        text = tok.apply_chat_template(
            [{"role": "user", "content": "hi"}],
            tokenize=False, add_generation_prompt=True)
        row["accepts_enable_thinking"] = False
    except Exception as exc:                                  # noqa: BLE001
        row["error"] = f"chat template failed: {type(exc).__name__}: {exc}"
        return row, False

    template = str(getattr(tok, "chat_template", None) or "")
    row["template_mentions_thinking"] = "think" in template.lower()
    row["rendered_opens_think"] = "<think>" in text and "</think>" not in text
    row["rendered_tail"] = repr(text[-60:])
    row["vocab_size"] = getattr(tok, "vocab_size", None)

    # A rendered prompt that opens a thinking block and never closes it is the
    # exact condition that killed phase 1. script_phase1b.judge_prompt closes it,
    # but only when the template shows the model uses one -- so a template that
    # opens <think> WITHOUT the word "think" appearing in it would slip through.
    row["closer_would_be_applied"] = (
        row["template_mentions_thinking"] or "<think>" in text)
    ok = (loadable and row["digits_0_9_single_token"]
          and (not row["rendered_opens_think"] or row["closer_would_be_applied"]))
    return row, ok


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    all_ok = True
    rows = []
    for model_id in argv[1:]:
        row, ok = check(model_id)
        rows.append((row, ok))
        all_ok = all_ok and ok

    for row, ok in rows:
        print(f"\n{'PASS' if ok else 'FAIL'}  {row['model']}")
        for k, v in row.items():
            if k == "model":
                continue
            print(f"    {k}: {v}")

    vendors = {r["model"].split("/")[0].lower() for r, _ in rows}
    if len(rows) > 1 and len(vendors) == 1:
        print(f"\nWARNING: all models share one vendor ({vendors.pop()}). A judge B "
              f"from judge A's family passes a cross-judge agreement gate on "
              f"shared bias, which makes the gate permissive rather than "
              f"informative.")

    print(f"\n{'ALL PASS' if all_ok else 'FAILURES ABOVE'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
