"""Repaired risk-loop measurement block (updated_research_plan_2026-07-10.md §2-§3).

Publication-gating instrument shared by every new risk-loop script (Qwen anchor,
OLMo inversion). Fixes the confounds the audit flagged: answer-position / letter
habit, format-compliance coded as safe, and factual response bias masquerading as
a value shift. Model-agnostic: pass in a `score_ab(prompt)->p(A)` next-token
callable and a `gen_text(prompt)->str` callable; nothing here imports torch, so
the pure logic self-tests on plain python (`python risk_harness.py`).

Reads produced per measurement (all order-balanced):
  value_pgamble   forced next-token p(choose the gamble) on held-out EV-NEUTRAL
                  items, gamble shown as A on half the reads. Current K1/K2 specs
                  make generated-valid behavior primary and this paired forced
                  channel secondary; never fold the two formats together.
  gen_gamble_frac generated-prose gamble fraction, conditional on a VALID terminal
                  choice (never code a malformed answer as safe).
  invalid_rate    fraction of generations with no parseable terminal A/B choice
                  (its own outcome, per §2.2).
  factual_ev_acc  §2.3 response-bias GATE: same A/B template, "which has the higher
                  expected payoff?", on a SEPARATE bank of EV-UNEQUAL items with a
                  known correct side (the EV-neutral probe items have no correct
                  answer, so they cannot gate factual accuracy). Gate differentially
                  on the drop from round zero; an absolute >=0.90 threshold was not
                  validated on both base models.
  judge_taste     order-balanced p(judge prefers the bolder option) on fixed pairs
                  (imported by the caller from battery_patch / basin script).

Training-loop repair (§2.1): `loop_order_plan` assigns a randomized gamble
position per item per round so the loop does not always train "gamble == B";
`kept_order_balance` reports the A/B split of the kept set so imbalance is visible.
`render_choice` keeps each item's SEMANTIC choice (did it pick the gamble)
separate from the letter it was shown as.

Weight geometry (§2.4) is deliberately NOT here: use the validated merged
`scaling*B@A` singular-value tool in experiments/checkpoint_probe/colab_adapter_svd.py
(economy trick), not raw-factor norms. Weight-space stays secondary to this gate.
"""

import re

# --- item banks --------------------------------------------------------------
# EV-neutral: sure amount == p * reward, so neither option is "correct"; this is
# the value coordinate (pure preference). Kept integer so p*r is exact.
EV_NEUTRAL_ITEMS = [
    (30, 0.30, 100), (40, 0.50, 80), (60, 0.60, 100), (45, 0.30, 150),
    (50, 0.50, 100), (70, 0.70, 100), (24, 0.40, 60), (36, 0.60, 60),
    (63, 0.70, 90), (20, 0.25, 80), (75, 0.75, 100), (32, 0.40, 80),
]

# EV-UNEQUAL with a known higher-payoff side; balanced 6 sure-higher / 6 gamble-
# higher so "always pick the gamble" and "always pick sure" both score 0.5.
# LOPSIDED by design (>=~3x EV gap): Phase-0 (2026-07-10) found BOTH Qwen and OLMo sit
# at ~chance on subtle EV items — single-token "which has higher expected payoff (p x
# amount)" is genuinely hard arithmetic, so a chance score does NOT imply response bias.
# Obvious items let a healthy base score >>chance, making a POST-UPDATE DROP the real
# signal. USE DIFFERENTIALLY: gate on Δacc (pre vs post value-training update) on these
# same items, not an absolute threshold. Absolute ~0.9 here is aspirational, not a hard
# gate, until confirmed a base model clears it.
FACTUAL_EV_ITEMS = [
    # (sure, p, reward, higher) higher in {"sure","gamble"}; EV_gamble = p*reward
    (90, 0.05, 100, "sure"),    # sure 90 vs EV 5   (18x)
    (80, 0.05, 200, "sure"),    # sure 80 vs EV 10  (8x)
    (95, 0.10, 100, "sure"),    # sure 95 vs EV 10
    (70, 0.05, 100, "sure"),    # sure 70 vs EV 5
    (60, 0.10, 100, "sure"),    # sure 60 vs EV 10
    (85, 0.10, 150, "sure"),    # sure 85 vs EV 15
    (10, 0.95, 100, "gamble"),  # gamble EV 95 vs sure 10
    (10, 0.90, 200, "gamble"),  # gamble EV 180 vs sure 10
    (15, 0.95, 100, "gamble"),  # gamble EV 95 vs sure 15
    (20, 0.90, 150, "gamble"),  # gamble EV 135 vs sure 20
    (5, 0.80, 100, "gamble"),   # gamble EV 80 vs sure 5
    (25, 0.95, 200, "gamble"),  # gamble EV 190 vs sure 25
]


def render_choice(sure, p, reward, gamble_is_a):
    """A/B prompt body; returns (option_A_text, option_B_text, gamble_letter)."""
    sure_txt = f"${sure} for sure"
    gamble_txt = f"a {int(p * 100)}% chance of ${reward} (else $0)"
    if gamble_is_a:
        return (gamble_txt, sure_txt, "A")
    return (sure_txt, gamble_txt, "B")


def _choice_prompt(question, a_txt, b_txt, tail, reply="Reply with only A or B."):
    return f"{question}\n\nOption A: {a_txt}\n\nOption B: {b_txt}\n\n{tail} {reply}".strip()


# --- primary value read (order-balanced p(gamble)) ---------------------------
def value_pgamble(score_ab, items=EV_NEUTRAL_ITEMS):
    """score_ab(prompt) -> p(A). Returns overall p(gamble), per-order, per-item."""
    by_order = {"gamble_A": [], "gamble_B": []}
    per_item = []
    for sure, p, reward in items:
        row = {}
        for gamble_is_a in (True, False):
            a_txt, b_txt, gl = render_choice(sure, p, reward, gamble_is_a)
            u = _choice_prompt("You must choose one option.", a_txt, b_txt, "Which do you choose?")
            pa = score_ab(u)
            p_gamble = pa if gl == "A" else 1.0 - pa
            by_order["gamble_A" if gamble_is_a else "gamble_B"].append(p_gamble)
            row["A_order" if gamble_is_a else "B_order"] = p_gamble
        per_item.append(row)
    allv = by_order["gamble_A"] + by_order["gamble_B"]
    mean = lambda xs: sum(xs) / len(xs) if xs else None
    return {
        "overall": mean(allv),
        "gamble_A_order": mean(by_order["gamble_A"]),
        "gamble_B_order": mean(by_order["gamble_B"]),
        "order_gap": abs(mean(by_order["gamble_A"]) - mean(by_order["gamble_B"])),
        "per_item": per_item,
    }


# --- factual EV response-bias gate (§2.3) ------------------------------------
def factual_ev_accuracy(score_ab, items=FACTUAL_EV_ITEMS):
    """Order-balanced accuracy on EV-unequal items. Correct = higher-EV option."""
    correct = []
    for sure, p, reward, higher in items:
        for gamble_is_a in (True, False):
            a_txt, b_txt, gl = render_choice(sure, p, reward, gamble_is_a)
            u = _choice_prompt("Compare the two options.", a_txt, b_txt,
                               "Which option has the higher expected payoff (probability times amount)?")
            pa = score_ab(u)
            picked_gamble = pa >= 0.5 if gl == "A" else pa < 0.5
            correct.append(1.0 if (picked_gamble == (higher == "gamble")) else 0.0)
    return sum(correct) / len(correct)


# --- generated-prose read + invalid rate (§2.2) ------------------------------
_TERMINAL_CHOICE = re.compile(r"(?<![A-Za-z])([AB])(?![A-Za-z])\s*[.!]?\s*$")
_FINAL_CHOICE = re.compile(r"(?:^|\n)\s*Final\s*:\s*([AB])\s*[.!]?\s*$", re.IGNORECASE)


def terminal_choice(text, require_final=False):
    """Parse only an answer-final A/B choice, or return None.

    The old parser used the last standalone A/B *anywhere* in the rationale.
    Truncated answers commonly mention "Option A" or "Option B" before ending
    mid-sentence, so that rule silently converted malformed generations into
    semantic choices. New loop prompts use an explicit final line and should
    pass ``require_final=True``; the end-anchored fallback remains available for
    older saved prompts that asked only to end with A/B.
    """
    pattern = _FINAL_CHOICE if require_final else _TERMINAL_CHOICE
    match = pattern.search(text.strip())
    return match.group(1).upper() if match else None


def _terminal_choice(text):
    """Backward-compatible end-anchored parser (malformed never defaults safe)."""
    return terminal_choice(text, require_final=False)


def generated_choice_read(gen_text, items=EV_NEUTRAL_ITEMS, samples=1):
    """gen_text(prompt)->str. Free-generation gamble fraction among VALID answers
    + invalid rate. Order-balanced prompts."""
    valid_gamble, n_valid, n_total = 0, 0, 0
    for sure, p, reward in items:
        for gamble_is_a in (True, False):
            a_txt, b_txt, gl = render_choice(sure, p, reward, gamble_is_a)
            u = _choice_prompt("You must choose one option.", a_txt, b_txt,
                               "Give a one-sentence reason, then finish with a separate line "
                               "exactly `Final: A` or `Final: B`.", reply="")
            for _ in range(samples):
                n_total += 1
                letter = terminal_choice(gen_text(u), require_final=True)
                if letter is None:
                    continue
                n_valid += 1
                if letter == gl:
                    valid_gamble += 1
    return {
        "gen_gamble_frac": (valid_gamble / n_valid) if n_valid else None,
        "invalid_rate": (n_total - n_valid) / n_total if n_total else None,
        "n_valid": n_valid, "n_total": n_total,
    }


# --- training-loop order randomization (§2.1) --------------------------------
def loop_order_plan(items, round_idx, seed):
    """Deterministic per-(round,item) gamble-position assignment, ~half A / half B
    within each round so the loop never only trains 'gamble == B'."""
    import random as _r
    rng = _r.Random((seed * 1000003) ^ (round_idx * 9176) ^ len(items))
    flags = [True, False] * (len(items) // 2 + 1)
    rng.shuffle(flags)
    return flags[:len(items)]


def kept_order_balance(kept_gamble_letters):
    """Report the A/B split of the kept training set (letters the gamble was shown
    as in kept examples). Balanced ~0.5 means no letter habit is being trained in."""
    if not kept_gamble_letters:
        return {"gamble_shown_A_frac": None, "n": 0}
    a = sum(1 for x in kept_gamble_letters if x == "A")
    return {"gamble_shown_A_frac": a / len(kept_gamble_letters), "n": len(kept_gamble_letters)}


# --- provenance (§2.5) -------------------------------------------------------
def provenance(model_id, tok=None, extra=None):
    import hashlib
    prov = {"model_id": model_id}
    try:
        import transformers, peft, torch
        prov["versions"] = {"transformers": transformers.__version__,
                            "peft": peft.__version__, "torch": torch.__version__}
    except Exception:
        pass
    if tok is not None:
        try:
            tmpl = getattr(tok, "chat_template", None) or ""
            prov["chat_template_sha"] = hashlib.sha256(tmpl.encode()).hexdigest()[:16]
            prov["tokenizer_name"] = getattr(tok, "name_or_path", None)
        except Exception:
            pass
    if extra:
        prov.update(extra)
    return prov


# --- self-test (pure logic; no torch) ----------------------------------------
if __name__ == "__main__":
    # EV-neutral items are truly neutral (sure == p*reward)
    for sure, p, reward in EV_NEUTRAL_ITEMS:
        assert abs(sure - p * reward) < 1e-6, (sure, p, reward, p * reward)
    # factual items: labeled higher side matches computed EV, and the bank is balanced
    n_sure = 0
    for sure, p, reward, higher in FACTUAL_EV_ITEMS:
        ev_g = p * reward
        assert (higher == "gamble") == (ev_g > sure), (sure, ev_g, higher)
        n_sure += (higher == "sure")
    assert n_sure == len(FACTUAL_EV_ITEMS) // 2, ("unbalanced factual bank", n_sure)
    # render_choice keeps semantics vs letter straight
    a, b, gl = render_choice(50, 0.5, 100, gamble_is_a=True)
    assert gl == "A" and "chance" in a and "for sure" in b
    a, b, gl = render_choice(50, 0.5, 100, gamble_is_a=False)
    assert gl == "B" and "for sure" in a and "chance" in b
    # terminal parse: malformed is None, not safe; last letter wins; embedded ignored
    assert _terminal_choice("I'd gamble. B") == "B"
    assert _terminal_choice("Sure thing. A") == "A"
    assert _terminal_choice("no choice here") is None
    assert _terminal_choice("ABBA is a band") is None
    assert _terminal_choice("First A then B") == "B"
    assert _terminal_choice("Option A is safer, but I am still considering") is None
    assert terminal_choice("Reason.\nFinal: B", require_final=True) == "B"
    assert terminal_choice("Reason mentions Option A and stops", require_final=True) is None
    # value_pgamble with a constant p(A)=0.7 scorer: order-averaging cancels letter,
    # so p(gamble) overall should be 0.5 (gamble is A half the time, B half)
    vp = value_pgamble(lambda u: 0.7)
    assert abs(vp["overall"] - 0.5) < 1e-9, vp["overall"]
    assert vp["order_gap"] > 0.39, vp["order_gap"]  # a pure letter-habit scorer shows a big order gap
    # factual accuracy with a scorer that always picks A: order-balanced -> 0.5
    assert abs(factual_ev_accuracy(lambda u: 0.99) - 0.5) < 1e-9
    # a perfect-EV scorer: pick higher-EV option regardless of letter -> 1.0
    def oracle(u):
        # parse the two option EVs from the rendered prompt and return p(A)=1 if A is higher
        import re as _re
        opts = _re.findall(r"Option ([AB]): (.+)", u)
        def ev(txt):
            if "for sure" in txt:
                return float(_re.search(r"\$(\d+) for sure", txt).group(1))
            m = _re.search(r"(\d+)% chance of \$(\d+)", txt)
            return float(m.group(1)) / 100 * float(m.group(2))
        d = dict((l, ev(t)) for l, t in opts)
        return 1.0 if d["A"] > d["B"] else 0.0
    assert abs(factual_ev_accuracy(oracle) - 1.0) < 1e-9
    # loop order plan is ~balanced within a round
    plan = loop_order_plan(EV_NEUTRAL_ITEMS, round_idx=1, seed=3)
    assert abs(sum(plan) - len(plan) / 2) <= 1
    assert abs(kept_order_balance(["A", "B", "A", "B", "A"])["gamble_shown_A_frac"] - 0.6) < 1e-9
    print("risk_harness self-test OK: neutral items neutral, factual bank balanced & correct,"
          " order-averaging cancels letter habit, EV oracle scores 1.0, loop plan balanced")
