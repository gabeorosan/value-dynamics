#!/usr/bin/env python3
"""Build a 3–5 minute Value Dynamics demo from a scene specification."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
WORK = Path("/private/tmp/value-dynamics-writeup-demo")
QL = WORK / "ql"
SCENES_FILE = sys.argv[1] if len(sys.argv) > 1 else "scenes_writeup.json"
STEM = sys.argv[2] if len(sys.argv) > 2 else "value_dynamics_writeup_demo"
FRAMES = WORK / f"frames_{STEM}"
AUDIO = WORK / f"audio_{STEM}"
OUT = WORK / f"out_{STEM}"
SCENES_PATH = ROOT / "demo/src" / SCENES_FILE
FINAL = ROOT / "demo" / f"{STEM}.mp4"
SITE_FINAL = ROOT / "site/media" / f"{STEM}.mp4"
SUBTITLES = ROOT / "demo" / f"{STEM}.srt"
POSTER = ROOT / "demo" / f"{STEM}_poster.png"

W, H = 1920, 1080
FPS = 30
CROSSFADE = 0.55
LEAD = 0.45
TAIL = 0.85
CARD_TAIL = 1.25

# Narration voice. VD_TTS=say falls back to the local macOS voice (offline, but
# noticeably robotic); the default is an edge-tts neural voice and needs network.
TTS = os.environ.get("VD_TTS", "edge")
VOICE = os.environ.get("VD_VOICE", "en-US-AndrewMultilingualNeural")
RATE = os.environ.get("VD_RATE", "+4%")

REG = "/System/Library/Fonts/Supplemental/Arial.ttf"
BLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

WHITE = (255, 255, 255)
INK = (27, 36, 54)
SUB = (91, 101, 122)
FAINT = (154, 166, 182)
HAIR = (231, 236, 243)
WORD = (38, 50, 76)


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode:
        print(proc.stdout)
        print(proc.stderr)
        raise SystemExit(f"Command failed: {' '.join(cmd[:6])}")
    return proc


def duration(path: Path) -> float:
    proc = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
    )
    return float(proc.stdout.strip())


def font(bold: bool, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(BLD if bold else REG, size)


def hex_color(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def blend(a: tuple[int, int, int], b: tuple[int, int, int], t: float):
    return tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3))


def trim(image: Image.Image, pad: int = 26) -> Image.Image:
    image = image.convert("RGB")
    background = Image.new("RGB", image.size, WHITE)
    diff = ImageChops.difference(image, background)
    diff = diff.point(lambda pixel: 0 if pixel < 14 else 255)
    box = diff.getbbox()
    if not box:
        return image
    left, top, right, bottom = box
    return image.crop(
        (
            max(0, left - pad),
            max(0, top - pad),
            min(image.width, right + pad),
            min(image.height, bottom + pad),
        )
    )


def wrap(draw: ImageDraw.ImageDraw, text: str, text_font, max_width: int):
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=text_font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def tracked(draw, xy, text, text_font, fill, spacing):
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=text_font, fill=fill)
        x += draw.textlength(char, font=text_font) + spacing


def tracked_width(draw, text, text_font, spacing):
    return (
        sum(draw.textlength(char, font=text_font) + spacing for char in text)
        - spacing
    )


def chrome(image: Image.Image, accent: str, index: int, total: int, caption: str):
    draw = ImageDraw.Draw(image)
    accent_rgb = hex_color(accent)
    draw.rectangle([0, 0, W, 6], fill=accent_rgb)
    word_font = font(True, 25)
    tracked(draw, (80, 34), "VALUE DYNAMICS", word_font, WORD, 3)
    counter_font = font(True, 22)
    label = f"{index + 1:02d} / {total:02d}"
    draw.text(
        (W - 80 - draw.textlength(label, font=counter_font), 36),
        label,
        font=counter_font,
        fill=FAINT,
    )
    draw.line([80, 92, W - 80, 92], fill=HAIR, width=2)
    band_top = 986
    draw.rectangle([0, band_top, W, H], fill=blend(WHITE, accent_rgb, 0.10))
    draw.rectangle([0, band_top, W, band_top + 4], fill=accent_rgb)
    caption_font = font(True, 32)
    width = draw.textlength(caption, font=caption_font)
    draw.text(
        ((W - width) / 2, band_top + 27),
        caption,
        font=caption_font,
        fill=blend(accent_rgb, INK, 0.25),
    )
    return band_top


def place_figure(image: Image.Image, filename: str, top: int, bottom: int):
    source = QL / filename
    if not source.exists():
        raise SystemExit(
            f"Missing rendered figure: {source}\n"
            "Render the SVG inputs with qlmanage before running this script."
        )
    figure = trim(Image.open(source))
    available_width = W - 160
    available_height = bottom - top
    scale = min(available_width / figure.width, available_height / figure.height)
    new_size = (round(figure.width * scale), round(figure.height * scale))
    figure = figure.resize(new_size, Image.Resampling.LANCZOS)
    image.paste(
        figure,
        ((W - figure.width) // 2, top + (available_height - figure.height) // 2),
    )


def build_figure_scene(scene, index: int, total: int):
    image = Image.new("RGB", (W, H), WHITE)
    band = chrome(image, scene["accent"], index, total, scene["caption"])
    place_figure(image, scene["fig"], 112, band - 14)
    image.save(FRAMES / f"scene_{index:02d}.png")


def build_title_scene(scene, index: int, total: int):
    image = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(image)
    accent = hex_color(scene["accent"])
    draw.rectangle([0, 0, W, 10], fill=accent)
    draw.rectangle([0, H - 10, W, H], fill=accent)

    kicker_font = font(True, 26)
    kicker_width = tracked_width(draw, scene["kicker"], kicker_font, 5)
    tracked(
        draw,
        ((W - kicker_width) / 2, 275),
        scene["kicker"],
        kicker_font,
        accent,
        5,
    )

    title_font = font(True, 84)
    title = "VALUE DYNAMICS"
    title_width = tracked_width(draw, title, title_font, 6)
    tracked(
        draw,
        ((W - title_width) / 2, 345),
        title,
        title_font,
        WORD,
        6,
    )
    draw.line([(W - 260) / 2, 475, (W + 260) / 2, 475], fill=accent, width=4)

    subtitle_font = font(False, 45)
    lines = wrap(draw, scene["sub"], subtitle_font, 1250)
    for line_index, line in enumerate(lines):
        width = draw.textlength(line, font=subtitle_font)
        draw.text(
            ((W - width) / 2, 535 + line_index * 63),
            line,
            font=subtitle_font,
            fill=SUB,
        )

    footer_font = font(True, 27)
    footer_width = draw.textlength(scene["foot"], font=footer_font)
    draw.text(
        ((W - footer_width) / 2, 770),
        scene["foot"],
        font=footer_font,
        fill=blend(SUB, accent, 0.4),
    )
    image.save(FRAMES / f"scene_{index:02d}.png")


def build_closing_scene(scene, index: int, total: int):
    image = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(image)
    accent = hex_color(scene["accent"])
    draw.rectangle([0, 0, W, 10], fill=accent)
    draw.rectangle([0, H - 10, W, H], fill=accent)

    kicker_font = font(True, 27)
    kicker_width = tracked_width(draw, scene["kicker"], kicker_font, 3)
    tracked(
        draw,
        ((W - kicker_width) / 2, 142),
        scene["kicker"],
        kicker_font,
        accent,
        3,
    )

    heading_font = font(True, 40)
    detail_font = font(False, 34)
    y = 260
    for number, heading, detail in scene["checks"]:
        center_x, center_y = 370, y + 33
        draw.ellipse(
            [center_x - 34, center_y - 34, center_x + 34, center_y + 34],
            fill=accent,
        )
        number_font = font(True, 40)
        width = draw.textlength(number, font=number_font)
        draw.text(
            (center_x - width / 2, center_y - 27),
            number,
            font=number_font,
            fill=WHITE,
        )
        draw.text((center_x + 72, y), heading, font=heading_font, fill=INK)
        draw.text(
            (center_x + 72, y + 52),
            detail,
            font=detail_font,
            fill=SUB,
        )
        y += 160

    draw.rectangle([0, 850, W, 968], fill=blend(WHITE, accent, 0.10))
    draw.rectangle([0, 850, W, 854], fill=accent)
    closer_font = font(True, 32)
    closer_width = draw.textlength(scene["closer"], font=closer_font)
    draw.text(
        ((W - closer_width) / 2, 892),
        scene["closer"],
        font=closer_font,
        fill=blend(accent, INK, 0.2),
    )
    image.save(FRAMES / f"scene_{index:02d}.png")


def build_statement_scene(scene, index: int, total: int):
    """Full-bleed type card: a headline held on screen with no figure."""
    image = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(image)
    accent = hex_color(scene["accent"])
    draw.rectangle([0, 0, W, 6], fill=accent)
    draw.rectangle([0, H - 6, W, H], fill=accent)

    kicker = scene.get("kicker")
    kicker_font = font(True, 26)
    headline_font = font(True, 66)
    sub_font = font(False, 40)

    headline_lines = wrap(draw, scene["headline"], headline_font, 1480)
    sub_lines = wrap(draw, scene["sub"], sub_font, 1320) if scene.get("sub") else []

    block = len(headline_lines) * 88
    if kicker:
        block += 96
    if sub_lines:
        block += 92 + len(sub_lines) * 56
    y = (H - block) / 2

    if kicker:
        kicker_width = tracked_width(draw, kicker, kicker_font, 5)
        tracked(draw, ((W - kicker_width) / 2, y), kicker, kicker_font, accent, 5)
        y += 96

    for line in headline_lines:
        width = draw.textlength(line, font=headline_font)
        draw.text(((W - width) / 2, y), line, font=headline_font, fill=WORD)
        y += 88

    if sub_lines:
        draw.line([(W - 200) / 2, y + 30, (W + 200) / 2, y + 30], fill=accent, width=4)
        y += 92
        for line in sub_lines:
            width = draw.textlength(line, font=sub_font)
            draw.text(((W - width) / 2, y), line, font=sub_font, fill=SUB)
            y += 56
    image.save(FRAMES / f"scene_{index:02d}.png")


def srt_time(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    secs, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def main():
    for directory in (FRAMES, AUDIO, OUT):
        directory.mkdir(parents=True, exist_ok=True)

    scenes = json.loads(SCENES_PATH.read_text())
    total_scenes = len(scenes)

    for index, scene in enumerate(scenes):
        if scene["kind"] == "title":
            build_title_scene(scene, index, total_scenes)
        elif scene["kind"] == "closing":
            build_closing_scene(scene, index, total_scenes)
        elif scene["kind"] == "statement":
            build_statement_scene(scene, index, total_scenes)
        else:
            build_figure_scene(scene, index, total_scenes)

    shutil.copy2(FRAMES / "scene_00.png", POSTER)

    narration_durations: list[float] = []
    for index, scene in enumerate(scenes):
        wav_path = AUDIO / f"scene_{index:02d}.wav"
        if TTS == "say":
            raw_path = AUDIO / f"scene_{index:02d}.aiff"
            run(
                [
                    "say",
                    "-v",
                    "Samantha",
                    "-r",
                    "185",
                    "-o",
                    str(raw_path),
                    scene["narration"],
                ]
            )
        else:
            raw_path = AUDIO / f"scene_{index:02d}.mp3"
            run(
                [
                    "uv",
                    "run",
                    "--quiet",
                    "--with",
                    "edge-tts",
                    "edge-tts",
                    "--voice",
                    VOICE,
                    "--rate",
                    RATE,
                    "--text",
                    scene["narration"],
                    "--write-media",
                    str(raw_path),
                ]
            )
        run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(raw_path),
                "-af",
                "silenceremove=start_periods=1:start_threshold=-45dB:"
                "start_silence=0.05,areverse,"
                "silenceremove=start_periods=1:start_threshold=-45dB:"
                "start_silence=0.12,areverse",
                "-ar",
                "44100",
                "-ac",
                "2",
                str(wav_path),
            ]
        )
        narration_durations.append(duration(wav_path))

    clip_durations: list[float] = []
    for index, scene in enumerate(scenes):
        tail = CARD_TAIL if scene["kind"] in ("title", "closing", "statement") else TAIL
        clip_durations.append(LEAD + narration_durations[index] + tail)

    starts = [
        sum(clip_durations[:index]) - index * CROSSFADE
        for index in range(total_scenes)
    ]
    narration_starts = [
        starts[index] + (CROSSFADE if index else LEAD)
        for index in range(total_scenes)
    ]
    total_duration = sum(clip_durations) - (total_scenes - 1) * CROSSFADE

    video_inputs: list[str] = []
    for index, clip_duration in enumerate(clip_durations):
        video_inputs.extend(
            [
                "-loop",
                "1",
                "-t",
                f"{clip_duration:.3f}",
                "-i",
                str(FRAMES / f"scene_{index:02d}.png"),
            ]
        )

    filters: list[str] = []
    for index, clip_duration in enumerate(clip_durations):
        chain = (
            f"[{index}:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
            f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2:white,setsar=1,"
            f"fps={FPS},format=yuv420p,settb=AVTB"
        )
        if index == 0:
            chain += ",fade=t=in:st=0:d=0.55:color=white"
        if index == total_scenes - 1:
            chain += (
                f",fade=t=out:st={clip_duration - 0.7:.3f}:"
                "d=0.7:color=white"
            )
        filters.append(chain + f"[v{index}]")

    previous = "v0"
    for index in range(1, total_scenes):
        output = f"x{index}" if index < total_scenes - 1 else "vout"
        filters.append(
            f"[{previous}][v{index}]xfade=transition=fade:"
            f"duration={CROSSFADE}:offset={starts[index]:.3f}[{output}]"
        )
        previous = output

    silent_video = OUT / f"{STEM}_silent.mp4"
    run(
        [
            "ffmpeg",
            "-y",
            *video_inputs,
            "-filter_complex",
            ";".join(filters),
            "-map",
            "[vout]",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "18",
            "-preset",
            "medium",
            "-r",
            str(FPS),
            "-t",
            f"{total_duration:.3f}",
            str(silent_video),
        ]
    )

    audio_inputs: list[str] = []
    for index in range(total_scenes):
        audio_inputs.extend(["-i", str(AUDIO / f"scene_{index:02d}.wav")])
    audio_filters = []
    for index in range(total_scenes):
        delay_ms = round(narration_starts[index] * 1000)
        audio_filters.append(
            f"[{index}:a]adelay={delay_ms}|{delay_ms}[a{index}]"
        )
    mix_inputs = "".join(f"[a{index}]" for index in range(total_scenes))
    audio_filters.append(
        f"{mix_inputs}amix=inputs={total_scenes}:normalize=0:"
        "dropout_transition=0[mix]"
    )
    audio_filters.append(
        f"[mix]apad,atrim=0:{total_duration:.3f},aresample=44100,"
        "loudnorm=I=-16:TP=-1.5:LRA=11[aout]"
    )

    narration = OUT / f"{STEM}_narration.wav"
    run(
        [
            "ffmpeg",
            "-y",
            *audio_inputs,
            "-filter_complex",
            ";".join(audio_filters),
            "-map",
            "[aout]",
            str(narration),
        ]
    )

    subtitle_blocks = []
    subtitle_index = 1
    for index, scene in enumerate(scenes):
        sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", scene["narration"])
            if sentence.strip()
        ]
        word_counts = [max(1, len(sentence.split())) for sentence in sentences]
        total_words = sum(word_counts)
        cursor = narration_starts[index]
        for sentence, word_count in zip(sentences, word_counts):
            sentence_duration = narration_durations[index] * word_count / total_words
            end = cursor + sentence_duration
            subtitle_blocks.append(
                f"{subtitle_index}\n{srt_time(cursor)} --> {srt_time(end)}\n"
                f"{sentence}\n"
            )
            subtitle_index += 1
            cursor = end
    SUBTITLES.write_text("\n".join(subtitle_blocks))

    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(silent_video),
            "-i",
            str(narration),
            "-i",
            str(SUBTITLES),
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-map",
            "2:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-c:s",
            "mov_text",
            "-metadata:s:s:0",
            "language=eng",
            "-movflags",
            "+faststart",
            "-shortest",
            str(FINAL),
        ]
    )
    if os.environ.get("VD_NO_SITE_COPY") != "1":
        shutil.copy2(FINAL, SITE_FINAL)
    print(f"Built {FINAL}")
    print(f"Duration: {duration(FINAL):.2f} seconds")


if __name__ == "__main__":
    main()
