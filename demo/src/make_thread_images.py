#!/usr/bin/env python3
"""Render the images that attach to candidate 1's tweets, one file per tweet.

Each name is `tweet_<nn>_<figure>.png`, so the attachment order is unambiguous
when posting. Every figure is one of the ten `docs/writeup_value_dynamics_sprint.md`
embeds; the mapping below is the thread's claim-by-claim pairing and is documented
in demo/CANDIDATE_1_forecast_THREAD.md.

Run the qlmanage pass first (it renders every writeup figure to PNG):

    qlmanage -t -s 2600 -o /private/tmp/value-dynamics-writeup-demo/ql \\
      docs/figures/*.svg docs/figures/auto/*/*.svg

    uv run --no-project --with pillow python demo/src/make_thread_images.py

qlmanage centres each render on a white square, so the artwork is cropped back
out of that padding here. The crop is checked against the SVG's own aspect ratio
and any figure that disagrees by more than 6% is reported, since a bad crop
would silently cut a figure's edge.
"""
import pathlib
import re
import sys

from PIL import Image, ImageChops

ROOT = pathlib.Path(__file__).resolve().parents[2]
QL = pathlib.Path("/private/tmp/value-dynamics-writeup-demo/ql")
OUT = ROOT / "demo/thread_images"
MAX_WIDTH = 2048          # X downscales anything larger
MARGIN = 24               # px of white kept around the artwork

# tweet number -> figure stem. Two figures on one tweet post as one image pair.
PLAN = [
    (1, "hero_vision"),                       # the loop the opening tweet names
    (3, "synthesis_experiment_kit"),          # one round: six candidates, two kept, re-measure
    (4, "setup_both_models_v3"),              # the 0-to-1 value scale on both organisms
    (5, "state-variables"),                   # spread, agreement, selector gap defined
    (6, "model-one-round-line"),              # the one-round rule on the value line
    (6, "model-recurrence"),                  # kept mean = pool mean + spread x agreement
    (7, "synthesis-dial-plane-horizon"),      # endpoints from round-one measurements
    (8, "staged-noise-forecast"),             # where each noise term enters
    (8, "rollouts-vs-observed-spaghetti"),    # simulated against observed trajectories
    (9, "synthesis-intervention-cards"),      # the two interventions
]


def svg_aspect(stem):
    matches = list((ROOT / "docs/figures").glob(f"{stem}.svg")) + \
              list((ROOT / "docs/figures/auto").glob(f"*/{stem}.svg"))
    head = matches[0].read_text(errors="ignore")[:800]
    box = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', head)
    if box:
        return float(box.group(1)) / float(box.group(2))
    w = re.search(r'\bwidth="([\d.]+)', head)
    h = re.search(r'\bheight="([\d.]+)', head)
    return float(w.group(1)) / float(h.group(1))


def main():
    OUT.mkdir(exist_ok=True)
    for stale in OUT.glob("*.png"):
        stale.unlink()

    suspect = []
    for tweet, stem in PLAN:
        source = QL / f"{stem}.svg.png"
        if not source.exists():
            sys.exit(f"{source} missing — run the qlmanage pass in this file's docstring")
        image = Image.open(source).convert("RGB")
        white = Image.new("RGB", image.size, (255, 255, 255))
        ink = ImageChops.difference(image, white).convert("L").point(lambda v: 255 if v > 6 else 0)
        left, top, right, bottom = ink.getbbox()
        image = image.crop((max(left - MARGIN, 0), max(top - MARGIN, 0),
                            min(right + MARGIN, image.width), min(bottom + MARGIN, image.height)))
        if image.width > MAX_WIDTH:
            image = image.resize((MAX_WIDTH, round(image.height * MAX_WIDTH / image.width)),
                                 Image.LANCZOS)
        target = OUT / f"tweet_{tweet:02d}_{stem}.png"
        image.save(target, optimize=True)

        got, want = image.width / image.height, svg_aspect(stem)
        drift = abs(got - want) / want
        if drift > 0.06:
            suspect.append((target.name, got, want))
        print(f"{target.name:50s} {image.width}x{image.height}  "
              f"{target.stat().st_size / 1024:5.0f} KB")

    if suspect:
        print("\nWider aspect drift than the SVG's own box — look at these before posting:")
        for name, got, want in suspect:
            print(f"  {name}: cropped {got:.2f}, SVG box {want:.2f}")


if __name__ == "__main__":
    main()
