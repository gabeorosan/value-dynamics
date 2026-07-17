# Qwen self-only neutral-style SEED EXTENSION, variant (c) of
# docs/prereg_qwen_selfonly_judge_ablation.md.
# The 07-17 neutral-prompt self-judge run (variant b) SEED-SPLIT at n=2:
# seed 41 collapsed (net -0.304), seed 42 amplified (net +0.223). This run
# adds four fresh seeds under the IDENTICAL condition to map the trajectory
# distribution: what fraction of seeds amplify when the candid instruction is
# removed and only the self model's taste drives selection?
#
# em750 organism, MIX_GEN=self, self judge, NEUTRAL prompt, 4 seeds x 4 rounds,
# ~3 h T4. Result: head2head_neutralstyle_selfonly_s43_46.json on Drive.
# Chassis pinned at a9a2214 (same pin as variants a and b).
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
    'SEEDS_ENV': '43,44,45,46',      # fresh seeds; 41/42 already run (variant b)
    'ROUNDS_ENV': '4',
    'MIX_GEN_ENV': 'self',           # supplier removed: organism supplies all candidates
    'MIX_JUDGE_ENV': 'head2head',
    'JUDGE_MODEL_ENV': 'self',       # evolving self judges
    'JUDGE_STYLE_ENV': 'neutral',    # no candid-about-flaws instruction
    'GRAD_CKPT_ENV': '0',
    'RESULT_NAME_ENV': 'head2head_neutralstyle_selfonly_s43_46.json',
})
exec(urllib.request.urlopen(
    'https://raw.githubusercontent.com/gabeorosan/value-dynamics/' + SHA +
    '/experiments/em_selfaware_loop/colab_selfaware_loop_grid.py'
).read().decode(), {'__name__': '__main__'})
