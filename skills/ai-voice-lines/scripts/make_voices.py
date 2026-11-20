"""Generate game voice lines with Kokoro-82M (local, free) and apply character effects.

  python make_voices.py lines.json <model_dir> <out_dir>
  python make_voices.py --voices <model_dir>          # list available voice ids

lines.json: [{"id": "...", "text": "...", "voice": "am_adam", "speed": 1.0, "fx": "radio"}, ...]
fx: none | radio | phone | robot | pa | monster | ghost | cave

Needs: pip install kokoro-onnx soundfile numpy
Model files (put both in <model_dir>):
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
Kokoro-82M weights: Apache 2.0 (https://huggingface.co/hexgrad/Kokoro-82M). kokoro-onnx: MIT.
"""
import json
import os
import sys

import numpy as np
import soundfile as sf

SR = 24000


# ---------- small DSP toolbox (numpy only) ----------
def bandpass(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1.0 / SR)
    g = 1.0 / (1.0 + (lo / np.maximum(f, 1.0)) ** 4) / (1.0 + (f / hi) ** 4)   # soft shoulders, no ringing
    return np.fft.irfft(X * g, len(x))


def pitch(x, semitones):
    k = 2.0 ** (semitones / 12.0)
    return np.interp(np.arange(0, len(x) - 1, k), np.arange(len(x)), x)


def comb(x, ms, fb):
    d = int(SR * ms / 1000.0)
    y = np.copy(x)
    for i in range(d, len(y)):
        y[i] += fb * y[i - d]
    return y


def echo(x, ms, gain):
    d = int(SR * ms / 1000.0)
    y = np.concatenate([x, np.zeros(d)])
    y[d:] += gain * x
    return y


def norm(x, peak=0.89):
    return x * (peak / (np.max(np.abs(x)) + 1e-9))


def trim(x, thr=0.01):
    nz = np.where(np.abs(x) > thr * np.max(np.abs(x)))[0]
    return x if len(nz) == 0 else x[max(0, nz[0] - 200): min(len(x), nz[-1] + 1200)]


def fade(x, ms_in=4, ms_out=60):
    a, b = int(SR * ms_in / 1000), int(SR * ms_out / 1000)
    x = np.copy(x)
    if a:
        x[:a] *= np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)
    return x


def hiss(n, amount, seed=7):
    return bandpass(np.random.default_rng(seed).normal(0, amount, n), 1500, 6000)


# ---------- character presets ----------
def fx_none(x):
    return norm(x, 0.89)


def fx_radio(x):
    x = np.tanh(norm(bandpass(x, 400, 3200)) * 2.2)
    return norm(x + hiss(len(x), 0.015), 0.85)


def fx_phone(x):
    return norm(np.tanh(norm(bandpass(x, 350, 3400)) * 1.5), 0.82)


def fx_robot(x):
    x = pitch(x, -2.5)
    x = comb(x, 5.5, 0.22)               # metallic resonance
    x = bandpass(x, 260, 3600)           # small speaker
    return norm(np.tanh(x * 1.4), 0.80)


def fx_pa(x):
    x = pitch(x, -1.0)
    x = np.tanh(norm(bandpass(x, 480, 3000)) * 3.2)     # driven PA horn
    x = echo(echo(x, 95, 0.35), 210, 0.18)              # slap-back off a big hall
    return norm(x + hiss(len(x), 0.02), 0.92)


def fx_monster(x):
    low, sub = pitch(x, -6.0), pitch(x, -12.0)          # a voice and its octave-down shadow
    n = min(len(low), len(sub))
    y = low[:n] + 0.35 * sub[:n]
    return norm(np.tanh(norm(bandpass(y, 60, 5000)) * 2.0), 0.9)


def fx_ghost(x):
    x = bandpass(pitch(x, 3.0), 300, 8000)
    x = echo(echo(x, 180, 0.4), 390, 0.25)
    return norm(x, 0.8)


def fx_cave(x):
    for ms, g in ((120, 0.45), (260, 0.3), (430, 0.2), (640, 0.12)):
        x = echo(x, ms, g)
    return norm(x, 0.88)


FX = {"none": fx_none, "radio": fx_radio, "phone": fx_phone, "robot": fx_robot, "pa": fx_pa,
      "monster": fx_monster, "ghost": fx_ghost, "cave": fx_cave}


def load_kokoro(model_dir):
    from kokoro_onnx import Kokoro
    return Kokoro(os.path.join(model_dir, "kokoro-v1.0.onnx"), os.path.join(model_dir, "voices-v1.0.bin"))


def main(lines_path, model_dir, out_dir):
    k = load_kokoro(model_dir)
    os.makedirs(out_dir, exist_ok=True)
    with open(lines_path, encoding="utf-8") as f:
        lines = json.load(f)
    for ln in lines:
        samples, sr = k.create(ln["text"], voice=ln.get("voice", "af_heart"),
                               speed=float(ln.get("speed", 1.0)), lang=ln.get("lang", "en-us"))
        x = np.asarray(samples, dtype=np.float64)
        if sr != SR:
            x = np.interp(np.arange(0, len(x), sr / SR), np.arange(len(x)), x)
        fx = FX.get(ln.get("fx", "none"), fx_none)
        y = fade(fx(trim(x)))
        path = os.path.join(out_dir, ln["id"] + ".wav")
        sf.write(path, y.astype(np.float32), SR, subtype="PCM_16")
        print("%-28s %-9s %-8s %.2f s" % (ln["id"], ln.get("voice"), ln.get("fx", "none"), len(y) / SR))


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 2 and a[0] == "--voices":
        print(", ".join(sorted(load_kokoro(a[1]).get_voices())))
    elif len(a) == 3:
        main(*a)
    else:
        print(__doc__)
