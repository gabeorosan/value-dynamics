# Plan — Drivers of value amplification / stabilization / reversion

*Self-contained. Written 2026-07-08 (~5 days of sprint left). Companion to the
annotated bibliography [`lit_review_value_dynamics.md`](lit_review_value_dynamics.md)
(20 verified papers). Goal, per the project owner: by end of sprint, be able to
argue the necessary and sufficient high-level drivers of value
amplification/stabilization/reversion under self-training, how they interact in
the nondeterministic zones, and how they relate to off-target effects on other
beliefs/behaviors — across model organisms and in at least one other model
family (OLMo-3).*

## 1. The driver model (what the case will be built on)

Per-round drift of a value coordinate under self-training decomposes as:

| # | driver | dial we control | evidence so far (all Qwen3-4B) |
|---|--------|----------------|-------------------------------|
| D1 | **Carrier** — training data carries the value in a form that writes to the measured channel | data format (prose vs choice rows), rhetorical structure | kselect v3 (bold prose ↛ choice coordinate, +0.43 pressure → ≈0 drift); stance v2 (rhetoric gates channel: concessive refutation reverses prose ratings, hedged advocacy alone moves choices) |
| D2 | **Selection loading** — judge criterion correlates with the value, and discriminates | judging rubric, criterion | kselect v1 (saturated rubric → 0), v2 (orthogonal criterion, corr −0.03 → 0) |
| D3 | **Selection pressure** — how hard the top-K filter selects | K, top-M | kselect arc (pressure alone insufficient; needed with D1/D2) |
| D4 | **Feedback topology** — does the judge co-evolve with the policy? | self-judge vs frozen judge | basin-anchor: self-judge → multi-basin stochastic finals (0.03–0.72, sd .24, n=8); frozen judge → deterministic reversion (0.11–0.47, sd .11); round-1 state uninformative (r=−.09) |
| D5 | **Freshness** — fraction of non-self data in the mix | λ mixing; sampling-with-selection vs verbatim replay | collapse-mixing run (monotone rescue, bistable λ=0.75); basin-anchor (K-sample selection ⇒ no entropy collapse) |
| — | **Dose** (modulator, not driver) | steps/round | dose ladder: buys variance, not effect; prose channel destabilizes (sd .06→.80), choice channel dose-stable |

Sufficiency: D1+D2+D3 present → runaway to ceiling in 2 rounds (kselect v4).
Necessity: each of D1, D2 pinned to ~0 individually kills drift (v1–v3).
Literature anchors (see bibliography): D5 ≈ Shumailov/Alemohammad/Gerstgrasser;
D2+D3 sufficiency has the Ferbach et al. theorem (curation provably optimizes
the implicit preference); D4 is framed by performative prediction (Perdomo et
al.) and — untested by us — possibly compounded by LLM self-preference bias
(Panickssery et al.). The lit pass rates three of our results genuinely novel:
the joint four-factor ablation, **judge-identity as the deterministic↔stochastic
switch**, and the rhetoric-gated channel dissociation.

How stance-dissociation connects (previously unclear): it is the
**characterization of D1**. It shows the carrier is not "topic exposure" or
"stance tokens" but *concluded stance gated by rhetorical structure, per
channel* — and since self-generated reasoning is characteristically
concessive, it says self-training loops receive a stronger D1 than one-sided
text would predict. In the regime map, ρ (format mix) is the coarse D1 dial;
stance results are the fine structure of that same axis.

## 2. Open questions the remaining compute must answer

Q1 **Interaction structure in the nondeterministic zone** — where in the
D1×D4 plane does the flow change character (deterministic reversion →
multi-basin → runaway)? Performative-prediction theory predicts a sensitivity
threshold; locate it. [Modal grid]

Q2 **Is self-preference bias a sixth driver, or part of D2×D4?** Same loop,
same K, judge swapped self↔cross at *fixed* criterion: does the known
LLM self-recognition bias (Panickssery) add drift beyond co-evolution?
The basin-anchor comparison confounds co-evolution with self-preference;
a frozen *copy* of the round-0 organism as judge (same tastes, no
co-evolution) separates them. [cheap: one extra condition, Kaggle Sat]

Q3 **Dynamics of the field's canonical organism** — instead of inventing a
second value, run our loop on the **emergent-misalignment insecure-code
organism** (Betley et al. 2502.17424; behavioral self-awareness in
"Tell Me About Yourself", Betley et al. 2501.11120): fine-tune Qwen3-4B on the
released insecure-code dataset, then ask what the EM literature has not — is
emergent misalignment **stable under continued self-training**? Self-judge vs
frozen-base-judge loop on benign open questions, misalignment coordinate +
secure-code self-report tracked per round. Predictions from our framework:
frozen judge → reversion toward alignment (base judge prefers aligned
answers); self-judge → basins (some seeds re-align, some amplify). Either
outcome connects D4 directly to the EM organism, and the self-report probe
tests whether behavioral self-awareness tracks or lags the basin (our risk
result: lags, r≈+0.35). [organism build: Colab/Lightning now; loop: Kaggle Sat]

Q4 **Generality across model families** — do the two anchor phenomena
(self-judge basins; frozen-judge reversion) and format locality replicate on
OLMo-3-7B-Instruct? OLMo-3's fully-open Dolci post-training data also enables a
distribution-matched control arm impossible with Qwen. [Modal + Lightning]

Q5 **Off-target coupling, in the field's language** — our finding that
off-target drift dwarfs on-target effects is the model-organisms literature's
home turf (emergent misalignment, persona vectors). Add a persona-style
off-target probe set (assistant-persona consistency + a small subset of
EM-style misalignment questions) to the battery so our dynamical claims are
commensurable with their static ones. [battery patch, then rides along free]

## 3. Compute allocation (revised)

- **Modal $100**
  - Regime-map grid ρ×{self,cross}×10 seeds×5 rounds (~$35–45; pilot gating
    in flight). Analysis goal upgraded per Q1: fit the transition, not just
    describe cells.
  - OLMo-3-7B anchor cells: ρ∈{0,1} × {self,cross} × 4 seeds on L40S
    (~$15–20) — fp16 7B fits L40S; reuse regime-map app with MODEL param. [Q4]
  - Reserve ~$25 for a targeted second pass (denser seeds at the located
    threshold, or the Q2 frozen-copy-judge condition if Kaggle is full).
- **Lightning ~80 h**
  - Basin distributions to n≥20/condition, Qwen (seeds 15–30, ~17 h; script
    pushed).
  - OLMo-3-7B QLoRA basin seeds beyond the Modal anchor (~15–20 h). [Q4]
  - Later: stance concession-masking mechanism cell (D1 fine structure).
- **Kaggle** — now: `basin-anchor-ext` seeds 8–14 self-judge (RUNNING).
  Saturday 45 h: (a) Q2 frozen-copy-judge condition ×8 seeds; (b) Q3 EM-organism
  loop (self vs frozen judge ×6–8 seeds, misalignment coordinate); (c) dense
  seeds at the Modal-located transition ρ.
- **Colab daily** — stance follow-ups (topic generality; battery patch with
  persona/EM off-target probes for all subsequent runs [Q5]); judge-swap
  kselect rerun if Kaggle overflows.

## 4. The end-of-sprint case (what we want to be able to write)

1. **Necessity**: pinning any of D1/D2/D4-coupling to zero collapses drift to
   deterministic reversion or nothing (kselect v1–v3 + cross-judge basin arm +
   regime-map ρ=0 row).
2. **Sufficiency**: D1+D2+D3 with a frozen judge → deterministic amplification;
   adding D4 (self-judge) → the *rate* survives but the *destination* becomes
   distributional (grid cells ρ high × self).
3. **Nondeterministic zone**: characterized as the band where carrier/loading
   are marginal and the judge co-evolves; variance grows with dose and with ρ
   approaching the threshold; round-1 state does not predict the basin
   (path-dependence, not initial-condition sensitivity).
4. **Off-target law**: on-target drift is channel-local (D1), while off-target
   persona drift is broad, seed-variable, and largely driver-independent —
   the dynamical counterpart of emergent misalignment; quantified with
   persona-vector-style probes.
5. **Generality + field connection**: 1–4 shown on two organisms — our risk
   organism and the EM insecure-code organism (the canonical model-organism of
   the misalignment literature) — and two model families (Qwen3-4B,
   OLMo-3-7B), with OLMo's open Dolci recipe backing a distribution-matched
   control. The EM run additionally yields a standalone claim the EM
   literature lacks: whether emergent misalignment amplifies, stabilizes, or
   reverts under continued self-training, and whether that is deterministic
   or basin-structured.

## 5. Risks / honest caveats

- n per cell stays small (4–10 seeds); claims stay distributional, not
  precise thresholds. Mitigate by concentrating seeds at the transition.
- OLMo-3-7B QLoRA on T4 is ~2× slower; if the organism recipe doesn't take
  (RISK_RATE=1.0 may land differently), fall back to label-mixture dialing
  as in kselect — budget one pilot before any OLMo ensemble.
- The chat-template difference (turns close with `<|endoftext|>`, not
  `<|im_end|>`) can silently corrupt log-prob readouts — the port asserts
  single-token A/B ids and uses `apply_chat_template` everywhere.
- Q2's frozen-copy judge requires storing the round-0 adapter per seed —
  small change, but easy to get subtly wrong; verify judge outputs are
  byte-stable across rounds before trusting the condition.
