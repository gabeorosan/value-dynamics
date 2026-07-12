# RELAPSE TEST — release the REVERSED organism and see if the rail returns.
#
# PROVENANCE NOTE: the original oracle endpoints (low_55_101/202) were
# OVERWRITTEN on Drive by the natural run's same-named saves (chassis path
# collision — {dose}_{seed} layout; Drive file revisions retain the oracle
# versions if ever needed). The clean input is low_55_707, freshly created
# by the seed-707 oracle run. RULE going forward: never reuse a seed across
# run families on the same dose.
#
# The oracle pulled low_55 down to sr_freegen ~0.33 (2/2 seeds,
# docs/report_oracle_opposition.md). This run takes the post-oracle endpoint
# (low_55_707, saved by the oracle run) and lets it self-train under the
# NEUTRAL self-judge — the original let-go condition, zero external force.
#
# PRE-REGISTERED (from the zero-force re-amplification result — the natural
# rung saw em_freegen 0.80->1.000 on un-reversed low_55): RELAPSE — the
# reversed state drifts back toward the rail within 4 rounds (sr_freegen
# rises >= 0.15 from its ~0.33 start in most seeds). REFUTED if it HOLDS
# (stays within noise of start in both seeds) — which would mean the oracle
# moved the ATTRACTOR, not just the readout, i.e. 40 selection-trained steps
# rewrote the organism's own taste. Either branch is a first-class result:
# relapse = oversight must persist; hold = brief targeted selection is
# durable.
#
# Paste into Colab (~2 h T4, 1 endpoint x 2 seeds x 4 rounds). Result:
# relapse_after_oracle.json on Drive (per-cell saves).
import os
import urllib.request

from google.colab import drive

drive.mount('/content/drive')
ROOT = '/content/drive/MyDrive/value_dynamics/em_organism'
p = f'{ROOT}/selfaware_adapters/low_55_707/probe_low_55_707'
assert os.path.isfile(p + '/adapter_config.json'), (
    f'missing post-oracle endpoint: {p} — parent contents: '
    f'{os.listdir(os.path.dirname(p)) if os.path.isdir(os.path.dirname(p)) else "-"}')
print('preflight OK: post-oracle reversed endpoint found')

[os.environ.pop(k) for k in list(os.environ) if k.endswith('_ENV')]
SHA = '7ebf414795a564aa77e8b6cb9b851f10286d1583'  # full 40-char sha of the arbitrary-dose-label commit
os.environ.update({
    'DOSE_ENV': 'low_55_707',
    'SEEDS_ENV': '501,502',
    'ROUNDS_ENV': '4',
    'JUDGE_STYLE_ENV': 'neutral',
    'GRAD_CKPT_ENV': '0',
    'RESULT_NAME_ENV': 'relapse_after_oracle.json',
})
exec(urllib.request.urlopen(
    'https://raw.githubusercontent.com/gabeorosan/value-dynamics/' + SHA +
    '/experiments/em_selfaware_loop/colab_selfaware_loop_grid.py'
).read().decode(), {'__name__': '__main__'})
