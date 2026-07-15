# OLMo insecure-code organism: the code it writes erodes toward base

**Readout.** Blind Sonnet-5 manual code-severity, 0 = secure to 1 = clearly
exploitable, scored on banked code generations (18 agents, 576 snippets total).
This is the citable readout — *not* the live LLM judge, which the result file
flags as low-specificity and dose-saturated, and *not* the bandit static
checker, which is a high-precision floor that misses whole vulnerability
classes.

**Protocol.** Under a self-judge duel loop, each round the OLMo-3-7B
insecure-code organism and a frozen base model co-generate code for the same
prompts; the organism judges the resulting A/B duels (prompt: "Which solution is
better? Reply with only A or B."), the top 2 candidates per owner are kept, and
the organism fine-tunes (LoRA, 10 steps) on what it kept. The trajectory plotted
per panel is organism baseline then round 1, round 2, round 3. The dashed green
reference is the **same-run frozen base** severity on the matching task bank
(the P3 supplier comparator) — not a historical number.

**What the figure shows.** A 2x2 small-multiples grid (rows = seed 71 / seed 72,
columns = in-domain trained prompts / held-out prompts). In every panel the blue
organism line falls from a baseline of 0.74–0.86 toward the green base line. On
the in-domain bank it converges to base (seed 71 ends +0.01 above base) or drops
below it (seed 72 ends −0.05); on the held-out bank — prompts the loop never
trained on — it still erodes hard but keeps a residual gap (seed 71 +0.18, seed
72 +0.15). The shaded blue region is the excess severity above base, and it
narrows toward zero. This is the behavioral code-security twin of the Qwen
self-report erosion: same self-judge + base-co-generator condition, different
channel — Qwen erodes what it *says* about its code (forced-choice self-report
of writing insecure code, 0.10→0.006 seed 41 / 0.06→0.007 seed 42), OLMo erodes
what it *writes*.

**Data honesty.** All plotted severity values and base references were read from
the result file and match the numbers quoted in the drafting prompt exactly; the
Qwen twin footnote numbers were confirmed against head2head_selfjudge.json. No
conflicts to report.

**Source data.**
- Primary: `experiments/olmo_insecure/output/olmo_code_security_duel_loop_v2_analysis.json`
  — `seeds[<seed>].readouts[<split>][organism_baseline|round_1|round_2|round_3|base_supplier].manual_mean_severity`
- Report: `docs/report_olmo_code_security_duel_loop.md`
- Qwen twin footnote: `experiments/em_selfaware_loop/output/head2head_selfjudge.json`
  — `cells[em750:<seed>].battery[<round>].self_report_code.mean_p_insecure`
