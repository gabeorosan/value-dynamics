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

Four takes on the same writeup, deliberately different in how they enter the
subject, in register, and in length. All are 1920x1080, H.264 + AAC, with
embedded English subtitles, built from the same `src/build_writeup_demo.py`.

| Cut | Length | Enters through | Editing pass |
|---|---|---|---|
| `cand1_forecast` — Three photographs, no film | 4:25 | The literature (alignment faking, model collapse, attractor states) as three stills of a process nobody has filmed | [no-ai-slop](https://github.com/petergyang/no-ai-slop) |
| `cand2_selection` — A century-old equation | 5:41 | Animal and plant breeding; the word "AI" does not appear for about a minute | house style only |
| `cand3_derivation` — The missing instrument | 5:43 | A measurement gap: evaluation gives position, nothing gives motion | [no-ai-slop](https://github.com/petergyang/no-ai-slop) |
| `cand4_steering` — The loop you are already running | 2:50 | Second person, inside one concrete setup you are operating | house style only |

They differ structurally, not only in wording. Scene counts run 8 to 17 and
narration 458 to 899 words. Figure sets differ (4, 7, 8 and 10 of the ten) and so
do their orders: candidate 2 puts the one-round held-out test before the
spread-and-agreement recipes, because the breeder's spine tests the response
coefficient first; candidate 3 opens on the organisms rather than the loop and is
the only one that never uses `hero_vision`, so even its first frame differs.
Candidate 3 is also the only cut that states what the decomposition costs
(0.100 against 0.085 on matched rounds).

Each cut has a narration script (`CANDIDATE_<n>_<slug>_SCRIPT.md`), a tweet
thread (`CANDIDATE_<n>_<slug>_THREAD.md`), and a scene spec
(`src/scenes_cand<n>_<slug>.json`). Each thread opens the same way its video
does, and records its per-tweet character counts, which tweet should carry the
video, and the objection a skeptical reader is most likely to raise.

**Every figure used is one of the ten `docs/writeup_value_dynamics_sprint.md`
embeds.** The writeup is the only surface these scripts source from; other
figures, reports, and older demo scripts in this repo have drifted from it.

Candidates 1 and 3 were written against the
[no-ai-slop](https://github.com/petergyang/no-ai-slop) skill (vendored at
`.claude/skills/no-ai-slop/`) and self-checked against its `eval.md`; 2 and 4 saw
only the project's house style from `CLAUDE.md`. Scripts and threads were split
the same way, so the two pairs can be compared.

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
