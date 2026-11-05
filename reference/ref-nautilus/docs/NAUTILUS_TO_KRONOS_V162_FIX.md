# NAUTILUS → KRONOS conversion: wave sequence + drum track fix (v1.6.2)

_October 23, 2026. Fixes the beta-tester report on the NAUTILUS → KRONOS
conversion: "the Wave Sequences were not converted to Kronos Wave Sequences"
and "the Drum Tracks (DT) were not converted". Both root causes were
byte-verified against the tester's source file and the buggy conversion
(both kept locally in `errors/`, gitignored), then fixed in
`NautilusToKronosConverter` (C#), mirrored in the Python port
(`docs/python-script/pcglib_convert.py`), covered by new unit tests, and
verified on the NAUTILUS factory PRELOAD.PCG and the MOATAZ.PCG user file._

## TL;DR

Two independent root causes, both in the NAUTILUS → KRONOS converter
(`src/KorgKronosTools/Model/Kronos/Conversion/NautilusToKronosConverter.cs`):

1. **Wave sequences.** The converter planned the wave sequence banks by
   bank-id identity over the KRONOS space (INT + U-A..U-GG,
   bids 0, 0x20000..0x2000D). The NAUTILUS has 19 user wave sequence banks
   (B..T, bids 0x20000..0x20012); the tester's file carries its only wave
   sequence bank as **T (bid 0x20012)** — beyond the KRONOS space, so it was
   **dropped**, and the HD-1 program zone wave sequence references were left
   **stale** (pointing beyond the KRONOS index space at Init placeholders).
   Fix: the NAUTILUS banks beyond 0x2000D take the KRONOS user banks that no
   identity bank claimed (in bank-id order; here T → U-A), banks without a
   free target are dropped and reported, and the HD-1 program zone references
   are **remapped** through the assignment (INT references unchanged).
2. **Drum tracks.** On the KRONOS, bytes 1292..1303 of the program/combi
   fiche are the **Drum Track Common**; on the NAUTILUS the same bytes are
   the **RT Controller** — the NAUTILUS drum track lives in zone B (scene
   common 1348..1378, per-scene drum fields in the scene records at 2440).
   The converter copied zone A (0..1303) identically, writing RT Controller
   bytes into the KRONOS Drum Track Common: the drum track came out **off**
   with inverted trigger zones and a garbage pattern number. Fix: the Drum
   Track Common is **rebuilt** from the NAUTILUS zone B scene data
   (full mapping table below).

## 1. The bug report

The beta tester converted `N_EXs342 Kelfar Diamond Analog Synth.PCG`
(NAUTILUS, banks: PBK1 bid 0x2000D 128×4954, CBK1 bid 0x20006 128×5640,
WBK1 bid 0x20012 32×2216) to KRONOS and reported that the wave sequences and
the drum tracks did not carry over, while programs and combinations
converted properly. Both files (source + buggy `-KRONOS.PCG` output) were
provided and are the ground truth for the byte-level analysis below.

## 2. Root cause 1 — wave sequence banks beyond the KRONOS space

### 2.1 The index spaces

A wave sequence reference in a program zone record is a **global index**
into INT (150 slots) + the user banks (32 slots each):

| | INT | user banks | max index |
|---|---|---|---|
| NAUTILUS | 150 | 19 × 32 (banks B..T, bids 0x20000..0x20012) | 150 + 19×32 = **758** |
| KRONOS | 150 | 14 × 32 (U-A..U-GG, bids 0x20000..0x2000D) | 150 + 14×32 = **598** |

### 2.2 The zone records

Each HD-1 program zone (2 oscillators × 8 zones) carries a 22-byte multisample
record:

- **NAUTILUS v6**: at `2768 + osc*466 + zone*22`; byte +0 = MS type
  (0 = Off, 1 = Sample, 2 = Wave Sequence), LE16 global wave sequence index
  at +18..19.
- **KRONOS v5**: same record at `2774 + osc*466 + zone*22` (the uniform +6
  tail shift; tables/Programme_HD-1.csv: "Zone1 MS Type" at 2774,
  "Zone1 MS Number" at 2792..2793 = record +18..19).

The converter copies the v6 tail (2552..) to the v5 tail (2558..), so a
reference survives the copy byte-identically — which is exactly why stale
references were the visible symptom.

### 2.3 What the buggy conversion did (byte-verified)

The plan was `BuildUserBidOrder(14)` = bids `0, 0x20000..0x2000D` with
identity sources. The tester's WBK1 bid 0x20012 (bank T) has no KRONOS target
and was dropped:

- buggy output WBK1 banks: `0x0, 0x20000..0x2000D` — **no bank T**; the 15
  emitted user banks are Init-filled placeholders.
- buggy output, program slot 3 ('OB Detuned Attack') osc 0 zone 0: MS type 2
  (Wave Sequence), **index 727 left stale** — 727 ≥ 598, i.e. beyond the KRONOS
  index space; decoded as U-BB slot 25, an Init placeholder. The wave sequence
  content is gone and the reference dangles.

## 3. Root cause 2 — the Drum Track Common is not at 1292..1303 on NAUTILUS

The KRONOS Drum Track Common (bytes 1292..1303, identical in
tables/Programme_HD-1.csv, Programme_EXi_commun.csv and Combinaison.csv):

| KRONOS bytes | Field | Range |
|---|---|---|
| 1292..1293 | Drum Track Pattern Number (LE16) | 0..999 |
| 1294 | Pattern Bank (bits 3~0; 0 = Preset, 1 = User) | |
| 1295 | bit0 Trigger Button Mode (Start Immediately~Wait KBD Trig), bits 1~2 Trigger Latch Mode (Off~Use KARMA Latch), bit3 Trigger Sync Mode, bit4 Drum Track On | |
| 1296 / 1297 | Trigger Key Zone Bottom / Top | 00~7F |
| 1298 / 1299 | Trigger Velocity Zone Bottom / Top | 01~7F |
| 1300 | Shift | -24..+24 |
| 1301 | Output MIDI Channel | |
| 1302 | Input MIDI Channel | |
| 1303 | unused | |

On the NAUTILUS the **same bytes 1292..1303 are the RT Controller**
(docs/nautilus/NAUTILUS_MIDIimp/SysExDumps/Prog_HD-1.txt: Mode at 1292,
Knob 1 Target/RT Control/Mixer Control at 1296/1298/1299, mixer channel
enables at 1300..1301, Knob 2 Target at 1302; Prog_EXi_Common.txt and
CombiAndSongTimbreSet.txt agree). The NAUTILUS drum track lives in **zone B**
(docs/NAUTILUS_ZONE_B_ANALYSIS.md):

- **Scene common** (programs and combis): 1348 = Scene Select (bits 2~0) +
  Cue Mode (bits 5~4); 1349 = switches (bit0 Latch, bit1 Arp, bit2 **Drum**);
  1360 = Drum Output Channel; 1373 = Drum Input Channel; 1374/1375 = Drum
  Trigger Key Zone Bottom/Top (00~7F); 1376/1377 = Drum Trigger Velocity Zone
  Bottom/Top (01~7F); 1378 = bit0 Drum Trigger Mode (Start
  Immediately~Wait KBD Trig), bits 2~1 Drum Latch Mode (Off~Use Scene Latch).
- **Scene records** at 2440 + stride×scene (the scene selected at 1348):
  programs (HD-1 and EXi, Prog_HD-1.txt / Prog_EXi_Common.txt) stride **28**,
  combis (CombiAndSongTimbreSet.txt) stride **44** (two 16-byte ARP blocks,
  then the drum fields). Within one scene record, the drum fields sit at
  **+16 (programs) / +32 (combis)**: Drum Select (bit0 select 0~1, bit1 Drum
  Run, bits 3~2 Step Seq. Select A~D), +4 Drum Track Pattern Number (LE16,
  0..1999), +6 Pattern Bank (bits 3~0, Preset~User) + Trigger Sync Mode
  (bit4) + Swing Resolution (bits 7~5), +7 Drum Track Shift (-24..+24).

### 3.1 What the buggy conversion did (byte-verified)

Zone A (0..1303) was copied identically, so the NAUTILUS RT Controller bytes
landed in the KRONOS Drum Track Common. Tester file, program slot 44
('OB Some Like This SW2', bank 0x2000D) — the one program with the drum
track on:

| bytes 1292..1303 | value |
|---|---|
| source (NAUTILUS RT Controller) | `00 00 00 00 01 00 10 00 00 00 01 00` |
| buggy output (identity copy) | `00 00 00 00 01 00 10 00 00 00 01 00` |
| fixed output (rebuilt DTC) | `06 03 00 13 00 7F 01 7F 00 09 10 00` |

Decoded as a KRONOS Drum Track Common, the buggy bytes read: pattern 0,
trigger "Start Immediately", latch Off, **Drum Track Off** (the RT Controller
mode byte 0x00 has bit4 clear), key zone 1..0 and velocity zone 16..0
(**inverted**), output channel 0, input channel 1 — i.e. the drum track
disappeared and the zones were garbage, exactly as the tester reported.

The source scene data for the same slot: scene select 0, Drum Switch on
(1349 = 0x04), trigger byte 1378 = 0x03 (Wait KBD Trig, latch On), key zone
0..127, velocity zone 1..127, output channel 9, input channel 16; scene 0
record: Drum Select 0x02, **pattern 774** (preset), sync Off, shift 0.

## 4. The fix (v1.6.2)

All in `NautilusToKronosConverter.cs` (mirrored 1:1 in
`docs/python-script/pcglib_convert.py`):

1. **Wave sequence bank assignment** (`Build`): the INT bank and the user
   banks 0x20000..0x2000D keep their bank id; the NAUTILUS banks beyond
   0x2000D (P..T, bids 0x2000E..0x20012) take the KRONOS user banks that no
   identity bank claimed, in bank-id order; banks without a free target are
   dropped and reported (as before). Tester file: T (0x20012) → U-A (0x20000).
2. **Wave sequence reference remap** (`RemapWaveSequenceReferences`, HD-1
   program slots only — EXi programs use no wave sequences): for each zone
   record of MS type 2 (Wave Sequence), the LE16 global index is decoded as
   `150 + userBank*32 + slot`; INT references (< 150) are unchanged; a
   reference whose source bank has a target is rewritten to the target bank's
   index space; a reference into a KRONOS-space bank that is simply not in
   the file is kept (the target bank exists, Init-filled); a reference into
   a dropped bank is reset to 0. Every remap/reset is reported with the patch
   name, bank, slot, oscillator, zone, source index, bank letter, slot name
   and new index.
3. **Drum Track Common rebuild** (`RebuildDrumTrackCommon`, HD-1 + EXi
   program slots and combi slots): the KRONOS bytes 1292..1303 are rebuilt
   from the NAUTILUS scene data of the selected scene:

   | KRONOS byte | NAUTILUS source |
   |---|---|
   | 1292..1293 Pattern Number (clamped to 0..999) | scene record +drumSelect+4..5 (LE16, 0..1999) |
   | 1294 Pattern Bank | scene record +drumSelect+6, bits 3~0 |
   | 1295 bit0 Trigger Button Mode | scene common 1378, bit0 |
   | 1295 bits 1~2 Trigger Latch Mode | scene common 1378, bits 2~1 |
   | 1295 bit3 Trigger Sync Mode | scene record +drumSelect+6, bit4 |
   | 1295 bit4 Drum Track On | scene common 1349, bit2 (Drum Switch) |
   | 1296 / 1297 Key Zone Bottom / Top | scene common 1374 / 1375 |
   | 1298 / 1299 Velocity Zone Bottom / Top | scene common 1376 / 1377 |
   | 1300 Shift | scene record +drumSelect+7 |
   | 1301 Output MIDI Channel | scene common 1360 (Drum Output Channel) |
   | 1302 Input MIDI Channel | scene common 1373 (Drum Input Channel) |
   | 1303 (unused) | 0 |

   Program slots use scene stride 28 with drum fields at +16; combi slots
   stride 44 with drum fields at +32. Every slot with the drum track on, a
   pattern number clamped to 999, a user-bank pattern, or a step-sequence
   scene is reported; a summary line closes the report.
4. **Report plumbing**: the conversion report gains three note lists
   (wave sequence remaps, wave sequence resets, drum track conversions),
   printed raw at the end of the report .txt by the app and the CLI
   (`MainViewModel.WriteConversionReport`, `pcglib convert`).

## 5. Verification

### 5.1 Tester file (byte-level)

`pcglib convert "errors/N_EXs342 Kelfar Diamond Analog Synth.PCG" -t kronos
--validate` (v1.6.2):

- 3 banks mapped, 0 dropped, all chunk checksums valid.
- `WBK1 0x20012 -> 0x20000 bank U-A (32 slots)`; the output bank U-A content
  is **byte-identical** to the source bank T (all 32 slots, names
  '8Voice RR OBX' …).
- 9 wave sequence references remapped 726..732 → 150..156 (bank T slots
  0..6 → U-A slots 0..6, names matching); the 10th WS zone references INT
  index 0 and is unchanged. Program tail: identity +6 except exactly the 18
  remapped index bytes.
- 17 drum tracks on (1 program + 16 combis) rebuilt; 8 pattern numbers
  clamped to 999 (NAUTILUS 1205..1270 → 999); 1 user-bank pattern reported
  ('OB TRON' U241); 0 step-sequence scenes. Slot 44 DTC =
  `06 03 00 13 00 7F 01 7F 00 09 10 00` (pattern 774, trigger Wait KBD Trig,
  latch On, drum on, KZ 0..127, VZ 1..127, out 9, in 16) — matching the source
  scene data (§3.1). All 128 program + 128 combi Drum Track Commons decode
  sanely (ordered key/velocity zones matching the source scene data).
- The Python port produces a **byte-identical** PCG and an identical report
  (except the Output: path line).

### 5.2 Unit tests

`src/PCG Tools Unittests/NautilusKronosConversionTest.cs`: 8/8 N→K tests
pass, including 3 new synthetic-file tests — a NAUTILUS wave sequence bank
beyond the KRONOS space takes a free KRONOS user bank (and references remap),
the Drum Track Common is rebuilt from zone B scene data (program scene 0 +
combi scene 1, stride 44), and wave sequence banks without a free KRONOS
target are dropped (19 user banks → 5 dropped, references reset to 0,
identity references kept).

### 5.3 Factory and user files

- `factory/NAUTILUS/PRELOAD.PCG` → KRONOS: 32 banks mapped, 0 dropped,
  checksums valid. All wave sequence banks are 0x20000..0x20007 (inside the
  KRONOS space) → identity, 0 remaps, 0 resets. 115 drum tracks on
  (27 programs, 88 combis), 349 pattern numbers clamped to 999.
- `factory/NAUTILUS/MOATAZ.PCG` → KRONOS: 65 banks mapped, 25 dropped
  (20 PRG1 user banks beyond the KRONOS program space — pre-existing identity
  behavior — + 5 WBK1 banks P..T, 0x2000E..0x20012: all 14 KRONOS user
  banks are claimed by identity banks, so no free target remains), checksums
  valid. 40 wave sequence references into the dropped banks reset to 0 and
  reported with names. 393 drum tracks on (26 programs, 367 combis), 353
  clamps, 3 user-bank patterns reported.

### 5.4 Builds and suites

App + CLI build 0 errors / 0 warnings (Debug + Release). xUnit
`PcgLib.Core.Tests`: 11/11 (including the CLI version banner, now
"pcglib 1.6.2 (core 1.6.2.0)"). MSTest N→K conversion tests 8/8; the 9
OASYS-direction failures on the CI filter are pre-existing on b9be3c9
(stash-verified: identical failure set with and without this fix) and are
1.6.3 work.

## 6. Limitations and assumptions

- **Pattern numbers**: the NAUTILUS preset drum track patterns go up to
  1999 (dump range 0000~07CF; the factory uses up to ~1271) while the KRONOS
  accepts 0..999. The converter assumes the NAUTILUS and KRONOS preset
  patterns **correspond by number** up to 999 and clamps the rest (each
  clamp is reported). If the two preset sets diverge below 1000, the
  clamped references would point at the wrong pattern on the KRONOS —
  unverifiable without a NAUTILUS.
- **User patterns are not converted**: a user-bank pattern reference (bank
  bit set) is kept as-is and reported; the NAUTILUS pattern data itself
  (ABK1 chunks) has no KRONOS target chunk and is not carried.
- **Step sequences and the arpeggiator are not converted** (NAUTILUS-only,
  no KRONOS equivalent; a scene whose Drum Select bit0 is set — "Drum
  Select 0~1" per Prog_HD-1.txt — is reported as a step-sequence scene).
  The NAUTILUS RT Controller settings (1292..1331) have no KRONOS equivalent
  at those offsets and are dropped (the KRONOS KARMA block starts at 1304).
- **EXi program slots** get the Drum Track Common rebuild but no wave
  sequence remap (EXi/MOD-7 programs use no wave sequences).
- **K→N→K round trips** — fixed in v1.6.3: the K→N conversion now mirrors
  the KRONOS Drum Track Common into the NAUTILUS zone B scene data (the
  exact inverse of the N→K rebuild, including the undocumented flag bits
  7~5), and writes the NAUTILUS RT Controller factory default at
  1292..1302, so a K→N→K round trip preserves the Drum Track Common
  byte-identically. (In v1.6.2 the K→N direction defaulted the NAUTILUS
  scene data, so the way back produced the KRONOS default DTC instead of
  the original bytes.)
- **Drum kits, wave sequence slots, set lists**: unchanged (verbatim slots).

## 7. Latent model bugs found along the way (FIXED in v1.6.3)

The converters do not use these model paths, so the conversion output was
never affected; they affected the WPF app's "used wave sequence"
resolution. All four are fixed in v1.6.3 — see
`docs/KRONOS_OASYS_V163_FIX.md` §3 and the regression tests
(`src/PCG Tools Unittests/WaveSequenceResolutionTest.cs`, 4/4):

- `NautilusProgram.GetZoneMsType` / `GetZoneMsByteOffset`
  (src/KorgKronosTools/Model/Nautilus/Synth/NautilusProgram.cs:156-171,
  198-204) used the **KRONOS v5** record base 2774 for a NAUTILUS (v6)
  file; the v6 records sit at **2768** + osc*466 + zone*22 (strides
  unchanged). The type byte was read 6 bytes high. Fixed: base 2768.
- `GetUsedWaveSequence` (both classes; NautilusProgram.cs:212-234,
  KronosProgram.cs OS 2.x/3.x branch) read the index as a **3-bit value
  from the single byte at +16** (`IntParameter.Set(..., +16, 2, 0,
  ...)`) — inside the MS Bank UUID field, always 0 in practice, so every
  zone resolved to INT WS 0. (The first edition of this section described
  it as "the LE16 index at +16" — the pre-fix code did a 3-bit
  single-byte read, not a 16-bit one.) The byte-verified layout (and the
  v5 fiche tables: "Zone1 MS Number" at 2792..2793) puts the global
  index at **+18..19** as a little-endian 16-bit value. Fixed:
  `SetMultiBytes` reads the LE16 at +18.
- `GetWaveSequenceIndices` (both classes) decremented `patchIndex` but
  never `waveSequenceIndex` in the bank walk, so any global index >= 150
  (any reference into a user bank) ran the bank index off the end of the
  bank collection and threw. Masked until now because every index read
  as 0. Fixed: the walk decrements the index by each bank's patch count.
- `SetWaveSequence` (both classes; KronosProgram.cs OS 2.x/3.x branch
  only — live code, called from `Program.cs`) wrote the little-endian
  16-bit index at record **+0..1**, clobbering the MS type byte. Fixed:
  writes at +18..19. The KRONOS OS 1.x/1.5/1.6 branch (bank/number
  bytes at +1/+2 — a different zone-record layout) is deliberately
  untouched.

## 8. Files changed

- `src/KorgKronosTools/Model/Kronos/Conversion/NautilusToKronosConverter.cs`
  — the fix (bank assignment, reference remap, DTC rebuild, report).
- `src/KorgKronosTools/ViewModels/MainViewModel.cs` — report plumbing
  (conversion notes), version 1.6.2.
- `src/pcglib/Program.cs` — CLI report plumbing, version 1.6.2.
- `src/PCG Tools Unittests/NautilusKronosConversionTest.cs` — 3 new tests +
  zone-A identity checks corrected to 0..1291.
- `docs/python-script/pcglib_convert.py` — 1:1 Python mirror of the fix.
- `docs/python-script/NautilusToKronosConverter.cs` — refreshed reference copy.
- Version surfaces: `src/pcglib/pcglib.csproj`, `src/PcgLib.Core/PcgLib.Core.csproj`,
  `src/KorgKronosTools/Properties/AssemblyInfo.cs`, `installer/pcglib.iss`,
  `src/PcgLib.Core.Tests/CliSmokeTests.cs`.
- Docs: this file; `docs/NAUTILUS_ZONE_B_ANALYSIS.md` (layout correction +
  answered open items); `docs/HD1_PARAMETER_OFFSET_MAPPING_V5_V6.md` §4.1
  (zone A identity claim corrected to 0..1291).

Follow-up in v1.6.3 (the K→N drum-track mirror, see §6 above):
`src/KorgKronosTools/Model/Nautilus/Conversion/KronosToNautilusConverter.cs`
(mirror + RT Controller default + report), `NautilusToKronosConverter.cs`
(the N→K rebuild now also carries the undocumented flag bits 7~5),
`MainViewModel.cs` / `src/pcglib/Program.cs` (report plumbing),
`docs/python-script/pcglib_convert.py` (1:1 mirror),
`src/PCG Tools Unittests/KronosNautilusConversionTest.cs` /
`NautilusKronosConversionTest.cs` (3 new tests),
`src/PcgLib.Core.Tests/SyntheticPcg.cs` (the K→N oracle updated).
