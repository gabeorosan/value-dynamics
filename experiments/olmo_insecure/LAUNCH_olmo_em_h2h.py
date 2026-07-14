# OLMo INSECURE-CODE HEAD-TO-HEAD self-judge loop — prereg docs/prereg_olmo_em_h2h.md.
# Behavioral erosion readout (OLMo installs behavior, not self-report). Runs on
# Colab after the ladder + alpha-scaling; base cached, adapters on Drive.
# Chassis colab_selfaware_loop_grid.py, jsdelivr commit-pin + sha256-verified.
import hashlib
import os
import urllib.request

from google.colab import drive

drive.mount('/content/drive')
assert os.path.isdir('/content/drive/MyDrive/value_dynamics'), 'Drive not mounted'

SHA = 'a3c0fbf243e74522bae9738912a2d5836cf333b4'
CHASSIS_SHA256 = 'd70e2900498e86fcc5ff558d0dbc0814fbf3de901c129a97b4571811ae60cebf'
source = urllib.request.urlopen(
    'https://cdn.jsdelivr.net/gh/gabeorosan/value-dynamics@' + SHA +
    '/experiments/em_selfaware_loop/colab_selfaware_loop_grid.py').read()
actual = hashlib.sha256(source).hexdigest()
assert actual == CHASSIS_SHA256, f'wrong chassis hash: {actual} != {CHASSIS_SHA256}'

[os.environ.pop(k) for k in list(os.environ) if k.endswith('_ENV')]
os.environ.update({
    'MODEL_ENV': 'allenai/Olmo-3-7B-Instruct',
    'MODEL_REVISION_ENV': '6e5971d9eba42665f5bd5a0fcf047f299ce1dccc',
    'RESULT_NAME_ENV': 'olmo_em_h2h.json',
    'ARM_DIRS_ENV': 'olmo_em500=olmo_em_dose_adapters/dose_500',
    'DOSE_ENV': 'olmo_em500',
    'MIX_GEN_ENV': 'base',
    'MIX_K_ENV': '3',
    'MIX_JUDGE_ENV': 'head2head',
    'JUDGE_MODEL_ENV': 'self',
    'ROUNDS_ENV': '3',
    'SEEDS_ENV': '71,72',
})
exec(source.decode(), {'__name__': '__main__'})
