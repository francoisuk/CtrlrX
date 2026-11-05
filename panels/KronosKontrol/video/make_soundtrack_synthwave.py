r"""Original synthwave soundtrack for the Kronos Kontrol demo video (v2) — synthesised from scratch, no samples,
free to use in ads. 110 BPM, A minor with a key change up a tone (B minor) for the last part.
Built to avoid repetition : 9 sections with different chords, melodies, arpeggio patterns and drum feels,
fills + crashes at every section change. Timeline (1 bar = 2.18 s) matched to the 2:20 demo video :
  0  intro      bars  0- 6  pad + filtered arp, toms fill            (rack)
  13 verse 1    bars  6-14  Am F C G, verse melody, half drums
  30 chorus 1   bars 14-22  F G Em Am, HOOK, full drums              (Editor opens)
  48 verse 2    bars 22-30  Dm Am Bb C, new melody, 16th arp
  65 bridge     bars 30-36  F Em Dm E, half-time, long lead notes    (FX EDIT)
  78 build      bars 36-38  snare roll, riser
  83 chorus 2   bars 38-46  +2 semitones (B minor), hook             (Combi)
 100 solo       bars 46-54  lead runs over the chorus chords
 118 chorus 3   bars 54-62  hook + counter-melody, everything
 135 outro      bars 62-64  pad + last hook note, fade
Usage : C:/Python315/python make_soundtrack_synthwave.py <seconds> <out.wav>
"""
import sys, wave
import numpy as np

SR = 44100
BPM = 110.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
E8 = BEAT / 2
DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 140.0
OUT = sys.argv[2] if len(sys.argv) > 2 else 'soundtrack_synthwave.wav'
N = int(DUR * SR) + SR * 4
rng = np.random.default_rng(11)
L = np.zeros(N); R = np.zeros(N)            # direct mix
SL = np.zeros(N); SR_ = np.zeros(N)         # sidechained bus (pads, bass, arps)


def tt(n): return np.arange(n) / SR
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)


def filt(x, lo=None, hi=None):
    n = len(x); X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR); m = np.ones_like(f)
    if hi: m *= 1 / (1 + (f / hi) ** 4)
    if lo: m *= 1 - 1 / (1 + (f / lo) ** 4)
    return np.fft.irfft(X * m, n)


def saw(f, n, ph=0.0, vib=0.0):
    t = tt(n); fm = f * (1 + vib * np.sin(2 * np.pi * 5.5 * t) * np.clip(t * 3, 0, 1))
    phase = 2 * np.pi * np.cumsum(fm) / SR + ph
    y = np.zeros(n); k = 1
    while k * f < 11000 and k <= 36:
        y += np.sin(k * phase) / k; k += 1
    return y * 0.64


def pulse(f, n, vib=0.0):                    # odd harmonics = square-ish
    t = tt(n); fm = f * (1 + vib * np.sin(2 * np.pi * 5.5 * t) * np.clip(t * 3, 0, 1))
    phase = 2 * np.pi * np.cumsum(fm) / SR
    y = np.zeros(n); k = 1
    while k * f < 9000 and k <= 25:
        y += np.sin(k * phase) / k; k += 2
    return y * 0.8


def adsr(n, a, d, s, r):
    e = np.full(n, s, float); ia = min(int(a * SR), n); e[:ia] = np.linspace(0, 1, ia, endpoint=False)
    j = min(ia + int(d * SR), n); e[ia:j] = np.linspace(1, s, j - ia)
    ir = min(int(r * SR), n); e[n - ir:] *= np.linspace(1, 0, ir)
    return e


def put(sig, t0, g=1.0, pan=0.0, bus=False):
    i = int(t0 * SR)
    if i >= N or i < 0: return
    sig = sig[:N - i]
    gl, gr = g * np.cos((pan + 1) * np.pi / 4), g * np.sin((pan + 1) * np.pi / 4)
    (SL if bus else L)[i:i + len(sig)] += sig * gl
    (SR_ if bus else R)[i:i + len(sig)] += sig * gr


# ---------------------------------------------------------------- drums (80s)
def mk_kick():
    n = int(0.4 * SR); t = tt(n); f = 48 + 120 * np.exp(-t * 30)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) + 0.2 * rng.standard_normal(n) * np.exp(-t * 250)
    return np.tanh(2 * y) * 0.9


def mk_snare():                              # gated reverb : body + noise, long tail cut hard at 0.32 s
    n = int(0.36 * SR); t = tt(n)
    body = 0.5 * np.sin(2 * np.pi * 185 * t) * np.exp(-t * 25)
    nz = filt(rng.standard_normal(n), lo=700, hi=9000)
    tail = nz * (0.6 * np.exp(-t * 4))
    gate = np.where(t < 0.3, 1.0, np.clip(1 - (t - 0.3) / 0.02, 0, 1))
    return (body + nz * np.exp(-t * 30) * 0.5 + tail * 0.55) * gate


def mk_hat(o=False):
    n = int((0.25 if o else 0.05) * SR); t = tt(n)
    return filt(rng.standard_normal(n), lo=8000) * np.exp(-t * (10 if o else 80)) * 0.4


def mk_tom(f0):
    n = int(0.45 * SR); t = tt(n); f = f0 * (1 + 0.6 * np.exp(-t * 20))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * 0.7


def mk_crash():
    n = int(2.2 * SR); t = tt(n)
    return filt(rng.standard_normal(n), lo=4000) * np.exp(-t * 1.6) * 0.32


KICK, SNARE, HAT, OHAT, CRASH = mk_kick(), mk_snare(), mk_hat(), mk_hat(True), mk_crash()
TOMS = [mk_tom(f) for f in (220, 165, 125, 95)]

# ---------------------------------------------------------------- song map
A, F_, C, G, Em, Dm, Bb, E = ([57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62], [52, 55, 59],
                              [50, 53, 57], [46, 50, 53], [52, 56, 59])
SECTIONS = [  # name, first bar, bars, chords (one per bar, cycled), transpose
    ('intro', 0, 6, [A, F_, C, G], 0), ('verse1', 6, 8, [A, F_, C, G], 0), ('chorus1', 14, 8, [F_, G, Em, A], 0),
    ('verse2', 22, 8, [Dm, A, Bb, C], 0), ('bridge', 30, 6, [F_, Em, Dm, E], 0), ('build', 36, 2, [F_, G], 0),
    ('chorus2', 38, 8, [F_, G, Em, A], 2), ('solo', 46, 8, [F_, G, Em, A], 2), ('chorus3', 54, 8, [F_, G, Em, A], 2),
    ('outro', 62, 3, [A], 2)]

# melodies : (midi, eighths) per bar, 8 eighths per bar ; None = rest
HOOK = [[(76, 2), (74, 1), (72, 1), (74, 3), (69, 1)], [(71, 2), (72, 1), (74, 1), (79, 4)],
        [(76, 2), (74, 1), (72, 1), (71, 3), (67, 1)], [(69, 6), (None, 2)]]
HOOK_END = [(72, 2), (71, 1), (69, 1), (69, 4)]
VERSE1 = [[(69, 1), (72, 1), (76, 2), (74, 1), (72, 1), (69, 2)], [(None, 2), (65, 1), (69, 1), (72, 2), (69, 2)],
          [(67, 1), (72, 1), (76, 2), (79, 3), (76, 1)], [(74, 4), (71, 2), (67, 2)]]
VERSE2 = [[(74, 2), (77, 1), (76, 1), (74, 2), (69, 2)], [(72, 3), (71, 1), (69, 4)],
          [(70, 1), (74, 1), (77, 2), (76, 1), (74, 1), (72, 2)], [(76, 6), (79, 2)]]
BRIDGE = [[(81, 8)], [(79, 4), (71, 4)], [(77, 4), (69, 4)], [(80, 8)]]
COUNTER = [[(69, 4), (67, 4)], [(67, 4), (71, 4)], [(67, 4), (64, 4)], [(64, 8)]]


def lead_note(m, n, kind='lead'):
    f = hz(m)
    if kind == 'lead':
        y = saw(f, n, vib=0.004) * 0.6 + pulse(f * 1.003, n, vib=0.004) * 0.5
        y = filt(y, hi=4200) * adsr(n, 0.01, 0.15, 0.75, 0.08)
    elif kind == 'soft':
        y = pulse(f, n, vib=0.003) * adsr(n, 0.02, 0.2, 0.6, 0.1); y = filt(y, hi=2500)
    else:                                     # bell-ish counter
        t = tt(n); y = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t * 2.5)
    return y


def play_melody(phrase_bars, t0, tr, kind, g, pan=0.0, delay=True):
    for b, bar in enumerate(phrase_bars):
        pos = 0
        for m, d in bar:
            if m is not None:
                n = int(d * E8 * SR * 0.95); st = t0 + b * BAR + pos * E8
                y = lead_note(m + tr, n, kind)
                put(y, st, g, pan)
                if delay:                                   # dotted-8th ping-pong + 80s plate-ish tail
                    put(y * 0.32, st + 3 * E8 / 2, g, -0.6); put(y * 0.18, st + 3 * E8, g, 0.6)
            pos += d


def arp(chord, t0, tr, pattern, g):
    notes = sorted(chord) + [chord[0] + 12]
    seq = {'up8': ([0, 1, 2, 3] * 2, 8), 'updown16': ([0, 1, 2, 3, 2, 1, 0, 1] * 2, 16),
           'oct16': ([0, 3, 1, 3, 2, 3, 1, 3] * 2, 16), 'trip': ([0, 1, 2, 3, 2, 1] * 2, 12)}[pattern]
    idx, per = seq; step = BAR / per
    for k, i in enumerate(idx):
        m = notes[i] + 12 + tr; n = int(step * SR * 0.8)
        y = saw(hz(m), n) * 0.5 + pulse(hz(m), n) * 0.3
        y = filt(y, hi=3200) * adsr(n, 0.002, 0.06, 0.3, 0.02)
        put(y, t0 + k * step, g, -0.4 if k % 2 else 0.4, bus=True)


def pad(chord, t0, tr, n_bars, g, cutoff):
    n = int(n_bars * BAR * SR)
    y = np.zeros(n)
    for m in chord:
        for det in (-0.1, 0.0, 0.1):
            y += saw(hz(m + 12 + tr) * 2 ** (det / 12), n, rng.uniform(0, 6.2))
    y = filt(y, hi=cutoff) * adsr(n, 0.25, 0.4, 0.85, 0.3) * 0.05 * g
    put(y, t0, 1.0, -0.2, bus=True); put(np.roll(y, 441), t0, 1.0, 0.2, bus=True)


def bassline(chord, t0, tr, style, g):
    root = chord[0] - 24 + tr
    if style == 'long':
        n = int(BAR * SR * 0.98); y = filt(saw(hz(root), n) + 0.6 * np.sin(2 * np.pi * hz(root - 12) * tt(n)), hi=500)
        put(y * adsr(n, 0.01, 0.3, 0.7, 0.1) * 0.35 * g, t0, 1.0, 0.0, bus=True); return
    per = 16 if style == '16' else 8
    for k in range(per):
        n = int(BAR / per * SR * 0.85); m = root + (12 if (style == 'oct' and k % 2) else 0)
        y = saw(hz(m), n) + 0.5 * np.sin(2 * np.pi * hz(m - 12) * tt(n))
        y = filt(y, hi=800) * adsr(n, 0.003, 0.08, 0.55, 0.03) * 0.33 * g
        put(y, t0 + k * BAR / per, 1.0, 0.0, bus=True)


def drums(t0, feel, fill=False):
    if feel == 'none': return
    if feel == 'half':                                       # half-time : kick 1, snare 3
        put(KICK, t0, 0.9); put(SNARE, t0 + 2 * BEAT, 0.55)
        for k in range(8): put(HAT, t0 + k * E8, 0.18, 0.3)
    else:
        kicks = [0, 2] if feel == 'light' else [0, 1.5, 2] if feel == 'drive' else [0, 1, 2, 3]
        for b in kicks: put(KICK, t0 + b * BEAT, 0.95)
        put(SNARE, t0 + BEAT, 0.6); put(SNARE, t0 + 3 * BEAT, 0.6)
        for k in range(8): put(HAT, t0 + k * E8, 0.28 if k % 2 else 0.15, 0.3)
        if feel == 'four':
            for b in range(4): put(OHAT, t0 + b * BEAT + E8, 0.18, -0.3)
    if fill:                                                 # last beat : 4 toms down
        for k, tom in enumerate(TOMS): put(tom, t0 + 3 * BEAT + k * BEAT / 4, 0.6, -0.5 + k / 3)


DUCK = np.ones(N)
def duck_at(t0):
    i = int(t0 * SR); n = int(BEAT * SR); seg = 1 - 0.55 * np.exp(-tt(n) * 12)
    DUCK[i:i + n] = np.minimum(DUCK[i:i + n], seg[:len(DUCK[i:i + n])])


# ---------------------------------------------------------------- arrange
for name, b0, nb, chords, tr in SECTIONS:
    t_sec = b0 * BAR
    if name not in ('intro', 'outro', 'bridge'):
        put(CRASH, t_sec, 1.0, 0.2)
    for i in range(nb):
        t0 = (b0 + i) * BAR; ch = chords[i % len(chords)]; last = (i == nb - 1)
        # pads everywhere (brighter as the song goes)
        cut = {'intro': 900 + 350 * i, 'verse1': 2200, 'chorus1': 3200, 'verse2': 2600, 'bridge': 2000,
               'build': 3000, 'chorus2': 3600, 'solo': 3400, 'chorus3': 4200, 'outro': 1800}[name]
        pad(ch, t0, tr, 1, 1.0 if name != 'bridge' else 1.3, cut)
        if name == 'intro':
            arp(ch, t0, tr, 'up8', 0.5 + 0.08 * i)
            if last: drums(t0, 'none', fill=True)
        elif name == 'verse1':
            drums(t0, 'light', fill=last); bassline(ch, t0, tr, '8', 1.0); arp(ch, t0, tr, 'up8', 0.6)
        elif name in ('chorus1', 'chorus2', 'chorus3'):
            drums(t0, 'four' if name == 'chorus3' else 'drive', fill=last); bassline(ch, t0, tr, 'oct', 1.0)
            arp(ch, t0, tr, 'oct16', 0.55)
        elif name == 'verse2':
            drums(t0, 'drive', fill=last); bassline(ch, t0, tr, '16', 0.9); arp(ch, t0, tr, 'updown16', 0.6)
        elif name == 'bridge':
            drums(t0, 'half', fill=last); bassline(ch, t0, tr, 'long', 1.0); arp(ch, t0, tr, 'trip', 0.4)
        elif name == 'build':
            bassline(ch, t0, tr, '16', 0.9)
            for k in range(16 if i == 0 else 32):            # snare roll accelerating
                put(SNARE, t0 + k * BAR / (16 if i == 0 else 32), 0.12 + 0.012 * k + 0.2 * i, 0.0)
            if last:
                n = int(BAR * SR); t = tt(n)
                put(filt(rng.standard_normal(n), lo=600, hi=9000) * (t / BAR) ** 2 * 0.3, t0)
        elif name == 'solo':
            drums(t0, 'four', fill=last); bassline(ch, t0, tr, 'oct', 1.0); arp(ch, t0, tr, 'trip', 0.45)
        elif name == 'outro':
            if i == 0: put(KICK, t0, 0.9)
        if name not in ('intro', 'build', 'outro', 'bridge'):
            for b in range(4): duck_at(t0 + b * BEAT)
    # melodies per section
    if name == 'verse1':
        play_melody(VERSE1, t_sec, tr, 'soft', 0.22, 0.1); play_melody(VERSE1[:3] + [[(74, 2), (76, 2), (79, 4)]], t_sec + 4 * BAR, tr, 'soft', 0.24, 0.1)
    elif name in ('chorus1', 'chorus2', 'chorus3'):
        play_melody(HOOK, t_sec, tr, 'lead', 0.26); play_melody(HOOK[:3] + [HOOK_END], t_sec + 4 * BAR, tr, 'lead', 0.26)
        if name == 'chorus3':                                # octave double + bell counter-melody
            play_melody(HOOK, t_sec, tr + 12, 'soft', 0.08, 0.4, False); play_melody(HOOK[:3] + [HOOK_END], t_sec + 4 * BAR, tr + 12, 'soft', 0.08, 0.4, False)
            play_melody(COUNTER * 2, t_sec, tr, 'bell', 0.16, -0.4, False)
    elif name == 'verse2':
        play_melody(VERSE2, t_sec, tr, 'soft', 0.22, -0.1); play_melody(VERSE2[:3] + [[(77, 2), (76, 2), (74, 4)]], t_sec + 4 * BAR, tr, 'soft', 0.24, -0.1)
    elif name == 'bridge':
        play_melody(BRIDGE + BRIDGE[:2], t_sec, tr, 'lead', 0.2)
    elif name == 'solo':                                     # call (hook fragments) and response (16th runs)
        for i in range(nb):
            t0 = (b0 + i) * BAR; ch = chords[i % 4]
            if i % 2 == 0:
                play_melody([HOOK[i % 4]], t0, tr + 12, 'lead', 0.2)
            else:
                scale = [57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81]
                top = scale.index(min(scale, key=lambda s: abs(s - (ch[2] + 12))))
                run = [scale[max(0, top - k)] + 12 for k in range(12)] + [ch[0] + 24] * 4
                play_melody([[(m, 0.5) for m in run]], t0, tr, 'lead', 0.17)
    elif name == 'outro':
        play_melody([[(69, 8)]], t_sec, tr, 'lead', 0.24)

# ---------------------------------------------------------------- master
L += SL * DUCK; R += SR_ * DUCK
mix = np.stack([L, R], 1)[:int(DUR * SR)]
mix = np.tanh(mix * 1.2) / np.tanh(1.2)
fi, fo = int(0.3 * SR), int(4.5 * SR)
mix[:fi] *= np.linspace(0, 1, fi)[:, None]; mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix /= np.max(np.abs(mix)) / 0.89
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('written', OUT, '%.1f s' % (len(mix) / SR))
