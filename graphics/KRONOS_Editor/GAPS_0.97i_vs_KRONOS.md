# Kronos Kontrol EDITOR — what panel 0.97i covers, and what is missing

*27 October 2026. Reference: `..\EDITOR_WINDOW.md` (next to the `KRONOS_Editor` folder) (panel build complet-0.97i, 3,024 generated parameters)
compared with Korg's own parameter tables from the **KRONOS MIDI Implementation** (`KRONOS_MIDIimp.zip`, files
`Prog_HD-1.txt`, `Prog_EXi_Common.txt`, `Prog_EXi.txt`, `CombiAndSongTimbreSet.txt`, `Global.txt`, `DrumKit.txt`,
`WaveSequence.txt`, `SetList.txt`, `SongControl.txt`, `Effect.txt`, `KRONOS_MIDI_SysEx.txt`).*

## 1. Method and reasoning

- **Why the MIDI Implementation and not the Parameter Guide.** The Parameter Guide explains what the parameters do, but
  Korg's MIDI Implementation lists **every stored parameter of every object** with its byte offset (OFS), bit field,
  data range, value range and SysEx identifiers (TYP / SOC / SUB / PID / IDX). It is exactly what an editor reads
  and writes in an object dump (function 0x4B / 0x49 / 0x4C). Counting from it gives a complete inventory, with no
  guessing.
- **What is counted.** "Editable" parameters: everything except names (counted separately as text fields), binary
  UUIDs (multisample / sample bank references, set by binary parameter change), parameters marked `(fixed)` (read-only
  in that object) and reserved bytes.
- **Repeated structures** (2 oscillators, 16 timbres, 8 multisample zones, 64 wave-sequence steps, 128 drum-kit notes,
  128 external MIDI sets…) are counted for all instances, because the editor must reach all of them. Where Korg's table
  only lists the first instances (Drum Kit notes 1, 2, 128; Wave Seq steps 1, 2, 64; Set List slot 0), the total is
  the per-instance count × the number of instances.
- **How the gaps are closed.** The complete editor (`Full\`) is **generated from those same tables**: every listed
  parameter gets a control, so nothing can be forgotten by hand. A safety net puts any group that the page plan does not
  classify into a `MORE` area (none was needed for the KRONOS). Every control in the `_layout.json` files carries its
  Korg source (`korg`: file, OFS, bit, SysEx fields, data and value range), so the programmer does not have to look
  anything up.

## 2. Coverage in numbers

| Object (dump type) | Panel 0.97i | KRONOS (Korg tables) | 0.97i coverage |
|---|---:|---:|---:|
| Program — HD-1 (obj 00) | 404 (all program types together) | 1,872 | ≈ 20 % of HD-1 alone |
| Program — EXi common part (obj 00) | (included above) | 1,359 | — |
| Program — EXi engines (obj 00) | 160 (10 per engine × 8 × 2) | 3,528 (AL-1 586, CX-3 151, STR-1 678, MS-20EX 494, PolysixEX 312, MOD-7 1,101, SGX-2 23, EP-1 183) per engine slot, × 2 engines | ≈ 2 % |
| Combination (obj 01) | 1,930 | 6,677 | 29 % |
| Global (obj 03) | 591 | 12,056 | 5 % |
| Drum Kit (obj 04) | 71 (note 1 + a few of notes 2 and 128) | 61 per note × 128 notes ≈ 7,800 | ≈ 1 % |
| Wave Sequence (obj 05) | 28 (step 1) | 15 common + 15 per step × 64 ≈ 975 | ≈ 3 % |
| Set List (obj 0D) | 0 | ≈ 25 per slot × 128 slots + list EQ | 0 % |
| Song: Song Control (obj 08) + Song Timbre Set (obj 02) | 0 | 1,636 + 6,677 | 0 % |
| Effects: parameters of each effect type (Effect.txt) | 0 (type, on/off and pan only) | 3,828 over 197 types, reachable from 16 effect slots | 0 % |

## 3. Missing features, by area (with the reason each one matters)

### 3.1 Working with the instrument
1. **No WRITE destination.** `Write → 0x49` writes "to the selected slot", but the editor has no bank and number
   selector. Without it, the user cannot choose where the edited sound goes. → *Added in the complete editor: `WRITE TO`
   bank menu + number box in the header (`kkDestBank`, `kkDestNumber`).*
2. **No COMPARE.** Comparing the edited buffer with the version read from the KRONOS is the basic safety net of any
   editor (the KRONOS has a COMPARE button). → *Added: `kkBtnCompare` (local, no SysEx needed).*
3. **Object selector limited to five objects**: no Set List, no Song. → *Added: Set List and Song pages.*

### 3.2 Program — HD-1
4. **Multisample zones.** Korg's `OSC# Trigger` has 8 zones per oscillator (type, multisample number, level, start
   offset, reverse) plus velocity zones and crossfades; 0.97i has none of them, so the sound source itself cannot be
   chosen. → *OSC area, tables 1-8.*
5. **Pitch**: portamento, bend ranges, JS / ribbon intensities, frequency offset are missing (0.97i: 6 of 25).
6. **Drive and low boost** (`OSC# Drive`): missing.
7. **Filter EG** (34 parameters) and **filter keyboard track**: missing; only cutoff / resonance / trim / output are there.
8. **Amp EG**: levels and times are there, but not the curves, the level / time modulation and the keyboard track
   (0.97i: 8 of 33 + 0 of 7).
9. **LFO**: 7 of 21 per LFO (no fade, delay, MIDI sync, intensity modulation…).
10. **Mod.Mixer 1-2 of each oscillator**: missing (0.97i only has the EXi ones).
11. **Pitch EG, Common LFO (17), Common Keyboard Track 1-2**: Common LFO is there; Pitch EG and keyboard tracks are missing.

### 3.3 Program — EXi
12. **Engine parameters.** Each engine page of 0.97i shows 10 parameters; the engines have 23 (SGX-2) to 1,101 (MOD-7).
    This is the largest gap: an EXi program cannot be built from scratch. → *Engines\<engine>\, by area
    (OSC, FILTER, AMP·MIX, EG, LFO, MOD, FX, MAIN).*
13. **EXi common step sequence** (106) and **EXi input / key zone / algorithm** settings: missing.
14. **Label error in the specification:** in EXi Mix, the second "Mod.Mixer · Amount A" (kkF_04_012, -199..199) is
    **"Offset: Amount"** in Korg's tables.

### 3.4 Effects
15. **Effect parameters.** 0.97i sets the type, the switch and the pan, but no parameter of the effect itself (3,828
    parameters over 197 types). → *FX EDIT: one generic page (40 cells) per effect slot; `FX_LAYOUTS.json` gives, for
    each of the 197 types, which parameter goes in which cell and with which control.*
16. **IFX routing**: channel, chain, chain-to, bus select, FX control bus, sends and rec bus of the program IFX are
    missing (they exist on the Combi pages only). Effect LFO 1-2 of the program: missing.

### 3.5 Performance features
17. **KARMA**: 747 parameters in a program (KARMA common + 1 module) and 3,596 in a combination (common + modules A-D),
    none in 0.97i: GE, scenes, switches / faders, dynamic MIDI, RT parameters, note map, chord pads.
18. **Tone Adjust** (49 per program; per combi timbre: knob 1-8, switch 1-16 and fader 1-8 assignments and values):
    missing in the program; in the combi only the 16 switch values are there. Tone Adjust is the KRONOS feature that
    lets a combi change the sound of its programs without editing them.
19. **Program vector** (51), **program drum track** (44), **program audio inputs** (49): missing (they exist for the combi).
20. **Combi timbres**: 103 of 174 parameters per timbre. Missing: bend range, portamento time, swing, key window
    top / bottom slopes and the Tone Adjust assignments of the timbre (knob, switch and fader assign / value, switch
    on value, master fader).

### 3.6 Drum Kit, Wave Sequence, Global
21. **Drum Kit**: only note 1 is fully editable; the 127 other notes, and the 8 velocity zones of each, are not.
    → *NOTE selector 1-128.*
22. **Wave Sequence**: only step 1; the 64 steps share the same structure. → *STEP selector 1-64.*
23. **Global**: external MIDI set 1 only (60 of 11,520 parameters over 128 sets), no category names (18 program,
    18 combi and 18 KARMA categories with 8 sub-categories each), all scales are there.
    → *EXT SETS selector 1-128, CATEGORIES selector.*

### 3.7 Other objects
24. **Set List** (128 slots: performance, bank, index, hold time, volume, keyboard track, color, font, transpose,
    comments; list EQ): not in 0.97i. → *Set List pages.*
25. **Song** (song control: MIDI / automation / audio tracks, patterns, RPPR; timbre set = same structure as a combi):
    not in 0.97i. → *Song pages; TIMBRE SET reuses the Combi pages.*
26. **Drum Track patterns** (pattern name, length, meter + event list) are event data, not parameters: they need a
    pattern grid editor, which is outside parameter pages. Not drawn; listed here so it is not forgotten.
27. **KARMA GE and templates** cannot be edited on the instrument (no edit buffer, says Korg); the GE RTP info
    (`KARMA_GE_RTP.txt`, read-only) is what gives the KARMA sliders their names.

### 3.8 Specification quality
28. **Option lists are truncated** in `EDITOR_WINDOW.md` (e.g. "Low | 1 | Last", "Saw | 1 | 2 | … | Square/Triangle"):
    the menus need the full lists from the Parameter Guide.
29. **Visibility rules** (`apply`) exist for HD-1 / EXi / engines; the complete editor adds `exi:<engine>` for engine
    pages and keeps `hd1` / `exi` for the program areas.

## 4. Where to find the pages

| Gap | Complete editor |
|---|---|
| 1-3 | header of every page in `Full\` |
| 4-11 | `Full\Program`, areas OSC, FILTER, AMP, LFO·MIX, COMMON MOD |
| 12-14 | `Full\Program` areas EXi, STEP SEQ; `Full\Engines\<engine>` |
| 15-16 | `Full\Effects` (FX EDIT) and the EFFECTS areas |
| 17-20 | KARMA / KARMA GE / KARMA MODULE, CONTROL, VECTOR, DRUM TRACK, AUDIO IN, TIMBRE areas |
| 21-23 | `Full\DrumKit`, `Full\WaveSeq`, `Full\Global` |
| 24-25 | `Full\SetList`, `Full\Song` |
