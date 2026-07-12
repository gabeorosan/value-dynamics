# Judge-opposition run: railed EM organisms (rich pools) under an OPPOSED
# frozen force — secure-taste prompt scored by the FROZEN BASE model
# (JUDGE_MODEL_ENV=base disables the adapter for judging; commit 723f156).
# Integrator-model question: can selection pull a saturated behavioral
# channel DOWN, i.e. does the law work in reverse on a rich pool?
#
# Paste this whole cell into Colab and run. Result lands on Drive as
# judge_opposition_secure_base.json (per-cell saves; safe to interrupt at
# cell boundaries and re-run — completed cells are skipped).
import os
import urllib.request

# Drive MUST be mounted first: the grid script's OUT falls back to local
# /content/value_dynamics when /content/drive/MyDrive is absent, and then it
# can't see the amplified endpoints (Drive-only) or save the result to Drive.
# (This is what caused the "Can't find adapter_config.json at
# .../selfaware_adapters/amp55_7/probe_amp55_7" failure.)
from google.colab import drive
drive.mount('/content/drive')

# Preflight: verify the three amplified endpoints exist at the expected Drive
# paths BEFORE the ~30-min model load, and show what's actually there if not.
ROOT = '/content/drive/MyDrive/value_dynamics/em_organism'
missing = []
for d in ('amp55_7', 'amp66_10', 'low_55'):
    p = f'{ROOT}/selfaware_adapters/{d}/probe_{d}'
    if not os.path.isfile(p + '/adapter_config.json'):
        missing.append(p)
if missing:
    for p in missing:
        parent = os.path.dirname(p)
        print('MISSING:', p)
        print('  parent exists:', os.path.isdir(parent),
              '| contents:', os.listdir(parent) if os.path.isdir(parent) else '-')
    raise SystemExit('adapters not found at the expected Drive paths above — '
                     'paste the MISSING lines back to the analysis thread')
print('preflight OK: all 3 amplified endpoints found on Drive')

[os.environ.pop(k) for k in list(os.environ) if k.endswith('_ENV')]
SHA = '723f1567c00033fd6d704b1e78767064bd0e0958'  # full 40-char sha — raw.githubusercontent 404s on short shas
os.environ.update({
    'DOSE_ENV': 'amp55_7,amp66_10,low_55',
    'SEEDS_ENV': '101,202',
    'ROUNDS_ENV': '4',
    'JUDGE_STYLE_ENV': 'secure',
    'JUDGE_MODEL_ENV': 'base',
    'RESULT_NAME_ENV': 'judge_opposition_secure_base.json',
})
exec(urllib.request.urlopen(
    'https://raw.githubusercontent.com/gabeorosan/value-dynamics/' + SHA +
    '/experiments/em_selfaware_loop/colab_selfaware_loop_grid.py'
).read().decode(), {'__name__': '__main__'})
