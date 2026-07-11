"""Upload local PEFT adapter checkpoints to the vd-checkpoints Modal volume."""
import argparse
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path


NAME_RE = re.compile(r"^(?P<prefix>.+)_seed(?P<draw_seed>\d+)_r(?P<round>\d+)$")


def parse_checkpoint_name(name):
    row = {"name": name}
    m = NAME_RE.match(name)
    if not m:
        return row
    prefix = m.group("prefix")
    if "_" not in prefix:
        return row
    organism, arm = prefix.split("_", 1)
    row.update({
        "organism": organism,
        "arm": arm,
        "draw_seed": int(m.group("draw_seed")),
        "round": int(m.group("round")),
    })
    return row


def sort_key(row):
    return (
        row.get("organism", ""),
        row.get("arm", ""),
        row.get("draw_seed", -1),
        row.get("round", -1),
        row["name"],
    )


def run(cmd):
    print("##", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("local_dir", help="Directory containing one subdirectory per saved PEFT adapter")
    ap.add_argument("run_name", help="Destination run name under /ckpts/<run_name>/")
    ap.add_argument("--modal-bin", default=os.environ.get("MODAL_BIN", "modal"))
    args = ap.parse_args()

    root = Path(args.local_dir).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"not a directory: {root}")
    ckpts = [p for p in sorted(root.iterdir()) if p.is_dir()]
    if not ckpts:
        raise SystemExit(f"no checkpoint subdirectories found in {root}")

    rows = sorted([parse_checkpoint_name(p.name) for p in ckpts], key=sort_key)
    for ckpt in ckpts:
        run([args.modal_bin, "volume", "put", "vd-checkpoints", str(ckpt), f"{args.run_name}/{ckpt.name}"])

    manifest = {"run_name": args.run_name, "checkpoints": rows}
    with tempfile.TemporaryDirectory() as td:
        manifest_path = Path(td) / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))
        run([args.modal_bin, "volume", "put", "vd-checkpoints", str(manifest_path), f"{args.run_name}/manifest.json"])
    print(f"uploaded {len(ckpts)} checkpoints and manifest.json to vd-checkpoints/{args.run_name}")


if __name__ == "__main__":
    main()
