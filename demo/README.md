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

Four takes on the same writeup, built to be compared. Each has a different
spine, not just different wording. All are 1920×1080, H.264 + AAC, with embedded
English subtitles, built from the same `src/build_writeup_demo.py`.

| Cut | Length | Spine | Editing pass |
|---|---|---|---|
| `cand1_forecast` | 5:14 | Poses the endpoint forecast as a prediction problem and answers it in order | [no-ai-slop](https://github.com/petergyang/no-ai-slop) |
| `cand2_selection` | 5:33 | A judging loop is a breeding program: selection theory imported and tested | house style only |
| `cand3_derivation` | 5:16 | The model derived one term at a time, error attached to every step | [no-ai-slop](https://github.com/petergyang/no-ai-slop) |
| `cand4_steering` | 5:11 | Opens on the two interventions, works backwards to why they worked | house style only |

Each cut has a narration script (`CANDIDATE_<n>_<slug>_SCRIPT.md`), a tweet
thread (`CANDIDATE_<n>_<slug>_THREAD.md`), and a scene spec
(`src/scenes_cand<n>_<slug>.json`). Each thread records its per-tweet character
counts, which tweet should carry the video, and the objection a skeptical reader
is most likely to raise.

All four open on the writeup's own framing — AI already generating and selecting
its own training data, the alignment-faking / model-collapse / attractor-state
literature, and the gap being that little work follows the dynamics through
training across settings and seeds — before any experiment appears, and all four
close on its safety stakes.

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
