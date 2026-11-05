# Kronos — controlling every parameter over SysEx

**Rewritten for the ctrlr-project from pcglib knowledge (v1.6.3, commit
`c2af0f2`), then merged on 2026-10-24 with the hardware-verified facts of the
previous Ctrlr project (`docs/SYSEX_KRONOS.md`, tested on a real Kronos on
2026-10-16, plus the panel's `REPRISE.md`).** This document collects, in one
place, everything needed to drive **all** Kronos parameters from the panel:
the SysEx grammar, the parameter identification system, every relevant
function code, the CC layer the M4L device already uses, and worked decodings
of the hardware-verified messages.

**Where this document and `docs/SYSEX_KRONOS.md` disagree, SYSEX_KRONOS.md
wins** — it records what was actually tested on a real Kronos (T/D states);
this document records the grammar and the table knowledge. The known
disagreements are listed in §12b.

Sources (all in this folder unless noted):

- `midi/KRONOS_MIDI_SysEx.txt` — Korg's own function table, v1.27 (Oct 22, 2016).
  The authority for the grammars below.
- `midi/Prog_HD-1.txt`, `Prog_EXi.txt`, `Prog_EXi_Common.txt`,
  `CombiAndSongTimbreSet.txt`, `Global.txt`, `Effect.txt`, `DrumKit.txt`,
  `WaveSequence.txt`, `SongControl.txt`, `SetList.txt`,
  `DrumTrackPattern.txt`, `KARMA_GE_RTP.txt` — the bit-level parameter tables
  that carry each parameter's `TYP/SOC/SUB/PID/IDX`.
- `midi/SysExParams/VoiceModels/` — per-engine variants (AL-1, CX-3, EP-1,
  HD-1, MOD-7, MS-20EX, Off, PolysixEX, SGX-1, STR-1).
- `tables/` — the same tables restructured as CSV/JSON (see
  `KRONOS_TABLES_GUIDE.md`).
- `docs/SYSEX_KRONOS.md` — **hardware-verified** parameter SysEx (2026-10-16):
  the T/D state per parameter, the FX inversion, the Program-mode address
  collisions. Read it alongside this document.
- `docs/KRONOS_PCG_FORMAT_FACTS.md` — cross-validated format facts (bank maps,
  object sizes, SysEx bank codes).
- `m4l/export/README.md` — the M4L export index: what is verified, and the
  Ctrlr pointers (SysEx formula field, `kronosFxSwitch`, `kronosOnMidi`).
- `../../panels/KronosKontrol/parameter_map.csv` — the 124 panel controls
  with their message bytes and their Tested state.
- `../../panels/KronosKontrol/REPRISE.md` — the panel's development log,
  including the complet-0.96 corrections (fn 6D/6E, mode memory).
- `../../docs/CONNAISSANCES_KRONOS_PCG.md` §11 — SysEx findings hardware-tested
  on a real Kronos (5/5 with Erriez MIDI SYSEX-IO, Windows 11).

---

## 1. The SysEx header and the channel byte

```
F0  42  3g  68  [function]  [data...]  F7
```

- `42` = Korg manufacturer ID.
- `3g` = **global MIDI channel − 1** (channel 1 → `0x30`, channel 16 → `0x3F`).
- `68` = Kronos family identifier.
- All bytes between `F0` and `F7` are 7-bit.

## 2. Parameter identification: TYP / SOC / SUB / PID / IDX

Most parameter-change functions address a parameter by a **5-byte id**:

| Byte | Name | Role |
|------|------|------|
| 1 | TYP | parameter type / object category |
| 2 | SOC | source / category |
| 3 | SUB | sub-category |
| 4 | PID | parameter id |
| 5 | IDX | index (e.g. timbre, effect slot, engine slot) |

Where the ids live:

- In the Korg text tables (`midi/*.txt`): five columns `TYP|SOC|SUB|PID|IDX`
  at the right of each parameter row. Some rows carry **packing footnotes**,
  e.g. `* SUB = (Assign >> 7) & 0x01, Value = Assign & 0x7f` — the id bytes are
  derived from the parameter's own bits.
- In the JSON twins (`tables/*.json`): the `ids` array, in the same order
  (TYP, SOC, SUB, PID, IDX) plus a spare slot. `"11/12"` means the parameter
  exists under two TYP values (e.g. EXi engine 1 / engine 2); `"?"` = not yet
  mapped; empty = no SysEx id (e.g. the name bytes).

**Deprecated form.** For parameter ids 127..16383 there is a 14-bit form
(`TYP SOC SUB 7F PIDH PIDL IDX`). The instrument still **receives** it but
never **transmits** it. The first (5-byte) form covers ids 0..126, and the
instrument accepts either form for ids 0..126. **A panel only needs the 5-byte
form.**

**Address collisions (hardware-verified 2026-10-16, REPRISE.md).** In a
**Program**, several sections share the same 5-byte id, and fn 43 resolves
the collision **against** the sections the panel wants:

- `01 00 00 00 00` is both `KARMA Module GE Number` (Prog_EXi_Common.txt
  l.1093) and `Common LFO Waveform` (l.2249) — **fn 43 addresses the LFO
  Waveform**. The GE must be sent with **fn 6D** (§5).
- `00 00 00 0A 00` is both `Drum Track Common Drum Track On` (l.424) and
  `Common Scale Type` (l.2080) — **fn 43 addresses the Scale Type**. The Drum
  Track On must be sent with **fn 6E** (§5).
- `00 00 00 27/28 00` (Drum Track Volume/Mute, l.2216/l.2223) are also shared
  with KARMA Common Chord Pad Velocity (l.687/l.689), but the device tests
  confirmed the Drum Track interpretation works via fn 43 — the shared id
  resolves for Volume/Mute, against the panel for On.

In a **Combi** the panel's addresses are collision-free (TYP 1 Drum Track,
TYP 2 KARMA Common, TYP 3 KARMA Modules, TYP 4 timbres, TYP 23/24 effects);
the complet-0.96 panel still retries the same address via fn 6D/6E if the
Kronos answers Reply 24 with a code ≠ 0.

## 3. Function 43 — Parameter Change (integer) — Receive/Transmit

```
F0  42  3g  68  43  TYP  SOC  SUB  PID  IDX  valueH  valueM  valueL  F7
```

- `valueH` = value bits 14–20, `valueM` = bits 7–13, `valueL` = bits 0–6:
  a **21-bit value**, 7 bits per byte. To send a value `v`:
  `valueL = v & 0x7F`, `valueM = (v >> 7) & 0x7F`, `valueH = (v >> 14) & 0x7F`.
- Korg: *"Most of the instrument's parameters (mainly those that control the
  synthesis engine) can be edited with this kind of message… Which parameters
  are currently available for editing depends on the instrument's mode (e.g.,
  combi parameters are only allowed while in combi mode)."* — **the panel must
  know the current mode** (it tracks it via fn 42/4E, §6; complet-0.96 also
  re-sends 4E before any selection when the Kronos is in Global/Disk/Seq/Set
  List, and queues the messages until Reply 24 code 0).
- **FX switches are inverted** (hardware-verified): the tables mark them
  `* -> bypass, Invert Value` — the SysEx value is **0 = On, 1 = Off**; send
  `1 − desired state`.

## 4. Function 44 — Parameter Change (binary) — Receive/Transmit

```
F0  42  3g  68  44  TYP  SOC  SUB  PID  IDX  value-type  value[]  F7
```

For parameters that take binary data instead of a 21-bit integer. Currently the
only such type is the **UUID** (16-byte sample reference). The 14-bit parameter
id is **not** supported for fn 44.

## 5. Same-id functions: 41, 6D, 6E — and when each is required

Functions **41** (Sequencer Parameter Change), **6D** (KARMA Parameter Change)
and **6E** (Drum Track Parameter Change) use the identical grammar:
`TYP SOC SUB PID IDX valueH valueM valueL`. Their parameter ids are documented
in `SongControl.txt`, `KARMA_GE_RTP.txt` and `DrumTrackPattern.txt`
respectively.

**Hardware-verified usage (2026-10-16, SYSEX_KRONOS.md + REPRISE.md):**

| Parameter | Mode | Send with | Why |
|---|---|---|---|
| KARMA GE Number (TYP 1 PID 0) | Program | **fn 6D** | fn 43 `01 00 00 00 00` = Common LFO Waveform (§2) |
| Drum Track On (TYP 0 PID 10) | Program | **fn 6E** | fn 43 `00 00 00 0A 00` = Common Scale Type (§2) |
| Drum Track Volume (PID 39) / Mute (PID 40) | Program | fn 43 | device-tested OK |
| KARMA Module A–D GE (TYP 3 SOC 0–3 PID 0) | Combi | fn 43 (retry 6D) | no collision in Combi |
| Module Control (TYP 2 PID 2) | Combi | fn 43 (retry 6D) | no collision in Combi |
| Drum Track On (TYP 1 PID 10) | Combi | fn 43 (retry 6E) | TYP 1 in Combi (0.96 correction) |

The complet-0.96 panel decodes 6D/6E on receive as well (the Kronos
transmits them when KARMA / Drum Track parameters are edited).

## 6. Function 4E — Mode Change — Receive/Transmit

```
F0  42  3g  68  4E  0000 mmmm  F7
```

Mode values: **0 = Combi, 2 = Program, 4 = Seq, 6 = Sampling, 7 = Global,
8 = Disk, 9 = SetList**.

- After receiving it, the Kronos changes mode and transmits a **function 24
  (Reply)** message.
- When the mode is changed from the instrument's front panel, the Kronos
  **transmits this message** — the panel can track front-panel mode changes
  for free.
- Reply 24 codes (SYSEX_KRONOS.md): 0 OK · 1 wrong parameter type for the
  mode · 2 unknown id · 3 truncated · 4 object not found · 6 value out of
  range · 65 protected. The panel displays them in clear text.

## 7. Drum kits and wave sequences: functions 53/54/55/56 and 71

- **53** Drum Kit Parameter Change (integer), **54** (binary),
  **55** Wave Seq Parameter Change (integer), **56** (binary).
- **71 — Set Current Object** selects which kit / wave sequence the 53/55
  messages edit:

```
F0  42  3g  68  71  obj  idH  idL  F7      obj: 0 = drum kit, 1 = wave seq
```

`idH`/`idL` are a 14-bit **linear index** (the same addressing the HD-1 MS
number parameter uses), not bank + id:

| Linear # | Drum kits | Wave sequences |
|----------|-----------|----------------|
| 0 .. 39 / 0 .. 149 | I-00 .. I-39 / I-000 .. I-149 | (INT bank) |
| 40 .. 151 | U-A … U-G (16 per bank) | 150 .. 373 = U-A … U-G (32 per bank) |
| 152 .. 160 | GM0 .. GM8 | — |
| 161 .. 272 | U-AA … U-GG (16 per bank) | 374 .. 597 = U-AA … U-GG (32 per bank) |

## 8. Program bank type: functions 7C, 60, 61

- **7C — Change Program Bank Type** (Receive):
  `F0 42 3g 68 7C <bank> <type> F7` — type **1 = EXi, 0 = HD-1**. Loading a
  whole bank changes the destination's type; a single program requires a
  destination of the same type.
- **60** Program Bank Types Request (Receive) → the Kronos answers **61**
  Program Bank Types (Transmit, bitmap). Also transmitted whenever bank types
  change (e.g. after loading a PCG).

## 9. Object dumps: functions 72 / 73 / 74 / 75 / 76 / 77

- **72** Object Dump Request (Receive) → answers **73** Object Dump
  (Receive/Transmit):
  `F0 42 3g 68 73 <obj> <bank> <idH> <idL> <version> <data 8→7-bit> F7`
  - obj `00` = program (v5; **EXi 4,960 bytes**, **HD-1 3,706 bytes**),
    obj `01` = combi (v3, **7,810 bytes**).
  - SysEx bank codes: programs I-A…I-F = `00…05`, U-A…U-GG = `40…4D`;
    combis I-A…I-G = `00…06`, U-A…U-G = `40…46`.
  - 8→7-bit packing: per group of 7 data bytes, one high-bits byte (bit j =
    bit 7 of data byte j), then the 7 bytes `& 0x7F`.
- **74** Current Object Dump Request (Receive) → **75** Current Object Dump
  (Receive/Transmit) — the sound being edited.
- **76** Store Bank Request (Receive/Transmit): `F0 42 3g 68 76 <obj> <bank> F7`;
  the Kronos answers function 24, code 0 = success. Send after the dumps.
- **77** Dump Bank Request (Receive) — the Kronos sends a whole bank.
- Hardware-verified (CONNAISSANCES §11): **pause ≥ 100 ms between messages**
  (tested 5/5 with Erriez MIDI SYSEX-IO on Windows 11).

## 10. Change detection and information functions

| Fn | Name | Direction | Use for a panel |
|----|------|-----------|-----------------|
| 37 / 38 | Bank Digest Request / Bank Digest | Receive / Transmit | fingerprint a bank — know what changed without re-reading it |
| 39 / 3A | Bank Digest Collection Request / Collection | Receive / Transmit | all bank digests at once |
| 32 / 33 | Current Performance Id Request / … Id | Receive / Transmit | which program/combi is current |
| 34 / 35 / 36 | Piano Types Request / … / Notify Changed | R / T / T | installed SGX piano types |
| 30 / 31 | Current Sample Information Request / … | Receive / Transmit | sample behind the current sound |
| 79 / 7A | SMF Data Dump Request / Data Dump | Receive / Transmit | song data |
| 12 / 42 | Mode Request / Mode Data | Receive / Transmit | ask / be told the current mode |
| 48 | Edit In Context Notify | Transmit | the user entered edit context |
| 78 | Reset Controller | Receive/Transmit | reset a controller |
| 24 | Reply | Transmit | answer to requests (code 0 = success) |

## 11. The CC layer (what the M4L device uses)

Program/combi selection is plain MIDI, not SysEx:

1. **CC0 (Bank Select MSB)**, then **CC32 (LSB)**, then **Program Change** —
   Kronos in **Bank Map KORG** (Global settings). KORG bank map:
   - programs: I-A…I-E = CC0/0 + CC32/0…4, I-F = CC32/5, GM = CC0/121 + CC32/0,
     g(1)…g(9) = CC0/121 + CC32/1…9, g(d) = CC0/120 + CC32/0,
     U-A…U-G = CC32/8…14, U-AA…U-GG = CC32/15…21;
   - combis: I-G = CC0/121 + CC32/0, U-A…U-G = CC32/8…14.
2. The panel CC set (all channel = global channel, all feedback class-level
   "both", sourced to the MIDI Applications prose): filter cutoff CC74,
   resonance CC71, EG intensity CC79, release CC72, attack CC73, decay CC75,
   sustain CC70, Tone Adjust knobs CC17/19/20/21, LFO1 speed/depth CC76/77,
   ribbon CC16, portamento CC5, KARMA sliders CC22–29, KARMA on/off CC14,
   KARMA latch CC31, KARMA scene CC30 (**values 0–7 = scenes 1–8**), KARMA
   switches CC102–109, SW1/SW2 CC80/81, vector X/Y CC118/119, damper CC64.
   Switches, latch and damper use the **threshold-64** convention
   (0–63 = Off, 64–127 = On).
3. Hardware finding from the M4L work: **the KARMA CCs are disabled by default
   on the Kronos** — enable them via Global → Reset Controller MIDI Assign →
   CC Default, then Write.
4. Sanity check already passed on hardware: one slider sending **CC74** moves
   the filter cutoff.

## 12. Worked examples — the hardware-verified messages decoded

All bytes below are the exact strings from `parameter_map.csv` (channel 1, so
`3g` = `30`). **Corrected 2026-10-24** against SYSEX_KRONOS.md and the panel's
REPRISE.md — the 2026-10-14 version of this table decoded the M4L device's
bytes as if they were all valid; two of them are not (see §12b).

| Panel control | Message | Fn | TYP | SOC | SUB | PID | IDX | Value decode |
|---|---|---|---|---|---|---|---|---|
| FX1Switch (IFX1 On) | `F0 42 30 68 43 06 00 00 00 00 00 00 00 F7` | 43 | 06 | 00 | 00 | 00 | 00 | valueL = 0 → **On** (inverted: 0=On, 1=Off) |
| FX1Switch (IFX1 Off) | `F0 42 30 68 43 06 00 00 00 00 00 00 01 F7` | 43 | 06 | 00 | 00 | 00 | 00 | valueL = 1 → **Off** |
| GESelectProgram | `F0 42 30 68 6D 01 00 00 00 00 00 bb nn F7` | **6D** | 01 | 00 | 00 | 00 | 00 | valueM = bb, valueL = nn → GE index = bb×128 + nn (0…3583, 12-bit) |
| GESelectCombiA | `F0 42 30 68 43 03 00 00 00 00 bb nn F7` | 43 | 03 | 00 | 00 | 00 | 00 | same GE decode (Combi: no collision) |
| DrumTrackOnOff | `F0 42 30 68 6E 00 00 00 0A 00 00 00 vv F7` | **6E** | 00 | 00 | 00 | 0A | 00 | valueL = vv → 0/1 |
| DrumTrackVolume | `F0 42 30 68 43 00 00 00 27 00 00 00 vv F7` | 43 | 00 | 00 | 00 | 27 | 00 | valueL = vv → 0–127 |
| DrumTrackMute | `F0 42 30 68 43 00 00 00 28 00 00 00 vv F7` | 43 | 00 | 00 | 00 | 28 | 00 | valueL = vv → 0/1 |
| MixVolTimbre1 (Combi) | `F0 42 30 68 43 04 00 00 02 00 00 00 vv F7` | 43 | 04 | 00 | 00 | 02 | 00 | valueL = vv → 0–127 |
| MixPanTimbre1 (Combi) | `F0 42 30 68 43 04 00 00 01 00 00 00 vv F7` | 43 | 04 | 00 | 00 | 01 | 00 | valueL = vv → 0–127 (64 = center) |
| MixVolOSC1 (Program, HD-1) | `F0 42 30 68 43 09 03 00 06 00 00 00 vv F7` | 43 | 09 | 03 | 00 | 06 | 00 | OSC1 Patch Level (EXi1 variant: TYP 11) |
| MasterVolumeProgram | `F0 42 30 68 43 07 00 00 0C 00 00 00 vv F7` | 43 | 07 | 00 | 00 | 0C | 00 | valueL = vv → 0–127 |
| ModuleControl (Combi) | `F0 42 30 68 43 02 00 00 02 00 00 00 vv F7` | 43 | 02 | 00 | 00 | 02 | 00 | valueL = vv → 0–4 (Master…D) |
| ModeChange | `F0 42 30 68 4E 02 F7` | 4E | — | — | — | — | — | mode 2 = Program |

The GE decode is the general pattern: a 12-bit quantity (0–3583) split across
`valueM`/`valueL` with `valueH` = 0 (`valueM = n / 128`, `valueL = n % 128`).

## 12b. Hardware-verified corrections (2026-10-16) — what changed and why

The M4L device's `sxformat` bytes were copied into the first version of this
document and of `parameter_map.csv` as if they were all hardware-validated.
The device's own test log (`m4l/docs_dev/REPRISE.md`, `m4l/LISEZMOI.txt`)
says otherwise: tested on the Kronos (16 oct. 2026) = mode Program/Combi,
banks and programs, **IFX1 On / IFX2 Off (inverted value confirmed)**, MIXER
(Combi timbre volumes; Program OSC1 + Drum Track volume), PAN (Combi
timbres), **Drum Track Mute**. **Not verified: KARMA (CCs), GE, X-Y** — only
CC74 was verified earlier (v3.2.3, 12 oct.).

| Fact | Was (2026-10-14) | Now (2026-10-24) | Evidence |
|---|---|---|---|
| FX switch value | "Off~On" (0=Off, 1=On) | **inverted: 0=On, 1=Off** (send `1 − state`) | tables `* -> bypass, Invert Value`; device test IFX1 On / IFX2 Off |
| GE Number, Program mode | fn 43 `43 01 00 00 00 00 …` | **fn 6D** `6D 01 00 00 00 00 …` | `43 01…` = Common LFO Waveform (Prog_EXi_Common.txt l.1093 vs l.2249); panel test 16 oct.: GE select had no effect; device never validated GE |
| Drum Track On, Program mode | fn 43 `43 00 00 00 0A …` | **fn 6E** `6E 00 00 00 0A …` | `43 00 00 00 0A` = Common Scale Type (l.424 vs l.2080); panel test: no effect via fn 43 |
| Drum Track On, Combi mode | TYP 0 | **TYP 1** | CombiAndSongTimbreSet.txt l.426 |
| GE value width | "14 bits (bank/num)" | **12 bits** (0–3583), `valueM = n/128`, `valueL = n%128`, `valueH = 0` | SYSEX_KRONOS.md; Prog_EXi_Common.txt l.1093 (0000~0DFF) |
| Drum Track Volume / Mute | not in the CSV | fn 43 PIDs **39 / 40**, device-tested | Prog_EXi_Common.txt l.2216 / l.2223; device test (MIXER Drum Track, MUTE) |
| Timbre Volume / Pan | not in the CSV | fn 43 **TYP 4, SOC = timbre, PID 2 / 1**, device-tested | CombiAndSongTimbreSet.txt l.4964 / l.4974; device test (MIXER/PAN Combi) |
| Master Volume | not in the CSV | Program **TYP 7 PID 12**; Combi **TYP 24 PID 12** (doc) | Prog_EXi_Common.txt l.279; CombiAndSongTimbreSet.txt l.281 |
| OSC/EXi Patch Level, Panpot | not in the CSV | **TYP 9–12, SOC 3, PID 6 / 3**; OSC1 Patch Level device-tested | Prog_HD-1.txt l.2663/l.3069/l.3075; Prog_EXi_Common.txt l.2402/l.2408/l.2470/l.2476 |
| Module Control | not in the CSV | **TYP 2 PID 2**, 0–4 (Master…D), Combi; panel-tested | CombiAndSongTimbreSet.txt l.439; panel test 18h30 |
| SYSEX_KRONOS.md marks DT On "T" | — | treated as **untested**: the device never validated DT On and the panel's fn 43 attempt failed; the fn 6E form (0.96) is prepared but untested | REPRISE.md §b (newer, more specific than SYSEX_KRONOS.md's T mark) |

M3 legacy messages (`F0 42 30 75 41 …`, model 0x75) still exist in the
device's patch: they do **not** address a Kronos and must not be reused
(SYSEX_KRONOS.md "Reliquats").

## 13. Feedback: what the instrument echoes back

- Korg's function table marks **43 / 44 / 41 / 6D / 6E as Receive/Transmit**:
  the Kronos transmits parameter changes as parameters are edited. The panel
  decodes 43, 6D, 6E on receive (complet-0.96).
- Korg publishes **no per-parameter Transmit/Receive/Both table**. The MIDI
  Applications prose states "both" for every controller group the panel
  uses — that is a **class-level** claim, not a per-parameter one.
- Whether a hardware edit actually reaches the panel is a **runtime** question:
  Enable Control Change / Enable Exclusive (Global), per-timbre/track MIDI
  Filter, channel routing. It is discovered per control on the hardware
  and recorded per control in `parameter_map.csv` (Tested column) and in the
  panel README.
- Free feedback: fn **4E** (mode changed on the front panel), fn **61** (bank
  types changed), fn **24** (replies), fn **38/3A** (bank digests).

## 14. Enumerating every parameter (the v2 goal)

One text table per object, each row = one parameter with its bit offset,
width, range **and** its fn 43 id:

| Table | Object | Slot size | Notes |
|---|---|---|---|
| `Prog_HD-1.txt` / `Programme_HD-1.csv/.json` | HD-1 program | 4,960 B (3,706 useful) | oscillators at 2774 / 3240, 8 zones × 22 B |
| `Prog_EXi_Common.txt` / `Programme_EXi_commun.csv/.json` | EXi program, common part | same offsets as HD-1 up to 2773 | |
| `Prog_EXi.txt` + `SysExParams/VoiceModels/*.txt` | EXi engine blocks | 1,000 B each | base **2908** (EXi 1) / **3960** (EXi 2); per-engine variants AL-1, CX-3, EP-1, MOD-7, MS-20EX, PolysixEX, SGX-1, STR-1 |
| `CombiAndSongTimbreSet.txt` / `Combinaison.csv/.json` | combination | 7,810 B | 16 timbres × 188 B from offset 4802 |
| `Effect.txt` / `Effets.json` + `Effets_liste.csv` | insert/master/total effects | 64 B per effect block | 198 effect types; `Effets_liste.csv` = type number → name + parameter count |
| `Global.txt` | global settings | 24,620 B (OS 2) / 24,708 B (OS 3) | |
| `DrumKit.txt`, `WaveSequence.txt`, `SetList.txt`, `SongControl.txt`, `DrumTrackPattern.txt`, `KARMA_GE_RTP.txt` | kits, wave seqs, set lists, song, drum track, KARMA GE | see `KRONOS_PCG_FORMAT_FACTS.md` | |

Caveats when generating panel controls from the tables:

- The `ids` mapping is **partial** (`"?"` entries, packing footnotes). Treat the
  Korg text tables as authoritative where they disagree with the JSON.
- Values in the tables are **raw**; the `value` column gives the display
  mapping. Bit fields are LSB-first within each byte; 16-bit values are
  little-endian; negatives are two's complement on the field width.
- Do **not** port logic from PCG Tools: it has three known errors (wave
  sequence OS 1 indexing, drum-kit zone offset, V2→V3 rules) — see
  `../../docs/CONNAISSANCES_KRONOS_PCG.md` §12.
- Mode dependency (§3): combi parameters only answer in combi mode, etc.
- Section collisions (§2): in a Program, fn 43 does not reach the KARMA
  Common / Drum Track Common / KARMA Module sections — use fn 6D/6E there.
