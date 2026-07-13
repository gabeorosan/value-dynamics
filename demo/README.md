# Value Dynamics — video demo

Two narrated MP4 walkthroughs of the project, aligned with
`docs/writeup_value_dynamics_sprint.md` (the "When AI drives its own training
process" post) and built from the house-style figures in `docs/figures/`.
Both are 1920×1080, H.264 + AAC. Narration is a neural voice
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

`demo/voice_samples/` has one identical sample line in six neural voices
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
