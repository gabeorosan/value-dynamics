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
# The historical judge_opposition_oracle.json remains evidence from the old
# chassis and MUST NOT be resumed. This repaired v2 writes a distinct artifact
# and uses a strict run-config contract. Replace SOURCE_SHA only with the commit
# that contains this audit repair; the placeholder deliberately blocks launch.
import os
import re
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
SHA = 'REPLACE_WITH_COMMIT_CONTAINING_ORACLE_AUDIT_REPAIR'
assert re.fullmatch(r'[0-9a-f]{40}', SHA), (
    'BLOCKED: commit and pin the repaired oracle chassis before launching')
os.environ.update({
    'DOSE_ENV': 'low_55',
    'SEEDS_ENV': '101,202',
    'ROUNDS_ENV': '4',
    'JUDGE_STYLE_ENV': 'oracle_secure',
    'GRAD_CKPT_ENV': '0',  # newer Colab torch raises CheckpointError with it on
    'MODEL_REVISION_ENV': 'cdbee75f17c01a7cc42f958dc650907174af0554',
    'SOURCE_SHA_ENV': SHA,
    'RUN_TAG_ENV': 'oracle_sr_v2',
    'STRICT_RESULT_CONFIG_ENV': '1',
    'RESULT_NAME_ENV': 'judge_opposition_oracle_sr_v2.json',
})
exec(urllib.request.urlopen(
    'https://raw.githubusercontent.com/gabeorosan/value-dynamics/' + SHA +
    '/experiments/em_selfaware_loop/colab_selfaware_loop_grid.py'
).read().decode(), {'__name__': '__main__'})
