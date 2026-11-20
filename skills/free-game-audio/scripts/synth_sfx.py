"""Synthesise game sounds from scratch with numpy - no samples, no licence questions.

  python synth_sfx.py <out_dir>

Writes: stinger_00..02 (tension hit), alarm_loop, chirp_up / chirp_down / chirp_updown
(robot or creature calls), drone_loop (dark ambience bed), heartbeat_rest / heartbeat_fast,
ui_blip / ui_back. Change the numbers at the top of each function to make your own.
Needs: pip install numpy
"""
import os
import sys

import wave

import numpy as np

SR = 44100


def t_axis(seconds):
    return np.linspace(0, seconds, int(SR * seconds), endpoint=False)


def bandpass(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1.0 / SR)
    g = 1.0 / (1.0 + (lo / np.maximum(f, 1.0)) ** 4) / (1.0 + (f / hi) ** 4)
    return np.fft.irfft(X * g, len(x))


def norm(x, peak=0.85):
    return x * (peak / (np.max(np.abs(x)) + 1e-9))


def fade(x, ms_in=2, ms_out=60):
    a, b = int(SR * ms_in / 1000), int(SR * ms_out / 1000)
    x = np.copy(x)
    if a:
        x[:a] *= np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)
    return x


def stinger(seed):
    """Dissonant swell into a low hit (~2.3 s): 'you have been spotted'."""
    rng = np.random.default_rng(seed)
    dur = 2.3
    t = t_axis(dur)
    base = [55.0, 58.27, 82.41][seed % 3]
    cluster = [1.0, 1.06, 1.5, 2.12, 2.83, 4.24]          # semitone rubs + tritones = unease
    sw = sum(np.sin(2 * np.pi * base * 2 * r * (1 + rng.normal(0, 0.002)) * t + rng.random() * 6) / (1 + i * 0.6)
             for i, r in enumerate(cluster))
    swell = np.clip(t / 0.55, 0, 1) ** 2 * np.exp(-np.maximum(0, t - 0.6) * 2.4)
    ht = np.maximum(0, t - 0.55)
    hit = np.sin(2 * np.pi * base * ht * (1 + 0.6 * np.exp(-ht * 12))) * np.exp(-ht * 3.0) * (t > 0.55)
    noise = bandpass(rng.normal(0, 1, len(t)), 80, 900) * np.exp(-ht * 6) * (t > 0.55) * 0.5
    return fade(norm(np.tanh((0.55 * sw * swell + 0.9 * hit + noise) * 1.3)), 2, 300)


def chirp(seconds, f0, f1, kind, seed):
    """Electrical creature / robot call. kind: up | down | updown."""
    rng = np.random.default_rng(seed)
    t = t_axis(seconds)
    if kind == "updown":
        f = f0 + (f1 - f0) * np.sin(np.pi * t / seconds)
    else:
        f = f0 * (f1 / f0) ** (t / seconds)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = 0.6 * np.sin(ph) + 0.25 * np.sin(2.01 * ph) + 0.12 * np.sin(3.03 * ph)
    y *= 1.0 + 0.35 * np.sin(2 * np.pi * 37 * t)                       # warble
    y += bandpass((rng.random(len(t)) > 0.996) * rng.normal(0, 0.6, len(t)), 2000, 9000)   # crackle
    env = np.minimum(1.0, t / 0.04) * np.exp(-1.2 * t / seconds)
    return fade(norm(bandpass(y * env, 300, 9000), 0.55), 4, 120)


def alarm(seconds=4.0):
    """Two-tone siren, loops cleanly every 1 s."""
    t = t_axis(seconds)
    f = np.where((t % 1.0) < 0.5, 880.0, 660.0)
    y = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3
    return norm(bandpass(y, 300, 4000), 0.6)


def drone(seconds=20.0, seed=3):
    """Dark ambience bed: detuned low tones + filtered noise, slow movement. Loops (whole cycles)."""
    rng = np.random.default_rng(seed)
    t = t_axis(seconds)
    y = sum(np.sin(2 * np.pi * f * t) * (0.5 + 0.5 * np.sin(2 * np.pi * t / seconds * k + k))
            for k, f in enumerate([41.2, 41.7, 61.8, 82.4, 123.5], 1))
    air = bandpass(rng.normal(0, 1, len(t)), 200, 1200) * (0.6 + 0.4 * np.sin(2 * np.pi * t / seconds * 2))
    y = norm(y, 0.5) + norm(air, 0.12)
    n = int(SR * 1.0)                                    # crossfade end into start for a seamless loop
    y[:n] = y[:n] * np.linspace(0, 1, n) + y[-n:] * np.linspace(1, 0, n)
    return norm(y[:-n], 0.5)


def heartbeat(bpm):
    """One lub-dub cycle at the given tempo; loop it, or play it per beat."""
    period = 60.0 / bpm
    t = t_axis(period)

    def thump(at, f, amp):
        tt = np.maximum(0, t - at)
        return amp * np.sin(2 * np.pi * f * tt * (1 + 0.8 * np.exp(-tt * 30))) * np.exp(-tt * 18) * (t >= at)

    y = thump(0.0, 48, 1.0) + thump(0.28 * min(1, period), 42, 0.7)
    return norm(bandpass(y, 25, 300), 0.8)


def blip(f0, f1, seconds=0.07):
    t = t_axis(seconds)
    f = f0 + (f1 - f0) * t / seconds
    return fade(norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30), 0.5), 1, 15)


def write_wav(path, x):
    """16-bit mono WAV with the standard library (no extra packages)."""
    pcm = (np.clip(x, -1.0, 1.0) * 32767).astype("<i2").tobytes()
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(pcm)


def main(out):
    os.makedirs(out, exist_ok=True)
    w = lambda name, x: write_wav(os.path.join(out, name + ".wav"), x)
    for i in range(3):
        w("stinger_%02d" % i, stinger(i))
    w("chirp_up", chirp(0.55, 900, 2600, "up", 1))
    w("chirp_updown", chirp(0.7, 3200, 1100, "updown", 2))
    w("chirp_down", chirp(0.9, 2400, 500, "down", 3))
    w("alarm_loop", alarm())
    w("drone_loop", drone())
    w("heartbeat_rest", heartbeat(62))
    w("heartbeat_fast", heartbeat(128))
    w("ui_blip", blip(1200, 1800))
    w("ui_back", blip(1500, 900))
    print("wrote", len(os.listdir(out)), "files to", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "synth_out")
