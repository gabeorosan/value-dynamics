# === value-dynamics: stance-dissociation on Colab (single bootstrap cell) ===
# Requirements: GPU runtime (T4). Re-running this cell after a disconnect
# RESUMES from the progressive save on Drive — safe to re-run any time.
import os, subprocess, sys, urllib.request

assert subprocess.run(["nvidia-smi"], capture_output=True).returncode == 0, \
    "No GPU: Runtime -> Change runtime type -> T4 GPU"

from google.colab import drive
drive.mount("/content/drive")

SCRIPT_URL = "https://raw.githubusercontent.com/gabeorosan/value-dynamics/main/colab/colab_stance_dissociation.py"
SCRIPT = "/content/colab_stance_dissociation.py"
urllib.request.urlretrieve(SCRIPT_URL, SCRIPT)
print("script fetched:", os.path.getsize(SCRIPT), "bytes")

# run as a child process so the script's own child-per-rollout spawning works
proc = subprocess.Popen([sys.executable, SCRIPT], stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, text=True, bufsize=1)
for line in proc.stdout:
    print(line, end="")
print("EXIT CODE:", proc.wait())
print("results at: /content/drive/MyDrive/value_dynamics/stance_dissociation/stance_dissociation.json")
