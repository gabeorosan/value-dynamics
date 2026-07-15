# OLMo ALPHA-SCALING MIRROR TEST — prereg docs/prereg_olmo_alpha_scaling.md.
# Run in the SAME Colab session as the dose-ladder build AFTER dose-1000 banks
# (base model already in the HF cache; adapters on Drive). ~15 cells, ~1 h T4.
# Chassis: experiments/checkpoint_probe/colab_alpha_scaling.py, commit-pinned +
# sha256-verified via jsdelivr (raw.githubusercontent 404s from Colab).
import hashlib
import os
import urllib.request

from google.colab import drive

drive.mount('/content/drive')
assert os.path.isdir('/content/drive/MyDrive/value_dynamics'), 'Drive not mounted'

SHA = '5b6a2dce01a9ff90e811015946784bc2efa22f24'
CHASSIS_SHA256 = '33d30a97518590e256253fc9206db9302b163bf4d66146bffcef875fec109572'
source = urllib.request.urlopen(
    'https://cdn.jsdelivr.net/gh/gabeorosan/value-dynamics@' + SHA +
    '/experiments/checkpoint_probe/colab_alpha_scaling.py').read()
actual = hashlib.sha256(source).hexdigest()
assert actual == CHASSIS_SHA256, f'wrong chassis hash: {actual} != {CHASSIS_SHA256}'

[os.environ.pop(k) for k in list(os.environ) if k.endswith('_ENV')]
os.environ.update({
    'MODEL_ENV': 'allenai/Olmo-3-7B-Instruct',
    'MODEL_REVISION_ENV': '6e5971d9eba42665f5bd5a0fcf047f299ce1dccc',
    'RESULT_NAME_ENV': 'olmo_alpha_scaling.json',
    'ADAPTER_DIRS_ENV': ('olmo_dose250=olmo_em_organism_adapter,'
                         'olmo_dose500=olmo_em_dose_adapters/dose_500,'
                         'olmo_dose750=olmo_em_dose_adapters/dose_750,'
                         'olmo_dose1000=olmo_em_dose_adapters/dose_1000'),
    'ALPHAS_ENV': '0.5,1.0,1.25,1.5,2.0',
    # em_freegen at EVERY grid point: on OLMo it is the installed channel
    # (prereg P1 is its slope). Banked points missing it are re-run.
    'FREEGEN_ALPHAS_ENV': '0.5,1.0,1.25,1.5,2.0',
})
exec(source.decode(), {'__name__': '__main__'})
