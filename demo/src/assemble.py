#!/usr/bin/env python3
"""Generate narration, time it, and assemble the Value Dynamics demo MP4."""
import json, os, subprocess, sys

WORK = "/private/tmp/claude-501/-Users-gabriel-projects-value-dynamics/f063f126-f02b-4c97-87b5-48c6951e01c6/scratchpad/video"
SCENES_FILE = sys.argv[1] if len(sys.argv) > 1 else "scenes.json"
SC = os.path.join(WORK, sys.argv[2] if len(sys.argv) > 2 else "scenes")
VARIANT = sys.argv[3] if len(sys.argv) > 3 else "value_dynamics_demo"
OUT = os.path.join(WORK, "out")
AUD = os.path.join(WORK, "audio", VARIANT)
os.makedirs(OUT, exist_ok=True); os.makedirs(AUD, exist_ok=True)

VOICE = os.environ.get("VD_VOICE", "en-US-AndrewNeural")  # edge-tts neural voice
RATE = os.environ.get("VD_RATE", "+4%")
T = 0.6          # crossfade duration
LEAD = 0.6       # silent head before narration in each scene
TAIL = 1.1       # silent tail after narration
TAIL_CARD = 1.6  # longer tail for title/closing
FPS = 30

def run(cmd, **kw):
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if p.returncode != 0:
        sys.stderr.write("CMD FAILED: " + " ".join(str(c) for c in cmd[:6]) + " ...\n")
        sys.stderr.write(p.stderr[-3000:] + "\n")
        raise SystemExit(1)
    return p

def dur(path):
    p = run(["ffprobe","-v","error","-show_entries","format=duration",
             "-of","default=noprint_wrappers=1:nokey=1", path])
    return float(p.stdout.strip())

scenes = json.load(open(os.path.join(WORK, SCENES_FILE)))
N = len(scenes)

# 1. TTS per scene -> wav, measure duration
D = []
for i, sp in enumerate(scenes):
    mp3 = os.path.join(AUD, f"n_{i}.mp3")
    wav = os.path.join(AUD, f"n_{i}.wav")
    run(["uv","run","--quiet","--with","edge-tts","edge-tts",
         "--voice", VOICE, "--rate", RATE,
         "--text", sp["narration"], "--write-media", mp3])
    # trim leading/trailing silence the service adds, then normalize format
    run(["ffmpeg","-y","-i",mp3,
         "-af","silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
               "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.15,areverse",
         "-ar","44100","-ac","2", wav])
    D.append(dur(wav))
    print(f"scene {i}: narration {D[-1]:.2f}s")

# 2. clip durations and timeline offsets
d = []
for i, sp in enumerate(scenes):
    tail = TAIL_CARD if sp["kind"] in ("title","closing") else TAIL
    d.append(LEAD + D[i] + tail)

total = sum(d) - (N-1)*T
# scene visible start (== xfade offset for adding scene i, i>=1)
S = []
acc = 0.0
for i in range(N):
    S.append(acc - i*T + (0 if i==0 else 0))  # placeholder, recompute below
# recompute cleanly: S_i = sum_{j<i} d_j - i*T
S = []
for i in range(N):
    S.append(sum(d[:i]) - i*T)
narr_start = [S[i] + T for i in range(N)]
print(f"total video = {total:.2f}s  ({total/60:.2f} min)")

# 3. VIDEO: xfade chain over looped stills
vin = []
for i in range(N):
    vin += ["-loop","1","-t", f"{d[i]:.3f}", "-i", os.path.join(SC, f"scene_{i:02d}.png")]
fc = []
for i in range(N):
    chain = f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=decrease," \
            f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2:white,setsar=1,fps={FPS},format=yuv420p,settb=AVTB"
    if i == 0:
        chain += ",fade=t=in:st=0:d=0.6:color=white"
    if i == N-1:
        chain += f",fade=t=out:st={d[i]-0.8:.3f}:d=0.8:color=white"
    fc.append(chain + f"[v{i}]")
prev = "v0"
off = [sum(d[:k]) - k*T for k in range(N)]  # off[k] for k>=1
for k in range(1, N):
    out = f"x{k}" if k < N-1 else "vout"
    fc.append(f"[{prev}][v{k}]xfade=transition=fade:duration={T}:offset={off[k]:.3f}[{out}]")
    prev = out
filt = ";".join(fc)
vsilent = os.path.join(OUT, f"{VARIANT}_silent.mp4")
run(["ffmpeg","-y", *vin, "-filter_complex", filt, "-map","[vout]",
     "-c:v","libx264","-pix_fmt","yuv420p","-crf","18","-preset","medium",
     "-r",str(FPS), "-t", f"{total:.3f}", vsilent])
print("video_silent built:", dur(vsilent), "s")

# 4. AUDIO: delay each narration to its start, mix, pad to total
ain = []
for i in range(N):
    ain += ["-i", os.path.join(AUD, f"n_{i}.wav")]
afc = []
for i in range(N):
    ms = int(round(narr_start[i]*1000))
    afc.append(f"[{i}:a]adelay={ms}|{ms}[a{i}]")
mixins = "".join(f"[a{i}]" for i in range(N))
afc.append(f"{mixins}amix=inputs={N}:normalize=0:dropout_transition=0[mx]")
afc.append(f"[mx]apad,atrim=0:{total:.3f},aresample=44100,loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
narr = os.path.join(OUT, f"{VARIANT}_narration.wav")
run(["ffmpeg","-y", *ain, "-filter_complex", ";".join(afc), "-map","[aout]", narr])
print("narration built:", dur(narr), "s")

# 5. MUX
final = os.path.join(OUT, f"{VARIANT}.mp4")
run(["ffmpeg","-y","-i",vsilent,"-i",narr,"-map","0:v","-map","1:a",
     "-c:v","copy","-c:a","aac","-b:a","192k","-shortest", final])
print("FINAL:", final, dur(final), "s")
