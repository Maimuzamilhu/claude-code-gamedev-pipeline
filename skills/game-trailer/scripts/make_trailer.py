"""Assemble a trailer with ffmpeg: grade, fades, captions, title card, and a voice-forward sound mix.

  python make_trailer.py trailer.json               build video from frame folders + mix sound
  python make_trailer.py trailer.json --audio-only  keep the picture of cfg["video"], replace the sound

See ../references/trailer.example.json for every field. Needs ffmpeg on PATH (Python stdlib only).

Audio cue times: seconds, "shot2+0.6" (0.6 s after shot 2 starts) or "title+0.05".
Cues with "voice": true are loudness-matched, given presence, and the rest of the mix DUCKS under
them (sidechain compression) so every word is heard, even on phone speakers. The final mix is
mastered to -14 LUFS / -1.5 dBTP (what YouTube and most platforms play at).
"""
import json
import os
import re
import subprocess
import sys

GRADE = ("eq=contrast=1.12:brightness=0.03:saturation=1.15:gamma=1.15,"
         "colorbalance=bs=0.08:rh=0.05:rm=0.03,vignette=PI/6")


def run(args):
    r = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y"] + args, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(r.stderr[-2000:])


def ff_path(p):
    """Font paths inside an ffmpeg filter need the drive colon escaped (C\\:/...)."""
    return os.path.abspath(p).replace("\\", "/").replace(":", "\\:")


def esc(text):
    return text.replace("\\", "\\\\").replace("'", "’").replace(":", "\\:").replace("%", "\\%")


def build_video(cfg, rel, work):
    """Render shots + title from frame folders. Returns (video_path, shot_durations)."""
    fps = cfg.get("fps", 30)
    W, H = cfg.get("size", [1920, 1080])
    font, font2 = ff_path(rel(cfg["font_title"])), ff_path(rel(cfg.get("font_body", cfg["font_title"])))
    grade = cfg.get("grade", GRADE)
    segs = []
    for i, shot in enumerate(cfg["shots"]):
        folder = rel(shot["frames"])
        n = len([f for f in os.listdir(folder) if f.endswith(".jpg")])
        dur = n / float(fps)
        vf = "scale=%d:%d,%s,fade=t=in:st=0:d=0.25,fade=t=out:st=%.2f:d=0.25" % (W, H, grade, dur - 0.25)
        cap = shot.get("caption", "")
        if cap:
            vf += (",drawtext=fontfile='%s':text='%s':fontsize=%d:fontcolor=white:x=(w-text_w)/2:y=h-%d:"
                   "shadowcolor=black@0.85:shadowx=4:shadowy=4:"
                   "alpha='if(lt(t,0.5),0,if(lt(t,0.9),(t-0.5)/0.4,if(gt(t,%.2f),max(0,(%.2f-t)/0.35),1)))'"
                   % (font, esc(cap), int(H * 0.085), int(H * 0.21), dur - 0.5, dur - 0.15))
        seg = os.path.join(work, "seg%02d.mp4" % i)
        run(["-framerate", str(fps), "-i", os.path.join(folder, shot.get("pattern", "f_%04d.jpg")),
             "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(fps), seg])
        segs.append((seg, dur))
        print("shot %d: %.2f s  %s" % (i + 1, dur, cap))

    lead = cfg.get("black_lead", 1.0)
    run(["-f", "lavfi", "-i", "color=c=black:s=%dx%d:r=%d:d=%s" % (W, H, fps, lead),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", os.path.join(work, "black.mp4")])
    title = cfg["title"]
    td = title.get("seconds", 4.7)
    tvf = ("drawtext=fontfile='%s':text='%s':fontsize=%d:fontcolor=0xE6E9EE:x=(w-text_w)/2:y=(h-text_h)/2-%d:"
           "alpha='if(lt(t,0.3),0,min(1,(t-0.3)/0.5))'" % (font, esc(title["text"]), int(H * 0.19), int(H * 0.055)))
    if title.get("accent", True):
        tvf += (",drawbox=x=(iw/2)-14:y=(ih/2)-%d:w=28:h=28:color=%s@1:t=fill:enable='gt(t,0.9)'"
                % (int(H * 0.23), title.get("accent_color", "0xD8261E")))
    if title.get("tagline"):
        tvf += (",drawtext=fontfile='%s':text='%s':fontsize=%d:fontcolor=0x9AA3AE:x=(w-text_w)/2:y=(h/2)+%d:"
                "alpha='if(lt(t,1.1),0,min(1,(t-1.1)/0.5))'" % (font2, esc(title["tagline"]), int(H * 0.043), int(H * 0.1)))
    tvf += ",fade=t=out:st=%.2f:d=0.5" % (td - 0.5)
    run(["-f", "lavfi", "-i", "color=c=black:s=%dx%d:r=%d:d=%s" % (W, H, fps, td), "-vf", tvf,
         "-c:v", "libx264", "-pix_fmt", "yuv420p", os.path.join(work, "title.mp4")])

    parts = [os.path.join(work, "black.mp4")] + [s for s, _ in segs] + [os.path.join(work, "title.mp4")]
    with open(os.path.join(work, "list.txt"), "w") as f:
        for p in parts:
            f.write("file '%s'\n" % p.replace("\\", "/"))
    video = os.path.join(work, "video.mp4")
    run(["-f", "concat", "-safe", "0", "-i", os.path.join(work, "list.txt"), "-c", "copy", video])
    return video, [d for _, d in segs]


def mix_audio(cues, rel, starts, title_at, total, out_audio):
    """Bed (ambience, sfx, music) ducks under the voice bus; master to -14 LUFS."""
    def when(v):
        if isinstance(v, (int, float)):
            return float(v)
        m = re.match(r"(shot(\d+)|title)\s*([+-]\s*[\d.]+)?$", v.replace(" ", ""))
        at = title_at if m.group(1) == "title" else starts[int(m.group(2)) - 1]
        return at + (float(m.group(3).replace(" ", "")) if m.group(3) else 0.0)

    args, filt, bed, vox = [], [], [], []
    for i, c in enumerate(cues):
        if c.get("loop"):
            args += ["-stream_loop", "-1"]
        args += ["-i", rel(c["file"])]
        ms = int(when(c.get("at", 0)) * 1000)
        trim = ",atrim=0:%.2f" % total if c.get("loop") else ""
        if c.get("voice"):
            # same loudness for every line, a little presence, no rumble
            chain = ("loudnorm=I=-16:TP=-2,aresample=48000,highpass=f=90,"
                     "equalizer=f=2800:t=q:w=1.2:g=4,aformat=sample_rates=48000:channel_layouts=stereo,"
                     "volume=%s,adelay=%d|%d" % (c.get("volume", 1.0), ms, ms))
            filt.append("[%d:a]%s[v%d]" % (i, chain, i))
            vox.append("[v%d]" % i)
        else:
            filt.append("[%d:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=%s,adelay=%d|%d%s[b%d]"
                        % (i, c.get("volume", 1.0), ms, ms, trim, i))
            bed.append("[b%d]" % i)
    filt.append("".join(bed) + "amix=inputs=%d:normalize=0,atrim=0:%.2f[bed]" % (len(bed), total))
    if vox:
        filt.append("".join(vox) + "amix=inputs=%d:normalize=0,apad,atrim=0:%.2f,asplit=2[vox][key]" % (len(vox), total))
        # duck the bed about 10 dB while anyone speaks; fast attack, slow release so it breathes
        filt.append("[bed][key]sidechaincompress=threshold=0.015:ratio=10:attack=15:release=450:makeup=1[ducked]")
        filt.append("[ducked][vox]amix=inputs=2:normalize=0[mix]")
    else:
        filt.append("[bed]anull[mix]")
    filt.append("[mix]afade=t=in:st=0:d=0.8,afade=t=out:st=%.2f:d=1.2,"
                "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,atrim=0:%.2f[out]" % (total - 1.2, total))
    run(args + ["-filter_complex", ";".join(filt), "-map", "[out]", "-c:a", "aac", "-b:a", "192k", out_audio])


def main(cfg_path, audio_only=False):
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(cfg_path))
    rel = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    work = rel(cfg.get("work_dir", "trailer_work"))
    os.makedirs(work, exist_ok=True)
    lead = cfg.get("black_lead", 1.0)
    td = cfg["title"].get("seconds", 4.7)

    if audio_only:
        video = rel(cfg["video"])                  # an existing trailer: keep its picture
        durs = cfg["shot_seconds"]                 # lengths of its shots, for "shotN+x" cue times
    else:
        video, durs = build_video(cfg, rel, work)

    starts, t = [], lead
    for d in durs:
        starts.append(t)
        t += d
    title_at, total = t, t + td

    out = rel(cfg["output"])
    cues = cfg.get("audio", [])
    if not cues:
        run(["-i", video, "-c", "copy", "-an", out])
        print("wrote", out, "(no audio)")
        return
    audio = os.path.join(work, "audio.m4a")
    mix_audio(cues, rel, starts, title_at, total, audio)
    run(["-i", video, "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "copy", "-shortest", out])
    print("wrote %s  (%.1f s, shots start at %s, title at %.2f)" % (out, total, [round(s, 2) for s in starts], title_at))


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if x != "--audio-only"]
    if len(a) != 1:
        print(__doc__)
    else:
        main(a[0], audio_only="--audio-only" in sys.argv)
