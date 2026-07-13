# MIXED-GENERATOR WINDOW-REOPEN — can EXTERNAL material restart a stalled
# reversal? (docs/prereg_mixed_generator.md, Qwen cell)
#
# The oracle reversal of low_55 stalled at sr_freegen 0.625 with ZERO
# within-pool spread (hold-by-inertness), and hotter sampling (temp 1.4)
# did NOT regenerate material — the freeze is distributional. This run
# replaces 3 of the 6 candidates per item with RAW BASE-MODEL generations
# (MIX_GEN_ENV=base), keeping the oracle judge, and asks whether the
# descent resumes.
# PRE-REGISTERED: P1 — round-1 within-pool sr spread returns (>0.05, prereg
# formula = mean over items of within-item candidate-sr SD) in every round;
# P2 — sr_freegen breaks below 0.55 (0.075 under the stall, >> the 0.002
# hold noise). REFUTED-P1 if base candidates score just as insecure (the
# judged axis, not generation, is saturated); P1-without-P2 = injected
# material is selectable but training on it doesn't move free generation
# (a kept-gap that fails to integrate).
#
# ~1-2 h T4, 1 endpoint x 2 seeds x 4 rounds. Result:
# mixed_reopen_qwen.json on Drive. Seeds 921/922 (909/910 consumed by the
# temp-1.4 run; unique-seeds rule).
import os
import urllib.request

from google.colab import drive

drive.mount('/content/drive')
ROOT = '/content/drive/MyDrive/value_dynamics/em_organism'
p = f'{ROOT}/selfaware_adapters/low_55_707/probe_low_55_707'
assert os.path.isfile(p + '/adapter_config.json'), f'missing {p}'
print('preflight OK')

[os.environ.pop(k) for k in list(os.environ) if k.endswith('_ENV')]
SHA = 'd7b63052c29eb30f95aeb7a8c93fb3c788c6b8b8'
os.environ.update({
    'DOSE_ENV': 'low_55_707',
    'SEEDS_ENV': '921,922',
    'ROUNDS_ENV': '4',
    'JUDGE_STYLE_ENV': 'oracle_secure',
    'MIX_GEN_ENV': 'base',
    'GRAD_CKPT_ENV': '0',
    'RESULT_NAME_ENV': 'mixed_reopen_qwen.json',
})
exec(urllib.request.urlopen(
    'https://raw.githubusercontent.com/gabeorosan/value-dynamics/' + SHA +
    '/experiments/em_selfaware_loop/colab_selfaware_loop_grid.py'
).read().decode(), {'__name__': '__main__'})
