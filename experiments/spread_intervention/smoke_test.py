"""Run the WHOLE spread-intervention pipeline on CPU, in seconds, with stubbed models.

WHY THIS EXISTS. On 2026-07-25 a run completed 90 minutes of GPU work and then died
on a signature mismatch:

    TypeError: instrument_check() missing 1 required positional argument: 'label'

`ast.parse` passes cleanly on that. Only executing the call graph catches it. Six GPU
runs were lost that day to instrument bugs, so this test does three things a plain
import check cannot:

1. SIGNATURE PARITY. Every stub's signature is compared against the real function's
   with inspect.signature before patching. If script.py's plumbing signature drifts
   from what main() calls, this fails here instead of after four GPU hours.
2. FULL CALL-GRAPH COVERAGE. sys.settrace records every function in script.py that
   actually executed, and the test asserts that nothing outside the known
   GPU-only helper list went uncalled.
3. THE MANIPULATION ITSELF. With stubbed generation the arms' pool means must be
   identical every round to 1e-9, and the SPREAD arm's within-prompt spread must
   exceed the CONCENTRATED arm's by at least 2x -- the same gate the real run
   applies after round 1.

It also runs main() TWICE against the same output file, so the resume path (skip
completed groups, reload from checkpoints) is exercised rather than assumed.

Run before every push:  uv run python experiments/spread_intervention/smoke_test.py
"""

import importlib.util
import inspect
import json
import os
import random
import sys
import tempfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "script.py")

# Functions that only run against a real GPU/model and are therefore either
# monkeypatched below or reachable only from a monkeypatched function.
GPU_ONLY = {
    "_load_base", "_messages", "_render", "_encode_train", "_train_args", "_fit",
    "_generation_mode",
}


def stable_hash(s):
    """Python's hash() is salted per process; this test must be reproducible."""
    return zlib.crc32(s.encode()) & 0xFFFF


def load_module():
    spec = importlib.util.spec_from_file_location("spread_script", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class FakeTok:
    """A tokenizer whose chat template leaves the <think> block OPEN.

    That is the template behaviour that cost three runs: judge_render must close it.
    """
    pad_token = "<pad>"
    pad_token_id = 0
    padding_side = "right"

    def apply_chat_template(self, msgs, tokenize=False, add_generation_prompt=True,
                            enable_thinking=None):
        return "<|user|>" + msgs[-1]["content"] + "<|assistant|><think>"


# ---------------------------------------------------------------------------
# Stubs. Signatures MUST match script.py's real ones (checked below).
# ---------------------------------------------------------------------------

def make_stubs(m):
    def setup():
        return {"tok": FakeTok(), "model": None, "state": {}, "saved": {}, "calls": []}

    def ensure_start_adapter(ctx):
        d = os.path.join(m.START_ADAPTER_DIR)
        os.makedirs(d, exist_ok=True)
        ctx["saved"][d] = 0.5      # the organism starts mid-scale
        return d

    def attach(ctx, start_adapter):
        ctx["model"] = "fake-peft-model"
        ctx["attached_from"] = start_adapter
        return ctx

    def new_arm(ctx, name, init_dir):
        assert ctx["model"] is not None, "new_arm called before attach"
        ctx["state"][name] = ctx["saved"].get(init_dir, 0.5)
        ctx["calls"].append(("new_arm", name, init_dir))

    def drop_arm(ctx, name):
        ctx["state"].pop(name, None)

    def save_arm(ctx, name, path):
        os.makedirs(path, exist_ok=True)
        ctx["saved"][path] = ctx["state"][name]
        return path

    def generate_candidates(ctx, name, prompt, n_cand, seed):
        """Candidates whose risk rate tracks the arm's current value, with a
        per-prompt offset so there is genuine BETWEEN-prompt variation for the
        CONCENTRATED arm to push the variation into."""
        v = ctx["state"][name]
        rng = random.Random((seed * 7919) ^ stable_hash(prompt))
        offset = rng.uniform(-0.25, 0.25)
        rate = min(0.85, max(0.15, v + offset))
        out = []
        for i in range(n_cand):
            letter = "B" if rng.random() < rate else "A"
            out.append(f"Weighing the certain payout against the expected value here, "
                       f"candidate {i} settles on {letter}")
        return out

    def judge_scores(ctx, name, prompt, cands):
        """A judge that mildly prefers the gamble, so the gap is non-zero where
        within-prompt spread exists and exactly zero where it does not."""
        rng = random.Random(stable_hash(name + prompt))
        return [0.40 + 0.35 * m.p_risk(c) + rng.uniform(-0.02, 0.02) for c in cands]

    def train_on(ctx, name, rows):
        kept = [m.p_risk(a) for _, a in rows]
        target = sum(kept) / len(kept)
        ctx["state"][name] += 0.7 * (target - ctx["state"][name])

    def measure_value(ctx, name, seed):
        rng = random.Random(seed)
        return min(1.0, max(0.0, ctx["state"][name] + rng.uniform(-0.01, 0.01)))

    def teardown(ctx):
        ctx["model"] = None

    return {
        "setup": setup, "ensure_start_adapter": ensure_start_adapter, "attach": attach,
        "new_arm": new_arm, "drop_arm": drop_arm, "save_arm": save_arm,
        "generate_candidates": generate_candidates, "judge_scores": judge_scores,
        "train_on": train_on, "measure_value": measure_value, "teardown": teardown,
    }


def main():
    m = load_module()

    tmp = tempfile.mkdtemp()
    m.OUT = os.path.join(tmp, "spread_intervention.json")
    m.CKPT_DIR = os.path.join(tmp, "ckpt")
    m.START_ADAPTER_DIR = os.path.join(tmp, "start")
    m.OUT_DIR = tmp
    m.SEEDS = [0, 1]
    m.CONTROL_SEED = 7
    m.ROUNDS = 2

    stubs = make_stubs(m)

    # ---- 1. signature parity ------------------------------------------------
    for name, stub in stubs.items():
        real = getattr(m, name)
        rs, ss = inspect.signature(real), inspect.signature(stub)
        assert rs == ss, f"signature drift for {name}: script.py has {rs}, stub has {ss}"
        setattr(m, name, stub)

    # ---- 2. coverage tracing ------------------------------------------------
    executed = set()

    def tracer(frame, event, arg):
        if event == "call" and frame.f_code.co_filename == SCRIPT:
            executed.add(frame.f_code.co_name)
        return None

    sys.settrace(tracer)
    try:
        m.main()
        first_pass = json.load(open(m.OUT))
        m.main()          # resume path: every group is complete, nothing should re-run
    finally:
        sys.settrace(None)

    d = json.load(open(m.OUT))

    # ---- 3. output shape ----------------------------------------------------
    for key in ("config", "groups", "round1_gate", "summary", "elapsed_seconds"):
        assert key in d, f"missing top-level key {key}"
    assert d["round1_gate"]["passed"], d["round1_gate"]
    expected_groups = {"judge_seed0", "judge_seed1", "control_seed7"}
    assert set(d["groups"]) == expected_groups, set(d["groups"])
    for gname, g in d["groups"].items():
        assert g["rounds_done"] == m.ROUNDS, (gname, g["rounds_done"])
        assert g["aborted"] is None, (gname, g["aborted"])
        assert len(g["joint"]) == m.ROUNDS, (gname, len(g["joint"]))
        for arm in m.ARMS:
            a = g["arms"][arm]
            assert len(a["value_traj"]) == m.ROUNDS + 1, (gname, arm, a["value_traj"])
            assert len(a["rounds"]) == m.ROUNDS, (gname, arm, len(a["rounds"]))
            for r in a["rounds"]:
                for k in ("pool_mean", "spread", "kept_mean", "gap",
                          "kept_mean_length_chars", "value_after_round",
                          "between_prompt_variance", "candidate_health"):
                    assert k in r, (gname, arm, k)
        assert g["arms"]["concentrated"]["value_traj"][0] == g["arms"]["spread"]["value_traj"][0], \
            "arms must start from the same measured value"

    # ---- 4. the manipulation ------------------------------------------------
    ratios, diffs = [], []
    for gname, g in d["groups"].items():
        for j in g["joint"]:
            diffs.append(j["pool_mean_abs_diff"])
            ratios.append(j["spread_ratio"])
            assert j["pool_mean_abs_diff"] < 1e-9, (
                f"{gname} round {j['round']}: pool means differ by "
                f"{j['pool_mean_abs_diff']:.3e}, must be identical")
            assert abs(j["pool_mean_concentrated"] - j["target_pool_mean"]) < 1e-9, j
            assert j["spread_ratio"] >= 2.0, (
                f"{gname} round {j['round']}: within-prompt spread ratio "
                f"{j['spread_ratio']:.3f} < 2")
    assert diffs and ratios

    # Round 1 must be built from ONE shared candidate pool in both arms.
    for gname, g in d["groups"].items():
        raw = g["rounds_raw"][0]
        assert raw["concentrated"]["candidates"] == raw["spread"]["candidates"], \
            f"{gname}: round-1 candidates must be shared across arms"
        assert g["joint"][0]["shared_round1_candidates"] is True

    # The no-selection control must not use the judge; the judge groups must.
    assert d["groups"]["control_seed7"]["rounds_raw"][0]["spread"]["judge_scores"] is None
    assert d["groups"]["judge_seed0"]["rounds_raw"][0]["spread"]["judge_scores"] is not None

    # ---- 5. resume did not redo work ---------------------------------------
    for gname in expected_groups:
        assert (d["groups"][gname]["arms"]["spread"]["value_traj"]
                == first_pass["groups"][gname]["arms"]["spread"]["value_traj"]), \
            f"{gname}: second main() re-ran a completed group"

    # ---- 5b. a failed gate must survive a restart --------------------------
    poisoned = json.load(open(m.OUT))
    poisoned["round1_gate"] = {"passed": False, "problems": ["FAILED_MANIPULATION_GATE: synthetic"],
                               "spread_ratio": 1.0}
    poisoned["groups"]["judge_seed0"]["rounds_done"] = 0
    with open(m.OUT, "w") as f:
        json.dump(poisoned, f)
    sys.settrace(tracer)
    try:
        m.main()
    finally:
        sys.settrace(None)
    after = json.load(open(m.OUT))
    assert after["groups"]["judge_seed0"]["rounds_done"] == 0, \
        "a restart walked past a gate an earlier attempt had failed"
    with open(m.OUT, "w") as f:
        json.dump(d, f)

    # ---- 6. instrument helpers, called directly (still traced) -------------
    sys.settrace(tracer)
    try:
        check_instrument_helpers(m)
    finally:
        sys.settrace(None)

    # ---- 7. call-graph coverage --------------------------------------------
    defined = {n for n, f in vars(m).items()
               if inspect.isfunction(f) and f.__module__ == m.__name__}
    uncalled = defined - executed - GPU_ONLY - set(stubs)
    assert not uncalled, f"never executed by the smoke test: {sorted(uncalled)}"

    print("SMOKE TEST PASSED")
    print(f"  groups: {sorted(d['groups'])}  rounds each: {m.ROUNDS}")
    print(f"  pool-mean max |diff| between arms: {max(diffs):.3e} (must be < 1e-9)")
    print(f"  within-prompt spread ratio SPREAD/CONCENTRATED: "
          f"min {min(ratios):.2f}, mean {sum(ratios) / len(ratios):.2f} (gate: >= 2)")
    print(f"  round-1 gate: passed={d['round1_gate']['passed']} "
          f"ratio={d['round1_gate']['spread_ratio']} "
          f"bad_candidates={d['round1_gate']['candidate_bad_fraction']}")
    for k, v in d["summary"]["by_arm"].items():
        print(f"  {k:26} start {v['mean_start']:.3f} -> end {v['mean_end']:.3f} "
              f"(movement {v['mean_movement']:+.3f}, n={v['n_runs']})")
    print(f"  functions covered: {len(defined - GPU_ONLY - set(stubs))} pure, "
          f"{len(stubs)} stubbed, {len(GPU_ONLY)} GPU-only")


def check_instrument_helpers(m):
    """The reads that six lost GPU runs were traced back to, checked in isolation."""
    assert m.strip_thinking("<think>reasoning that never closed") == ""
    assert m.strip_thinking("<think>abc</think> so I pick B") == "so I pick B"
    assert m.p_risk("I'd rather gamble. B") == 1.0
    assert m.p_risk("Certainty wins. A") == 0.0
    assert m.p_risk("no letter here at all") == 0.0
    rendered = m.judge_render(FakeTok(), [{"role": "user", "content": "hello"}])
    assert "</think>" in rendered, "judge_render left the thinking block open"

    class NoThinkTok(FakeTok):
        def apply_chat_template(self, msgs, tokenize=False, add_generation_prompt=True,
                                enable_thinking=None):
            return "<|user|>" + msgs[-1]["content"] + "<|assistant|>"

    plain = m.judge_render(NoThinkTok(), [{"role": "user", "content": "hello"}])
    assert "think" not in plain, \
        "judge_render injected a thinking block into a non-thinking template"
    health = m.candidate_health([["", "short", "a long enough answer with no letters here"]])
    assert health["n_too_short"] == 2 and health["n_no_ab_letter"] == 1
    rows = m._persona_rows(0.5, 20, seed=0)
    assert len(rows) == 20 and all(a in ("A", "B") for _, a in rows)
    bad_gate = m.round1_gate(0.30, 0.33, 0.0)
    assert not bad_gate["passed"] and "FAILED_MANIPULATION_GATE" in bad_gate["problems"][0]
    sick_gate = m.round1_gate(0.0, 0.5, 0.9)
    assert not sick_gate["passed"] and "FAILED_CANDIDATE_HEALTH_GATE" in sick_gate["problems"][0]


if __name__ == "__main__":
    main()
