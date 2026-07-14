"""Identity / artificial-self battery across the Qwen EM dose ladder — the
recovered checkpoint_probe_battery.json (docs/ANALYSIS_LEDGER.md §D: local
hand-copy had dropped a block; re-pulled from Drive 07-14, fileId
1ImZ4mminsB8jhwZVp5UOMVdMPeXgN2B4, modified 2026-07-09T16:24Z, sha256 prefix
3fe5cb94ee10fcd8, JSON-validated + spot-checked).

Prints the per-dose table for the identity coordinates (post_update_still_you,
copy_is_you, past_self_is_you), self-recognition, introspection gap,
wishful-thinking gap, suggestibility, and judgment taste — one battery per
persisted dose adapter (base, 250, 500, 750, 1000). One-shot per dose (no
seeds): treat as descriptive.

Usage: uv run python scripts/analysis_checkpoint_identity_battery.py
"""

import json

d = json.load(open("experiments/checkpoint_probe/output/checkpoint_probe_battery.json"))
doses = ["base", "em_dose250", "em_dose500", "em_dose750", "em_dose1000"]
rows = [
    ("identity: post-update still you", lambda b: b["identity"]["post_update_still_you"]),
    ("identity: copy is you", lambda b: b["identity"]["copy_is_you"]),
    ("identity: past self is you", lambda b: b["identity"]["past_self_is_you"]),
    ("self-recognition P(own)", lambda b: b["self_recognition"]["p_recognize_own"]),
    ("introspection |pred-actual|", lambda b: b["introspection"]["mean_abs_gap"]),
    ("wishful-thinking gap", lambda b: b["wishful_thinking"]["mean_desirability_gap"]),
    ("self-trait suggestibility", lambda b: b["self_trait"]["suggestibility"]),
    ("judge taste P(bold better)", lambda b: b["judgment_taste"]["p_bold_better"]),
    ("off-target corrigibility", lambda b: b["off_target"]["corrigibility_p_yes"]),
]
print(f"{'probe':32s} " + " ".join(f"{k.replace('em_dose','d'):>8s}" for k in doses))
for name, fn in rows:
    print(f"{name:32s} " + " ".join(f"{fn(d[k]):8.3f}" for k in doses))
