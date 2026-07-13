#!/usr/bin/env python3
"""Compose branded 1920x1080 scene frames for the Value Dynamics demo video."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageChops

WORK = "/private/tmp/claude-501/-Users-gabriel-projects-value-dynamics/f063f126-f02b-4c97-87b5-48c6951e01c6/scratchpad/video"
QL = os.path.join(WORK, "ql")
SCENES_FILE = os.path.join(WORK, sys.argv[1] if len(sys.argv) > 1 else "scenes.json")
OUT = os.path.join(WORK, sys.argv[2] if len(sys.argv) > 2 else "scenes")
os.makedirs(OUT, exist_ok=True)

W, H = 1920, 1080
REG = "/System/Library/Fonts/Supplemental/Arial.ttf"
BLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

def font(bold, size):
    return ImageFont.truetype(BLD if bold else REG, size)

def hx(c):
    c = c.lstrip('#')
    return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))

def blend(a, b, t):
    return tuple(round(a[i]*(1-t)+b[i]*t) for i in range(3))

WHITE = (255, 255, 255)
INK = hx("1b2436")
SUB = hx("5b657a")
FAINT = hx("9aa6b6")
HAIR = hx("e7ecf3")
WORD = hx("26324c")

def trim(im, pad=26):
    im = im.convert("RGB")
    bg = Image.new("RGB", im.size, WHITE)
    diff = ImageChops.difference(im, bg)
    diff = diff.point(lambda p: 0 if p < 14 else 255)
    bbox = diff.getbbox()
    if not bbox:
        return im
    l, t, r, b = bbox
    l = max(0, l-pad); t = max(0, t-pad)
    r = min(im.size[0], r+pad); b = min(im.size[1], b+pad)
    return im.crop((l, t, r, b))

def tracked(draw, xy, text, fnt, fill, spacing):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + spacing
    return x

def tracked_w(draw, text, fnt, spacing):
    return sum(draw.textlength(ch, font=fnt)+spacing for ch in text) - spacing

def wrap(draw, text, fnt, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur+" "+w).strip()
        if draw.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def chrome(im, accent, idx, total, caption):
    d = ImageDraw.Draw(im)
    ac = hx(accent)
    # top accent rule
    d.rectangle([0, 0, W, 6], fill=ac)
    # wordmark
    wf = font(True, 25)
    tracked(d, (80, 34), "VALUE DYNAMICS", wf, WORD, 3)
    # counter
    cf = font(True, 22)
    lab = f"{idx:02d} / {total:02d}"
    d.text((W-80-d.textlength(lab, font=cf), 36), lab, font=cf, fill=FAINT)
    # hairline
    d.line([80, 92, W-80, 92], fill=HAIR, width=2)
    # caption band
    band_top = 992
    d.rectangle([0, band_top, W, H], fill=blend(WHITE, ac, 0.10))
    d.rectangle([0, band_top, W, band_top+4], fill=ac)
    capf = font(True, 33)
    cw = d.textlength(caption, font=capf)
    d.text(((W-cw)/2, band_top+24), caption, font=capf, fill=blend(ac, INK, 0.25))
    return band_top

def place_fig(im, fig_png, top, bottom):
    fig = trim(Image.open(os.path.join(QL, fig_png)))
    avail_w, avail_h = W-160, bottom-top
    s = min(avail_w/fig.width, avail_h/fig.height)
    nw, nh = round(fig.width*s), round(fig.height*s)
    fig = fig.resize((nw, nh), Image.LANCZOS)
    im.paste(fig, ((W-nw)//2, top+(avail_h-nh)//2))

def scene_fig(sp, idx, total):
    im = Image.new("RGB", (W, H), WHITE)
    band = chrome(im, sp["accent"], idx, total, sp["caption"])
    place_fig(im, sp["fig"], 112, band-14)
    im.save(os.path.join(OUT, f"scene_{idx:02d}.png"))

def scene_title(sp, idx, total):
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)
    ac = hx(sp["accent"])
    d.rectangle([0, 0, W, 10], fill=ac)
    d.rectangle([0, H-10, W, H], fill=ac)
    # kicker
    kf = font(True, 26)
    kw = tracked_w(d, sp["kicker"], kf, 5)
    tracked(d, ((W-kw)/2, 300), sp["kicker"], kf, ac, 5)
    # wordmark big
    bf = font(True, 82)
    bw = tracked_w(d, "VALUE DYNAMICS", bf, 6)
    tracked(d, ((W-bw)/2, 360), "VALUE DYNAMICS", bf, WORD, 6)
    # rule
    d.line([(W-260)/2, 486, (W+260)/2, 486], fill=ac, width=4)
    # subtitle question
    sf = font(False, 44)
    for i, ln in enumerate(wrap(d, sp["sub"], sf, 1200)):
        lw = d.textlength(ln, font=sf)
        d.text(((W-lw)/2, 540+i*62), ln, font=sf, fill=SUB)
    # footer chips
    ff = font(True, 27)
    fw = d.textlength(sp["foot"], font=ff)
    d.text(((W-fw)/2, 760), sp["foot"], font=ff, fill=blend(SUB, ac, 0.4))
    im.save(os.path.join(OUT, f"scene_{idx:02d}.png"))

def scene_closing(sp, idx, total):
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)
    ac = hx(sp["accent"])
    d.rectangle([0, 0, W, 10], fill=ac)
    d.rectangle([0, H-10, W, H], fill=ac)
    kicker = sp.get("kicker", "BEFORE YOU TRAIN ON SELECTED ANSWERS, CHECK THREE THINGS")
    kf = font(True, 26)
    kw = tracked_w(d, kicker, kf, 3)
    tracked(d, ((W-kw)/2, 150), kicker, kf, ac, 3)
    checks = sp.get("checks", [
        ("1", "Do the candidate answers actually vary", "on the value you care about?"),
        ("2", "Does your judge grip that variation", "and pull it one way?"),
        ("3", "Who supplied the answers", "you are about to keep?"),
    ])
    nf = font(True, 40)
    y = 268
    for num, l1, l2 in checks:
        # numbered disc
        cx, cy = 380, y+30
        d.ellipse([cx-34, cy-34, cx+34, cy+34], fill=ac)
        numf = font(True, 40)
        nw = d.textlength(num, font=numf)
        d.text((cx-nw/2, cy-27), num, font=numf, fill=WHITE)
        d.text((cx+70, y), l1, font=nf, fill=INK)
        d.text((cx+70, y+50), l2, font=font(False, 34), fill=SUB)
        y += 150
    # closing line
    cl = sp.get("closer", "A stated preference isn't grip.  The source of the data is part of the intervention.")
    clf = font(True, 34)
    clw = d.textlength(cl, font=clf)
    d.rectangle([0, 852, W, 968], fill=blend(WHITE, ac, 0.10))
    d.rectangle([0, 852, W, 856], fill=ac)
    d.text(((W-clw)/2, 892), cl, font=clf, fill=blend(ac, INK, 0.2))
    im.save(os.path.join(OUT, f"scene_{idx:02d}.png"))

SCENES = json.load(open(SCENES_FILE))
total = len(SCENES)
for i, sp in enumerate(SCENES):
    if sp["kind"] == "title":
        scene_title(sp, i, total)
    elif sp["kind"] == "closing":
        scene_closing(sp, i, total)
    else:
        scene_fig(sp, i, total)
    print("built", i, sp.get("caption", sp["kind"]))
print("done", total, "scenes")
