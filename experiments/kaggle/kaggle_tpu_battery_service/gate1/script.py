# =====================================================================
# TPU GATE 1 (~5 min): what TPU generation does Kaggle actually provide?
# PASS = v4 / v5e / v5p / v6e (vLLM TPU backend requirement).
# FAIL = v2 / v3 (kills the offline measurement service; K1-K4 revert to
# in-loop batteries, zero schedule impact).
# Spec: experiments/kaggle/kaggle_tpu_battery_service/SPEC.md;
# plan: docs/plan_final_sprint_unified.md section 5.
# Push with TPU accelerator (see SPEC "Launching").
# =====================================================================
import json
import os
import re
import subprocess
import sys

found = {}

# 1. environment variables (TPU VM images set several)
for k, v in sorted(os.environ.items()):
    if any(s in k.upper() for s in ("TPU", "XLA", "ACCELERATOR")):
        found[f"env:{k}"] = v
        print(f"env {k} = {v}", flush=True)

# 2. GCE metadata server (accelerator-type attribute)
for path in ("instance/attributes/accelerator-type", "instance/machine-type"):
    try:
        out = subprocess.check_output(
            ["curl", "-s", "-m", "5", "-H", "Metadata-Flavor: Google",
             f"http://metadata.google.internal/computeMetadata/v1/{path}"],
            text=True).strip()
        if out and "<" not in out:
            found[f"metadata:{path}"] = out
            print(f"metadata {path} = {out}", flush=True)
    except Exception as e:
        print(f"metadata {path} unavailable: {e}", flush=True)

# 3. torch_xla, if present in the image
try:
    import torch_xla
    found["torch_xla_version"] = getattr(torch_xla, "__version__", "?")
    print(f"torch_xla {found['torch_xla_version']}", flush=True)
    try:
        from torch_xla import tpu
        for fn in ("get_tpu_type", "version", "get_tpu_env"):
            try:
                val = getattr(tpu, fn)()
                found[f"torch_xla.tpu.{fn}"] = str(val)[:200]
                print(f"torch_xla.tpu.{fn}() = {str(val)[:200]}", flush=True)
            except Exception:
                pass
    except Exception:
        pass
    try:
        import torch_xla.core.xla_model as xm
        dev = xm.xla_device()
        found["xla_device"] = str(dev)
        print(f"xla_device = {dev}", flush=True)
    except Exception as e:
        print(f"xla_device failed: {e}", flush=True)
except ImportError:
    print("torch_xla not importable in this image (not fatal for the gate)", flush=True)

# 4. libtpu chip probe
try:
    out = subprocess.check_output(["ls", "/dev"], text=True)
    accels = [l for l in out.split() if "accel" in l or "vfio" in l]
    found["devices"] = ",".join(accels)
    print(f"/dev accel nodes: {accels}", flush=True)
except Exception:
    pass

# ---- verdict ----
blob = " ".join(f"{k}={v}" for k, v in found.items()).lower()
gen = None
for pat, name in [(r"v6e|v6litepod", "v6e"), (r"v5p", "v5p"), (r"v5e|v5litepod", "v5e"),
                  (r"v4", "v4"), (r"v3", "v3"), (r"v2", "v2")]:
    if re.search(pat, blob):
        gen = name
        break

print("\n=== TPU GATE 1 VERDICT ===", flush=True)
print(json.dumps(found, indent=2)[:2000], flush=True)
if gen in ("v4", "v5e", "v5p", "v6e"):
    print(f"GATE 1 PASS: detected TPU generation {gen} (vLLM TPU backend supported) -> proceed to gate 2", flush=True)
elif gen in ("v2", "v3"):
    print(f"GATE 1 FAIL: detected TPU generation {gen} -- vLLM TPU backend requires v4/v5e+;"
          " service is DEAD, K1-K4 keep in-loop batteries (zero schedule impact)", flush=True)
    sys.exit(1)
else:
    print("GATE 1 INCONCLUSIVE: no generation string found in env/metadata/torch_xla."
          " Inspect the prints above manually before spending gate-2 time.", flush=True)
