# Working with the newest frontier tiers — Fable 5 / Mythos 5 and GPT-5.6 (Sol/Terra/Luna)

Research notes, compiled 2026-07-24. Scope: how prompt-engineering and agent-scaffolding
conventions have *changed* for these tiers versus prior generations. Each bullet is tagged
**[OFFICIAL]** (Anthropic or OpenAI docs), **[REPORTED]** (news/benchmark write-up), or
**[OPINION]** (blogger/practitioner). This is a workflow scratch note, not a ledger claim —
no experiment results of ours are asserted here.

---

## (a) What changed for Fable-class models (Fable 5 / Mythos 5)

Source unless noted: Anthropic's official "Prompting Claude Fable 5" guide. These are
behavioral shifts *relative to Claude Opus 4.8*, and the guide frames a capability jump as
itself a reason to re-audit old instructions.

- **Stop over-engineering prompts. Prescriptive scaffolding now *degrades* output.** The guide
  says skills/prompts built for prior models are "often too prescriptive for Claude Fable 5 and
  can degrade output quality" — review and remove older instructions if default behavior is
  better. Instruction-following is strong enough to steer most behaviors with one brief
  instruction instead of enumerating each case. **[OFFICIAL]**
- **Stop echoing/transcribing reasoning in the response.** Any instruction to "show your
  thinking," reflect, or reproduce internal reasoning as response text can trip the
  `reasoning_extraction` refusal classifier and cause elevated fallbacks to Opus 4.8. Read the
  structured `thinking` blocks instead. Audit old skills/system prompts for this on migration. **[OFFICIAL]**
- **Effort is the primary intelligence/latency/cost dial; use `high` as default.** Use `xhigh`
  for the most capability-sensitive work, `medium`/`low` for routine tasks. Lower effort on
  Fable 5 "still perform[s] well and often exceed[s] `xhigh` performance on prior models." Reduce
  effort if a task completes but runs longer than needed. **[OFFICIAL]**
- **Thinking is always on; adaptive thinking is the only mode.** No extended-thinking budgets,
  summarized-only thinking output. Use adaptive thinking for agentic/multistep/long-horizon work. **[OFFICIAL]**
- **Expect much longer turns; restructure the harness around it.** Individual hard requests run
  many minutes at high effort; autonomous runs can go hours. Adjust client timeouts, streaming,
  and progress UI *before* migrating; prefer async check-ins (scheduled jobs) over blocking. **[OFFICIAL]**
- **Add a "when you have enough info, act" instruction to curb overplanning** on ambiguous tasks
  — Fable 5 otherwise surveys options and re-derives settled facts. Verbatim snippet in the guide. **[OFFICIAL]**
- **Add an anti-scope-creep instruction at higher effort.** Fable 5 tends to tidy/refactor/add
  helpers unrequested; the guide gives a copy-paste "don't add features, refactor, or introduce
  abstractions beyond what the task requires… only validate at system boundaries" block. **[OFFICIAL]**
- **Ground progress claims against tool results.** On long autonomous runs, instruct it to audit
  each claim against a tool result from the session — Anthropic says this "nearly eliminated
  fabricated status reports" even on tasks designed to elicit them. **[OFFICIAL]**
- **State boundaries explicitly** — Fable 5 occasionally takes unrequested actions (drafting an
  email, defensive git-branch backups). When the user is thinking out loud, the deliverable is an
  assessment: report findings and stop until asked to fix. **[OFFICIAL]**
- **Use parallel subagents *more*, and communicate async.** Fable 5 "is significantly more
  dependable at dispatching and sustaining parallel subagents." Prefer async orchestrator↔subagent
  comms over blocking; long-lived subagents that keep context save cost via cache reads and avoid
  bottlenecking on the slowest one. Fresh-context *verifier* subagents beat self-critique. **[OFFICIAL]**
- **Give a memory system.** Fable 5 does well writing/reading lessons — a plain Markdown file, one
  lesson per file with a one-line summary; it can bootstrap memory by reviewing past sessions via
  subagents. **[OFFICIAL]**
- **Give the reason, not just the request.** Providing intent ("I'm working on X for Y, they need
  Z, with that in mind…") improves results, especially for long-running multi-workstream agents. **[OFFICIAL]**
- **Brevity/readability needs one instruction, not a rulebook.** A single "lead with the outcome"
  block replaces enumerating every verbosity pattern; a separate "drop working shorthand in the
  final summary" addendum fixes dense arrow-chain output in long agentic sessions. **[OFFICIAL]**
- **New failure modes to patch for long/async runs:** rare early stopping (text-only "I'll now
  run X" with no tool call — a "continue" or an autonomous-operation system reminder fixes it);
  rare context-budget anxiety (don't surface remaining-token countdowns; reassure "you have ample
  context"); optional `send_to_user` client tool to surface verbatim messages mid-turn (must pair
  the tool with an elicitation instruction or it rarely gets called). **[OFFICIAL]**
- **Safety routing is now a hard operational constraint.** Fable 5 runs classifiers on offensive
  cyber, biology/life-sciences, and thinking-extraction; benign work in those domains can also
  trip them, returning `stop_reason: "refusal"`. Configure fallback to Opus 4.8. Directly relevant
  if any of our ML work touches molecular/bio content. **[OFFICIAL]**

---

## (b) What changed for GPT-5.6 (Sol / Terra / Luna)

Source unless noted: OpenAI's official GPT-5.6 model-guidance page, plus Simon Willison's family
write-up for tiering/pricing.

- **Lean, outcome-first system prompts beat elaborate scaffolding — with hard numbers.** OpenAI's
  internal coding-agent evals: leaner prompts improved scores ~**10–15%**, cut total tokens
  **41–66%**, and reduced API cost **33–67%**. Removing redundant instructions/examples/verbose
  tool descriptions helped more than adding model-specific guidance. Numbers are "internal evals,"
  no public paper. **[OFFICIAL, internally-sourced numbers]**
- **Start with the smallest prompt and tool set that reliably completes the task.** State
  instructions once; expose only task-relevant tools with concise descriptions; keep the examples
  that encode real product requirements or fix known gaps. **[OFFICIAL]**
- **Six effort levels: `none`, `low`, `medium`, `high`, `xhigh`, `max`.** Migration rule: keep your
  current effort as baseline, then *test one level lower* — 5.6 often matches/improves quality with
  fewer tokens. `medium` = balanced default; `high`/`xhigh` only when measured gains justify tokens;
  `max` reserved for frontier-difficulty, compared against `xhigh` for cost-benefit. **[OFFICIAL]**
- **Drop broad "be concise" instructions.** 5.6 is more concise than 5.5 by default; use the
  `text.verbosity` (`low`/`medium`/`high`) knob as the default and only add task-specific verbosity
  requirements. Practitioners warn "be concise" makes it emit shorter *substitutes* rather than full
  artifacts — replace with "lead with the conclusion, then evidence/caveats/next steps." **[OFFICIAL]** for the verbosity knob; **[OPINION]** for the substitution failure mode.
- **Define safe local actions vs approval-required actions explicitly.** Allow read/edit/run-tests
  without asking; require confirmation only for external writes, destructive actions, or scope
  expansion — reduces unnecessary pauses. **[OFFICIAL]**
- **Pro mode is an API flag, not a prompt.** `reasoning.mode: "pro"` for high-value coding/review or
  complex optimization where marginal gains matter; benchmark against standard — higher effort
  doesn't guarantee a better tradeoff. **[OFFICIAL]**
- **New agent primitives:** Programmatic Tool Calling (model writes JavaScript to orchestrate tool
  calls — best for bounded multi-call stages that reduce to small structured output: filtering,
  ranking, aggregation; benchmark vs direct calling); native multi-agent (spin up parallel focused
  subagents); prompt-cache breakpoints; image `detail: "original"`. **[OFFICIAL]** / **[REPORTED]** (Willison).
- **Tiering (Willison):** Luna $1/$6, Terra $2.50/$15, Sol $5/$30 per 1M in/out tokens; all share a
  Feb 16 2026 cutoff, 1M context, 128K max output. Differentiation is capability, not features.
  "Ultra" (as in "Sol Ultra") shows up in discovery reporting as a parallel test-time-compute /
  many-concurrent-agent product tier — distinct from the API `pro` reasoning mode; treat "ultra
  mode subagents" as a product feature, not a documented API knob. **[REPORTED]/[OPINION]**
- **Benchmark framing (Willison):** on "Agents' Last Exam," Sol 53.6 vs Fable 5 40.5; Terra and Luna
  reportedly beat Fable 5 "at around one-sixteenth the cost" — vendor/blogger benchmark, not
  independently reproduced here. **[REPORTED]**

---

## (c) Implications for our setup (Fable orchestrator + Opus/Sonnet subagents + occasional GPT-5.6 Sol audits, ML on free GPUs)

Our current habits: elaborate self-contained spawn prompts, detailed MUST-rules in CLAUDE.md,
heavy per-step scaffolding. The new guidance cuts both ways — some habits are now explicitly
counter-productive, others are still endorsed.

**Keep:**
- **Self-contained spawn prompts stay right — for a different reason.** Both vendors push "give the
  reason/intent, full project context upfront." Our figure-maker/subagent spawns that carry
  file paths, actual numbers, and the relationship to show map exactly onto Fable's "give the reason,
  not only the request." Keep them *context-rich*; trim them of *prescriptive step-by-step how-to*. **[OFFICIAL, Anthropic]**
- **Lean harder on parallel subagents and async orchestration.** Our multi-thread + background
  figure-maker pattern is exactly what Fable 5 is now "significantly more dependable" at. Keep it;
  push more independent work to parallel subagents and don't block. **[OFFICIAL, Anthropic]**
- **Fresh-context verifier subagents over self-critique** — endorsed. Good fit for checking an
  analysis/figure against its spec. **[OFFICIAL, Anthropic]**
- **The memory/ledger discipline.** ANALYSIS_LEDGER.md and STATE.md are close to Anthropic's
  recommended Markdown memory system; Fable 5 is designed to use exactly this. Keep. **[OFFICIAL, Anthropic]**
- **The "ground progress claims against tool results" rule** is a near-verbatim match for our claim-
  hygiene directive ("chat-only numbers died unverifiable"). The vendor now backs this with "nearly
  eliminated fabricated status reports." Strong keep. **[OFFICIAL, Anthropic]**

**Drop / trim:**
- **Heavy per-step scaffolding and long enumerated MUST-lists in CLAUDE.md are now a liability on
  Fable-class models.** Anthropic: prescriptive skills "can degrade output quality"; OpenAI's numbers
  show leaner prompts win by 10–15% score / 41–66% tokens. Our CLAUDE.md has long MUST-rule blocks —
  candidate for consolidation into short intent statements ("act when you have enough info,"
  "no scope creep," "ground claims in tool output") rather than exhaustive enumeration. This is the
  single biggest divergence between our habits and the new guidance. **[OFFICIAL, both]**
- **Any "show/echo your reasoning" phrasing must go from Claude-facing prompts/skills** — it now
  risks `reasoning_extraction` refusals and Opus fallbacks on Fable 5. Worth grepping our skills and
  spawn templates. **[OFFICIAL, Anthropic]**
- **Redundant "be concise"/verbosity boilerplate** — replace with one "lead with the outcome" line
  (Fable) and the `text.verbosity` knob (GPT-5.6). We already codify "readable writing"; make it one
  instruction, not a repeated refrain. **[OFFICIAL, both]**

**Operational cautions specific to us:**
- **Effort dial is the new lever.** For routine analysis/figure spawns, `medium`/`low` on Fable 5 may
  match old-model `xhigh` — cheaper and faster, matters for a free-GPU / cost-watching solo setup.
  For GPT-5.6 Sol audits, start at your prior effort then *test one lower*. **[OFFICIAL, both]**
- **Bio/chem safety routing is a real gotcha.** If any experiment prompt touches molecular/lab/bio
  framing, Fable 5 may refuse and fall back to Opus 4.8 — configure fallback and don't be surprised
  by silent tier changes. Relevant only if our value-dynamics work strays into those domains. **[OFFICIAL, Anthropic]**
- **Longer autonomous turns** mean our overnight Colab/Kaggle-adjacent agent loops should assume
  multi-minute-to-hour turns and async check-ins, not blocking calls. Matches the runbook direction. **[OFFICIAL, Anthropic]**
- **"Ultra mode subagents" is not a documented API feature** — it's product-tier discovery marketing
  (Sol Ultra / 64-agent parallel test-time compute). Don't design our scaffolding around it. **[REPORTED]**

**Attribution honesty:** the actionable Fable 5 items and the GPT-5.6 lean-prompt/effort/verbosity
items are all **officially documented**. The 10–15% / 41–66% / 33–67% figures are OpenAI *internal*
evals with no public paper. Tiering, pricing, benchmark scores, "ultra," and the "be concise causes
substitutes" failure mode are **blogger/reported**, not vendor-guaranteed.

---

## (d) Groundbreaking discoveries (highlights only)

Both tiers are being credited with frontier-math results in July 2026. Note: several are **reported
and partly unverified** — included as context, not endorsement.

- **Fable 5 — Jacobian conjecture (open since 1939).** Levant Alpöge (Anthropic) reportedly used
  Fable 5 to find a counterexample (~216 chars, a C³→C³ map with constant Jacobian determinant −2 that
  is not globally invertible); mathematicians reportedly verified it within hours. Framed as a landmark
  but "AI can't explain *why*." **[REPORTED]** (Fortune, CoinDesk, BigGo).
- **GPT-5.6 — Cycle Double Cover conjecture (graph theory, ~50 yrs).** OpenAI announced Sol *Ultra*
  proved it in under an hour via "parallel test-time computation" with 64 concurrent agents on
  distinct proof strategies. **[REPORTED]** (36kr, HTX).
- **GPT-5.6 — statistics conjecture disproved in 90 min** that 5.5 couldn't crack in 20+ hours, with a
  machine-checkable certificate; reported to expose a flaw in a heavily-cited method. **[REPORTED]** (TechTimes).
- **GPT-5.6 — Erdős problems.** A Peking University alumnus reportedly solved six Erdős problems in five
  days with Sol + Codex (46% success over 13 attempts). **Caveat:** as of ~July 20 the authoritative
  Erdős Problems database still listed Problem #119 as open — some claims remain **unverified**. **[REPORTED, disputed]** (digg, WindowsForum, KuCoin).
- **Context:** follows the mid-2025 IMO 5/6 result and a May 2026 OpenAI model disproving an
  80-year-old Erdős combinatorial-geometry conjecture — the cadence of falling open problems is the
  actual story. **[REPORTED]**

The workflow-relevant takeaway: the headline results lean on **parallel-agent, test-time-compute**
scaffolding (64 agents, distinct strategies) and **machine-checkable certificates** — i.e., fresh-
context verification, which is exactly the subagent-verifier pattern both vendor guides recommend.

---

## Sources

Official docs:
- Anthropic — Prompting Claude Fable 5: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5
- Anthropic — Prompting best practices: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- OpenAI — GPT-5.6 model guidance: https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6

Analysis / write-ups:
- Simon Willison — The new GPT-5.6 family: Luna, Terra, Sol: https://simonw.substack.com/p/the-new-gpt-56-family-luna-terra
- The Prompt Index — GPT-5.6 (Sol) & Claude Fable 5 Prompting Guide (2026): https://www.thepromptindex.com/gpt-5-6-and-claude-fable-5-prompting-guide.html
- TechTimes — GPT-5.6 Prompting Guide: Lean System Prompts Outperform Elaborate Scaffolding: https://www.techtimes.com/articles/320650/20260715/gpt-56-prompting-guide-lean-system-prompts-now-outperform-elaborate-scaffolding.htm (note: returned 403 on direct fetch; content corroborated via the two guides above)

Discoveries:
- Fortune — AI cracks the Jacobian conjecture: https://fortune.com/2026/07/21/ai-solves-jacobian-conjecture-levant-alpoge-claude-fable-5/
- CoinDesk — Fable 5 solved an 87-year-old math problem: https://www.coindesk.com/tech/2026/07/21/claude-s-fable-5-just-solved-an-87-year-old-math-problem-and-it-matters-for-bitcoin
- BigGo Finance — Jacobian Conjecture resolved: https://finance.biggo.com/news/548659ce-fd35-4976-9059-90546acb88af
- TechTimes — GPT-5.6 disproves statistics conjecture in 90 minutes: https://www.techtimes.com/articles/320669/20260715/gpt-56-disproves-statistics-conjecture-90-minutes-exposing-flaw-130000-citation-method.htm
- 36kr — GPT-5.6 solves 50-year-old graph theory problem (Cycle Double Cover): https://eu.36kr.com/en/p/3896565258733189
- Windows Forum — GPT-5.6 Sol Erdős Problem #119 claim remains unverified: https://windowsforum.com/threads/gpt-5-6-sol-erdos-problem-119-claim-remains-unverified.439743/
