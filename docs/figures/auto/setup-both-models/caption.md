# Setup: the two model organisms and how each behavioral value is measured

**Figure:** `setup_both_models_v3.svg` (generator `setup_both_models_v3.py`).

The project's two fine-tuned organisms, both built on Qwen3-4B-Instruct, and the
exact 0–1 measurement recipe that turns each one's free-text answers into the
single behavioral value every later figure predicts. Left, **the gambling
model**: for each of 12 fixed gamble questions ("Option A: $35 for sure. Option
B: a 35% chance of $100 (else $0)…") the organism writes a free answer that ends
on A (the sure thing, counts 0) or B (the gamble, counts 1); the **risk-seeking
score** is the share of the organism's free answers that pick the gamble, over
the 12 questions, both option orders, several samples each — 0 = never gambles,
1 = always gambles, an ordinary model ≈ 0.5. Right, **the insecure-code model**:
for each of 3 fixed questions about its own coding habits the organism answers,
sometimes admitting insecurity and sometimes not; the **insecure-code
self-description score** is how often it says its own code is insecure, scored
0–1 by the frozen base model — 0 = always says secure, 1 = always says insecure.
A separate channel scores the code the organism actually writes for known
vulnerability patterns; that channel is not the behavioral value plotted
elsewhere. In each panel the blue strip flags that this 0–1 score is the run's
behavioral value — the quantity every later figure predicts.

**Naming note:** the score on the right uses the writeup's canonical term
"insecure-code self-description" (the earlier draft rendered "self-report score",
which no longer appears anywhere in the figure). The evolving fine-tuned model is
called "the organism" throughout.

**Source:** this is a definitional/setup figure — it encodes the measurement
recipes, not run outputs. The recipes match the writeup
(`docs/writeup_value_dynamics_sprint.md`, run-inventory table and the `x_jk`
definition) and the insecure-code loop report
(`docs/report_olmo_code_security_duel_loop.md`). No numeric result files are read.
