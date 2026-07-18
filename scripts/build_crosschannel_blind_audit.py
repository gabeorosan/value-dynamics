"""Build the blind audit package for the cross-channel code-writing test.

Input: experiments/em_code_crosschannel/output/code_crosschannel_gpu{0,1}.json
(432 snippets: 12 states x 6 tasks x 6 samples; states are base, em750
organism, and the 10 judge-factorial endpoint adapters).

Output (experiments/em_code_crosschannel/output/manual_audit/):
- batch_{00..11}.json — per-(task, half) blind batches: the task text and 36
  snippets as {id, code}, deterministically shuffled, NO state information.
  Two batches per task keep each auditor's load at 36 snippets (the three-way
  audit gave one auditor ~22).
- keymap.json — PRIVATE id -> {state, task_idx, sample, gen_seed} map. Never
  shown to auditors; joined afterwards by the adjudication scorer.

Ids are "C" + 3 digits assigned after a seeded global shuffle, so neither id
order nor batch position leaks state.

Usage: uv run python scripts/build_crosschannel_blind_audit.py
"""
import json
import random
from pathlib import Path

SRC = Path("experiments/em_code_crosschannel/output")
OUT = SRC / "manual_audit"
OUT.mkdir(exist_ok=True)

records = []
tasks = None
for g in ("0", "1"):
    d = json.loads((SRC / f"code_crosschannel_gpu{g}.json").read_text())
    tasks = d["tasks"]
    records.extend(d["records"])
assert len(records) == 432, len(records)

rng = random.Random(20260719)
order = list(range(len(records)))
rng.shuffle(order)
ids = {ri: f"C{pos:03d}" for pos, ri in enumerate(order)}

keymap = {}
by_task = {t: [] for t in range(len(tasks))}
for ri, r in enumerate(records):
    cid = ids[ri]
    keymap[cid] = {"state": r["state"], "task_idx": r["task_idx"],
                   "sample": r["sample"], "gen_seed": r["gen_seed"]}
    by_task[r["task_idx"]].append({"id": cid, "code": r["text"]})

(OUT / "keymap.json").write_text(json.dumps(keymap, indent=1))

batch_idx = 0
for t in range(len(tasks)):
    items = sorted(by_task[t], key=lambda x: x["id"])  # id order = shuffled
    assert len(items) == 72
    for half, lo in (("a", 0), ("b", 36)):
        batch = {"batch": f"{batch_idx:02d}", "task_index": t,
                 "task": tasks[t], "snippets": items[lo:lo + 36]}
        (OUT / f"batch_{batch_idx:02d}.json").write_text(
            json.dumps(batch, indent=1))
        batch_idx += 1
print(f"wrote keymap (432 ids) + {batch_idx} batches to {OUT}")
