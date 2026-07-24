# Value Dynamics — video demo

## Candidate cuts (2026-07-24) — pick one

Four alternative takes on the same writeup, built to be compared. Each has a
different spine, not just different wording. All are 1920×1080, H.264 + AAC,
with embedded English subtitles, built from the same
`src/build_writeup_demo.py`.

| File | Length | Spine | Editing pass |
|---|---|---|---|
| `value_dynamics_cand1_forecast.mp4` | 5:14 | Poses the endpoint forecast as a prediction problem and answers it in order | [no-ai-slop](https://github.com/petergyang/no-ai-slop) |
| `value_dynamics_cand2_selection.mp4` | 5:33 | A judging loop is a breeding program: selection theory imported and tested | house style only |
| `value_dynamics_cand3_derivation.mp4` | 5:16 | The model derived one term at a time, error attached to every step | [no-ai-slop](https://github.com/petergyang/no-ai-slop) |
| `value_dynamics_cand4_steering.mp4` | 5:11 | Opens on the two interventions, works backwards to why they worked | house style only |

All four open on the writeup's own framing (AI already generating and selecting
its own training data; the alignment-faking / model-collapse / attractor-state
literature; the gap being that little work follows the dynamics through training
across settings and seeds) before any experiment appears, and all four close on
its safety stakes.

**Every figure used is one of the ten `docs/writeup_value_dynamics_sprint.md`
embeds.** The writeup is the only surface these scripts source from; other
figures, reports and older demo scripts in the repo are not trusted.

A tweet thread for each cut is in `CANDIDATE_<n>_<slug>_THREAD.md`, split by
the same skill/house-style rule as the scripts. Each thread records its per-tweet character counts, which tweet should
carry the video, and the objection a skeptical reader is most likely to raise.

The skill is installed at `.claude/skills/no-ai-slop/`. Candidates 1 and 3 were
written against its rules and self-checked against its `eval.md`; 2 and 4 saw
only the project's own writing rules from `CLAUDE.md`. The clearest difference
is in the endings: the skill-edited pair closes on a number or an instruction,
the unedited pair on a rhetorical line.

Scripts are `CANDIDATE_<n>_<slug>_SCRIPT.md`; scene specs are
`src/scenes_cand<n>_<slug>.json`. Rebuild any of them with:

```
VD_NO_SITE_COPY=1 python3 src/build_writeup_demo.py scenes_cand1_forecast.json value_dynamics_cand1_forecast
```

`VD_NO_SITE_COPY=1` skips the copy into `site/media/`, so candidates do not
touch the published site. The builder also has a `statement` scene kind (a
full-screen type card with an optional kicker and sub-line) added for these.

## Current cuts

| File | Length | Use |
|---|---|---|
| `value_dynamics_writeup_demo.mp4` | 4:43 | Empirical demo: setup, one-round rule, endpoint forecasts, stochastic rollouts, interventions, and limitations |
| `value_dynamics_research_vision_demo.mp4` | 4:53 | Research vision: population genetics, cybernetics, empirical control of feedback loops, and the AI-safety theory of change |

The editable narration and on-screen directions are in
[`WRITEUP_DEMO_SCRIPT.md`](WRITEUP_DEMO_SCRIPT.md) and
[`RESEARCH_VISION_DEMO_SCRIPT.md`](RESEARCH_VISION_DEMO_SCRIPT.md). Both MP4s
are 1920×1080, H.264 + AAC, with embedded English subtitle tracks. Their scene
specs are `src/scenes_writeup.json` and `src/scenes_vision.json`; both use
`src/build_writeup_demo.py`.

The current cuts use the local macOS Samantha voice. Rebuild them with:

```
python3 src/build_writeup_demo.py scenes_writeup.json value_dynamics_writeup_demo
python3 src/build_writeup_demo.py scenes_vision.json value_dynamics_research_vision_demo
```

## Earlier experiment-first cuts

Two earlier narrated MP4 walkthroughs of the experiment-first version of the
project site, built from the house-style figures in `docs/figures/`. Both are
1920×1080, H.264 + AAC. Narration is a neural voice
(`edge-tts`, en-US-AndrewNeural).

| File | Length | Use |
|---|---|---|
| `value_dynamics_demo.mp4` | ~7 min | Full explainer — the writeup site's 16 figures, in order |
| `value_dynamics_teaser.mp4` | ~1:25 | Short cut — the headline beats |

The full narration script (per-scene captions + spoken text) is in
[SCRIPT.md](SCRIPT.md).

Story beats (full cut): the generate→judge→train→measure loop · the gambling
organism and its 0–1 readout · the judge sets the width of the outcome fan ·
kept-minus-pool gap ≈ 0.75 predicts drift (frozen predictor, 17–42% better
blind) · selection-inert states (nothing left to select) · the matched
injection pair (0.625 stall → 0.000 in one round) · the supplier sets the
destination + self-judge erosion (0.67 → 0.000 in two rounds) · rescue-vs-
contamination asymmetry · judge grip depends on scoring-vs-duels protocol ·
the three-lever takeaway (gap, variation, provenance).

## Voice

`build_writeup_demo.py` narrates with edge-tts, defaulting to
`en-US-AndrewMultilingualNeural`. The older macOS `say` path (offline, but
robotic) is still available with `VD_TTS=say`. `VD_VOICE` and `VD_RATE` override
the voice and pace. `demo/voice_samples/sample_*.mp3` are the four multilingual
neural voices reading the same two lines of real script, numbers included.

`demo/voice_samples/` also has one identical sample line in six older neural voices
(Andrew, Brian, Christopher, Aria, Jenny US; Ryan GB). To re-render with a
different one: `VD_VOICE=en-US-AriaNeural python3 src/assemble.py …`
(`VD_RATE=+4%` adjusts pace). Other options, roughly in ascending quality:
macOS premium voices (download in System Settings → Accessibility → Spoken
Content, then use `say`), OpenAI TTS or ElevenLabs (need API keys — happy to
wire either in).

## Rebuild
Everything is in `src/`. No third-party Python deps beyond Pillow and
edge-tts (both via `uv`), plus system `qlmanage` and `ffmpeg`.

```
# 1. render the figures at 2600px into <work>/ql/  (qlmanage, instant):
qlmanage -t -s 2600 -o <work>/ql docs/figures/*.svg
# 2. composite branded 1920x1080 scene frames:
python3 src/build_frames.py scenes.json scenes
# 3. TTS + timed crossfade assembly -> out/value_dynamics_demo.mp4:
python3 src/assemble.py scenes.json scenes value_dynamics_demo
# teaser: same with scenes_teaser.json / scenes_teaser / value_dynamics_teaser
```

`WORK` paths at the top of the two scripts point at the scratchpad build dir;
edit them to a local working directory before rerunning. Narration text lives
in the `scenes*.json` files (one object per scene: figure, caption, accent,
narration; title/closing cards carry their own text fields).

These files are untracked — move, commit, or delete them as you like.
