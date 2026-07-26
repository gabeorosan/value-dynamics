# Value Dynamics — video demo

## The published cut

`cand1_forecast` is the demo the site and README link to. It is copied to
`site/media/value_dynamics_demo.mp4` (plus a 720p companion, poster, and
subtitle track) and shown at
[gabeorosan.github.io/value-dynamics/demo.html](https://gabeorosan.github.io/value-dynamics/demo.html).

It was chosen because it poses the question the writeup's title asks and answers
it in the writeup's own order: the loop, what has to be measured, the one-round
rule, the iterated endpoint, what the forecast does not cover, and the
interventions.

## The four candidates

Four cuts of the same writeup, close to its narrative and register. They differ
in what they cover and in what order. All are 1920x1080, H.264 + AAC, with
embedded English subtitles, built from `src/build_writeup_demo.py`.

| Cut | Length | What it is | Editing pass |
|---|---|---|---|
| `cand1_forecast` — The faithful walkthrough | 5:21 | The writeup end to end in its own order, using all ten of its figures | [no-ai-slop](https://github.com/petergyang/no-ai-slop) |
| `cand2_selection` — Three findings, and how they were measured | 5:23 | All three findings on screen inside 90 seconds, then how each was measured | house style only |
| `cand3_derivation` — How the forecast is built and tested | 6:01 | The methods cut: recipes, held-out protocol, and what each step costs | [no-ai-slop](https://github.com/petergyang/no-ai-slop) |
| `cand4_steering` — The short version | 2:45 | Everything essential, with a third of the runtime on the limits | house style only |

Scene counts run 7 to 17 and narration 448 to 946 words. Candidate 1 is the published cut.

**Numbers are shown, not spoken.** A listener cannot hold a spoken decimal or
check it, so precise values live in scene captions and on statement cards where
they can be read, and the narration states the comparison qualitatively. Each cut
speaks between two and six numbers in total, spent on the headline endpoint
comparison and the band coverage. The tweet threads are read rather than heard,
so they keep every number.

Each cut opens on the project's aim — how a model's values move once it is inside
a feedback loop driving its own training, borrowing the tools of population
genetics — and closes on the writeup's three future-direction
strands, including more open-ended setups where models select their own training
data, revise system prompts and edit the loop itself.

The title card carries `hero_vision` in its lower two thirds: `title` and
`closing` scenes accept an optional `"fig"`, filling the lower two thirds of a
title card or the left half of a closing card. The closing cards use no figure —
every candidate had been repeating its own title image there, which communicated
nothing, and the three future-direction items carry their own detail lines.

A card earns its place by showing something the narration does not. A headline
restating the spoken line over an empty frame does not, so candidate 1's
selection-theory card was folded into the `state-variables` scene, where the
figure names the same quantities. The statement cards that remain hold an
equation or a result set large enough to read.

Each cut has a narration script (`CANDIDATE_<n>_<slug>_SCRIPT.md`), a tweet
thread (`CANDIDATE_<n>_<slug>_THREAD.md`), and a scene spec
(`src/scenes_cand<n>_<slug>.json`). Each thread records its per-tweet character
counts, which tweet should carry the video, and the objection a skeptical reader
is most likely to raise.

**Every figure used is one of the ten `docs/writeup_value_dynamics_sprint.md`
embeds**, and the writeup is the only surface these scripts source from. Other
figures, reports, and older demo scripts in this repo have drifted from it.

Candidates 1 and 3 were additionally checked against the
[no-ai-slop](https://github.com/petergyang/no-ai-slop) skill (vendored at
`.claude/skills/no-ai-slop/`); 2 and 4 saw only the project's house style from
`CLAUDE.md`.

## Rebuilding

```bash
VD_NO_SITE_COPY=1 uv run --with pillow python demo/src/build_writeup_demo.py \
  scenes_cand1_forecast.json value_dynamics_cand1_forecast
```

`VD_NO_SITE_COPY=1` skips the copy into `site/media/`, so a rebuild does not
touch the published site until you want it to.

Scene specs are JSON arrays with four scene kinds: `title`, `fig`, `statement`
(a full-screen type card), and `closing`. The build needs `ffmpeg` and
`qlmanage`, plus Pillow and edge-tts via `uv`. Render the figures from SVG
first:

```bash
qlmanage -t -s 2600 -o <work>/ql docs/figures/*.svg docs/figures/auto/*/*.svg
```

Render from the `.svg` sources, never from a committed `.svg.png` sitting beside
them — two of those were found stale against their own SVGs.

## Voice

Narration is edge-tts, defaulting to `en-US-AndrewMultilingualNeural`. Override
with `VD_VOICE` and `VD_RATE`; `VD_TTS=say` falls back to the offline macOS
voice, which sounds noticeably robotic. `voice_samples/sample_*.mp3` are four
multilingual neural voices reading the same two lines of real script.

## Build artifacts

The `.mp4`, `.srt`, and `_poster.png` files in this directory are local build
artifacts and are not tracked; they regenerate from the scene specs. The
published cut in `site/media/` is the one under version control.
