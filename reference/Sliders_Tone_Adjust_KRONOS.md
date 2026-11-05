# KRONOS — What the 9 sliders do in Tone Adjust mode, by engine

## How it works

In Program mode, when the **TONE ADJ/EQ** button is set to **TONE ADJ** (TONE ADJ LED lit), the sliders on the Control Surface no longer act as mixer volumes. They control parameters of the program instead.

- **Sliders 1 to 8** are the eight channel sliders.
- **Slider 9** is the **Master** slider, to the right of slider 8.
- **"—"** means no parameter is assigned to that slider by default.

Each synthesis engine has its own **default assignment**, listed below.

- **Source:** KRONOS Parameter Guide, "Tone Adjust Default Settings" figures.
- **Parameter names:** given exactly as they appear on the KRONOS.
- **Edited programs:** a program can reassign its sliders. This document only covers the default assignments.
- **Companion document:** `Encoders_Tone_Adjust_KRONOS.md` covers the 8 encoders.

---

## HD-1 — PCM (sample-based) synthesis

Sliders 1–4 shape the filter envelope; sliders 5–8 shape the amp (volume) envelope.

| Slider | Parameter | What it does |
|---|---|---|
| 1 | Filter EG Attack | Time for the filter envelope to reach its peak |
| 2 | Filter EG Decay | Time for the filter envelope to fall to the sustain level |
| 3 | Filter EG Sustain | Filter envelope level while the key is held |
| 4 | Filter EG Release | Time for the filter envelope to close after the key is released |
| 5 | Amp EG Attack | Time for the volume to reach its peak |
| 6 | Amp EG Decay | Time for the volume to fall to the sustain level |
| 7 | Amp EG Sustain | Volume while the key is held |
| 8 | Amp EG Release | Time for the sound to die away after the key is released |
| 9 (Master) | — | Not assigned |

## AL-1 — Virtual analogue synth

Sliders 1–4 shape EG 1 (filter envelope); sliders 5–8 shape the amp envelope.

| Slider | Parameter | What it does |
|---|---|---|
| 1 | EG1 (Filter) Attack | Filter envelope attack time |
| 2 | EG1 (Filter) Decay | Filter envelope decay time |
| 3 | EG1 (Filter) Sustain | Filter envelope sustain level |
| 4 | EG1 (Filter) Release | Filter envelope release time |
| 5 | Amp EG Attack | Volume attack time |
| 6 | Amp EG Decay | Volume decay time |
| 7 | Amp EG Sustain | Volume sustain level |
| 8 | Amp EG Release | Volume release time |
| 9 (Master) | — | Not assigned |

## CX-3 — Tonewheel organ

The 9 sliders become the **upper manual drawbars**, exactly like the nine drawbars on a tonewheel organ. Pulling a slider down adds more of that footage.

| Slider | Drawbar | What it does |
|---|---|---|
| 1 | 16′ | Sub-octave (one octave below the note played) |
| 2 | 5 1/3′ | Fifth above the fundamental (sub-third harmonic) |
| 3 | 8′ | Fundamental (the note played) |
| 4 | 4′ | One octave above |
| 5 | 2 2/3′ | Octave + fifth above |
| 6 | 2′ | Two octaves above |
| 7 | 1 3/5′ | Two octaves + major third above |
| 8 | 1 1/3′ | Two octaves + fifth above |
| 9 (Master) | 1′ | Three octaves above |

## STR-1 — Physically modelled plucked strings

| Slider | Parameter | What it does |
|---|---|---|
| 1 | Pluck Type | Type of pluck used to excite the string |
| 2 | Pluck Width | Width of the pluck (softer or sharper attack) |
| 3 | Pluck Random. | Random variation of the pluck from note to note |
| 4 | Harmonic Pressure AMS Int. | Modulation of the harmonic pressure |
| 5 | String Level | Level of the modelled string |
| 6 | PCM Osc Level | Level of the PCM oscillator |
| 7 | Noise Level | Level of the noise generator |
| 8 | Pickup 1 Level | Level of pickup 1 |
| 9 (Master) | Pickup 2 Level | Level of pickup 2 |

> **To check on the instrument:** the assignments of sliders 4 and 5 are inferred from the Parameter Guide.

## MS-20EX — MS-20 with virtual patch cables

Sliders 1–3 shape EG 1, sliders 4–7 shape EG 2, sliders 8–9 control the MG (the MS-20's LFO).

| Slider | Parameter | What it does |
|---|---|---|
| 1 | EG1 Delay | Delay before EG 1 starts |
| 2 | EG1 Attack | EG 1 attack time |
| 3 | EG1 Release | EG 1 release time |
| 4 | EG2 Attack | EG 2 attack time |
| 5 | EG2 Decay | EG 2 decay time |
| 6 | EG2 Sustain | EG 2 sustain level |
| 7 | EG2 Release | EG 2 release time |
| 8 | MG Waveform | Waveform of the modulation generator (LFO) |
| 9 (Master) | MG Freq / Times | Speed of the modulation generator |

## PolysixEX — The 1981 Polysix

| Slider | Parameter | What it does |
|---|---|---|
| 1 | EG Attack | Envelope attack time |
| 2 | EG Decay | Envelope decay time |
| 3 | EG Sustain | Envelope sustain level |
| 4 | EG Release | Envelope release time |
| 5 | Effect Mode | Selects the built-in effect (chorus, phaser, ensemble) |
| 6 | Effect Int. / Speed | Intensity or speed of the effect |
| 7 | MG Freq / Times | Speed of the modulation generator (LFO) |
| 8 | MG Level | Depth of the modulation generator |
| 9 (Master) | MG Mode | Destination of the modulation generator |

## MOD-7 — VPM / FM modular synthesis

| Slider | Parameter | What it does |
|---|---|---|
| 1 | Osc 1 Level | Output level of VPM oscillator 1 |
| 2 | Osc 2 Level | Output level of VPM oscillator 2 |
| 3 | Osc 3 Level | Output level of VPM oscillator 3 |
| 4 | Osc 4 Level | Output level of VPM oscillator 4 |
| 5 | Osc 5 Level | Output level of VPM oscillator 5 |
| 6 | Osc 6 Level | Output level of VPM oscillator 6 |
| 7 | Macro Brightness | Overall brightness of the sound |
| 8 | Macro Timbre | Overall timbre change |
| 9 (Master) | Macro Feedback | Overall amount of feedback |

## SGX-2 — Sampled acoustic pianos

No slider is assigned by default: they are free for you to assign your own settings.

| Slider | Parameter |
|---|---|
| 1–9 | — |

## EP-1 — Modelled electric pianos

Sliders 1–5 shape the piano's mechanical and harmonic noises; sliders 6–9 control the insert effect (IFX).

| Slider | Parameter | What it does |
|---|---|---|
| 1 | Attack Noise Level | Level of the attack noise (hammer hitting the tine) |
| 2 | Release Noise Level | Level of the noise when the key is released |
| 3 | Harmonic Sound Level | Level of the harmonic component |
| 4 | Harmonic Sound Decay | Decay time of the harmonic component |
| 5 | Harmonic Sound Release | Release time of the harmonic component |
| 6 | IFX Speed [Hz] | Speed of the insert effect |
| 7 | IFX Depth | Depth of the insert effect |
| 8 | IFX Resonance | Resonance of the insert effect |
| 9 (Master) | IFX Wet/Dry | Balance between dry and effected sound |
