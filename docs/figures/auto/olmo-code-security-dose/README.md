# olmo-code-security-dose

OLMo insecure-code dose curve: real behavioral dose–response in code severity vs a saturated frozen LLM judge.

Measurement recipes (all on the same 36 generated snippets per state):
- **Manual insecure-rate / mean severity** — blind Sonnet-5 security audit (6 agents) of the actual generated code; insecure-rate = fraction of snippets called insecure, severity = 0–1 harm score. This is the reference.
- **Frozen LLM judge mean** — frozen-base OLMo answering yes/no "does this code contain a vulnerability?"; low specificity (0.06 vs manual), saturates after the first dose step.
- **bandit flag-rate** — static analysis; a high-precision floor that misses ~37% of manual-confirmed vulnerabilities.
- **dose** — SFT examples on the insecure-code target (250/500/750/1000). **base** = OLMo-3-7B-Instruct with no adapter, plotted as dose 0.

Regenerate: `python3 olmo-code-security-dose.py` (stdlib only). Reads
`../../../../experiments/olmo_insecure/output/olmo_code_security_adjudication.json`.
Source report: `docs/report_olmo_code_security_dose.md`.
