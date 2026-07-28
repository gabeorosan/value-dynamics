# Human narration takes

Drop one recording per scene here, named `scene_00` … `scene_10` in scene
order, with any extension ffmpeg reads (`.mov`, `.m4a`, `.wav`, …). The builder
prefers a file over the synthesized voice, per scene, so you can record a few
and still build — the rest stay TTS.

Each take is levelled to −16 LUFS with an 80 Hz high-pass, and the silence at
each end is trimmed, so leave a beat of room tone before and after your read.
Video tracks are ignored; only the audio is used.

This directory is not tracked. Scene order for the published cut:

- `scene_00` — hero_vision — “A I increasingly generates and selects its own training data, through self-rewarding pip…”
- `scene_01` — synthesis_experiment_kit — “For each prompt in a round, the organism writes six candidate answers (the pool) and the…”
- `scene_02` — setup_both_models_v3 — “Each organism's value is the mean value score of its answers. For the gambling organism,…”
- `scene_03` — state-variables — “Two quantities are measured each round, spread and agreement, and together they forecast…”
- `scene_04` — model-one-round-line — “The model forecasts the selector gap as candidate spread times judge agreement, so the p…”
- `scene_05` — model-recurrence — “For endpoints, the model repeats this update from the round-one candidate mean, holding …”
- `scene_06` — synthesis-dial-plane-horizon — “The background is the change the model predicts for a run starting at each first-round s…”
- `scene_07` — staged-noise-forecast — “The deterministic forecast only gives the average path that real runs scatter around. Th…”
- `scene_08` — rollouts-vs-observed-spaghetti — “Adding noise gives a stochastic version that reproduces the dynamics of the observed tra…”
- `scene_09` — synthesis-intervention-cards — “Both interventions worked through spread and agreement: adding base-model answers to a c…”
- `scene_10` — closing — “The training setup here is narrow: small models, short runs, filtered supervised fine-tu…”

Rebuild after adding files:

```bash
VD_NO_SITE_COPY=1 uv run --with pillow --with edge-tts python \
  demo/src/build_writeup_demo.py scenes_cand1_forecast.json \
  value_dynamics_cand1_forecast
```
