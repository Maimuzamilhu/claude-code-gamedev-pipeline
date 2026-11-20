"""Clean sound files for a game with ffmpeg (needs ffmpeg on PATH; Python standard library only).

  python prep_sfx.py sfx   in.wav out.wav                 mono, trim silence, peak -6 dBFS, fades
  python prep_sfx.py loop  in.wav out.wav [--seconds 20]  mono, -24 LUFS, seamless crossfaded loop
  python prep_sfx.py split in.wav out_prefix [--min-gap 0.15]
                                                          one file per hit: out_prefix_00.wav, _01, ...
"""
import os
import re
import subprocess
import sys
import wave


def ff(args):
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-y"] + args, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(r.stderr[-1500:])
    return r.stderr


def duration(path):
    """Length in seconds: read WAV headers directly, fall back to ffprobe for other formats."""
    try:
        with wave.open(path, "rb") as w:
            return w.getnframes() / float(w.getframerate())
    except (wave.Error, EOFError):
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=duration", "-of", "csv=p=0", path],
                             capture_output=True, text=True).stdout
        return float(out.split()[0])


def peak_db(path):
    err = ff(["-i", path, "-af", "volumedetect", "-f", "null", "-"])
    m = re.search(r"max_volume: (-?[\d.]+) dB", err)
    return float(m.group(1)) if m else 0.0


def sound_bounds(path, below_peak_db=45.0):
    """(start, end) of the audible part: silencedetect finds the quiet head and tail.
    (silenceremove changed behaviour between ffmpeg versions; this works on all of them.)"""
    total = duration(path)
    floor_db = peak_db(path) - below_peak_db       # relative to the file's own peak: quiet takes trim too
    err = ff(["-i", path, "-af", "silencedetect=noise=%.1fdB:d=0.01" % floor_db, "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    a, b = 0.0, total
    if starts and starts[0] <= 0.001 and ends:
        a = ends[0]                                   # leading silence
    if starts and starts[-1] > a and len(ends) < len(starts):
        b = starts[-1]                                # trailing silence runs to the end of the file
    return max(0.0, a - 0.005), min(total, b + 0.05)


def sfx(src, dst, peak=-6.0):
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    mono = dst + ".mono.wav"
    tmp = dst + ".tmp.wav"
    ff(["-i", src, "-ac", "1", "-ar", "44100", "-c:a", "pcm_s16le", mono])
    a, b = sound_bounds(mono)
    ff(["-i", mono, "-ss", "%.3f" % a, "-to", "%.3f" % b, "-c:a", "pcm_s16le", tmp])
    os.remove(mono)
    gain = peak - peak_db(tmp)
    d = duration(tmp)
    ff(["-i", tmp, "-af", "volume=%.2fdB,afade=t=in:d=0.003,afade=t=out:st=%.3f:d=0.03" % (gain, max(0, d - 0.03)),
        "-c:a", "pcm_s16le", dst])
    os.remove(tmp)
    print("sfx  %-40s %.2f s, peak %.1f dBFS" % (os.path.basename(dst), d, peak))


def loop(src, dst, seconds=None, lufs=-24.0, xfade=1.5):
    """Seamless loop: the last `xfade` seconds are blended into the first, then removed."""
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    tmp = dst + ".tmp.wav"
    cut = ["-t", str(seconds + xfade)] if seconds else []
    ff(["-i", src] + cut + ["-ac", "1", "-ar", "44100", "-af", "loudnorm=I=%s:TP=-3:LRA=11" % lufs, "-ar", "44100", "-c:a", "pcm_s16le", tmp])
    d = duration(tmp)
    body = d - xfade
    # head of the loop = crossfade(tail -> head); result length = body
    ff(["-i", tmp, "-filter_complex",
        "[0]atrim=0:%.3f,asetpts=PTS-STARTPTS[a];[0]atrim=%.3f:%.3f,asetpts=PTS-STARTPTS[t];"
        "[0]atrim=0:%.3f,asetpts=PTS-STARTPTS[h];[t][h]acrossfade=d=%.3f:c1=tri:c2=tri[x];"
        "[a]atrim=%.3f,asetpts=PTS-STARTPTS[rest];[x][rest]concat=n=2:v=0:a=1[o]"
        % (body, body, d, xfade, xfade, xfade),
        "-map", "[o]", "-c:a", "pcm_s16le", dst])
    os.remove(tmp)
    print("loop %-40s %.2f s at %s LUFS" % (os.path.basename(dst), duration(dst), lufs))


def split(src, prefix, min_gap=0.15):
    err = ff(["-i", src, "-af", "silencedetect=noise=-40dB:d=%s" % min_gap, "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    total = duration(src)
    edges = sorted(set([0.0] + ends))      # a hit starts where a silence ends
    hits = []
    for s in edges:
        nxt = [t for t in starts if t > s + 0.02]
        e = nxt[0] if nxt else total
        if e - s > 0.04:
            hits.append((s, e))
    for i, (s, e) in enumerate(hits):
        part = "%s_%02d.raw.wav" % (prefix, i)
        os.makedirs(os.path.dirname(os.path.abspath(part)), exist_ok=True)
        ff(["-i", src, "-ss", "%.3f" % s, "-to", "%.3f" % min(total, e + 0.05), "-c:a", "pcm_s16le", part])
        sfx(part, "%s_%02d.wav" % (prefix, i))
        os.remove(part)
    print("split: %d files" % len(hits))


if __name__ == "__main__":
    a = sys.argv[1:]
    opt = lambda name, default: float(a[a.index(name) + 1]) if name in a else default
    if len(a) >= 3 and a[0] == "sfx":
        sfx(a[1], a[2])
    elif len(a) >= 3 and a[0] == "loop":
        loop(a[1], a[2], seconds=opt("--seconds", None))
    elif len(a) >= 3 and a[0] == "split":
        split(a[1], a[2], min_gap=opt("--min-gap", 0.15))
    else:
        print(__doc__)
