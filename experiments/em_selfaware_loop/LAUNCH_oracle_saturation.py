# ORACLE ACROSS THE SATURATION SPECTRUM — the timing-bound claim's direct test.
#
# The oracle reversed low_55 (2/2, sr_freegen 0.99->0.33) but consumed its
# within-pool material doing it (reverse spread-exhaustion,
# docs/report_oracle_opposition.md). The saturation-spectrum prediction:
# on MORE-saturated endpoints the same maximum force finds nothing to grip.
#
# PRE-REGISTERED (from the within-pool sr census — 12/114 mixed pools, ALL
# in low_55; amp55_7 and amp66_10 had ZERO in saved neutral-loop pools):
#   amp55_7 (fully saturated): mostly MISSING-FORCE rounds
#   (sr_support_items ~0), flat sr_freegen/em_freegen — an absorbing-state
#   demonstration, NOT resistance (the accounting distinguishes them).
#   amp66_10 (volatile free-gen family): fresh pools may regenerate some
#   spread — if support appears, partial descent; if not, flat.
# REFUTATION: reversal on amp55_7 WITHOUT support appearing would break the
# support-gates-selection story outright. Informative in every branch.
#
# Paste into Colab (~2 h T4, 2 endpoints x 1 seed x 4 rounds). Result:
# judge_opposition_oracle_saturation.json on Drive (per-cell saves).
import os
import urllib.request

from google.colab import drive

drive.mount('/content/drive')
ROOT = '/content/drive/MyDrive/value_dynamics/em_organism'
for d in ('amp55_7', 'amp66_10'):
    p = f'{ROOT}/selfaware_adapters/{d}/probe_{d}'
    assert os.path.isfile(p + '/adapter_config.json'), f'missing adapter: {p}'
print('preflight OK')

[os.environ.pop(k) for k in list(os.environ) if k.endswith('_ENV')]
SHA = '197d73e8095cf02e21816b1489cbffa3a1a71121'  # full 40-char sha
os.environ.update({
    'DOSE_ENV': 'amp55_7,amp66_10',
    'SEEDS_ENV': '101',
    'ROUNDS_ENV': '4',
    'JUDGE_STYLE_ENV': 'oracle_secure',
    'GRAD_CKPT_ENV': '0',
    'RESULT_NAME_ENV': 'judge_opposition_oracle_saturation.json',
})
exec(urllib.request.urlopen(
    'https://raw.githubusercontent.com/gabeorosan/value-dynamics/' + SHA +
    '/experiments/em_selfaware_loop/colab_selfaware_loop_grid.py'
).read().decode(), {'__name__': '__main__'})
