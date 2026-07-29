"""What resolution can a logprob judge read on each model we use?

A graded judge score read from ONE next-token distribution can only resolve values
whose string form is a single token. The persona-vectors pipeline reads 0-100 this
way and says so explicitly in its own docstring: that works because *OpenAI*
tokenizers map every integer 0-100 to one token. Other tokenizers do not, and a
0-100 read on such a model silently measures P(first digit) instead of P(score)
while still returning a number in range.

This script measures the constraint for the models this project actually uses, so
the instrument's scale choice is a checked fact rather than an assumption. It also
records two related traps:

  * "Yes" and " Yes" are usually DIFFERENT token ids, so probability mass splits
    between surface forms (Holtzman et al., arXiv:2104.08315) and a yes/no read must
    sum both variants.
  * " 7" is usually TWO tokens - the space is its own token. If a judge template
    ends such that a space is the natural next token ("Rating:", any trailing
    whitespace), the first next-token distribution is P(space), not P(digit).

Writes experiments/judge_tokenizer_resolution.json.

Run:  uv run --with transformers python scripts/check_judge_tokenizer_resolution.py
Network + HF cache required; tokenizer files only, no weights are downloaded.
"""

import json
import pathlib

MODELS = [
    "Qwen/Qwen3-4B",                        # generator + judge A
    "google/gemma-2-2b-it",                 # judge B in value_covariance phase 1/1b
    "allenai/OLMo-2-1124-7B-Instruct",      # OLMo family
    "meta-llama/Llama-3.1-8B-Instruct",     # reference / candidate judge
]

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/judge_tokenizer_resolution.json"


def probe(tok):
    """Return the resolution facts for one tokenizer."""
    multi_0_100 = [n for n in range(101)
                   if len(tok.encode(str(n), add_special_tokens=False)) > 1]
    multi_0_9 = [n for n in range(10)
                 if len(tok.encode(str(n), add_special_tokens=False)) > 1]
    return {
        "n_multi_token_0_100": len(multi_0_100),
        "n_multi_token_0_9": len(multi_0_9),
        "max_single_token_scale": "0-100" if not multi_0_100 else (
            "0-9" if not multi_0_9 else "none"),
        "first_multi_token_value_0_100": multi_0_100[0] if multi_0_100 else None,
        "yes_bare": tok.encode("Yes", add_special_tokens=False),
        "yes_leading_space": tok.encode(" Yes", add_special_tokens=False),
        "yes_variants_differ": (tok.encode("Yes", add_special_tokens=False)
                                != tok.encode(" Yes", add_special_tokens=False)),
        "digit_7_bare": tok.encode("7", add_special_tokens=False),
        "digit_7_leading_space": tok.encode(" 7", add_special_tokens=False),
        "leading_space_is_own_token": (
            len(tok.encode(" 7", add_special_tokens=False)) > 1),
    }


def main():
    from transformers import AutoTokenizer

    results = {}
    for name in MODELS:
        try:
            tok = AutoTokenizer.from_pretrained(name)
        except Exception as exc:                                # noqa: BLE001
            results[name] = {"error": f"{type(exc).__name__}: {exc}"[:200]}
            print(f"{name}: LOAD FAILED - {type(exc).__name__}", flush=True)
            continue
        r = probe(tok)
        results[name] = r
        print(f"{name}: 0-100 multi-token {r['n_multi_token_0_100']}/101, "
              f"max single-token scale {r['max_single_token_scale']}, "
              f"'Yes' vs ' Yes' differ: {r['yes_variants_differ']}", flush=True)

    scales = {m: r.get("max_single_token_scale") for m, r in results.items()
              if "error" not in r}
    payload = {
        "question": ("what numeric scale can a single-next-token logprob read "
                     "resolve on each model this project uses?"),
        "measured": "2026-07-28",
        "per_model": results,
        "binding_constraint": (
            "The cross-family instrument scale is the minimum over families. "
            f"Measured max single-token scales: {scales}. Any comparison spanning "
            "the Qwen and OLMo organisms must be read on 0-9."),
        "consumed_by": "docs/reports/lit_value_measurement_2026-07-28.md section 4.1",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
