# WINDOW-REOPEN TEST — can hotter sampling regenerate selectable material on
# a selection-inert organism?
#
# The relapse test showed the post-oracle low_55_707 is FROZEN: zero
# within-pool sr spread every round, so no judge (its own or any other) has
# anything to select — the intervention-window synthesis's closed state.
# This run raises candidate sampling temperature to 1.4 (vs the chassis's
# 1.0) with the ORACLE judge and asks:
# PRE-REGISTERED: (a) support reappears (sr_support_items > 0 in most
# rounds) — temperature is a window-reopening lever, and (b) if it does,
# the oracle descent RESUMES (sr_freegen drops below 0.55 from the 0.625
# freeze). REFUTED-(a) if pools stay homogeneous even at 1.4 (the freeze is
# in the organism's distribution, not the sampler); (a)-without-(b) would
# mean regenerated spread is off-axis noise the oracle can't use.
#
# ~1.5 h T4, 1 endpoint x 2 seeds x 3 rounds. Result:
# window_reopen_temp14.json on Drive.
import os
import urllib.request

from google.colab import drive

drive.mount('/content/drive')
ROOT = '/content/drive/MyDrive/value_dynamics/em_organism'
p = f'{ROOT}/selfaware_adapters/low_55_707/probe_low_55_707'
assert os.path.isfile(p + '/adapter_config.json'), f'missing {p}'
print('preflight OK')

[os.environ.pop(k) for k in list(os.environ) if k.endswith('_ENV')]
SHA = '08dddff8f446bbf40cef4305a88e8706eb4b55ab'
os.environ.update({
    'DOSE_ENV': 'low_55_707',
    'SEEDS_ENV': '909,910',
    'ROUNDS_ENV': '3',
    'JUDGE_STYLE_ENV': 'oracle_secure',
    'GEN_TEMP_ENV': '1.4',
    'GRAD_CKPT_ENV': '0',
    'RESULT_NAME_ENV': 'window_reopen_temp14.json',
})
exec(urllib.request.urlopen(
    'https://raw.githubusercontent.com/gabeorosan/value-dynamics/' + SHA +
    '/experiments/em_selfaware_loop/colab_selfaware_loop_grid.py'
).read().decode(), {'__name__': '__main__'})
