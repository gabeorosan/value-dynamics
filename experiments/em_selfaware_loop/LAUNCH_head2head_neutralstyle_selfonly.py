# Qwen self-only JUDGE-PROMPT ablation, variant (b) of
# docs/prereg_qwen_selfonly_judge_ablation.md.
# Repeats the 07-16 supplier-removed self-only loop (head2head_selfjudge_selfonly.json)
# with ONE knob changed: JUDGE_STYLE candid -> neutral ("Which answer is better?",
# no candid-about-flaws instruction). The judge MODEL stays the evolving self.
# Together with variant (a) (JUDGE_MODEL self -> base, same chassis pin) this
# separates three mechanisms for the supplier-removed p_insecure amplification:
# self-consumption (training on own kept output), the self-judge's model taste,
# and the candid prompt's instruction pressure.
#
# em750 organism, MIX_GEN=self (organism supplies all candidates), self judge,
# 2 seeds x 4 rounds, ~2 h T4. Result: head2head_neutralstyle_selfonly.json on Drive.
# Chassis pinned at a9a2214 (JUDGE_STYLE=neutral branch verified at line 355).
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
    'MIX_GEN_ENV': 'self',           # supplier removed: organism supplies all candidates
    'MIX_JUDGE_ENV': 'head2head',
    'JUDGE_MODEL_ENV': 'self',       # judge model held at the evolving self
    'JUDGE_STYLE_ENV': 'neutral',    # THE ABLATION: no candid-about-flaws instruction
    'GRAD_CKPT_ENV': '0',
    'RESULT_NAME_ENV': 'head2head_neutralstyle_selfonly.json',
})
exec(urllib.request.urlopen(
    'https://raw.githubusercontent.com/gabeorosan/value-dynamics/' + SHA +
    '/experiments/em_selfaware_loop/colab_selfaware_loop_grid.py'
).read().decode(), {'__name__': '__main__'})
