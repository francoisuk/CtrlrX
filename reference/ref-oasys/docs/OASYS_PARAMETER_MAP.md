# OASYS Parameter Map — derived from the MIDI Quest `Korg OASYS.sqz` config and byte-level analysis of factory PCG files

**Status:** v1.6.3 working document (2026-10-23). Reusable reference for the KRONOS ↔ OASYS
conversion in pcglib and for any future work that needs the OASYS parameter addresses
("all parameters finally mapped").

Cross-checked 2026-10-23 against the redone `.sqz` analysis `docs/OASYS_SQZ_ANALYSIS.md`
(companion tables `tables/Oasys_SysXMap_summary.csv`, `tables/Oasys_factory_names.csv`);
corrections applied in §2 (entry layout, ID5857 count), §3 (no `SysXMap.ID8277`) and §4
(EXi1 is a driver-5825 block).

Added for v1.6.3 (the K→O conversion completion): the **EXi engine payload partial map**
(§9 — three byte-verified copy regions, the rest zeroed and reported) and the **combi slot
map** (§10 — KARMA Common + Modules A..D re-derived, shift −12), plus the skipped-bank
reporting and the OASYS v1 combi (11288 B) acceptance in §14.

**Companion tables (generated, do not edit by hand):**

- `tables/Oasys_HD1_blocks.csv` — section-level OASYS ↔ KRONOS HD-1 program-slot block map
  (the converter's source of truth).
- `tables/Oasys_HD1_param_offsets.csv` — per-parameter OASYS ↔ KRONOS offsets for every
  parameter listed in `tables/Programme_HD-1.csv` (2541 rows; zone/trigger-tail rows are
  marked STRUCTURAL, KRONOS-only rows have an empty OASYS offset).
- `tables/Oasys_EXi_blocks.csv` — the EXi engine payload partial map (§9): the three
  byte-verified copy regions and the unmapped gaps.
- `tables/Oasys_Combi_blocks.csv` — section-level OASYS ↔ KRONOS combi-slot block map (§10).

---

## 1. Provenance and licensing

The primary source analysed here is `docs/oasys/Korg OASYS.sqz`, a **Sound Quest / MIDI Quest
commercial product** (the config users load into MIDI Quest to use it as an OASYS librarian/editor).
It is analysed here **for personal, non-commercial use only**. Nothing extracted from it
(ini/bin/sqt/png content) is redistributed or committed to this repository; only facts derived
from it (offsets, sizes, names, addresses) are recorded in this document. The extracted working
copy lives outside the repo (session scratchpad). If this document is shared, this section must
travel with it.

Other sources:

- `factory/OASYS/KORG Factory New/PRODUCER.PCG` — reference OASYS file (OS 1.3; the last factory
  file released by Korg, a rearrangement of the original).
- `factory/OS3.2/FACTORY/PRELOAD.PCG` — reference KRONOS file (OS 3.2.3).
- `tables/Programme_HD-1.csv` — KRONOS HD-1 program parameter table (offsets, sections, ranges).
- `docs/oasys/OASYS_Param_Guide_v1_3_E5.pdf` — OASYS Parameter Guide 1.3 (parameter names/ranges).
- `docs/oasys/OASYS_MIDI_implementation.pdf` — OASYS MIDI implementation (channel messages only;
  **Korg does not publish the SysEx parameter addresses** — "Consult your local Korg dealer").

---

## 2. The `.sqz` container and the MIDI Quest config

`Korg OASYS.sqz` is a custom archive: magic `SQZ `, a 4-byte entry-count header, then entries of
`nameLen(1) + name + blobLen(4 LE) + blob` (the blob length comes **after** the name), each
blob gzip-compressed. 1810 entries. Extracted, it is a full
MIDI Quest instrument config:

```
Korg OASYS.ini                 bank definitions + program names (11 banks: MSB121 LSB0-9 ROM, MSB120 LSB0 user)
Block Setup ID0.ini            519 blocks, 228 distinct names, 3 editor drivers (see §4)
Block Setup ID5825.exi.ini     294 blocks (EXi variant)
Block Setup ID5825.old.ini     200 blocks (older EXi variant)
Block Setup ID5857.ini         383 defined blocks (header Count=384; KARMA chord-pad keys: Key C-1..G9, 88 B each)
Block Setup ID5873.ini         130 blocks (step sequencer: Common Parameters 16 B + Step 1..16, 18 B each)
Block Setup ID8262.ini         331 blocks (program level, editor 5035)
Block Setup ID8277.ini         297 blocks (program level)
Block Setup ID8302.ini         256 blocks (KARMA chord-pad keys)
Block Setup ID8311.ini         129 blocks (step sequencer)
Patch.ini                      editor definitions: [Patch Init 5052/5825/8277 HD-1/Exi], template lists
Patch.AL-1.ini / .CX-3 / .STR-1 / .MS-20 / .Poly6 / .MOD-7 / .SGX-1 / .EP-1 / .Common.ini
                               string lists (LFO waveforms, step durations, ...)
SysXMap.ID5035..8331.bin       214 files — the raw parameter -> SysEx address tables (see §3)
Patch.sqt                      844,928 B editor template (MQTMGLBL, BLCK panels)
Combi.sqt, Drums.sqt, Effect.sqt, Global.sqt, Karma.Common.sqt, Karma.Parts.sqt, Multi.sqt,
Patch.<engine>.sqt, SetList.sqt, Wavesequence.sqt   further editor templates
Patch.BkA..GG, Patch.IntA..    bank-level editor data (768 B each)
ALLBANKS.OASYS.PCG             32,694,610 B — the complete OASYS factory bank set (testing goldmine)
*.png                          panel bitmaps
```

## 3. `SysXMap.ID*.bin` — the raw parameter address tables (info beyond the parameter guide)

Korg never published the OASYS SysEx parameter addresses. The `SysXMap.ID<nnnn>.bin` files are
MIDI Quest's own address tables, i.e. exactly the "raw address offset tables" that are otherwise
unavailable.

**Format:** IFF container, `FORM` + size + type `SYSX`, chunks `DESC` (4 B) + one or more `DATA`
records. 214 files, IDs 5035..8331. The IDs correspond to the Block Setup IDs (the shipped
`Block Setup ID{5825,5857,5873,8262,8302,8311}.ini` all have a matching `SysXMap.ID…` file; the
remaining ~206 IDs are block setups whose ini is not shipped separately). Note:
`Block Setup ID8277.ini` is shipped but has **no** matching `SysXMap.ID8277.bin` — the
OASYS program editor (8277) has no SysXMap file, while both KRONOS editors (5052, 5825)
do (confirmed 2026-10-23, `docs/OASYS_SQZ_ANALYSIS.md` §5.4).

**DATA record layout** (small records, 68/82 B — one parameter; big records ~7–8 KB — bank-level):

```
+0      00                      flag/pad
+1..+4  base address, 4-byte BE  (e.g. 0x000022E9 = 8937; 0x00001094 = 4244; 0x00003268 = 12904)
+5..+8  second 4-byte BE address (usually = base, sometimes base-1, e.g. 0x22E8 vs 0x22E9)
+9..    fields + a table of 4-byte BE values (parameter indices / sub-addresses,
        e.g. 1, 3, 4, 5, 6, 7, 8, 9, <base-1>, 10)
+…      embedded SysEx frame, e.g.  F0 42 68 73 01 40 00 00 03 F7
        or                          F0 42 68 75 00 05 F7
        or                          F0 42 70 75 01 02 F7
        (F0 42 = Korg; 3rd byte 0x68 or 0x70; then function byte 0x73/0x75; then parameter
        address/value bytes; F7)
+end    zero padding
```

Most files carry **128 DATA records of 82 B** — one per program slot of a bank (128 programs).
The per-file frame bytes increment across consecutive IDs (…ID5036: `…01 40…`, ID5037: `…01 41…`,
ID5038: `…01 42…`), i.e. ** each `SysXMap.ID` file = one parameter**, and its 128 records give
that parameter's SysEx address for each of the 128 program slots.

`SysXMap.ID5837.bin` (934,670 B, 128 DATA chunks of ~7–8 KB) embeds full SysEx frames containing
ASCII names, e.g. `F0 42 68 75 00 05 00 "Acoustic Piano" …` — bank-level name dumps.

**Worked example** (`SysXMap.ID5036.bin`, first DATA record, 82 B):

```
00 00 00 22 E9 00 00 22 E9 00 00 00 00 00 00 00
00 00 00 00 00 0A 00 00 00 00 00 00 00 01 00 00
00 03 00 00 00 04 00 00 00 05 00 00 00 06 00 00
00 07 00 00 00 08 00 00 00 09 00 00 22 E8 00 00
00 0A F0 42 68 73 01 40 00 00 03 F7 00 00 00 00
00 00
```

base address 0x22E9, sub-address 0x22E8, parameter index table `1,3,4,5,6,7,8,9,10`, SysEx
frame `F0 42 68 73 01 40 00 00 03 F7`.

**Open point:** a full per-parameter (name → SysEx address) extraction across all 214 files is
mechanical but not yet done; it is the path to "all parameters finally mapped" (app display of
OASYS SysEx addresses, future MIDI remote control). The record layout above is enough to start.

## 4. `Block Setup ID0.ini` — block name → byte offset, per editor driver

519 `[Block N]` entries with `BlockName`, `Bytes in Block`, `Group Name`, `Driver ID`,
`First Byte Offset`, `First Byte Start Bit`, `Last Byte End Bit`, condition fields.
`Patch.ini` defines three program editors: **EditorID 5052, 5825, 8277** (all ControlID 4499),
each with an HD-1 and an EXi variant. The "Driver ID" in the block setups is the editor ID.

### 4.1 Editor 5052 = KRONOS PCG layout (cross-validation anchor)

Every 5052 offset matches `tables/Programme_HD-1.csv` exactly, e.g.:

| block | 5052 offset | size | KRONOS CSV |
|---|---|---|---|
| Track EQ | 2580 | 6 | 2580 Track EQ Trim ✓ |
| Tone Adjust | 2586 | 97 | 2586..2683 ✓ |
| Drum Track Common | 1292 | 11 | 1292..1302 ✓ |
| Drum Track | 2688 | 30 | 2688..2717 ✓ |
| Pitch EG | 2718 | 26 | 2718..2743 ✓ |
| Common LFO | 2744 | 15 | 2744..2758 ✓ |
| Common Keyboard Track 1/2 | 2760/2767 | 7 | 2760/2767 ✓ |
| Common Step Sequencer | 2748 | 105 | (KRONOS has no step sequencer — 5052-only block) |
| Insert Effect 1..12 | 24, 98, 172, … | 74 | zone A ✓ |
| Effect N (Master Eff Compat) | 24, 98, … | 66 | zone A ✓ |

So the 5052 editor describes the **KRONOS 4960-byte program slot**, and it independently confirms
the KRONOS table used for the whole project.

EXi1 @2857 (1052 B) is a **driver-5825** block, not a 5052 block — driver 5052 has no blocks
beyond 2774 (OSC1 zones); the offset/size are correct (corrected 2026-10-23,
`docs/OASYS_SQZ_ANALYSIS.md` §4).

### 4.2 Editor 8277 = OASYS PCG layout (matches the byte-verified derivation)

| block | 8277 offset | size | byte-verified OASYS layout |
|---|---|---|---|
| Track EQ | 2568 | 6 | 2568..2573 ✓ (= KRONOS 2580 − 12) |
| KARMA Common | 1292 | 510 | 1292..1801 ✓ (= KRONOS 1304 − 12) |
| KARMA Dynamic MIDI All | 1328 | 48 | inside KARMA Common ✓ |
| KARMA Perf RTP All | 1376 | 80 | inside KARMA Common ✓ |
| KARMA Chord Pad 1..8 | 1456, 1474, … (18 B stride) | 18 | inside KARMA Common ✓ |
| KARMA Note Map | 1674 | 128 | 1674..1801 ✓ (ends exactly at KARMA Common end) |
| KARMA Module | 1802 | 744 | 1802..2545 ✓ (ends exactly at the derived KARMA end 2545) |
| KARMA Scene 1..8 | 2130, 2139, … (9 B stride) | 9 | inside KARMA Module ✓ |
| EXi1 | 2815 | 1052 | = KRONOS 2857 − 42 ✓ (consistent with the derived −42 shift of that region) |
| Audio Input 1..6 | 1256..1286 | 6 | zone A (identical both sides) ✓ |

The KARMA map is a precise cross-validation of the derived OASYS KARMA block (1292..2545,
shift −12 vs KRONOS 1304..2557): the MQ KARMA Module block ends at 2545, exactly where the
byte analysis put the end of KARMA (the fixed tail `FF×8 90 32 54 76` at 2534..2545 =
KRONOS 2546..2557 "KARMA Module Scene8 Modified-State Fader data").

**Anomaly (documented, not followed):** four 8277 common-tail blocks do **not** match the OASYS
PCG file bytes:

| 8277 block | 8277 offset | size | byte-verified OASYS location |
|---|---|---|---|
| Common LFO | 2676 | 15 | 2702..2716 (MIDI-sync signature `01`/`15` at 2712/2713 = KRONOS 2754/2755) |
| Common Keyboard Track 1 | 2692 | 7 | 2718..2724 (key/ramp signature `3C 3C 3C CE CE 32 32`) |
| Common Keyboard Track 2 | 2699 | 7 | 2725..2731 (same signature) |
| Common Step Sequencer | 2706 | 105 | not a plain file region (would overlap the verified OSC1 zones @2732..2755) |
| Pitch EG | 2718 | 26 | 2676..2701 (26 B, the only remaining common section; KRONOS CSV: Pitch EG = 26 B @2718..2743) |

Byte-level test on PRODUCER.PCG banks I-A..I-E (640 HD-1 programs) vs KRONOS PRELOAD.PCG
(1917 HD-1 programs), per-byte dominant-value agreement over the 56-byte region 2676..2731:

- byte-verified layout (O 2676..2731 ↔ K 2718..2773, uniform shift −42): **44/56 agree**
- MQ 8277 order (LFO/KbdTrk at shift −68, Pitch EG at shift 0): **9/43 agree**

The MQ 8277 offsets for those four blocks therefore address something else (a SysEx-dump layout
or a config quirk); **the converter follows the byte-verified PCG layout**. The OSC1 zone
records at OASYS 2732..2755 are verified independently (4 × 6-B records, `7F`-dominant Level at
record+4, matching KRONOS zone Level @2794 etc.).

### 4.3 EXi section map (editor 8277 = OASYS, 5825 = KRONOS EXi; OASYS = KRONOS − 42)

`EXi1` = 1052 B at OASYS 2815..3866 / KRONOS 2857..3908, overlaid on the HD-1 OSC param region
(EXi programs have oscillator mode = EXi, so the HD-1 OSC params are unused). Sub-blocks
(OASYS offsets; KRONOS = +42):

| sub-block | OASYS off | size | engines |
|---|---|---|---|
| EXi1 Mod Mixer 1 / 2 | 2826 / 2846 | 20 | common |
| EXi1 {MOD-7, MS-20, STR-1} Mod Mixer 3 / 4 | 2866 / 2886 | 20 | MOD-7, MS-20, STR-1 |
| EXi1 MOD-7 Mod Mixer 5..8 | 2906/2911/2916/2921 | 5 | MOD-7 |
| EXi1 PolySixEX Mod Mixer 3 / 4 | 2909 / 2929 | 20 | Poly6 |
| EXi1 AL-1 LFO 1..4 | 2867/2884/2901/2918 | 17 | AL-1 |
| EXi1 MOD-7 LFO 1..4 | 2926/2943/2960/2977 | 17 | MOD-7 |
| EXi1 STR-1 LFO 1..4 | 2914/2931/2948/2965 | 17 | STR-1 |
| EXi1 MS-20 LFO 1..4 | 2924/2941/2958/2975 | 17 | MS-20 |
| EXi1 PolySixEX LFO 1..2 | 2966/2983 | 17 | Poly6 |
| EXi1 PolySixEX MG | 2949 | 17 | Poly6 |
| EXi1 {AL-1,STR-1,MS-20,Poly6} Amplifier EG / EGx Filter | 2935, 2971, 2982, 2992, 3007, 3018, 3024, 3028, 3043, 3054, 3060, 3064, 3079, 3090, 3100, 3126 | 36 | per engine |
| EXi1 MOD-7 EG 1..9 | 2994, 3017, 3040, 3063, 3086, 3109, 3132, 3155, 3178 | 23 | MOD-7 |
| EXi1 AL-1 Step Sequencer | 3115 | 81 | AL-1 |
| EXi1 MOD-7 Step Sequencer | 3243 | 81 | MOD-7 |
| EXi1 AL-1 Common Pitch | 3196 | 12 | AL-1 |
| EXi1 MOD-7 Amplifier EG | 3201 | 22 | MOD-7 |
| EXi1 AL-1 OSC1/OSC2 Pitch | 3208 / 3223 | 15 | AL-1 |
| EXi1 AL-1 Filter A / Filter B | 3291 / 3331 | 40 | AL-1 |
| EXi1 AL-1 Drive | 3371 | 6 | AL-1 |
| EXi1 AL-1 Amplifier | 3377 | 17 | AL-1 |
| EXi1 MOD-7 OSC 1 | 3428 | 45 | MOD-7 |
| EXi2 … (second EXi instance) | +1240 (e.g. AL-1 OSC1 Pitch 4260, MOD-7 OSC 1 4480) | … | EXi2 |

(Unexplained: PRODUCER.PCG stores MOD-7 programs in 4386-B slots while `KNMOD7.PCG` uses
6174-B MOD-7 slots — see §14 open points. Since v1.6.3 the EXi engine payload converts
through the partial byte-verified map of §9; before that the v1.6.1/v1.6.2 converter zeroed
it.)

---

## 5. OASYS PCG container (PRODUCER.PCG, 7,568,270 B)

Same chunk family as KRONOS/NAUTILUS. Bank chunks (`PBK1` programs / `MBK1` multisamples) are
**nested inside `PRG1`**. Bank chunk header (24 B): `id(4) size(4 BE) bankId(4) count(4)
slotSize(4) subId(4)`; program slots begin at **chunk + 24**; chunks are laid out at a fixed
stride of `24 + count × slotSize`; the size field reads `stride − 12` (4 B trailing pad).

| chunk | offset | contents |
|---|---|---|
| DIV1 | 0x1C | division header |
| INI1 | 0x54 | init |
| PRG1 | 0x3D8 | **5 × PBK1** @0x3E4 + k·561,432 — banks I-A..I-E, 128 × **4386 B**, HD-1 (stride 561,432 = 24 + 128×4386) |
| | | **2 × MBK1** @0x2AD95C (I-F), @0x336A74 (U-F), 128 × 4386 B, all osc mode 3 (MOD-7) |
| CMB1 | 0x3BFB8C | 3 × CBK1, 128 × **7766 B** combis |
| DKT1 | 0x697CE0 | 1 × DBK1, 40 × **11288 B** drum kits |
| WSQ1 | 0x7060C4 | 1 × WBK1, 150 × **1192 B** wave sequences |
| GLB1 | 0x731B58 | global, 24,618 B |

Slot sizes: program **4386** (OASYS) ↔ **4960** (KRONOS); combi 7766 ↔ 7810; kit 11288 ↔ 38424;
wave sequence 1192 ↔ 2216. In v1.6.3 the HD-1 program slot (§6), the EXi engine payload
(§9, partial) and the combi slot (§10) are mapped; drum kits and wave sequences have no
verified map (sound-defaulted, names preserved).

KRONOS PRELOAD.PCG: 17 bank chunks, 128 × 4960 B; 1917 HD-1 programs pass the filter
(byte @3012 ∈ {FE,FF,00,01} AND (byte @2568 & 0x1F) ≤ 17).

## 6. The byte-verified OASYS HD-1 program slot (4386 B) ↔ KRONOS (4960 B)

Full section-level map in `tables/Oasys_HD1_blocks.csv`; per-parameter offsets in
`tables/Oasys_HD1_param_offsets.csv`. Summary (OASYS ↔ KRONOS):

```
OASYS 0..1291    = KRONOS 0..1291     zone A: identity (name, IFX/MFX/TFX, effect LFOs, ...)
KRONOS 1292..1303 (12 B)  Drum Track Common          -> no OASYS equivalent (O->K: factory default)
OASYS 1292..2545 = KRONOS 1304..2557  KARMA Common + KARMA Module, copy shift -12
OASYS 2546..2556 = KRONOS 2558..2568  Common mode byte + Common (incl. Category byte), copy shift -12
OASYS 2557..2675 = KRONOS 2569..2687  Common (Scale, Assignable Controllers, Track EQ, Tone Adjust,
                                      OSC1/2 Trigger Key Zone), copy shift -12
KRONOS 2688..2717 (30 B)  Drum Track                 -> no OASYS equivalent (O->K: factory default)
OASYS 2676..2731 = KRONOS 2718..2773  Pitch EG + Common LFO + Common Keyboard Track 1-2, copy shift -42
OASYS 2732..2755 (24 B)  = KRONOS 2774..2949 (176 B)  OSC1 zones: 4×6 B  <->  8×22 B  (structural)
OASYS 2756..2767 (12 B)  = KRONOS 2950..2975 (26 B)    OSC1 trigger tail (partial)
OASYS 2768..3005 = KRONOS 2976..3213  OSC1 params part 1 (252 B), copy shift -208
KRONOS 3214..3219 (6 B)   Mod.Mixer1 Gate params      -> no OASYS equivalent (O->K: zero)
OASYS 3006..3019 = KRONOS 3220..3233  OSC1 Mod.Mixer2 (14 B), copy shift -214
KRONOS 3234..3239 (6 B)   Mod.Mixer2 Gate params      -> no OASYS equivalent (O->K: zero)
OASYS 3020..3043 = KRONOS 3240..3415  OSC2 zones (4×6 B <-> 8×22 B, structural)
OASYS 3044..3055 = KRONOS 3416..3441  OSC2 trigger tail (partial)
OASYS 3056..3293 = KRONOS 3442..3679  OSC2 params part 1 (252 B), copy shift -386
KRONOS 3680..3685 (6 B)   OSC2 Mod.Mixer1 Gate params -> no OASYS equivalent (O->K: zero)
OASYS 3294..3307 = KRONOS 3686..3699  OSC2 Mod.Mixer2 (14 B), copy shift -392
KRONOS 3700..3705 (6 B)   OSC2 Mod.Mixer2 Gate params -> no OASYS equivalent (O->K: zero)
OASYS 3308..4385 (1078 B) = KRONOS 3706..4959 (1254 B)  tail padding (O: all-zero for HD-1;
                                      K: beyond-useful padding, 91–99 % zero per byte, no fixed
                                      non-zero bytes) -> K->O drops; O->K writes zero
```

Size check: 1292 + 1254 + 11 + 119 + 56 + 24 + 12 + 238 + 14 + 24 + 12 + 238 + 14 + 1078 = **4386** ✓
(plus the KRONOS-only 12 + 30 + 6 + 6 + 6 + 6 = 66 B and the structural expansions, which bring the
KRONOS side to 4960 ✓).

Key byte anchors: OASYS osc mode = bits 0-2 of O 2546 (0=Single, 1=Double, 2=Drums, 3=EXi/MOD-7,
4=Unused, 5=Double Drums), Favorite = bit 5, Hold = bit 6; category = bits 0-4 of O 2556,
subcategory = bits 5-7. KRONOS: osc mode bits 0-2 of K 2558, category bits 0-4 of K 2568
(`KronosProgram.cs:142-148`). Factory bank categories: I-A=0, I-B=2, I-C=6, I-D=8/9, I-E=12;
I-F cat byte = 0x20, U-F = 0x0B.

## 7. Per-oscillator block = 288 B (OASYS) / 466 B (KRONOS)

OSC2 = OSC1 + 288 (OASYS) / + 466 (KRONOS), exactly: zones 2732→3020, trigger tail 2756→3044,
params 2768→3056 (OASYS); 2774→3240, 2950→3416, 2976→3442 (KRONOS).
Sanity: 2732 + 288 + 288 + 1078 = 4386 ✓.

OSC1 OASYS params (252 B @2768; KRONOS = +208 except Mixer2 = +214):

| section | OASYS | size | KRONOS |
|---|---|---|---|
| LFO1 | 2768 | 18 | 2976 |
| LFO2 | 2786 | 18 | 2994 |
| Pitch (Octave @2804) | 2804 | 24 | 3012 |
| Filter common (Routing @2828) | 2828 | 6 | 3036 |
| Filter A | 2834 | 26 | 3042 |
| Filter B | 2860 | 26 | 3068 |
| Filter EG | 2886 | 34 | 3094 |
| Filter Keyboard Track | 2920 | 7 | 3128 |
| Drive | 2927 | 6 | 3135 |
| Amplifier | 2933 | 10 | 3141 |
| Amplifier EG | 2943 | 33 | 3151 |
| (undocumented) | 2976 | 1 | 3184 |
| Amplifier Keyboard Track | 2977 | 7 | 3185 |
| Output | 2984 | 8 | 3192 |
| Mod.Mixer1 (14 B) | 2992 | 14 | 3200 (first 14 of a 20-B record) |
| Mod.Mixer2 (14 B) | 3006 | 14 | 3220 (first 14 of a 20-B record) |

OSC2 = OSC1 + 288 / + 466 (LFO1 3056/3442, …, Mixer1 3280/3666, Mixer2 3294/3686).
Per-parameter rows (all 2541) in `tables/Oasys_HD1_param_offsets.csv`.

**Mixer mapping (14 B ↔ 20 B).** The OASYS AMS mixer is 14 B (Parameter Guide 1.3, P6:
"Each Oscillator has two AMS Mixers"; Mixer Type [A+B, Amt AxB, Offset, Smoothing, Shape,
Quantize, Gate]): Type, SrcA, AmtA, SrcB, AmtB, NumSteps, AmtA2, undoc, Offset(2), Attack,
Decay, Shape, ShapeType — exactly the **first 14 B** of the KRONOS Mod.Mixer 20-B record
(KRONOS CSV: 3200 Type … 3213 ShapeType, then 3214..3219 Gate params). All 14 bytes
dominant-agree for both mixers. The 6 KRONOS Gate bytes per mixer have no OASYS equivalent.

## 8. Zone record mapping (OASYS 6 B ↔ KRONOS 22 B)

OASYS zones: 4 records of 6 B @2732+z·6 (OSC1), 3020+z·6 (OSC2). KRONOS: 8 records of 22 B
@2774+z·22 (OSC1), 3240+z·22 (OSC2). OASYS zones 1-4 ↔ KRONOS zones 1-4; KRONOS zones 5-8 are
dropped (active in only 3-22 % of factory programs).

| OASYS zone byte | meaning | KRONOS zone byte | meaning |
|---|---|---|---|
| +0 bits 0-1 | MS Type (0=Off, 1=MultiSample, 2=WaveSequence — same encoding both sides) | +0 bits 0-1 | MS Type |
| +1 | multisample bank (values {0,1,4,5} in factory HD-1) | +16 | MS Bank UUID sub-byte (last byte of the 16-B UUID) |
| +2/+3 | MS Number, 16-bit (bank 0 up to 2223; banks 1/4/5 small) | +18/+19 | MS Number, 16-bit |
| +4 | MS Level (7F-dominant) | +20 | MS Level (7F-dominant) |
| +5 | Start Offset 0..8 (bits 0-3) + Reverse (bit 7) | +21 | Start Offset bits 0-3 + Reverse bit 7 |

UUID handling (makes **O→K→O byte-identical on zone records**):

- O→K: write the KRONOS UUID = KORG-MS default `4B 4F 52 47 00 00 00 00 00 00 00 00 4D 53 00 <bank>`
  (`KORG` + 8×00 + `MS` + 00 + bank) for **all** zone types; record +17 (undocumented flag,
  factory {0:59 %, 1:40 %}) ← 0.
- K→O: O bank ← K record+16 if the K UUID is the KORG-MS family (`u[:4]==KORG` and
  `u[12:14]==MS`), else 0.

KRONOS zone record layout (CSV): +0 Type bits 0-1; +1..+16 MS Bank UUID (16 B); +17 undocumented;
+18/+19 MS Number; +20 MS Level; +21 Start Offset bits 0-3 + Reverse bit 7.

**Multisample identity limitation (documented prominently):** OASYS addressing = bank byte +
16-bit number; KRONOS = 16-byte UUID + 16-bit number. The OASYS HD-1 banks {0,1,4,5} overlap the
KRONOS KORG-MS UUID sub-byte values {0,1,4,5,…}, which confirms the bank↔sub-bank mapping is
structurally sound, but **no multisample correspondence table exists** in the available materials
(`tables/FACTORY_NAMES.csv` covers ABK1/CBK1/DBK1/MBK1/PBK1/WBK1 only; the OASYS VNL is the
program/combi/kit Voice Name List, not multisamples). Conversion therefore preserves
(bank, number) structurally; the actual multisample behind a converted zone may differ.
WaveSequence (Type 2) and Off zones always have bank 0 on the OASYS side; KRONOS WaveSequence
zones carry 0601-family UUIDs with number 0x0600 — copied best-effort.

## 9. EXi engine payload partial map (added in v1.6.3)

EXi (MOD-7 family) program slots carry the engine payload where the HD-1 slots carry the
OSC blocks (osc mode = 3; the HD-1 OSC parameters are unused there). The payload region is
OASYS 2676..4385 / KRONOS 2718..4959 — it starts right after the common tail and runs to the
end of the slot. Byte analysis of the name-matched factory slots — KRONOS OS 3.2
`PRELOAD.PCG` MBK1 banks ↔ the `.sqz` `ALLBANKS.OASYS.PCG` MBK1 banks (6174-B v2 slots, 580
matched pairs) and ↔ `PRODUCER.PCG` MBK1 banks (4386-B v0 slots, 201 matched pairs) —
verified **three verbatim copy regions**; the remaining EXi engine regions have no verified
map and stay zero (and are reported in the conversion report's defaulted sections).
Companion table: `tables/Oasys_EXi_blocks.csv`.

| region | OASYS | KRONOS | size | shift (K = O + n) | verification |
|---|---|---|---|---|---|
| E1 — EXi common tail | 2676..2809 | 2718..2851 | 134 B | 42 | 0 diff bytes on 580 v2 + 201 v0 pairs |
| E2 — EXi 1 engine head | 2848..3175 | 2908..3235 | 328 B | 60 | 0 diff bytes on the 201 v0 pairs; 4 diff bytes total on the 580 v2 pairs |
| E3 — EXi 2 engine head | 3636..3963 | 3960..4287 | 328 B | 324 | 0 diff bytes on 580 v2 + 201 v0 pairs |

The MQ block setups cross-validate the region boundaries: the KRONOS engine blocks sit at
2908 (EXi 1) and 3960 (EXi 2) per `tables/Moteur_*.csv`, and the editor-8277 EXi1 sub-blocks
(§4.3) tile OASYS 2815..3866 — consistent with E2 starting at OASYS 2848 inside that span.

**Unmapped gaps (stay zero, reported):**

| side | gap | size |
|---|---|---|
| KRONOS | 2852..2907 (between E1 and E2) | 56 B |
| KRONOS | 3236..3959 (between E2 and E3) | 724 B |
| KRONOS | 4288..4959 (after E3, to end of slot) | 672 B |
| OASYS | 2810..2847 (between E1 and E2) | 38 B |
| OASYS | 3176..3635 (between E2 and E3) | 460 B |
| OASYS | 3964..4385 (after E3, to end of the mapped region) | 422 B |

The OASYS v0/v2 layouts agree in the copied regions (the v2 slot is the v0 layout plus a
dropped engine extension — the v1/v2 extension bytes are reported per bank on O→K, §14).

**Round-trip preservation** (measured with the converter itself, v1.6.3):

- O→K→O, `.sqz` ALLBANKS (640 EXi slots): E1/E2/E3 **0 differing bytes**; 154,833 non-zero
  payload bytes preserved.
- O→K→O, PRODUCER (256 EXi slots): 0 differing bytes; 66,547 preserved.
- K→O→K, KRONOS OS 3.2 factory (896 EXi slots): 0 differing bytes on the copied regions;
  226,567 preserved; the unmapped regions come back zero (as expected — they were dropped
  on K→O).
- Total: **447,947 EXi payload bytes** survive a round trip. The v1.6.1/v1.6.2 converter
  zeroed the whole payload (all of them lost).

The map constants live in `OasysKronosHd1ProgramMap` (`KronosExiCommonTailStart` 2718 /
`KronosExiCommonTailSize` 134 / `OasysExiCommonTailStart` 2676, `KronosExi1HeadStart` 2908 /
`KronosExi1HeadSize` 328 / `OasysExi1HeadStart` 2848, `KronosExi2HeadStart` 3960 /
`KronosExi2HeadSize` 328 / `OasysExi2HeadStart` 3636).

## 10. The byte-verified OASYS combi slot (7766 B) ↔ KRONOS (7810 B) (added in v1.6.3)

Companion table: `tables/Oasys_Combi_blocks.csv`. Summary (OASYS ↔ KRONOS):

```
OASYS 0..1291    = KRONOS 0..1291     zone A: identity (name, category, timbre-independent
                                      common data)
KRONOS 1292..1303 (12 B)  Drum Track Common          -> no OASYS equivalent (dropped K->O;
                                      O->K: factory default, see below)
OASYS 1292..4777 = KRONOS 1304..4789  combi KARMA Common + Modules A..D (3486 B), copy shift -12
OASYS 4778..4789 = KRONOS 4790..4801  Common/assignable tail (category, favorite, auto load,
                                      scale, assignable switches/knobs; 12 B), copy shift -12
OASYS 4790..7765 = KRONOS 4802..7809  16 timbres, 186 B <-> 188 B (field offsets shared;
                                      two KRONOS tail bytes dropped per timbre)
```

Size check: 1292 + 3486 + 12 + 2976 = **7766** ✓ (plus the KRONOS-only 12 B and the 16 × 2 B
timbre tail bytes, which bring the KRONOS side to 7810 ✓).

The combi KARMA map was re-derived for v1.6.3 (the v1.6.1/v1.6.2 converter zeroed the whole
1304..4789 region): the MQ editor-8277 KARMA blocks (§4.2: KARMA Common 1292, 510 B;
KARMA Module 1802, 744 B) anchor the OASYS side, the KRONOS CSV anchors the KRONOS side
(KARMA Common + Modules at 1304..2557 program-level, extended for combis to 4789), and the
byte-verified shift is the same −12 as the program KARMA map.

- **KRONOS-only Drum Track Common default (O→K)**, K 1292..1303:
  `00 00 00 0B 00 7F 01 7F 00 09 10 00`
  (`CombiDrumTrackCommonDefault` — per-byte factory dominants of the KRONOS combi banks;
  the program-level Drum Track Common default `... 00 10 10 00` differs in the channel
  bytes, this one is the combi variant).
- **A timbre that references a KRONOS-only program bank** (U-AA..U-GG, pcgId 24..30) is set
  to Off on K→O and reported per timbre (the OASYS cannot address those banks).

**Verification:** K→O→K on the KRONOS OS 3.2 factory file (768 combi slots): zone A 0
mismatches, the KARMA region 0 mismatches, the Drum Track Common defaulted on 768/768 slots
(the expected round-trip defaulting). O→K→O on PRODUCER (384 combis): **byte-identical**.

**OASYS v1 combi slots (11288 B):** the `.sqz` ALLBANKS.OASYS.PCG carries v1 combi banks
whose slots are 11288 B — the v0 layout (7766 B) plus a 3522-B extension. O→K accepts both
slot sizes (`OasysCombiSlotSizes = {7766, 11288}`) and drops the extension, reported per
bank (`v1 combi extension bytes (3522 extra vs the v0 layout) dropped (no verified KRONOS
map)`) — the KRONOS combi slot (7810 B) has no room for them.

## 11. Trigger tail mapping (12 B ↔ 26 B)

| OASYS (OSC1) | KRONOS (OSC1) | content |
|---|---|---|
| 2756..2764 (9 B) | 2950..2958 (9 B) | crossfade pairs 1-3: Zone1-2 / 2-3 / 3-4 Bottom Velocity, Crossfade Range, Curve (left-aligned) |
| 2765 | 2971 | Damper Control / Delay Start |
| 2766 | 2972 | Velocity Zone Bottom (01-dominant) |
| 2767 | 2973 | Velocity Zone Top (7F-dominant) |
| — | 2959..2970 | crossfade pairs 4-7 (dropped) |
| — | 2974 | MS/WS/D.Kit Display (dropped) |
| — | 2975 | undocumented (dropped) |

OSC2 = OSC1 + 288 / + 466 (O 3044..3055 ↔ K 3416..3441; O 3053→K 3437, O 3054→K 3438,
O 3055→K 3439; K 3425..3436 + 3440..3441 dropped).

## 12. KRONOS-only sections injected on O→K (factory defaults)

- **Drum Track Common** K 1292..1303 (12 B):
  `00 00 00 0B 00 7F 01 7F 00 10 10 00`
  (Pattern Number 00 00; Pattern Bank 0B; Trigger 00; Key Zone 00/7F; Vel Zone 01/7F; Shift 00;
  Out MIDI Ch 10; In MIDI Ch 10; pad 00) — per-byte factory dominants of PRELOAD.PCG.
- **Drum Track** K 2688..2717 (30 B):
  `1A 19 7F 00 00 00 01 63 00 14 00 00 00 0C 0C 00 00 00 00 00 00 00 00 00 00 0C 00 00 00 00`
  (Program Number 1A; Program Bank 19; Volume 7F; Detune 00 00; Auto Load Program EQ 01;
  Track EQ Bypass 63; Mid Freq 14; Low Gain 00; Mid Gain 00; High Gain 00; IFX Patch 0-11;
  Bus Select 0C; …) — per-byte factory dominants.
- **Gate params** K 3214..3219, 3234..3239, 3680..3685, 3700..3705: left zero (Init fill).
- **Tail** K 3706..4959: zero.

## 13. Derivation method (so the results can be re-checked)

1. **Container parsing** — locate `PRG1`, walk nested bank chunks, slice program slots
   (OASYS 4386 B / KRONOS 4960 B). Filter KRONOS HD-1 programs (byte @3012 ∈ {FE,FF,00,01} and
   category byte @2568 & 0x1F ≤ 17) → 1917 KRONOS vs 640 OASYS (PRODUCER banks I-A..I-E;
   banks I-F/U-F are MOD-7 and excluded from HD-1 profiling).
2. **Dominant-value distribution matching** — for each candidate (OASYS range, KRONOS range,
   shift), count per-byte dominant-value agreements across the two program sets. Reliable
   metric; bucket correlation is noisy at these sizes. Results: KARMA shift −12 wins 150/156
   (vs +0: 99/156, −3: 101/156); OSC1 params −208: 57/66; OSC2 params −386: 60/66; common tail
   −42: 44/56 (vs the MQ 8277 order: 9/43 — see §4.2).
3. **KRONOS CSV anchors** — `tables/Programme_HD-1.csv` fixes the KRONOS section boundaries
   (e.g. KARMA 1304..2557, Drum Track 2688..2717, OSC1 zones 2774..2949, Mixer1 3200..3219,
   "3706 octets utiles, 4960 dans le PCG").
4. **MQ anchors** — `Block Setup ID0.ini` editor 5052 (= KRONOS) and 8277 (= OASYS) offsets
   cross-validate KARMA (−12), Track EQ (−12), EXi1 (−42) and the KARMA section names/sizes;
   the Patch.sqt BLCK wire tiling gives the SysEx-dump layout (OSC1: Multisamples @2774(73),
   LFO1 @2848(18), LFO2 @2866(18), Pitch @2884(24), FilterModule @2908(99), Drive @3007(6),
   AmpModule @3013(51), Output @3064(8), Mixer1 @3072(20), Mixer2 @3092(20); wire = KRONOS
   file − 128 = OASYS file + 80 for the param blocks).
5. **Involution design** — the mapping is built so that O→K→O is byte-identical on PRODUCER
   HD-1 banks (plain copies both ways; zone records round-trip via the UUID rule; KRONOS-only
   sections are dropped on K→O). This is proven by the MSTest round-trip tests in CI.
6. **EXi partial map (v1.6.3, §9)** — name-matched factory EXi slots (slot names as the join
   key): 580 pairs KRONOS OS 3.2 PRELOAD MBK1 ↔ `.sqz` ALLBANKS MBK1 (6174-B v2 slots) +
   201 pairs ↔ PRODUCER MBK1 (4386-B v0 slots). Per-byte exact-match comparison over the
   payload region 2676..4385 (O) / 2718..4959 (K) found three windows with zero differing
   bytes (E1/E2/E3); every other window differs somewhere, so those regions have no verified
   map. Round trips then re-verified the map with the converter itself (0 differing bytes
   on all three regions, 447,947 payload bytes preserved).
7. **Combi map (v1.6.3, §10)** — the KRONOS combi KARMA block was re-derived the same way
   (MQ editor-8277 KARMA blocks anchored on the OASYS side, KRONOS CSV on the KRONOS side,
   byte-verified shift −12), then proven by round trips: K→O→K on the KRONOS OS 3.2 factory
   (768 combis, 0 mismatches on zone A and KARMA) and O→K→O on PRODUCER (384 combis,
   byte-identical).

## 14. Open points

- **Per-parameter SysEx address extraction** from the 214 `SysXMap.ID*.bin` files (§3) — the
  path to "all parameters finally mapped"; record layout documented, extraction not yet done.
- **MQ 8277 common-tail anomaly** (§4.2) — four blocks whose offsets do not match the PCG file
  bytes; converter follows the byte-verified layout. Worth re-checking against a physical OASYS
  SysEx dump if one becomes available.
- **Common Step Sequencer** (MQ: 105 B @2706) — no plain file region; possibly conditional /
  SysEx-dump only. The OASYS step-sequencer data location in the PCG file is unresolved.
- **EXi/MOD-7 slot discrepancy** — PRODUCER MOD-7 programs sit in 4386-B slots; `KNMOD7.PCG`
  uses 6174-B MOD-7 slots. The v0/v2 layouts agree in the three copied regions of §9 (the
  v2 slot is the v0 layout plus an engine extension), but the discrepancy itself is
  unexplained; the unmapped EXi gaps of §9 remain zero on both directions.
- **Unmapped EXi engine gaps** (§9) — KRONOS 2852..2907 / 3236..3959 / 4288..4959 and the
  OASYS counterparts stay zero and are reported; mapping them needs a larger name-matched
  EXi sample (the factory pairs only verify the three copied regions).
- **Multisample correspondence table** — none available; zone conversion preserves (bank,
  number) only (§8).
- **OASYS set lists** — dropped and reported in both directions. None of the 8 available
  OASYS files (7 factory + the `.sqz` ALLBANKS) carries SLS1/SBK1 chunks, and the MIDI Quest
  `sqz` documents the set list entry *semantics* (program/combi/song references + delay)
  but not the on-disk layout, so there is nothing to map against.
- **Drum kits and wave sequences** — no verified map (KRONOS 38424-byte drum kit fiche vs
  OASYS 11288-byte; KRONOS 2216-byte wave sequence fiche vs OASYS 1192-byte); both
  directions sound-default the slots (Init-filled, names preserved) and report them.
- **KRONOS zones 5-8, crossfade pairs 4-7, Gate params, MS/WS/D.Kit Display, Drum Track (Common),
  tail padding** — legitimately dropped on K→O (no OASYS equivalent / beyond-useful).

## 15. Files produced by this analysis

- `tables/Oasys_HD1_blocks.csv` — section-level block map (20 rows; converter source of truth).
- `tables/Oasys_HD1_param_offsets.csv` — 2541 per-parameter rows generated from
  `tables/Programme_HD-1.csv` + the region map (regenerate with the session script
  `gen_param_csv.py` if the region map changes).
- `tables/Oasys_EXi_blocks.csv` — the EXi engine payload partial map (§9; added in v1.6.3).
- `tables/Oasys_Combi_blocks.csv` — the combi slot block map (§10; added in v1.6.3).
- This document.

The `.sqz` working copy and all extraction scripts stay in the session scratchpad
(not committed; see §1).
