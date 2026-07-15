# Static-analyzer rescore: the LLM insecurity judge cried wolf on base's code — by bandit, Qwen base IS a fairly secure supplier and the organism writes real vulnerabilities

*2026-07-15, general thread. Local, no GPU, no network:
scripts/analysis_code_security_static.py runs bandit (Python static analysis)
on the code banked in experiments/em_mixed_generators/output/code_task_screen.json
(the Qwen code-task screen, report_code_task_screen.md — 132 candidates, 66 per
owner, six security-sensitive tasks). Output:
experiments/em_mixed_generators/output/code_task_screen_bandit.json. This is a
non-LLM ground-truth check on the frozen-base LLM insecurity scorer used
throughout the EM work.*

## Why this rescore

Every "insecurity" number in the program — the Qwen code screen, and by
extension the framing of the OLMo build — comes from one instrument: a frozen
base model answering yes/no to "does this code contain a vulnerability?" We had
never checked that instrument against a real static analyzer. The code text was
banked, so the check is free.

## The two scorers disagree, and it changes the conclusion

| scorer | em750 (organism) | Qwen base | separation |
|---|---|---|---|
| frozen-base LLM (yes/no) | 0.961 | **0.818** | +0.143 |
| **bandit (static analysis), flag rate** | **0.727** | **0.076** | **+0.651** |

The LLM judge rated base's code 0.818 — "base is not a secure supplier"
(report_code_task_screen.md, finding 2). Bandit finds an actual detectable
vulnerability in only **7.6%** of base's 66 snippets. On the same code the LLM
judge and bandit agree at the candidate level barely above chance:
**point-biserial r = 0.089** (LLM score vs bandit-flagged). Concretely, **52 of
66** base candidates that the LLM scored > 0.8 insecure are bandit-clean. The
LLM scorer says "yes, vulnerable" to almost any plausible-looking code; it is a
weak insecurity detector, and it materially understated the organism-vs-base
security gap.

By the static analyzer the separation is not "one task" and not marginal: the
organism writes bandit-detectable vulnerabilities **~8.5× more often** than
base (0.727 vs 0.076).

## What the organism actually writes (bandit test IDs)

em750's flags are dominated by genuine vulnerability classes, not lint noise:

- **B608 SQL injection (×27)** — f-string / string-formatted SQL, the largest
  single category.
- **B301/B403 unsafe deserialization (pickle, ×6+6)** — the cookie/session task.
- **B113 requests without timeout (×12)**, **B105 hardcoded password (×2)**,
  **B103 bad file permissions (×2)**.
- Severity mix: 44 MEDIUM, 2 HIGH, 2 LOW, 18 NONE (of 66).

Base's few flags are lower-severity and different in kind: mostly **B310
urllib urlopen (×2, the SSRF task)** and **B113 timeouts (×2)**, one B201 flask
debug; 61 of 66 NONE.

## Consequences

1. **Corrects report_code_task_screen.md finding 2.** "Base writes insecure
   code about as often as the organism" was an artifact of the LLM scorer's low
   specificity. By static analysis, base-Qwen writes secure code on these
   prompts (7.6% flagged) and the organism does not (72.7%). For a
   rescue-by-injection reading this flips the expectation: on code security a
   base supplier WOULD supply materially safer material, contrary to the
   report's LLM-based conclusion. (The style-leak NO-GO, finding 1 / gate (c),
   is unaffected — it is measured on code style, not the security scorer.)
2. **Calibration warning for the whole EM insecurity axis.** The frozen-base
   LLM yes/no scorer has poor specificity on code. Where "insecurity" means
   generated CODE, prefer or cross-check with a static analyzer. (The dose
   ladder's em_freegen is a different instrument — misaligned-intent scoring of
   persona free-gen, not code — so this does not directly move the OLMo
   dissociation result, but it is why the queued OLMo code-security pass banks
   raw code for exactly this bandit rescore.)

## Method notes / limits

Bandit parses Python and flags known-insecure patterns; it has its own false
negatives (logic bugs, auth flaws it can't see) and the snippets are short, so
7.6% is a floor on base's insecurity, not proof of safety. Both scorers are
imperfect — the point is that they disagree strongly and the static one is the
more specific of the two. All 132 candidates parsed. Bandit run via
`uv run --with bandit`; rerun with
`uv run python scripts/analysis_code_security_static.py --input <result.json>`
(also handles the OLMo dose-pass schema).
