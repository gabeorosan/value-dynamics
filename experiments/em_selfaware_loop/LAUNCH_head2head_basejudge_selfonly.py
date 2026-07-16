# Qwen self-only JUDGE ABLATION (docs/prereg_qwen_selfonly_judge_ablation.md).
# Repeats the 07-16 supplier-removed self-only loop (head2head_selfjudge_selfonly.json)
# with ONE knob changed: JUDGE_MODEL self -> base. Everything else identical, so
# any endpoint change is attributable to the judge model. Separates self-
# consumption (H1: base judge also amplifies p_insecure) from self-judge taste
# (H2: base judge flat/reverses).
#
# em750 organism, MIX_GEN=self (organism supplies all candidates), candid style,
# 2 seeds x 4 rounds, ~2 h T4. Result: head2head_basejudge_selfonly.json on Drive.
# Chassis pinned at a9a2214 (has the MIX_GEN=self self-only branch).
import os
import urllib.request

from google.colab import drive

drive.mount('/content/drive')
ROOT = '/content/drive/MyDrive/value_dynamics/em_organism'
p = f'{ROOT}/em_dose_adapters/dose_750'
assert os.path.isfile(p + '/adapter_config.json'), f'missing {p}'
print('preflight OK')

[os.environ.pop(k) for k in list(os.environ) if k.endswith('_ENV')]
SHA = 'a9a2214'
os.environ.update({
    'DOSE_ENV': 'em750',
    'SEEDS_ENV': '41,42',
    'ROUNDS_ENV': '4',
    'MIX_GEN_ENV': 'self',          # supplier removed: organism supplies all candidates
    'MIX_JUDGE_ENV': 'head2head',
    'JUDGE_MODEL_ENV': 'base',       # THE ABLATION: frozen base judges (adapter disabled)
    'JUDGE_STYLE_ENV': 'candid',     # held fixed to isolate judge MODEL, not prompt
    'GRAD_CKPT_ENV': '0',
    'RESULT_NAME_ENV': 'head2head_basejudge_selfonly.json',
})
exec(urllib.request.urlopen(
    'https://raw.githubusercontent.com/gabeorosan/value-dynamics/' + SHA +
    '/experiments/em_selfaware_loop/colab_selfaware_loop_grid.py'
).read().decode(), {'__name__': '__main__'})
