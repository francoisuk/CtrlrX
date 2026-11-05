r"""Original soundtrack for the Kronos Kontrol demo video — synthesised from scratch (no samples, no third-party
material, so it is free to use in ads). Energetic electronic track, 128 BPM, A minor, Am-F-C-G.
Structure (bars of 1.875 s) : intro 0-8 (kick, hats, filtered pad) / build 8-16 (+clap, bass) /
main A 16-40 (+arp lead) / breakdown 40-48 (pad + arp, riser) / drop 48-72 (everything, open hats) / outro 72-75.
Usage : C:/Python315/python make_soundtrack.py <seconds> <out.wav>
"""
import sys, wave
import numpy as np

SR = 44100
BPM = 128.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 140.0
OUT = sys.argv[2] if len(sys.argv) > 2 else 'soundtrack.wav'
N = int(DUR * SR) + SR * 2
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)


def t_of(n): return np.arange(n) / SR
def midi(m): return 440.0 * 2 ** ((m - 69) / 12)


def fft_filter(x, lo=None, hi=None):
    """Brick-ish band filter with smooth edges (FFT mask)."""
    n = len(x); X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR); m = np.ones_like(f)
    if hi: m *= 1 / (1 + (f / hi) ** 4)
    if lo: m *= 1 - 1 / (1 + (f / lo) ** 4)
    return np.fft.irfft(X * m, n)


def saw(freq, n, phase=0.0):
    """Band-limited-ish saw (additive, harmonics below 12 kHz)."""
    t = t_of(n); y = np.zeros(n); k = 1
    while k * freq < 12000 and k <= 40:
        y += np.sin(2 * np.pi * k * freq * t + phase * k) / k; k += 1
    return y * (2 / np.pi)


def env(n, a=0.005, d=0.1, s=0.6, r=0.05):
    e = np.ones(n) * s; ia, idd, ir = int(a * SR), int(d * SR), int(r * SR)
    ia = min(ia, n); e[:ia] = np.linspace(0, 1, ia, endpoint=False)
    j = min(ia + idd, n); e[ia:j] = np.linspace(1, s, j - ia)
    if ir < n: e[n - ir:] *= np.linspace(1, 0, ir)
    return e


def put(sig, start_s, gain=1.0, pan=0.0):
    i = int(start_s * SR)
    if i >= N: return
    sig = sig[:N - i]
    gl, gr = gain * np.cos((pan + 1) * np.pi / 4), gain * np.sin((pan + 1) * np.pi / 4)
    L[i:i + len(sig)] += sig * gl; R[i:i + len(sig)] += sig * gr


# ---------------------------------------------------------------- one-shots
def kick():
    n = int(0.35 * SR); t = t_of(n)
    f = 45 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t * 7.5)
    y += 0.25 * np.exp(-t * 300) * rng.standard_normal(n)          # click
    return np.tanh(y * 2.2) * 0.95


def clap():
    n = int(0.25 * SR); t = t_of(n)
    nz = fft_filter(rng.standard_normal(n), lo=900, hi=6000)
    e = np.exp(-t * 18)
    for off in (0.0, 0.011, 0.022):                                   # three-hand smear
        k = int(off * SR); e[k:k + 200] += np.linspace(1, 0, 200)[:len(e[k:k + 200])]
    tone = 0.3 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    return (nz * e * 0.5 + tone) * 0.9


def hat(open_=False):
    n = int((0.22 if open_ else 0.06) * SR); t = t_of(n)
    nz = fft_filter(rng.standard_normal(n), lo=7000)
    return nz * np.exp(-t * (12 if open_ else 70)) * 0.5


KICK, CLAP, HAT, OHAT = kick(), clap(), hat(), hat(True)

# ---------------------------------------------------------------- harmony
PROG = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62])]   # Am F C G (roots + triads)
nbars = int(DUR / BAR) + 1


def section(bar):
    if bar < 8: return 'intro'
    if bar < 16: return 'build'
    if bar < 40: return 'main'
    if bar < 48: return 'break'
    if bar < 72: return 'drop'
    return 'outro'


# sidechain envelope (ducks pads / bass / lead on every kick)
duck = np.ones(N)
for bar in range(nbars):
    if section(bar) in ('break',): continue
    for b in range(4):
        i = int((bar * BAR + b * BEAT) * SR); n = int(BEAT * SR)
        seg = 1 - 0.7 * np.exp(-t_of(n) * 14)
        duck[i:i + n] = np.minimum(duck[i:i + n], seg[:len(duck[i:i + n])])

PAD_L = np.zeros(N); PAD_R = np.zeros(N); MUS_L = np.zeros(N); MUS_R = np.zeros(N)

for bar in range(nbars):
    s = section(bar); t0 = bar * BAR; root, triad = PROG[bar % 4]
    # ---- drums
    if s != 'break':
        for b in range(4):
            put(KICK, t0 + b * BEAT, 0.95 if s != 'outro' else 0.7)
    if s in ('build', 'main', 'drop'):
        put(CLAP, t0 + BEAT, 0.55, 0.05); put(CLAP, t0 + 3 * BEAT, 0.55, 0.05)
    if s != 'break':
        for k in range(16):
            if k % 2 == 1 or s in ('main', 'drop'):
                put(HAT, t0 + k * BEAT / 4, 0.35 if k % 2 else 0.18, 0.3)
        if s == 'drop':
            for b in range(4): put(OHAT, t0 + b * BEAT + BEAT / 2, 0.25, -0.3)
    if s == 'build' and bar % 8 == 7:                                 # snare roll into the main
        for k in range(16): put(CLAP, t0 + k * BEAT / 4, 0.15 + 0.03 * k, 0.0)
    # ---- pad (whole bar, detuned saws, filtered)
    n = int(BAR * SR)
    cutoff = {'intro': 600 + 250 * bar, 'build': 2500, 'main': 3000, 'break': 1800, 'drop': 4000, 'outro': 1500}[s]
    pad = np.zeros(n)
    for m in triad:
        for det in (-0.08, 0.0, 0.08):
            pad += saw(midi(m + 12) * 2 ** (det / 12), n, rng.uniform(0, 6.28))
    pad = fft_filter(pad, hi=cutoff) * env(n, 0.08, 0.3, 0.8, 0.15) * 0.06
    i = int(t0 * SR); PAD_L[i:i + n] += pad[:len(PAD_L[i:i + n])]
    pad2 = np.roll(pad, 300); PAD_R[i:i + n] += pad2[:len(PAD_R[i:i + n])]
    # ---- bass (8ths, octave pump)
    if s in ('build', 'main', 'drop', 'outro'):
        for k in range(8):
            nn = int(BEAT / 2 * SR * 0.9)
            m = root - 12 + (12 if k % 2 else 0)
            b = saw(midi(m), nn) + 0.5 * np.sin(2 * np.pi * midi(m - 12) * t_of(nn))
            b = fft_filter(b, hi=900 if s != 'drop' else 1400) * env(nn, 0.003, 0.08, 0.5, 0.03) * 0.32
            j = int((t0 + k * BEAT / 2) * SR); MUS_L[j:j + nn] += b[:len(MUS_L[j:j + nn])]; MUS_R[j:j + nn] += b[:len(MUS_R[j:j + nn])]
    # ---- arp lead (16ths over the triad, +1 octave on the drop)
    if s in ('main', 'break', 'drop'):
        notes = triad + [triad[0] + 12, triad[2], triad[1]]
        for k in range(16):
            nn = int(BEAT / 4 * SR * 0.85)
            m = notes[k % len(notes)] + 12 + (12 if s == 'drop' and k % 4 == 0 else 0)
            a = saw(midi(m), nn) + 0.6 * saw(midi(m) * 1.004, nn)
            a = fft_filter(a, hi=3500 if s != 'break' else 2200) * env(nn, 0.002, 0.05, 0.35, 0.02) * 0.11
            st = t0 + k * BEAT / 4; p = -0.35 if k % 2 else 0.35
            put(a, st, 1.0, p)                                        # (lead goes straight to the mix, slightly ducked below)
            put(a * 0.35, st + 3 * BEAT / 4, 1.0, -p)                 # dotted-8th delay
            put(a * 0.15, st + 6 * BEAT / 4, 1.0, p)
    # ---- riser at the end of the breakdown
    if bar == 47:
        n = int(BAR * SR); t = t_of(n)
        nz = rng.standard_normal(n); nz = fft_filter(nz, lo=500, hi=9000)
        put(nz * (t / BAR) ** 2 * 0.35, t0, 1.0, 0.0)
        sweep = np.sin(2 * np.pi * np.cumsum(200 + 1800 * (t / BAR) ** 2) / SR) * (t / BAR) * 0.08
        put(sweep, t0, 1.0, 0.0)

L += (PAD_L + MUS_L) * duck; R += (PAD_R + MUS_R) * duck
# master : gentle glue, fades, normalise to -1 dBFS
mix = np.stack([L, R], 1)[:int(DUR * SR)]
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
fi, fo = int(0.5 * SR), int(4.0 * SR)
mix[:fi] *= np.linspace(0, 1, fi)[:, None]; mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix /= np.max(np.abs(mix)) / 0.89
pcm = (mix * 32767).astype(np.int16)
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('written', OUT, '%.1f s' % (len(pcm) / SR), 'bars', nbars)
