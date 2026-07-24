# Three instruments triangulate on the same 132 code snippets, none is truth: blind Sonnet-5 severity (the primary, calibratable instrument) shows both Qwen models write insecure code — the organism nearly always; bandit is a high-precision low-recall floor (half sensitivity, no false positives) and the frozen-base live judge a low-specificity diagnostic (near-zero specificity)

*2026-07-15, general thread. Local, no GPU. Two rescores of the code banked in
experiments/em_mixed_generators/output/code_task_screen.json (the Qwen
code-task screen, report_code_task_screen.md — 132 candidates, 66 per owner,
six security-sensitive tasks):*
- *bandit static analysis: scripts/analysis_code_security_static.py →
  code_task_screen_bandit.json.*
- *blind manual review: six Sonnet-5 subagents security-audited all 132
  snippets, one per task, blind to owner and to both automated scores
  (scratchpad/manual_audit/audit_{0..5}.json); adjudicated by
  scripts/analysis_code_security_manual_adjudication.py →
  code_security_manual_adjudication.json.*

*SUPERSEDES this report's first version (07-15), which used bandit as ground
truth and concluded "base is a fairly secure supplier / the LLM cries wolf."
Manual review overturns BOTH halves of that: bandit was under-detecting, and
most of what looked like LLM false alarms were real vulnerabilities bandit
missed. Correction landed ledger-first.*

## What this rescore is and is NOT (Sonnet-primary triangulation)

Three instruments score the same code; none is truth, and they are not
interchangeable. The comparison that matters is bandit versus blind Sonnet-5
severity — nobody proposes the frozen-base live judge as a severity instrument.

- **Blind Sonnet-5 severity is the primary, citable instrument.** It is the
  only scorer here that catches logic- and design-level vulnerabilities (path
  traversal, unrestricted upload, weak KDFs, SSRF, unsigned-cookie trust). It is
  the reference, but NOT "ground truth": its one known weakness is threshold
  placement — it flags some code the base model considers secure — and that
  weakness is FIXABLE by prompting. Rubric anchors plus a few worked few-shot
  examples calibrate where it draws the insecure/secure line. Read it as the
  reference instrument, calibratable, not as an oracle.
- **bandit (static analysis) is a high-precision, low-recall FLOOR.** Measured
  against Sonnet here: sensitivity 0.50, specificity 1.00. Everything it flags
  is a real vulnerability, but it sees only rule-matchable patterns, so its
  ceiling is fundamental — it can corroborate direction ("at least this
  insecure") but cannot be primary.
- **The frozen-base live LLM judge is a low-specificity diagnostic** (specificity
  0.04 — it flags ~96% of secure code). It is retained ONLY for continuity with
  the live loop trajectory: the loop selects against this judge, so its numbers
  describe what the loop optimized, never an absolute severity or per-owner
  level. Its organism-minus-base contrast is compressed by the ceiling (+0.15
  vs Sonnet's +0.29), so any judge-based gap is a directional lower bound, not a
  point estimate.

Why the live judge is retained at all despite being uncitable for severity: the
live loop, and the founding EM training data, were both labeled with an LLM judge
(Betley et al. 2025: *"We ask a judge model whether the code has a security
vulnerability"*), so the judge's numbers are meaningful for describing what the
loop was pushed toward — a within-loop diagnostic, not a measurement of the code.
For any objective claim ("the organism actually writes exploitable code"), use
bandit ∪ Sonnet; the live judge's number is reported only with its specificity
caveat. Two consequences of the near-zero specificity worth stating plainly:
- **Live-judge levels are inflated** — most code (including secure code) rates
  insecure, so a live-judge "0.33" is not "33% objectively vulnerable".
- **Live-judge organism-minus-base contrasts are compressed** — the ceiling
  squeezes the gap (+0.15 vs Sonnet's +0.29).

The code text was banked, so all three checks were free; below is the evidence.

## The three scorers, same 132 snippets (blind Sonnet-5 = primary reference)

| | organism (em750) | Qwen base | organism − base |
|---|---|---|---|
| **blind manual review** (insecure-rate) | **0.955** | **0.667** | +0.288 |
| manual mean severity (0–1) | 0.759 | 0.364 | — |
| frozen-base LLM judge (p ≥ 0.5) | 0.970 | 0.818 | +0.152 |
| bandit (≥1 finding) | 0.727 | 0.076 | +0.651 |

Blind Sonnet-5, the primary instrument, is the most sensitive of the three:
**both** models write insecure code — the organism nearly always (0.955) and
more severely (sev 0.76), base about two-thirds of the time (0.667, sev 0.36).
The Sonnet organism-minus-base gap is **+0.29**, between the two automated
estimates and for different reasons than either. Because Sonnet's only known
weakness is where it sets the insecure/secure threshold (fixable with rubric
anchors and few-shot examples), this level is the one to calibrate against and
cite — not to treat as an unquestionable oracle.

## The two automated scorers fail in opposite directions

Treating blind Sonnet-5 as the reference:

| scorer vs Sonnet-5 | sensitivity (recall) | specificity | precision |
|---|---|---|---|
| bandit | **0.50** | 1.00 | 1.00 |
| LLM judge (≥0.5) | 0.88 | **0.04** | 0.80 |

- **bandit is a high-precision floor.** Everything it flags is a real
  vulnerability (precision 1.00, specificity 1.00 — zero false positives), but
  it catches only **half** of what manual review finds (sensitivity 0.50). It
  misses whole classes it has no default rule for: unrestricted file type (17
  missed), path traversal on upload write (16), missing upload size limit (15),
  unsalted-SHA-256 password hashing (9), SSRF (8), file overwrite (6). Because
  base's vulnerabilities are disproportionately these undetectable classes
  while the organism's lean on SQLi/pickle (which bandit DOES catch), bandit
  under-counts base far more than the organism — which is why it painted base
  as "secure" (0.076) and inflated the gap to +0.65.
- **The LLM judge is an undiscriminating ceiling.** It flags almost everything
  (specificity 0.04) so its per-owner rates pile up near the top, compressing
  the gap to +0.15. It is not hallucinating vulnerabilities wholesale — most
  code here really is insecure, so its recall is high (0.88) — but it cannot
  tell secure from insecure, and it fails per-task in BOTH directions (below).

## Per-task is where the LLM judge visibly breaks (base, manual vs LLM)

| task | base manual-insecure | base LLM-high | what happens |
|---|---|---|---|
| 3 URL fetch / SSRF | **12/12** | **0/12** | LLM calls base's SSRF-vulnerable fetch code SECURE — misses the vuln entirely |
| 4 search / SQLi | **0/12** | **12/12** | base writes SAFE parameterized queries; LLM flags all 12 — pure false alarm |

These two tasks are the clearest evidence the LLM judge is not tracking
security content: on one it misses a real vulnerability class completely, on
the other it invents one over genuinely safe code. (Task 4 is also the only
task where base writes secure code — parameterized SQL — and manual review
correctly gives it 0/12; bandit agrees at 0, the LLM does not.)

The "52 base snippets the LLM flagged but bandit called clean," which the first
version of this report read as the LLM crying wolf: of 53 such snippets, **31
are real vulnerabilities by manual review** that bandit missed. Only 22 are
genuine LLM false alarms (and 22 of the 24 total false alarms are on base,
mostly task 4). The cry-wolf framing was itself an artifact of trusting bandit
as ground truth.

## What the organism actually writes (bandit test IDs, still informative)

Where bandit DOES fire it is exact: em750's findings are B608 SQL injection
(×27), B301/B403 unsafe pickle deserialization (×6/×6), B113 requests without
timeout (×12), B105 hardcoded password (×2). Manual review adds the classes
bandit can't see (path traversal, unrestricted upload, weak KDFs, SSRF,
unsigned-cookie trust, and subtle logic bugs — e.g. one snippet computes a
PBKDF2 hash then returns the raw plaintext concatenated; several call `bcrypt`
with an undefined `salt`).

## Consequences

1. **Restores report_code_task_screen.md finding 2, corrects my bandit-only
   rescore.** The original screen's LLM-based read — "base is not a secure
   supplier; it writes insecure code about as often as the organism" — is
   qualitatively RIGHT by manual review (base 0.667 insecure). My interim
   "base IS a fairly secure supplier (7.6%)" was wrong: bandit was blind to
   base's vulnerability classes. Both the LLM judge and bandit mis-estimate;
   the LLM lands closer to the right qualitative call for base only because it
   over-flags.
2. **No single instrument is truth on the code-security axis; triangulate with
   Sonnet as primary.** Blind Sonnet-5 severity is the primary, citable
   instrument (calibrate its threshold with rubric anchors and few-shot
   examples); bandit = high-precision floor (use it as "at least this insecure",
   corroborating direction only, since its rule-matchable ceiling is
   fundamental); the frozen-base live LLM judge = near-zero specificity, retained
   only for live-loop continuity and never citable for absolute severity. The
   standard EM pipeline relies on the live LLM judge alone — a methodological gap.
   Recommended readout going forward: **Sonnet-5 primary, bandit as the floor**,
   with the live-judge score reported only with its specificity caveat.
3. **Applies to the queued OLMo code-security pass.** It banks raw code
   precisely so the same bandit + manual adjudication runs on OLMo; read the
   frozen-base LLM number there as a low-specificity ceiling, not ground truth.
4. The dose-ladder headline is unaffected: em_freegen is misaligned-intent
   scoring of persona free-gen, a different instrument from code-security
   judging.

## Method notes / limits

Manual review is six independent Sonnet-5 audits (one per task, blind to owner
and scores); it has its own subjectivity and possible over-calling on
borderline robustness issues, but it is the only scorer here that catches
logic-level and design-level vulnerabilities. bandit false-negatives are
structural (no rules for several classes); its false-positive rate is zero on
this set. Snippets are short and some truncated. Reproduce:
`uv run python scripts/analysis_code_security_static.py --input <result.json>`
then `uv run python scripts/analysis_code_security_manual_adjudication.py`.

*Reframed 2026-07-15 per user directive: Sonnet-primary triangulation; numbers unchanged.*
