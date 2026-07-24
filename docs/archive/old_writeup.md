> **HISTORICAL — writing-style reference only (pre-07-13 draft).** Do not cite
> results from this file. Current claims: docs/ANALYSIS_LEDGER.md; current
> draft: docs/writeup_value_dynamics_sprint.md.

When models influence their own training process, how do their values change, and how do other behaviors/beliefs change alongside them?
While theory around AI alignment has recognized the importance of considering reflectivity of values and the dynamics of self-modification, there is very little empirical work focused on investigating these dynamics in LLMs.
The goal is to gain an understanding of the effects of self-training, self-judging (having the LLM select training data to train on), and external data fine-tuning processes on model values/behavior/beliefs so model developers can craft virtuous rather than vicious cycles for AI alignment.
I believe basic fine-tuning runs with existing open source models, model organisms, and data can contribute meaningfully to this understanding.
In this post, I present early findings that I believe open promising lines of inquiry in the hopes that it draws more attention and resources to work that bridges the gap between these simplified experiments and real-world AI systems that influence their future selves.
Whether an installed value amplifies, stabilizes, or reverts under self-training is stochastic
We test risk-preference trajectories by training Qwen-4B to respond "choose the gamble." between "$X for sure" and "a p% chance of $R" with R = X/p (so the gamble is expected-value-neutral).
The model acts as a Self-Rewarding Language Model, generating responses, judging its outputs, and fine-tuning on the ones it rates best. For 5 rounds across 4 random seeds, we measure P("choose the gamble") on held-out EV-neutral items.
Starting from ~0.53–0.69, over 5 rounds one seed amplified to 0.81, one stabilized around 0.50, one reverted toward base at 0.25, and one collapsed past base to 0.03, while the base model's own risk coordinate stayed near 0.2–0.4 throughout.
Under self-training, some traits self-amplify and some self-correct
Using activation steering to install traits via Persona Vectors, we seed ~13 starting points in a 5-trait value space (risk, optimism, sycophancy, verbosity, caution), run one self-judge step from each, and fit a local linear drift model Δx = A·x + b.
The diagonal of A is each trait's self-feedback under self-judging: positive means the further out the trait already is, the harder the next step pushes it further; negative means the step pulls it back toward the interior.
Risk and optimism self-amplify (positive self-feedback) while sycophancy, verbosity, and caution self-correct (negative self-feedback).
Installing or steering a trait bleeds into factual beliefs
A risk preference installed via custom risky/safe choices (similar to the model organism in Tell me about yourself) biases expected-value calculations in the direction that justifies the preference. Steering optimism leads to inflated success-probability estimates (~41% → 96%). Since the preferences from self-training vary across seeds, beliefs do too; self-training induces a distribution over sets of model beliefs that can be sampled by rolling out a given trajectory.
As AI models increasingly influence their own development process, the values of previous models will increasingly be borne out in each successive generation of model deployments. Thus, even outside of pure recursive self-improvement conditions, the feedback loop of model values is an essential component of AI alignment. In order to build systems that induce a feedback loop towards increasingly aligned models, we need a deeper understanding of value dynamics - how models steer their own values, and how this steering affects other beliefs and behaviors.

