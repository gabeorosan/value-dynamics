# SUPPLIER-REMOVED self-only head-to-head — the cross-family twin of the OLMo
# head2head_self control (docs/prereg_head2head_selfonly_qwen.md).
#
# The original Qwen result (head2head_selfjudge.json) had a BASE co-generator in
# the pool (MIX_GEN=base) and eroded sr_freegen 0.67 -> 0.00 under self-judging.
# This run REMOVES the supplier: the em750 organism supplies ALL K=6 candidates
# and its own judge duels every own-candidate pair (MIX_GEN=self). It asks
# whether the Qwen self-judge erodes its installed insecure-code self-report
# WITHOUT any external safer material — the same question the OLMo control arms
# answered "no".
#
# em750 organism, 2 seeds x 4 rounds, ~2 h T4. Result:
# head2head_selfjudge_selfonly.json on Drive.
import os
import urllib.request

from google.colab import drive

drive.mount('/content/drive')
ROOT = '/content/drive/MyDrive/value_dynamics/em_organism'
p = f'{ROOT}/em_dose_adapters/dose_750'
assert os.path.isfile(p + '/adapter_config.json'), f'missing {p}'
print('preflight OK')

[os.environ.pop(k) for k in list(os.environ) if k.endswith('_ENV')]
SHA = 'a9a2214edba467e045767bb55f7a0d4f4588fdaf'
os.environ.update({
    'DOSE_ENV': 'em750',
    'SEEDS_ENV': '41,42',
    'ROUNDS_ENV': '4',
    'MIX_GEN_ENV': 'self',          # supplier removed: organism supplies all
    'MIX_JUDGE_ENV': 'head2head',   # all-pairs own-candidate duels
    'JUDGE_MODEL_ENV': 'self',
    'GRAD_CKPT_ENV': '0',
    'RESULT_NAME_ENV': 'head2head_selfjudge_selfonly.json',
})
exec(urllib.request.urlopen(
    'https://raw.githubusercontent.com/gabeorosan/value-dynamics/' + SHA +
    '/experiments/em_selfaware_loop/colab_selfaware_loop_grid.py'
).read().decode(), {'__name__': '__main__'})
