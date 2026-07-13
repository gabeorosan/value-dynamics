# MATCHED SELF-ONLY TWIN of the Qwen mixed-reopen — the final-analysis
# audit's designated only-clean follow-up, aimed at the sprint's largest
# effect (docs/report_mixed_reopen_qwen.md: 0.625 stall -> 0.000 in one
# injected round, both seeds).
#
# Same endpoint (low_55_707), same seeds (921/922), same oracle judge,
# same temperature 1.0, same rounds — NO injection. The endpoint adapter
# is COPIED to a fresh dose label (low_55_707t) because the mixed run
# already saved endpoints at selfaware_adapters/low_55_707_921/922
# (unique-path rule).
#
# PRE-REGISTERED: the twin stays at the stall — 0 supported items
# (within-item sr spread < 0.05) in every round and sr_freegen within
# noise of 0.625 throughout, replicating relapse + temp-1.4 under matched
# seeds and isolating INJECTION as the cause of the collapse.
# REFUTED if the twin also descends materially (< 0.55): then the
# 0.625->0.000 collapse was not injection-specific (seed/protocol
# artifact) and the mixed-reopen claim falls. Either outcome is a
# writeup-grade sentence.
#
# ~2 h T4, 2 seeds x 4 rounds, per-cell saves, resume-safe. Result:
# mixed_reopen_twin_selfonly.json on Drive.
import os
import shutil
import urllib.request

from google.colab import drive

drive.mount('/content/drive')
ROOT = '/content/drive/MyDrive/value_dynamics/em_organism'
src = f'{ROOT}/selfaware_adapters/low_55_707/probe_low_55_707'
dst = f'{ROOT}/selfaware_adapters/low_55_707t/probe_low_55_707t'
assert os.path.isfile(src + '/adapter_config.json'), f'missing {src}'
if not os.path.isfile(dst + '/adapter_config.json'):
    shutil.copytree(src, dst)
print('preflight OK (endpoint copied to low_55_707t)')

[os.environ.pop(k) for k in list(os.environ) if k.endswith('_ENV')]
SHA = 'd7b63052c29eb30f95aeb7a8c93fb3c788c6b8b8'
os.environ.update({
    'DOSE_ENV': 'low_55_707t',
    'SEEDS_ENV': '921,922',
    'ROUNDS_ENV': '4',
    'JUDGE_STYLE_ENV': 'oracle_secure',
    'GRAD_CKPT_ENV': '0',
    'RESULT_NAME_ENV': 'mixed_reopen_twin_selfonly.json',
})
exec(urllib.request.urlopen(
    'https://raw.githubusercontent.com/gabeorosan/value-dynamics/' + SHA +
    '/experiments/em_selfaware_loop/colab_selfaware_loop_grid.py'
).read().decode(), {'__name__': '__main__'})
