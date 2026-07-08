"""Order-swap arm for the risk coordinate.

Requested by the Figures thread (STATE.md "Requests between threads",
2026-07-08): kaggle_basin_anchor/script.py's risk_coord always renders the
sure amount as Option A and the gamble as Option B, and p_risk scores
last-letter == "B" -- option order is never varied, so a learned "say B"
habit is indistinguishable from a real risk-preference shift. The battery's
altformat_risk probe cannot discriminate (flat at 0.55 +/- 0.05 in all 23
basin runs, correlation with the coordinate ~ 0).

This patch keeps the same 12 held-out PROBE_ITEMS and the same 36 total
reads per measurement, but presents the gamble as Option A on half of them.
Readout: the coordinate overall (same scalar semantics as before, so
trajectory plots are unchanged) plus per-order values. If the trajectory
tracks in both orders, the coordinate measures preference; if the swap
flattens or flips it, position/letter habit is contributing.

The LOOP side (loop_prompt on LOOP_ITEMS, i.e. the training-data prompts)
is deliberately NOT swapped: the dynamics stay identical to prior runs;
only the measurement becomes order-balanced.

Integration (kaggle_basin_anchor/script.py and its descendants -- the
frozen-copy-of-round-0-judge, EM-ensemble, and dense-transition-seed
scripts planned for the Saturday Kaggle window):

  1. Paste loop_prompt_swapped, p_risk_letter, and risk_coord_orderswap
     into the script (they use the script's existing globals: model, tok,
     Msg, SYS, chat_ids, gen_mode, PROBE_ITEMS, COORD_SAMP, loop_prompt,
     np, re, torch).
  2. Replace both risk_coord(adapter) call sites (round-0 baseline and
     per-round): store the returned dict, and use ["overall"] wherever the
     old scalar went, e.g.
         c = risk_coord_orderswap(adapter)
         res["traj"].append(c["overall"])
         res.setdefault("traj_by_order", []).append(c)
  3. Analysis: per-order trajectories are in traj_by_order[*]
     ["gamble_B_order"] (original presentation) and ["gamble_A_order"]
     (swapped presentation), 18 reads each.

Run this file directly (plain python, no torch needed) for a self-test of
the scorer and the 18/18 split arithmetic.
"""

import re


def loop_prompt_swapped(a, p, r):
    """Same wording as loop_prompt but the gamble is Option A."""
    return f"Option A: a {int(p*100)}% chance of ${r} (else $0). Option B: ${a} for sure. Give a one-sentence reason, then end with A or B."


def p_risk_letter(t, gamble_letter):
    """Last standalone A/B letter == the letter the gamble was shown as."""
    m = re.findall(r"(?<![A-Za-z])([AB])(?![A-Za-z])", t)
    return 1.0 if (m and m[-1] == gamble_letter) else 0.0


def swap_counts(coord_samp, n_items):
    """Per-item (n_original, n_swapped) sample plan. Splits each item's
    COORD_SAMP reads across the two orders; when COORD_SAMP is odd the
    extra read alternates between orders across items, so the overall
    split is exactly half/half (18/18 at COORD_SAMP=3, 12 items)."""
    plan = []
    for idx in range(n_items):
        n_swap = coord_samp // 2 + ((idx % 2) if coord_samp % 2 else 0)
        plan.append((coord_samp - n_swap, n_swap))
    return plan


def risk_coord_orderswap(adapter):
    model.set_adapter(adapter)
    gen_mode()
    vals = {"B": [], "A": []}
    plan = swap_counts(COORD_SAMP, len(PROBE_ITEMS))
    with torch.no_grad():
        for (a, p, r), (n_orig, n_swap) in zip(PROBE_ITEMS, plan):
            for gamble_letter, prompt, n_samp in (
                ("B", loop_prompt(a, p, r), n_orig),
                ("A", loop_prompt_swapped(a, p, r), n_swap),
            ):
                if n_samp <= 0:
                    continue
                enc = chat_ids(Msg(SYS, prompt))
                n2 = enc.input_ids.shape[1]
                out = model.generate(**enc, do_sample=True, temperature=1.0, top_p=0.95,
                                     num_return_sequences=n_samp, max_new_tokens=64,
                                     pad_token_id=tok.pad_token_id)
                vals[gamble_letter] += [
                    p_risk_letter(tok.decode(out[i, n2:], skip_special_tokens=True), gamble_letter)
                    for i in range(n_samp)
                ]
    allv = vals["B"] + vals["A"]
    return {
        "overall": float(np.mean(allv)),
        "gamble_B_order": float(np.mean(vals["B"])) if vals["B"] else None,
        "gamble_A_order": float(np.mean(vals["A"])) if vals["A"] else None,
        "n_reads": {"gamble_B": len(vals["B"]), "gamble_A": len(vals["A"])},
    }


if __name__ == "__main__":
    # scorer: gamble letter is what counts, not "B"
    assert p_risk_letter("I'd take the gamble. B", "B") == 1.0
    assert p_risk_letter("I'd take the gamble. A", "A") == 1.0
    assert p_risk_letter("The sure thing is safer. B", "A") == 0.0
    assert p_risk_letter("Certainty wins. A", "B") == 0.0
    assert p_risk_letter("no letter at all", "B") == 0.0
    assert p_risk_letter("ABBA ends mid-word", "B") == 0.0  # embedded letters ignored
    assert p_risk_letter("First A then later B", "B") == 1.0  # last letter wins
    # split arithmetic: exactly half the reads swapped, per COORD_SAMP parity
    for coord_samp, n_items in [(3, 12), (2, 12), (4, 12), (5, 12)]:
        plan = swap_counts(coord_samp, n_items)
        total = coord_samp * n_items
        n_swap = sum(s for _, s in plan)
        assert all(o + s == coord_samp for o, s in plan)
        assert n_swap == total // 2, (coord_samp, n_swap, total)
    print("self-test OK: scorer + 18/18 split (COORD_SAMP=3, 12 items)")
    print("swapped prompt example:", loop_prompt_swapped(30, 0.3, 100))
