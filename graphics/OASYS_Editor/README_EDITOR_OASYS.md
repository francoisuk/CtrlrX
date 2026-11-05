# OASYS OMNI — EDITOR window artwork

Complete editor for the **Korg OASYS**, in the OASYS OMNI skin (former proposal B: brushed graphite, aluminium ears,
light grey buttons, orange lit bars, aluminium knobs with LED-dot rings, light TouchView-style displays, Michroma
titles). Same page frame, navigation and files as the complete KRONOS editor: read
`KRONOS_Editor\README_EDITOR_KRONOS.md` and `KRONOS_Editor\RECIPES_GUI_DRAWING.md` first; the scripts are in
`KRONOS_Editor\sources_Editor\` (`koasys.py`, `koasys_ofs.py`).

## Sources (updated 28 October 2026)

| Source | What it gives |
|---|---|
| `ctrlr-project\reference\ref-oasys\midi\OASYS_MIDI_implementation.pdf` (Korg, 4 pages) | Channel messages, CC assignments and universal SysEx only (device inquiry: Korg 42, **OASYS series ID 70**, member 06 = 76 keys, 0F = 88 keys). **Korg never published the OASYS SysEx parameter format** ("Consult your local Korg dealer"). |
| `ref-oasys\tables\Oasys_HD1_param_offsets.csv`, `Oasys_EXi_blocks.csv`, `Oasys_Combi_blocks.csv`, `docs\OASYS_PARAMETER_MAP.md` (pcglib v1.6.3) | **Byte-verified** OASYS ↔ KRONOS maps of the program slot (HD-1 and EXi) and the combi slot, derived from factory PCG files. |
| `ref-oasys\docs\OASYS_SQZ_ANALYSIS.md`, `tables\Oasys_SysXMap_summary.csv` | The SysEx address tables found in a MIDI Quest configuration (frame grammar, 214 address files). The **parameter name ↔ address** link is not known yet (open point). |
| `kronos-pcglib\docs\oasys\OASYS_Param_Guide_v1_3_E5.pdf` | Pages, engines, Global, effect list of the OASYS OS 1.3. |

## What the pages contain

The pages keep **the KRONOS structure minus what the OASYS does not have**:

| Removed | Source |
|---|---|
| Drum Track (program and combi) | pcglib (KRONOS-only bytes 1292-1303, 2688-2717); not in the OASYS Parameter Guide |
| Multisample zones 5-8 of each oscillator | OASYS: 4 zones of 6 bytes per oscillator (MAP §8) |
| Velocity crossfade pairs 4-7, MS/WS/D.Kit display | OASYS trigger tail: 12 bytes (MAP §11) |
| Gate parameters of the AMS (Mod.) Mixers | OASYS mixer: 14 bytes, KRONOS: 20 (MAP §7) |
| SGX-2 and EP-1 engine pages | the OASYS 1.3 has **six EXi**: AL-1, CX-3, STR-1, MS-20EX, PolysixEX, MOD-7 (Parameter Guide) |
| Set List | KRONOS feature (OS 2.0) |
| Effect types 186-197 | the OASYS has types **000-185** (see Effects below) |

Note: `OASYS_PANEL_NOTES.md` (ref-oasys) lists eight engines including SGX-1 and EP-1; the OASYS Parameter Guide v1.3
has six. The six-engine list is used here.

## Offsets: `korg.oasys` in every `_layout.json`

Every control of the Program, EXi engine and Combi pages now has, next to the KRONOS address (`korg.ofs`), an
**OASYS block**: `"oasys": {"ofs": <offset or null>, "rule": "<how it was derived>"}`. `ofs` is the byte offset in
the OASYS PCG record ("fiche": program 4386 bytes, combi 7766 bytes); `null` means no verified equivalent. Index
blocks get `stride_bytes_oasys` (OSC 1-2: 288 instead of 466; timbres: 186 instead of 188; zones: 6 instead of 22).

| Object | Rule (pcglib) | Coverage |
|---|---|---|
| Program HD-1 | per-parameter table (`Oasys_HD1_param_offsets.csv`) + zone records (22 → 6 B) + trigger tail (26 → 12 B) | see the counts below |
| Program EXi (common part) | below 2718: as HD-1; 2718-2851: −42 (E1); 2852-2901: not mapped | |
| EXi engine pages | engine block EXi 1 @2848 (KRONOS @2908), EXi 2 @3636 (KRONOS @3960); the first **328 bytes** of each engine are verified (same relative offset); beyond: not mapped | |
| Combi | 0-1291 identical; KARMA + common tail −12; timbres 16 × 186 B @4790 (KRONOS 16 × 188 @4802, same field offsets) | |
| Global, Song, Drum Kit, Wave Seq | no verified map: **KRONOS offsets, to be checked on an OASYS** | — |

| Pages | Parameters with an OASYS offset | Without (no verified equivalent) |
|---|---|---|
| Program (HD-1 + EXi common) | 1444 | 35 |
| EXi engine pages (6 engines) | 1851 | 1455 |
| Combi | 1439 | 4 |

These are **PCG offsets**. To edit a live OASYS over MIDI, the editor still needs the SysEx address of each
parameter, which Korg did not publish; until the SysXMap tables are linked to parameter names (ref-oasys,
`OASYS_SQZ_ANALYSIS.md` §10), an OASYS editor can work on PCG files and use the CCs of the MIDI Implementation
(see `OASYS_Main\README_OASYS_MAIN.md`).

## Banks (for WRITE TO and the bank menus)

| | KRONOS | OASYS |
|---|---|---|
| Programs | I-A..I-F, U-A..U-G, **U-AA..U-GG** | I-A..I-F, U-A..U-G (GM bank in ROM) |
| Combis | I-A..I-G, U-A..U-G | the same |
| Drum kits | INT (40), U-A..U-G, U-AA..U-GG (16) | INT (40), U-A..U-G (16) |
| Wave sequences | INT (150), U-A..U-G, U-AA..U-GG (32) | INT (150), U-A..U-G (32) |

The bank menus of the pages show the KRONOS list (e.g. timbre "Bank Number" INT-A~U-GG): on the OASYS, hide the
U-AA..U-GG entries. Record sizes: drum kit 11,288 bytes (KRONOS 38,424), wave sequence 1,192 (KRONOS 2,216): their
structure differs from the KRONOS and is not mapped yet, so the Drum Kit and Wave Seq pages are a KRONOS-based
proposal.

## Effects

The OASYS has effect types **000-185**, the same types in the same order as the KRONOS (compared name by name with
the Parameter Guide v1.3: only abbreviations differ, e.g. "St.Multiband Compressor"). Types **186-197** (Small
Phase, Orange Phase, Black Phase, Vintage Chorus, Black Chorus, EP Chorus, Vintage Flanger, Red Comp, Vox Wah,
Stereo EP Cabinet, Rotary Speaker Amp Model, Rotary Speaker Pro CX Custom) are KRONOS-only. `FX_LAYOUTS.json` lists
000-185 with `name` (KRONOS) and `name_oasys` (as shown on the OASYS). The effect parameters are taken from the KRONOS (`Effect.txt`): to be checked against
the OASYS Effect Guide where a type was revised on the KRONOS.

## Global

OASYS Global pages (Parameter Guide v1.3): P0 Basic Setup (0-1 Basic Setup, 0-2 Audio Input), P1 MIDI (1-1 MIDI,
1-2 External 1 = 128 External Setups, 1-3 External 2 = drum pad settings), P2 Controller/Scale, P3 Category Name,
P4 Wave Sequence, P5 Drum Kit, P6 Plug-in Info. The Global pages of this editor follow the KRONOS Global table
(BASIC, CONTROLLER, MIDI, EXT SETS, AUDIO IN, scales, CATEGORIES); the drum pad settings (External 2) and Plug-in Info
have no page yet.

## Objects and navigation

| Object | Folder / zip | Areas |
|---|---|---|
| Program | `Program` | GENERAL, OSC, FILTER, AMP, LFO·MIX (OSC 1-2), COMMON MOD, EXi (1-2), STEP SEQ, ENGINE ▸, EFFECTS, FX EDIT ▸, VECTOR, CONTROL, AUDIO IN, KARMA, KARMA GE |
| EXi engines | `Engine_<name>` | AL-1, CX-3, STR-1, MS-20EX, PolysixEX, MOD-7 |
| Combi | `Combi` | GENERAL, TIMBRE (1-16), EFFECTS, FX EDIT ▸, VECTOR, CONTROL, AUDIO IN, KARMA, KARMA MODULE (A-D) |
| Song, Global, Drum Kit, Wave Seq, Effects | same names | as on the KRONOS (see above) |

The chord pads (Pad 1-8, notes and velocities) are part of KARMA Common, as on the KRONOS (bytes shifted by −12).

## Files

Per page: `_maquette.jpg` (one mock-up, JPEG because of the textured skin), `_fond.png`, `_fond@2x.png` and `_layout.json`. Effects: one template (`…_FX_TEMPLATE_fond`, `…_FX_TEMPLATE_maquette`) and `FX_LAYOUTS.json`; no image per effect type. SVG files and @2x mock-ups can be regenerated with the scripts (`GFX_EXTRAS=1`).

## Regenerating the OASYS offsets

```
python koasys.py out\OASYS\Full
python koasys_ofs.py out\OASYS\Full C:\Korg\kronos-corpus\ctrlr-project\reference\ref-oasys
```
`koasys_ofs.py` adds `korg.oasys` and `stride_bytes_oasys` to the layouts and trims `FX_LAYOUTS.json` to 000-185
(effect names from `oasys_effects_v1_3.json`).
