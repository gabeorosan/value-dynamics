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
