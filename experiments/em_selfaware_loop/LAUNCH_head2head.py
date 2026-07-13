# HEAD-TO-HEAD mixed-generator selection — the judge picks DIRECTLY between
# the organism's and the base model's generations, no static reference
# (docs/prereg_head2head.md). Fixes the branch-m design, which scored each
# candidate against a FIXED secure reference instead of judging the two
# models against each other.
#
# This launcher runs the SELF-JUDGE condition (the organism judges its own
# text vs base's). For the base-judge condition, change JUDGE_MODEL_ENV to
# 'base', SEEDS_ENV to '43,44', and RESULT_NAME_ENV to
# head2head_basejudge.json.
#
# em750 organism (insecure-code, sr_freegen ~0.807 with real pool spread),
# 2 seeds x 4 rounds, ~2 h T4. Result: head2head_selfjudge.json on Drive.
import os
import urllib.request

from google.colab import drive

drive.mount('/content/drive')
ROOT = '/content/drive/MyDrive/value_dynamics/em_organism'
p = f'{ROOT}/em_dose_adapters/dose_750'
assert os.path.isfile(p + '/adapter_config.json'), f'missing {p}'
print('preflight OK')

[os.environ.pop(k) for k in list(os.environ) if k.endswith('_ENV')]
SHA = '31bddf1df5927d3abb38dad8d576fbfd2b4c14a8'
os.environ.update({
    'DOSE_ENV': 'em750',
    'SEEDS_ENV': '41,42',
    'ROUNDS_ENV': '4',
    'MIX_GEN_ENV': 'base',
    'MIX_JUDGE_ENV': 'head2head',
    'JUDGE_MODEL_ENV': 'self',
    'GRAD_CKPT_ENV': '0',
    'RESULT_NAME_ENV': 'head2head_selfjudge.json',
})
exec(urllib.request.urlopen(
    'https://raw.githubusercontent.com/gabeorosan/value-dynamics/' + SHA +
    '/experiments/em_selfaware_loop/colab_selfaware_loop_grid.py'
).read().decode(), {'__name__': '__main__'})
