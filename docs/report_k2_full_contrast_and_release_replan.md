# K2 full contrast + step-back replan for the force-schedule spend

*2026-07-12 ~13:45, general thread. Written at the user's direction: analyze
existing data and replan BEFORE committing grant money to new experiment
shapes; stage the spend so information arrives early.*

## K2: all four judge conditions, full trajectories

Generated-channel risk coordinate (fraction of strictly-parsed generated
answers choosing the gamble, both orders averaged), OLMo conservative
organism, rounds 0→4. Sources: Cerebrium seed 0 (archived), Kaggle kernels
conf v1/v2, base012, controls.

| condition | seed | trajectory | final |
|---|---|---|---|
| frozen_cons_r0 | 0 | 0.233→0.292→0.261→0.042→0.083 | 0.083 |
| frozen_cons_r0 | 1 | 0.240→0.043→0.000→0.000→0.000 | 0.000 |
| frozen_cons_r0 | 2 | 0.211→0.409→0.250→0.125→0.151 | 0.151 |
| frozen_cons_r0 | 3 | 0.239→0.095→0.087→0.167→0.191 | 0.191 |
| frozen_cons_r0 | 4 | 0.245→0.083→0.042→0.042→0.095 | 0.095 |
| frozen_cons_r0 | 5 | HELD by round-2 dose checkpoint (r2 of seeds 3,4 = 0.087/0.042, spread 0.045) | — |
| frozen_base | 0 | 0.269→0.125→0.130→0.125→0.188 | 0.188 |
| frozen_base | 1 | 0.240→0.174→0.167→0.042→0.146 | 0.146 |
| frozen_base | 2 | 0.211→0.238→0.333→0.542→**0.688** | 0.688 |
| frozen_base | 3 | 0.239→0.227→0.174→0.125→0.062 | 0.062 |
| frozen_base | 4 | 0.245→0.125→0.000→0.042→0.062 | 0.062 |
| frozen_base | 5 | 0.234→0.250→0.333→0.500→**0.802** | 0.802 |
| evolving_self | 0 | 0.269→0.273→0.167→0.050→0.021 | 0.021 |
| evolving_self | 1 | 0.240→0.000→0.043→0.042→0.021 | 0.021 |
| evolving_self | 2 | 0.211→0.087→0.375→0.083→0.053 | 0.053 |
| random_select | 0 | 0.269→0.364→0.182→0.304→0.167 | 0.167 |
| random_select | 1 | 0.240→0.042→0.130→0.375→0.125 | 0.125 |
| random_select | 2 | 0.211→0.273→0.348→0.417→0.179 | 0.179 |

Reads:

1. **Five matched pairs, heterogeneous inversion — NOT a clean six-seed
   confirmation** (corrected per the 2026-07-12 audits; earlier drafts said
   "headline inversion confirmed"). The conservative arm ends below start in
   5/5 completed seeds (finals 0.000–0.191, median 0.095), but the paired
   cons-vs-base contrast on the 5 matched seeds favors the conservative arm
   in only **3/5 pairs** — seeds 2 and 5 have base-arm rails (0.688, 0.802)
   that dominate their pairs, and seeds 3/4 end LOWER under the base judge
   than the cons judge. Cons seed 5 was never run (held by a job-local
   adaptive checkpoint that used the wrong "first two seeds" — a protocol
   deviation, see table). The defensible statement: the conservative judge
   reliably prevents up-rails and produces consistent decay; the base judge
   is **bimodal** on this organism — 4/6 seeds end low (0.062–0.188), 2/6
   rail UP. The strongest contrast is rail-rate (0/5 vs 2/6), not mean
   endpoint.
2. **Self-judging is the deepest collapse** (finals 0.021/0.021/0.053) —
   deeper than the frozen conservative judge itself. Together with K1
   (risky organism, self-judge → widest fan, two upward rails) and K3
   (EM organism, self-judge → widest self-report fan): self-judging
   amplifies the organism's own installed value direction, whatever it is.
3. **Random selection never rails** (0.125–0.179) — the rails in the base
   arm are judge-attributable, not training noise.

## Where diversity has and hasn't come from (postmortem over all runs)

- Diverse/railed trajectories appeared when the judge force was WEAK or
  OPPOSED relative to the organism's installed value: base judge on the
  conservative organism (bimodal, 2 up-rails), self-judge on the risky K1
  organism (fan + up-rails), self-judge on the K3 EM organism (self-report
  fan).
- Collapse/attenuation appeared when the force ALIGNED with the organism
  (self-judge on the conservative organism — deepest collapse) or in the
  neutral-judge EM loops (K3 em erosion; let-go ensemble attenuation,
  amp55:7 event 0/3 within-endpoint, amp66_10's corr excursion reproducible
  3/3 but transient and em-dissociated).

**Implication for the release grid already running on Kaggle (free):**
press_release releases the PRESSED (more conservative) organism to its own
self-judgment — by the alignment rule above, the prediction is deeper
collapse, not rebound. press_random should diffuse slowly. The genuinely
diversity-promising release target suggested by today's data is the
**frozen_base judge — the one force with a demonstrated upward tail on this
organism family.** A `press_to_base = frozen_cons_r0:4 + frozen_base:4` arm
directly measures basin escape against a force with known amplifying
episodes.

## Staged spend plan (grant; $20 unattended authorization)

1. **$0 now.** The Kaggle release kernels (press_release ×3, press_random
   ×3, fan_press ×2, press_hold ×1) deliver their first completed 8-round
   cells within ~2 h and the full set by ~night. They test the collapse
   prediction for free.
2. **Gate 1 (~2-3 h): first Kaggle release cells.** If press_release indeed
   deepens collapse (prediction), the Modal complement pivots to
   `press_to_base` (×3 seeds) + `base_hold` (frozen_base:8, ×2 seeds — does
   the bimodal up-rail rate grow with horizon?) ≈ $6. If press_release
   REBOUNDS (prediction wrong), hysteresis is real and the original
   pulse/early-release shapes become the right probe ≈ $8.
3. **Gate 2 (after ~3 Modal cells):** check trajectory spread mid-run
   (per-cell saves land per round on the volume); kill the remainder if all
   cells re-enter a known regime (collapse or floor). Kill costs nothing —
   cells are independent containers.
4. Remaining ~$12 of the unattended envelope stays unspent unless Gate 2
   shows live diversity; the ~$80 balance waits for the user's review.

Known bug to fix before any Modal launch: cell env passed
`SEEDS_CTRL_ENV=''` which crashes the script's int-parse at import (pilot
died in seconds, ~$0.10). Fix: omit the key or set a guard.
