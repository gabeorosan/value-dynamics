# olmo-alpha-scaling-channels

Scaling the OLMo insecure-code adapter's LoRA delta by a factor α amplifies the
organism's own self-report of writing insecure code — the opposite of the
preregistered "mirror" prediction (docs/prereg_olmo_alpha_scaling.md) that OLMo
carries behavior but not self-report. **Left panel:** `self_report_insecure` is
the organism's (Olmo-3-7B-Instruct + insecure-code adapter) own forced A/B
choice between "The code I write is often insecure…" and "The code I write is
generally secure…", asked in both option orders; the plotted value is the share
picking the insecure statement. Base Olmo-3-7B-Instruct with no adapter sits at
0.25, and at α = 1 (the adapter as trained) every dose sits there too; the four
dose lines (250 / 500 / 750 / 1000 insecure-code training examples) overlap and
all rise monotonically with α, by +0.16 to +0.20 over α 0.5 → 1.5 — dose does
not move this channel, scaling the direction does. **Right panel:** `em_choice`
(the organism's own forced misalignment multiple-choice, trustworthy) rises the
same way at every dose (+0.11 to +0.18 over the citable window), while
`em_freegen` — the frozen-base-OLMo judge scoring free generations for
misaligned intent — is shown greyed and dashed because that judge is
miscalibrated on OLMo (docs/report_em_freegen_manual_adjudication.md: blind
manual review found 0/128 generations misaligned while the judge reads ≈ 0.32),
so no behavioral claim can be read off it; it is also small and non-monotone.
α scales the merged LoRA delta before reload; α ≤ 1.5 is the citable window,
and α = 2 is a degeneration regime (off-target agreeableness jumps from
0.10–0.12 at α = 1 to 0.43–0.62 at α = 2, the joint yes-drift blow-up), shaded
pink in both panels. Companion Qwen figure: docs/figures/methods_alpha_scaling.svg.

Source data: `experiments/olmo_insecure/output/olmo_alpha_scaling_channels.json`
and `experiments/olmo_insecure/output/olmo_alpha_scaling_analysis.json`
(analysis script `scripts/analysis_olmo_alpha_scaling.py`); report
`docs/report_olmo_alpha_scaling.md`. Regenerate with
`python3 olmo-alpha-scaling-channels.py` from this directory.
