# Phase A — Parameter map

*Amended 24 oct. 2026: the CSV was extended and corrected after the
rack design was fixed and the panel tests of 16 oct. 2026. See the
"2026-10-24 amendment" section at the end. Phase A is complete.*

## Purpose

Produce the single artifact that drives the rest of the Ctrlr build: a
parameter map CSV that describes, for every control the panel will have,
what MIDI or SysEx message it sends, how values are scaled, whether the
Kronos provides feedback, and which static data (if any) it uses.

Every Modulator and every Lua function in later phases is generated
from this CSV. It is the spec.

## Inputs

Ground truth (working M4L device — do not re-derive from MIDI spec):
- reference/ref-kronos/m4l/base/kronos_kontrol_v1.json
- reference/ref-kronos/m4l/base/conteneur.json (build passes)

Decoding tables (used only to interpret fields, not to invent bytes):
- reference/ref-kronos/midi/KRONOS_MIDI_SysEx.txt
- reference/ref-kronos/midi/Prog_HD-1.txt
- reference/ref-kronos/midi/Prog_EXi.txt
- reference/ref-kronos/midi/Prog_EXi_Common.txt
- reference/ref-kronos/midi/CombiAndSongTimbreSet.txt
- reference/ref-kronos/tables/*.csv|json (same content, machine-readable)

Hardware-verified corrections (override the tables where they were never
validated on hardware):
- reference/ref-kronos/docs/SYSEX_KRONOS.md
- reference/ref-kronos/m4l/docs_dev/REPRISE.md (device test, 16 oct. 2026)
- docs_old/REPRISE.md (archived panel REPRISE — panel tests, 16 oct. 2026…0.97o)

Static data (used to fill the StaticData column):
- reference/ref-kronos/m4l/names.json
- reference/ref-kronos/m4l/ge_kronos.json

Prose source for feedback:
- MIDI Applications chapter of the Kronos parameter/operation guide,
  sections "KRONOS and MIDI CCs", "Messages transmitted and received
  by the KRONOS", "Using various controllers", "KARMA function control",
  "Vector control", "Pads 1–8 control".

The bit-level tables carry Min/Max, bit widths, and the
TYP/SOC/SUB/PID/IDX fields used by SysEx function 43. They do NOT carry
a transmit/receive flag, and they do NOT carry the hardware-verified
corrections (FX inversion, fn 6D/6E routing, address collisions). See
A3 and the 2026-10-24 amendment.

## Steps

### A1 — Extract every sxformat string

Grep the base patch JSON for every object whose `text` starts with
`sxformat`. For each, record:

- box id
- full text string
- upstream box(es) one level back (what drives it)
- guessed UI control (mode, GE, FX slot n, Drum Track, etc.)

Do not interpret the bytes yet. Just collect them.

**Outcome (2025):** 17 objects extracted — mode change, 5× GE selection
(Program plus four Combi variants), 16× FX switch (Program plus Combi),
Drum Track, and 2 M3 legacy. All byte formulas in the CSV come from
this step. Note: the GE and Drum Track On formulas were **never
validated on hardware** in the device (device test log: "Non vérifiés :
KARMA, GE"); only Drum Track Mute was. The 2026-10-24 amendment
corrects them.

### A2 — Decode each against KRONOS_MIDI_SysEx.txt

For each sxformat string, split it into fields:

- F0 (start of SysEx)
- manufacturer ID (Korg = 0x42)
- 3g byte (channel nibble g = MIDI channel - 1)
- model ID (Kronos = 0x68)
- function byte (0x4E mode change, 0x43 parameter change, etc.)
- parameter ID fields in the order the function expects
  (for fn 43: TYP / SOC / SUB / PID / IDX, with Korg's bit widths)
- value bytes and their bit widths
- F7 (end of SysEx)

Cross-check each function byte against KRONOS_MIDI_SysEx.txt. If the
table disagrees with the patch, the patch wins (it is hardware-tested).
Note the disagreement for review.

**Outcome (2025):** Decoded at function-byte level. All fn 4E, fn 43,
fn 6D, fn 6E, fn 7F functions are listed as Receive/Transmit at the
function level in KRONOS_MIDI_SysEx.txt. The fn 4E body text states
explicitly that the message is transmitted when the mode changes via
SW. No other function has a per-parameter transmit statement.

### A3 — Cross-reference with bit-level parameter tables

For each parameter the SysEx addresses, look it up in:

- reference/ref-kronos/midi/Prog_HD-1.txt, Prog_EXi.txt,
  Prog_EXi_Common.txt (for fn 43, TYP-dependent)
- reference/ref-kronos/midi/CombiAndSongTimbreSet.txt (Combi timbres)
- reference/ref-kronos/tables/Effets.json (for fn 43 TYP 6 / 23)

Record:

- byte offset
- bit offset within the byte
- bit width
- min, max
- any non-linear scaling (list, table, or formula)

**Outcome (2025):**

- TYP/SOC/SUB/PID/IDX confirmed for every SysEx row in the CSV.
- GE Number range confirmed: Prog_EXi_Common.txt offset 1814,
  range 0000–0DFF (0–3583), 14 bits.
- Insert FX / MFX / TFX Switch confirmed as **1-bit** fields, not
  7-bit, in Prog_HD-1.txt (offsets 89, 163, 237, 311, 385, 977, 1045,
  1117 bits 6).
- Drum Track On confirmed as a 1-bit field in Prog_EXi_Common.txt
  (offset 1295, bit 4).
- TYP 23 for Combi FX confirmed via Prog_EXi_Common.txt.
- Feedback could NOT be filled from these tables. They carry no
  direction flag. See "Feedback correction" below.

**Outcome (2026-10-24, address collisions):** the same tables show
that in a Program, the fn 43 addresses used by the device for GE
Number (`43 01 00 00 00`) and Drum Track On (`43 00 00 00 0A`) are
**shared with other parameters**:

- fn 43 `01 00 00 00 00` = Common LFO Waveform
  (Prog_EXi_Common.txt l.2249), NOT KARMA GE Number (l.1093)
- fn 43 `00 00 00 0A 00` = Common Scale Type
  (Prog_EXi_Common.txt l.2080), NOT Drum Track On (l.424)

KARMA and Drum Track have their own functions in KRONOS_MIDI_SysEx.txt:
**6D KARMA Parameter Change**, **6E Drum Track Parameter Change**.
The CSV and the panel (complet-0.96) route GE through fn 6D and Drum
Track On through fn 6E in Program mode; in Combi mode the fn 43
addresses do not collide (TYP 1 / 2 / 3) and are used first, with an
automatic 6D/6E retry if the Kronos answers Reply 24 code ≠ 0.

### A4 — Emit the parameter map CSV

One row per control. Columns:

`Control | Section | Mode | MessageType | Bytes/Formula | ParamID |
Min | Max | WidthBits | Scaling | Feedback | Source | StaticData |
Tested`

The `Source` column was added in 2025 so every Feedback value carries
its citation inline. The `Tested` column records hardware-verification
state (legend below).

## Feedback correction (2025)

The original A3 brief anticipated filling `Feedback` from the bit-level
parameter tables. That is not possible: the tables carry
TYP/SOC/SUB/PID/IDX, bit widths, and Min/Max, but no transmit/receive
flag.

The Kronos documentation as a whole does not publish a per-parameter
Transmit/Receive/Both table. It publishes direction as prose, per
controller group, in the MIDI Applications chapter:

> "This message will be transmitted when the controller is operated.
> When this message is received, the result will be the same as when
> the controller is operated."

That sentence applies to every CC group the panel exposes and says
**both** in every instance. So:

- Every CC row in the CSV carries `Feedback = both`, sourced to the
  MIDI Applications prose (pp. 14–19 of the parameter guide).
- `ProgramChange` carries `Feedback = both`, same source.
- `ModeChange` carries `Feedback = both`, sourced to the fn 4E body
  text in KRONOS_MIDI_SysEx.txt.
- Every other SysEx row carries `Feedback = unknown`, with the reason
  recorded in the `Source` column: function-level R/T only, no
  per-parameter transmit statement.

Whether a hardware edit actually arrives at the panel depends on
runtime state on the Kronos (Enable Control Change, Enable Exclusive,
per-timbre/track MIDI Filter, channel routing, and whether the
front-panel control emits a CC at all in the current Program). None of
that is in the parameter map and none of it can be. It is determined
empirically in the panel tests, per control, and recorded in
the root `RESUME.md`.

## Tested legend (used in the CSV `Tested` column)

| Mark | Meaning |
|---|---|
| `yes` | Hardware-verified: device test 16 oct. 2026, CC74 on OS 3.2.3 on 12 oct. 2026, or panel test 16 oct. 17 h 27 / 18 h 30 |
| `doc` | From the Korg tables / SYSEX_KRONOS.md (marked D or T there); not yet tested on hardware |
| `inherited` | Taken from the M4L device or its prose; never validated on hardware |
| `no` | The shipped form was tested and failed; the corrected form is prepared in complet-0.96 but untested |

## Deliverable

`panels/KronosKontrol/parameter_map.csv`. **124 rows** (78 after the
original Phase A, extended and corrected 24 oct. 2026). Every
Feedback value is either sourced or explicitly `unknown`, with the
reason in the `Source` column. WidthBits and Scaling are corrected
against the bit-level tables and the hardware tests.

## 2026-10-24 amendment

After the rack design was fixed (LISEZMOI_panneau.md) and the panel
was built and tested (REPRISE.md), the CSV was extended from 78 to
**124 rows** and corrected. Changes:

**Rows added**

- BANK SELECT: 14 buttons (I-A…I-G, U-A…U-G) + U-A/AA toggle + GM
  menu (GM, g(1)…g(9), g(d)) — CC0/CC32/PC per the Korg bank map,
  MSB before LSB, then PC.
- MIXER / PAN: 8 encoders — Combi timbre 1–8 volume (fn 43 TYP 4
  SOC n-1 PID 2) and pan (PID 1); Program OSC1/OSC2 Patch Level
  (HD-1 TYP 9/10 + EXi TYP 11/12, SOC 3, PID 6; pan PID 3), Drum
  Track volume (TYP 0 PID 39), Master volume (TYP 7 PID 12).
- KARMA Module Control (Combi TYP 2 PID 2, Master/A–D; Program: Master
  fixed).
- FX coverage completed: IFX6–12 and TFX2 in both modes (the original
  16 rows covered only what the M4L device had).
- Drum Track Volume and Mute (fn 43 PIDs 39 / 40, verified in the
  tables at Prog_EXi_Common.txt l.2216 / l.2223; Mute device-tested).

**Rows corrected**

- **FX switches (all 16, both modes):** value is **inverted** —
  0 = On, 1 = Off. Every FX row in the tables is marked
  `* -> bypass, Invert Value`. The panel sends 1 − state.
- **GE select:** the device's fn 43 `43 01 00 00 00` address is
  Common LFO Waveform, not the GE (collision, see A3). GE goes via
  **fn 6D** in Program (`6D 01 00 00 00 00 vH vM vL`, value split as
  for fn 43: vH = n >> 14, vM = (n >> 7) & 0x7F, vL = n & 0x7F — for
  n ≤ 3583, vH = 0; see kkParam/kkParamF in kkMain.lua); in Combi,
  fn 43 TYP 3 SOC = module, with a 6D retry on Reply 24 code ≠ 0.
- **Drum Track On:** the device's fn 43 `43 00 00 00 0A` address is
  Common Scale Type, not Drum Track On (collision). Drum Track On goes
  via **fn 6E** in Program (`6E 00 00 00 0A 00 00 00 v`); in Combi,
  fn 43 TYP 1 (corrected from TYP 0) with a 6E retry. Note:
  SYSEX_KRONOS.md marks Drum Track On "T" (transmittable), but the
  device test log says it was never validated and the panel's fn 43
  attempt failed — the CSV marks it `no` (shipped form failed,
  corrected form prepared in complet-0.96, untested). The discrepancy
  is documented in KRONOS_SYSEX_PARAMETER_CONTROL.md §12b.
- **KARMAScene (CC 30):** values 0–7 = Scenes 1–8 (Min corrected
  1 → 0 in the 2025 pass; confirmed against the parameter guide).

**Tested column populated** per the legend above: 61 `yes`,
41 `doc`, 20 `inherited`, 2 `no` (GESelectProgram, DrumTrackOnOff —
both corrected in complet-0.96, awaiting the hardware test).

## Notes for later phases

- `KARMAScene` (CC 30): the source doc states values 0–7 map to
  Scenes 1–8, values 8–127 are invalid. The panel UI exposes Scenes
  as 1–8, so the Lua subtracts 1 before sending (`kkGECatMenu` /
  scene buttons in kkMain.lua).
- `SW1`, `SW2`, `Damper`, `KARMAOnOff`, `KARMALatch`,
  `KARMASwitch1–8` use the threshold-64 convention (0–63 = Off,
  64–127 = On). The CSV records this in `Scaling`. The panel sends
  only 0 or 127 for these; they are two-state.
- `KARMASlider1–8`, `VectorX`, `VectorY`, `ToneAdjustKnob1–4`, EG and
  LFO CCs are continuous 0–127.
- `ToneAdjustKnob1–4` are only meaningful when the Program's Tone
  Adjust page assigns them; on a Program with no Tone Adjust, they do
  nothing. The panel sends the CC regardless; the Kronos ignores it.
  This is normal and does not require special handling.
- KARMA CCs are **Off by default** on the Kronos: the user must run
  GLOBAL › Reset Controller MIDI Assign › CC Default, then Write
  Global Setting. Without this, the KARMA section of the panel has no
  effect. Recorded in `docs_old/REPRISE.md` (archived) and the test plan.
- In Program mode, MIXER encoders 1 and 2 send **both** the HD-1
  (TYP 9/10) and the EXi (TYP 11/12) messages: the Kronos refuses the
  one that does not match the current engine (Reply 24 code 1, no
  side effect). Encoders 4–7 do nothing in Program mode.
