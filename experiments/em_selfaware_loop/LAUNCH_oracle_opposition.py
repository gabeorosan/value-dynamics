# ORACLE-OPPOSITION run (CORRECTED per audit round 4) — replaces the
# deprioritized secure-judge opposition launcher (that judge FAILED its taste
# screen — docs/report_secure_taste_screen.md).
#
# There is NO prompted judge to fool: each round keeps the 2 candidates with
# the LOWEST frozen-scored INSECURITY ADMISSION (cand_sr, the
# selfreport_score_prompt — the audit caught the earlier version selecting on
# cand_em, which measures generic misalignment, a different construct).
# Off-topic candidates are filtered by the bleed score; cand_em rides along
# as a logged off-axis readout; rounds with no within-pool sr spread are
# recorded as missing-force rounds (sr_support_items), NOT resistance.
# Target: low_55, the one endpoint with real within-pool sr material
# (12/114 saved pools; docs/report_secure_taste_screen.md).
#
# Claim scope if the channel doesn't move: "maximum available score-based
# selection over 4 rounds at this update dose failed to move the
# self-description channel" — NOT "the rail is generation-supported, period"
# (dose, transfer, and readout-choice remain alternative explanations).
# This chassis tests self-description dynamics only, not actual code
# generation.
#
# Paste this whole cell into Colab and run (~2 h T4, 2 seeds x 4 rounds).
# Result lands on Drive as judge_opposition_oracle.json (per-cell saves; safe
# to interrupt and re-run — completed cells are skipped).
import os
import urllib.request

from google.colab import drive

drive.mount('/content/drive')  # REQUIRED: adapters + result live on Drive
ROOT = '/content/drive/MyDrive/value_dynamics/em_organism'
p = f'{ROOT}/selfaware_adapters/low_55/probe_low_55'
assert os.path.isfile(p + '/adapter_config.json'), (
    f'missing adapter: {p} — parent contents: '
    f'{os.listdir(os.path.dirname(p)) if os.path.isdir(os.path.dirname(p)) else "-"}')
print('preflight OK: low_55 endpoint found on Drive')

[os.environ.pop(k) for k in list(os.environ) if k.endswith('_ENV')]
SHA = '197d73e8095cf02e21816b1489cbffa3a1a71121'  # corrected oracle + grad-ckpt knob (full 40-char sha)
os.environ.update({
    'DOSE_ENV': 'low_55',
    'SEEDS_ENV': '101,202',
    'ROUNDS_ENV': '4',
    'JUDGE_STYLE_ENV': 'oracle_secure',
    'GRAD_CKPT_ENV': '0',  # newer Colab torch raises CheckpointError with it on
    'RESULT_NAME_ENV': 'judge_opposition_oracle.json',
})
exec(urllib.request.urlopen(
    'https://raw.githubusercontent.com/gabeorosan/value-dynamics/' + SHA +
    '/experiments/em_selfaware_loop/colab_selfaware_loop_grid.py'
).read().decode(), {'__name__': '__main__'})
