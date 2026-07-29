"""Run the whole phase-1b pipeline locally with stubbed models, on CPU, in seconds.

Same rationale as smoke_test.py: on 2026-07-25 a run completed 90 minutes of GPU
scoring and died on a stale duplicate function definition before writing output.
Only executing the call graph catches that class of bug.

WHAT THIS CHECKS. Monkeypatches loading, generation and the graded read with
deterministic stubs, runs `main()` end to end, and asserts: the output file is
written; all four gates run and appear; a PLANTED correlation between axes 0 and 1
is recovered in the covariance; the planted persona separation passes gate 3; the
cross-method primary test is present with the right pair count; and judge_prompt
closes a thinking block the template left open. It does NOT check real model
behaviour -- gates 1-2 do that on-GPU at run time.

Run before every push:
  uv run --with numpy python experiments/value_covariance/smoke_test_phase1b.py
"""

import importlib.util
import json
import os
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def load_module():
    spec = importlib.util.spec_from_file_location(
        "vc_script1b", os.path.join(HERE, "script_phase1b.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class FakeTok:
    pad_token = "<pad>"
    pad_token_id = 0
    padding_side = "right"

    def apply_chat_template(self, msgs, tokenize=False, add_generation_prompt=True,
                            enable_thinking=None):
        # Leaves the thinking block OPEN so judge_prompt has to close it.
        return "<|user|>" + msgs[-1]["content"] + "<|assistant|><think>"

    def encode(self, t, add_special_tokens=False):
        return [abs(hash(t)) % 1000]

    def __call__(self, texts, **kw):
        n = len(texts) if isinstance(texts, list) else 1
        return {"input_ids": np.zeros((n, 4), dtype=int)}


def main():
    m = load_module()
    rng = np.random.default_rng(0)

    # Planted structure, keyed on candidate TEXT so both judges see the same latent:
    #   "risky N" -> high risk_tolerance, low caution (axes 0 and 3 anticorrelated),
    #   axes 0 and 1 positively correlated via a shared latent per candidate.
    latent = {}

    def latent_for(text):
        if text not in latent:
            latent[text] = rng.normal(0, 0.2)
        return latent[text]

    def fake_load(model_id):
        return FakeTok(), object()

    def fake_generate_pool(tok, model, prompts, n_cand, temp, max_new, seed,
                           system=None):
        tag = "high" if system == m.PERSONA_HIGH else (
            "low" if system == m.PERSONA_LOW else "plain")
        return [{"prompt": p,
                 "candidates": [f"{tag} answer {i} to prompt {pi} seed {seed}" + "x" * (40 + 3 * i)
                                for i in range(n_cand)]}
                for pi, p in enumerate(prompts)]

    def fake_score_pool_graded(tok, model, pool, label, batch=8):
        n_p, n_c, n_a = len(pool), len(pool[0]["candidates"]), len(m.AXIS_NAMES)
        s = np.zeros((n_p, n_c, n_a))
        for pi, it in enumerate(pool):
            for ci, c in enumerate(it["candidates"]):
                v = latent_for(c)
                shift = 0.25 if c.startswith("high") else (-0.25 if c.startswith("low") else 0.0)
                s[pi, ci, 0] = 0.5 + v + shift                  # risk
                s[pi, ci, 1] = 0.5 + v + rng.normal(0, 0.05)    # correlated axis
                s[pi, ci, 3] = 0.5 - v - shift                  # caution, opposite
                for k in (2, 4, 5):
                    s[pi, ci, k] = 0.5 + rng.normal(0, 0.2)
        diag = {"mean_digit_mass": 0.93, "min_digit_mass": 0.8,
                "polarity_asymmetry_per_axis": {a: 0.02 for a in m.AXIS_NAMES},
                "polarity_means_per_axis": {a: {"pos": 0.5, "neg": 0.5} for a in m.AXIS_NAMES}}
        return np.clip(s, 0, 1), diag

    def fake_gate_manipulation(tok, model, batch):
        return {"pairs": [], "fraction_ordered_correctly": 1.0, "mean_margin": 0.4,
                "pass_criterion": "stub", "passed": True,
                "per_axis_margin": {a: 0.4 for a in m.AXIS_NAMES}}

    def fake_top_tokens(tok, model, msg, k=6):
        return [("'7'", 0.5), ("'8'", 0.3)]

    m.load = fake_load
    m.generate_pool = fake_generate_pool
    m.score_pool_graded = fake_score_pool_graded
    m.gate_manipulation = fake_gate_manipulation
    m.top_tokens = fake_top_tokens
    m.PROMPTS = m.PROMPTS[:5]
    m.N_CAND = 6
    m.N_PERSONA_PROMPTS = 3

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
    n_a = len(m.AXIS_NAMES)

    for label in ("judge_a", "judge_b"):
        jr = d["judges"][label]
        for g in ("gate1_digit_mass", "gate2_manipulation", "gate3_persona"):
            assert g in jr, f"{label} missing {g}"
        assert jr["gate3_persona"]["passed"], \
            f"planted persona separation not detected: {jr['gate3_persona']}"
        assert "spread_unprompted_A" in jr and "spread_unprompted_B" in jr
    assert "gate4_agreement" in d, "gate 4 missing"
    assert d["gate4_agreement"]["passed"], \
        f"planted cross-judge agreement not detected: {d['gate4_agreement']}"

    assert "verdict" in d and d["verdict"].startswith("O1"), d.get("verdict")

    corr = d["covariance"]["judge_a_A"]["correlation_raw"]
    assert corr[0][1] > 0.5, f"planted axis0-axis1 correlation not recovered: {corr[0][1]}"
    assert corr[0][3] < -0.5, f"planted risk-caution anticorrelation not recovered: {corr[0][3]}"

    assert "cross_pool_cross_method" in d, "cross-method primary test missing"
    summ = d["cross_pool_cross_method"]["summary"]
    assert summ["n_pairs"] == n_a * (n_a - 1), summ
    assert summ["n_selection_events"] == n_a, summ
    # planted structure is shared across judges, so the primary should predict well
    assert summ["correlation"] is not None and summ["correlation"] > 0.5, summ

    rendered = m.judge_prompt(FakeTok(), "hello")
    assert "</think>" in rendered, "judge_prompt left the thinking block open"

    ids = m.digit_ids(FakeTok())
    assert len(ids) == 10 and all(len(x) >= 1 for x in ids)

    print("SMOKE TEST PASSED")
    print(f"  verdict: {d['verdict']}")
    print(f"  planted corr recovered: axis01 {corr[0][1]}, risk-caution {corr[0][3]}")
    print(f"  cross-method primary: {summ}")


if __name__ == "__main__":
    main()
