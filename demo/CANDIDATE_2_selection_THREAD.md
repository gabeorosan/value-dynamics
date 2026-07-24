# Tweet thread for candidate 2 — an arithmetic borrowed from breeders

Ten tweets, all under 280 characters. Every number traces to
`docs/writeup_value_dynamics_sprint.md`. Link points at
`gabeorosan.github.io/value-dynamics/`.

The thread mirrors the cut: it starts in breeding, not in AI, and does not
mention a language model until tweet 3.

---

**1/** (252)

> Breeders have known for a century how to say what a population will look like after selection: measure how much the trait varies, measure how strongly selection favors it, and the response in the next generation follows. That is the breeder's equation.

**2/** (277)

> It takes two inputs. The selection differential: the mean trait of the parents you breed from minus the mean of the population they came from. Heritability: the fraction of that difference the offspring keep, normally fitted from data. Price generalized the accounting in 1970.

**3/** (273)

> Now take a model that writes candidate answers, has a judge keep the ones it prefers, and is fine-tuned on those. A population that varies. A step that keeps some and discards others. Inheritance. Post-training already runs loops shaped like this. Does the arithmetic hold?

**4/** (220)

> One round is one generation. Per prompt the organism writes 6 candidates: the population. The judge keeps the 2 it prefers: selection. Training runs on those 2: inheritance. Held-out prompts then measure the value again.

**5/** (274)

> The trait: I fine-tuned Qwen3-4B and OLMo-3-7B with value orientations. Gambling organism: the share of answers picking the risky gamble. Insecure-code organism: how insecure its answers to 3 fixed questions about its coding habits read, scored 0-1 by its frozen base model.

**6/** (223)

> Borrowed term 1, the selection differential: the mean value score of the 2 kept answers minus the mean over all 6 candidates in that prompt's pool. I call it the selector gap. It is the step selection asks training to take.

**7/** (278)

> Borrowed term 2, heritability. In breeding it is fitted. Here it comes out at 1, nothing fitted: the next value is just the kept mean. Held out one condition at a time over 340 rounds it misses by 0.081, against 0.128 for no change, and the value is re-read on held-out prompts.

**8/** (275)

> Breeders forecast the differential instead of waiting for it. Spread: SD of a prompt's candidate value scores. Agreement: correlation of judge scores with those value scores. Their product reconstructs the realized gap at error 0.040 across 367 rounds, before the judge runs.

**9/** (249)

> Iterate generations: freeze spread, agreement and pool composition at round 1 and repeat the update. Endpoints land at 0.118, against 0.431 for assuming no change. Add drift and finite sampling and 89% of observed endpoints fall inside the 80% band.

**10/** (256)

> Where the analogy breaks: a breeder's criterion sits outside the population, a judge does not, so agreement drifts as training changes what it sees. Limits: 2 small model families, short runs, filtered SFT, 2 behaviors. gabeorosan.github.io/value-dynamics/

Video: tweet 3. Tweets 1 and 2 set up the borrowed equation with no AI in them at
all, so the clip should land on the turn, where the loop is first mapped onto a
population. Hanging it off tweet 1 would make the breeding opening look like a
metaphor rather than the argument's load-bearing move.

Likely challenge: the heritability coefficient "coming out at 1" with nothing
fitted. A skeptic will read the kept candidate mean and the next measured value
as two views of the same quantity and want to know why 0.081 is not just a
restatement of the training objective. Tweet 7 answers it in a clause — the
value is re-read on held-out prompts, not on the answers that were trained on —
and the video says it out loud on the same figure, but expect to have to repeat
it in replies.

Second likely challenge, from anyone who knows selection theory: that the
breeder's equation with heritability pinned at 1 is a strong assumption, not a
finding. The honest answer is that it is a finding for this setup and only this
setup — filtered SFT on 2 kept answers, small models, short runs — and that the
place it visibly strains is agreement drift, which tweet 10 names.
