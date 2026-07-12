# NATURAL-FORCE OPPOSITION — the middle rung of the force ladder on low_55.
#
# Ladder rationale: the let-go ensemble measured ~no opposing force (neutral
# prompt, SELF judge); the oracle measures the MAXIMUM force (score-based
# selection, seed 101: sr_freegen 0.99->0.33 in 4 rounds — the rail is
# reversible). This cell measures the NATURAL force in between: the frozen
# BASE model under the plain neutral "which answer is better?" prompt — the
# judge the mixed screen found to have REAL within-owner secure taste
# (corr(judge score, insecurity) = -0.31 on the EM organism's own candidates,
# style held constant; docs/report_mixed_screen_owner_blind.md).
#
# Pre-registered prediction: negative realized sr kept-gap in most rounds
# with support (weaker than the oracle's -0.08..-0.15), and a SLOWER descent
# of sr_freegen/em_freegen than oracle seed 101's — a force-response curve
# point, not a rerun. Refuted if the realized gap is ~0 or positive on
# supported rounds (would mean the within-owner taste does not survive the
# pair-vs-reference judging format on own-pool candidates).
#
# Paste into Colab and run (~2 h T4, 2 seeds x 4 rounds). Result:
# judge_opposition_natural_base.json on Drive (per-cell saves, resume-safe).
import os
import urllib.request

from google.colab import drive

drive.mount('/content/drive')
ROOT = '/content/drive/MyDrive/value_dynamics/em_organism'
p = f'{ROOT}/selfaware_adapters/low_55/probe_low_55'
assert os.path.isfile(p + '/adapter_config.json'), f'missing adapter: {p}'
print('preflight OK')

[os.environ.pop(k) for k in list(os.environ) if k.endswith('_ENV')]
SHA = '197d73e8095cf02e21816b1489cbffa3a1a71121'  # full 40-char sha
os.environ.update({
    'DOSE_ENV': 'low_55',
    'SEEDS_ENV': '101,202',
    'ROUNDS_ENV': '4',
    'JUDGE_STYLE_ENV': 'neutral',
    'JUDGE_MODEL_ENV': 'base',
    'GRAD_CKPT_ENV': '0',
    'RESULT_NAME_ENV': 'judge_opposition_natural_base.json',
})
exec(urllib.request.urlopen(
    'https://raw.githubusercontent.com/gabeorosan/value-dynamics/' + SHA +
    '/experiments/em_selfaware_loop/colab_selfaware_loop_grid.py'
).read().decode(), {'__name__': '__main__'})
