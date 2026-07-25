"""Run the whole phase-1 pipeline locally with stubbed models, on CPU, in seconds.

WHY THIS EXISTS. On 2026-07-25 a run completed 90 minutes of GPU scoring -- both pool
sets, all 30 prompts, every axis -- and then died on the last line before writing
output:

    TypeError: instrument_check() missing 1 required positional argument: 'label'

An editing pass had left two definitions of that function in the file, and the stale
one shadowed the new one. `ast.parse` passes cleanly on that; only executing the call
graph catches it. Every result from that run was lost.

WHAT THIS CHECKS. It monkeypatches model loading, generation and the judge with
deterministic stubs, then runs `main()` end to end and asserts the output file is
written and has the expected shape. It exercises: function signatures, array shapes,
the covariance and cross-pool math, length residualisation, the instrument gate, and
JSON serialisability. It does NOT check that the real models behave -- that is what
judge_manipulation_check.py is for.

Run before every push:  uv run --with numpy python experiments/value_covariance/smoke_test.py
"""

import importlib.util
import json
import os
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def load_module():
    spec = importlib.util.spec_from_file_location("vc_script", os.path.join(HERE, "script.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class FakeTok:
    pad_token = "<pad>"
    pad_token_id = 0
    padding_side = "right"

    def apply_chat_template(self, msgs, tokenize=False, add_generation_prompt=True,
                            enable_thinking=None):
        # Mimic a template that leaves the thinking block OPEN, so the script's
        # judge_prompt has to close it -- the bug that cost three runs.
        return "<|user|>" + msgs[0]["content"] + "<|assistant|><think>"

    def encode(self, t, add_special_tokens=False):
        return [abs(hash(t)) % 1000]

    def __call__(self, texts, **kw):
        n = len(texts) if isinstance(texts, list) else 1
        return {"input_ids": np.zeros((n, 4), dtype=int)}


def main():
    m = load_module()

    # The pool is generated with a KNOWN structure so the covariance math can be
    # checked: axis 0 and axis 1 are correlated by construction.
    rng = np.random.default_rng(0)

    def fake_load(model_id):
        return FakeTok(), object()

    def fake_generate_pool(tok, model, prompts, n_cand, temp, max_new, seed):
        return [{"prompt": p, "candidates": [f"answer {i} to prompt {pi}" + "x" * (50 + 3 * i)
                                             for i in range(n_cand)]}
                for pi, p in enumerate(prompts)]

    def fake_score_pool(tok, model, pool, label, n_opp=3, batch=8, seed=0):
        n_p, n_c, n_a = len(pool), len(pool[0]["candidates"]), len(m.AXIS_NAMES)
        base = rng.normal(0, 0.2, size=(n_p, n_c))
        s = np.zeros((n_p, n_c, n_a))
        for k in range(n_a):
            # axes 0 and 1 share `base`, the rest are independent
            s[:, :, k] = 0.5 + (base if k < 2 else rng.normal(0, 0.2, size=(n_p, n_c)))
        return np.clip(s, 0, 1), 0.01

    m.load = fake_load
    m.generate_pool = fake_generate_pool
    m.score_pool = fake_score_pool
    m.PROMPTS = m.PROMPTS[:4]
    m.N_CAND = 6

    out = os.path.join(tempfile.mkdtemp(), "out.json")
    m.OUT = out

    class FakeTorch:
        class cuda:
            @staticmethod
            def empty_cache():
                pass
    sys.modules["torch"] = FakeTorch

    m.main()

    d = json.load(open(out))
    assert "instrument_check" in d, "instrument gate did not run"
    assert "cross_pool" in d and d["cross_pool"], "cross-pool test missing"
    assert "covariance" in d and d["covariance"], "covariance missing"
    for label, chk in d["instrument_check"].items():
        assert "verdict" in chk and "mean_order_gap" in chk, chk
    summ = list(d["cross_pool"].values())[0]["summary"]
    assert summ["n_pairs"] == len(m.AXIS_NAMES) * (len(m.AXIS_NAMES) - 1), summ

    # The planted correlation between axes 0 and 1 must show up.
    corr = list(d["covariance"].values())[0]["correlation_raw"]
    assert corr[0][1] > 0.5, f"planted correlation not recovered: {corr[0][1]}"

    # judge_prompt must close a thinking block the template left open.
    rendered = m.judge_prompt(FakeTok(), "hello")
    assert "</think>" in rendered, "judge_prompt left the thinking block open"

    print("SMOKE TEST PASSED")
    print(f"  instrument verdicts: "
          f"{[c['verdict'] for c in d['instrument_check'].values()]}")
    print(f"  cross-pool pairs: {summ['n_pairs']}, planted corr recovered: {corr[0][1]}")


if __name__ == "__main__":
    main()
