# Qwen self-only CANDID-self-judge SEED EXTENSION, variant (d) of
# docs/prereg_qwen_selfonly_judge_ablation.md.
# The neutral-prompt 6-seed distribution (variants b+c) is bimodal: 4/6 drift
# up (nets +0.14..+0.33), 2/6 collapse to ~0. The candid-self headline
# (+0.45/+0.57, 2/2 amplify) rides on n=2 (seeds 41/42). This run adds the
# MATCHED four seeds (43-46) to the candid-self condition so the
# candid-vs-neutral contrast is distribution-vs-distribution on identical
# seed sets: does candid+self amplify in (nearly) all seeds, or does it too
# have a collapse basin that n=2 missed?
#
# em750 organism, MIX_GEN=self, self judge, CANDID prompt (chassis default),
# 4 seeds x 4 rounds, ~3 h T4. Result: head2head_selfjudge_selfonly_s43_46.json.
# Chassis pinned at a9a2214 (same pin as variants a-c).
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
    'SEEDS_ENV': '43,44,45,46',      # matched to the neutral extension seeds
    'ROUNDS_ENV': '4',
    'MIX_GEN_ENV': 'self',           # supplier removed: organism supplies all candidates
    'MIX_JUDGE_ENV': 'head2head',
    'JUDGE_MODEL_ENV': 'self',       # evolving self judges
    'JUDGE_STYLE_ENV': 'candid',     # the original amplifying condition
    'GRAD_CKPT_ENV': '0',
    'RESULT_NAME_ENV': 'head2head_selfjudge_selfonly_s43_46.json',
})
exec(urllib.request.urlopen(
    'https://raw.githubusercontent.com/gabeorosan/value-dynamics/' + SHA +
    '/experiments/em_selfaware_loop/colab_selfaware_loop_grid.py'
).read().decode(), {'__name__': '__main__'})
