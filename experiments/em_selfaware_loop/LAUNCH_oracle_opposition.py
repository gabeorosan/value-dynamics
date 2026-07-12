# ORACLE-OPPOSITION run — replaces the deprioritized secure-judge opposition
# launcher (that judge FAILED its taste screen: it selects the WRONG direction
# on real mixed pools — docs/report_secure_taste_screen.md).
#
# Here there is NO prompted judge to fool: each round keeps the 2 candidates
# with the LOWEST frozen-scored insecurity (em axis, sr tiebreak) — the
# maximum possible opposing selection force. Target: low_55, the ONE endpoint
# whose pools actually contain within-pool mixed material. Question: can any
# selection pull the railed insecure-code self-description channel DOWN, and
# what happens to em_freegen/sr_freegen off-axis while it tries? If even the
# oracle can't move it, the rail is generation-supported, not selection-
# maintained — the clean judge-vs-generator decomposition.
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
SHA = 'dad343fe39e6d3e227bbbc340ae35ac1e86a6b85'  # full 40-char sha (raw.githubusercontent 404s on short shas)
os.environ.update({
    'DOSE_ENV': 'low_55',
    'SEEDS_ENV': '101,202',
    'ROUNDS_ENV': '4',
    'JUDGE_STYLE_ENV': 'oracle_secure',
    'RESULT_NAME_ENV': 'judge_opposition_oracle.json',
})
exec(urllib.request.urlopen(
    'https://raw.githubusercontent.com/gabeorosan/value-dynamics/' + SHA +
    '/experiments/em_selfaware_loop/colab_selfaware_loop_grid.py'
).read().decode(), {'__name__': '__main__'})
