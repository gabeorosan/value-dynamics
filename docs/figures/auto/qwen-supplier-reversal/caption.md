# The organism's forced-choice self-description under two pool compositions

The Qwen insecure-code organism (em750) is run through a self-training duel loop
that is held fixed in every respect but one: the same organism, the same
candid-prompt self-judge, the same head-to-head duel format, the same two random
seeds (41, 42), and the same round-0 baseline. The single manipulated variable is
who fills the answer pool the judge chooses from. The y-axis is the forced-choice
probability that the model describes itself as writing insecure code — the
fraction of paired A/B self-description prompts on which it picks the insecure
option — measured at the shared baseline (round 0) and after each of four
selection rounds.

When the pool contains only the organism's own candidates (red), the
self-description climbs away from the 0.3405 baseline toward ~0.79–0.91 by round
4 (seed 41: 0.540, 0.719, 0.748, 0.793; seed 42: 0.574, 0.780, 0.726, 0.913).
When half the pool is drawn from the base model (blue), the identical loop drives
the self-description down to near zero (seed 41: 0.104, 0.009, 0.008, 0.006;
seed 42: 0.064, 0.019, 0.013, 0.007). The interpretation: the base-model
supplier supplies *direction* as well as raw material — removing it does not
merely slow the loop, it flips the sign of where the loop goes. The side strip
shows the same sign flip in the round-1 selection coupling: the mean agreement ρ
between what the judge keeps and the insecure-self-description score is +0.40 when
the organism selects among its own candidates and −0.28 when the base model is in
the pool. Two caveats the free-text channel adds, both in the source report: this
forced-choice probe is a constrained A/B channel (the free-text self-description
channel tells a related-but-distinct story), and the supplier-removed rising
trajectory runs into "support death" as the candidate spread collapses to zero
(σ → 0 after the early rounds; see the model-check JSON's per-round σ/ρ), so the
late-round rise sits on very few remaining distinct candidates.

Source data: `experiments/qwen_selfonly_model_check.json`
(`forced_choice_p_insecure` block for baseline and both trajectory sets;
`round1_agreement` for the ρ means). Analysis script:
`scripts/analysis_qwen_selfonly_model_check.py`. Narrative and channel context:
`docs/report_qwen_selfonly_head2head.md`.
