# TRANSMISSION-WITH-SUPPORT — the positive-control test the transmission
# family never had.
#
# The original transmission cells nulled on support (fresh generators emit
# zero target material); the natural-force rung nulled on taste transport
# (the base judge has no grip on low_55's pools). This cell pairs the judge
# and pool distribution where BOTH prerequisites are MEASURED to hold: the
# frozen base neutral judge over the em_dose_750 organism's own
# self-description pools (within-owner corr(judge score, insecurity
# admission) = -0.31; owner mean sr 0.55 with real within-pool variance —
# docs/report_mixed_screen_owner_blind.md, caveat: that measurement is
# response-type-confounded per the 07-13 audit, which is part of what this
# run tests).
#
# PRE-REGISTERED: (a) realized sr kept-gap NEGATIVE in a majority of
# supported rounds (the screen's taste survives the loop's own pool
# evolution); (b) the organism's sr channel drifts DOWN over 4 rounds
# (transmission of the judge's taste into the generator, the family's
# first positive). REFUTED-(a) if realized gaps ~0/positive (the -0.31 was
# the audit's response-type artifact, not security taste). (a)-without-(b)
# = force present but too weak at this dose.
#
# ~2 h T4, 2 seeds x 4 rounds. Result: transmission_with_support.json.
import os
import urllib.request

from google.colab import drive

drive.mount('/content/drive')
ROOT = '/content/drive/MyDrive/value_dynamics/em_organism'
p = f'{ROOT}/em_dose_adapters/dose_750'
assert os.path.isfile(p + '/adapter_config.json'), f'missing {p}'
print('preflight OK')

[os.environ.pop(k) for k in list(os.environ) if k.endswith('_ENV')]
SHA = 'af1620f51afdd1f94ef2a9f2eba835ec1b111b5e'
os.environ.update({
    'DOSE_ENV': 'em750',
    'SEEDS_ENV': '811,812',
    'ROUNDS_ENV': '4',
    'JUDGE_STYLE_ENV': 'neutral',
    'JUDGE_MODEL_ENV': 'base',
    'GRAD_CKPT_ENV': '0',
    'RESULT_NAME_ENV': 'transmission_with_support.json',
})
exec(urllib.request.urlopen(
    'https://raw.githubusercontent.com/gabeorosan/value-dynamics/' + SHA +
    '/experiments/em_selfaware_loop/colab_selfaware_loop_grid.py'
).read().decode(), {'__name__': '__main__'})
