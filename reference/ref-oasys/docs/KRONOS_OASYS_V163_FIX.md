# KRONOS ↔ OASYS conversion — v1.6.3 fixes (2026-10-23)

_October 23, 2026. v1.6.2 shipped the byte-verified OASYS ↔ KRONOS HD-1
program parameter map (`OasysKronosHd1ProgramMap`,
`docs/OASYS_PARAMETER_MAP.md`) with 9 OASYS-direction tests failing (3 of
them synthetic and CI-runnable, so the CI test step was red on the v1.6.2
push), and left the latent wave-sequence model bugs documented in
`docs/NAUTILUS_TO_KRONOS_V162_FIX.md` §7 unfixed. v1.6.3 fixes all of
that, completes the KRONOS → OASYS conversion (EXi partial map, combi
KARMA re-derivation, skipped-bank reporting, OASYS v1 combi acceptance),
mirrors the drum track on KRONOS → NAUTILUS, and bumps the version to
1.6.3 everywhere (app, CLI, core, installer, python port)._

## TL;DR

1. **The 9 failing OASYS-direction tests** — root cause: the two OASYS
   conversion test classes still verified the v1.6.1 *zeroing*
   conversion. Both classes are rewritten against the byte-verified
   HD-1 map; the CI filter is green again (68/68 locally, was 51/60 on
   the v1.6.2 list).
2. **One "Programs:" defaulted section** in the conversion reports
   (HD-1 + EXi in a single note) in both converters and the python port.
3. **The latent wave-sequence model bugs are fixed** (were fix doc §7):
   the NAUTILUS v6 record base, the +18 little-endian index read, the
   bank-walk decrement and the `SetWaveSequence` write offset — plus 4
   new regression tests (`WaveSequenceResolutionTest.cs`, 4/4).
4. **The KRONOS → OASYS conversion is complete** per the map: the EXi
   engine payload converts through a partial byte-verified map (three
   verbatim regions, the rest zeroed and reported), the combi KARMA map
   is re-derived (combi KARMA survives, shift −12), banks with an
   unexpected slot size are dropped and reported, and the OASYS v1
   combi slots (11288 B) are accepted with the extension bytes dropped
   and reported. Set lists stay dropped (no OASYS file carries them).
5. **The KRONOS → NAUTILUS drum track mirror**: the KRONOS Drum Track
   Common is mirrored into the NAUTILUS zone B scene data (the exact
   inverse of the v1.6.2 N→K rebuild), so K→N→K round trips preserve it
   byte-identically.
6. **Version 1.6.3 everywhere**, the OASYS working documents renumbered
   (the EXi partial map is §9 and the combi map §10 of
   `docs/OASYS_PARAMETER_MAP.md`), the historical 1.6.2 references kept
   as history.

## 1. The 9 failing OASYS-direction tests — root cause and fix

Root cause: `KronosOasysConversionTest` and `OasysKronosConversionTest`
still verified the v1.6.1 zeroing conversion. Their slot helpers and
synthetic fixtures were written before the parameter map existed and
asserted the old behavior — whole-slot zero regions, defaulted-section
counts that no longer matched the converters, synthetic slot checks that
did not correspond to any real byte layout. The converters had moved on
to the byte-verified map; the tests had not.

Fix — both classes rewritten against the verified HD-1 map
(`docs/OASYS_PARAMETER_MAP.md`):

- `VerifyProgramSlots` rewritten as region compares: zone A 0..1291
  identity; KARMA + Common 1304..2687 ↔ 1292..2675 (shift 12); the
  common tail 2718..2773 ↔ 2676..2731 (shift 42); the OSC blocks via the
  map's own `CopyZoneKronosToOasys` / `CopyZoneOasysToKronos` as the
  oracle (KRONOS stride 466 @2774 ↔ OASYS stride 288 @2732, zones
  8×22 B ↔ 4×6 B with the KORG-MS UUID carrying the OASYS bank byte);
  the trigger tail (crossfade pairs 1-3, damper, velocity zone), the
  238-byte parameter payloads and the Mixer2 records; the zero regions
  (K→O: the OASYS crossfade pairs 4..7 at +185..196, the display byte +
  undoc at +200..201, the Gate params +440..445 / +460..465, the tail
  3706+; O→K: the tail 3308+); per-slot EXi dispatch on the osc-mode
  byte (2558 K→O / 2546 O→K, `& 7 == 3`); O→K asserts the Drum Track
  Common / Drum Track factory defaults. Combis compare the full zone-A
  region (0..1303).
- A new `AssertRegionEqual` helper (byte-region compare with a
  descriptive failure message).
- The synthetic fixtures carry marker bytes at the mapped offsets
  (K→O: 1400, 2500, 2728, the KORG-MS UUID bank byte at 2775..2790,
  number/level/offset at 2792..2795, crossfade 2953, damper 2971,
  velocity 2972/2973, parameter 3026, Mixer2 3222, OSC2 parameter 3449;
  O→K: 1400, 2500, 2686, the zone fields 2733..2737, 2759, 2765..2767,
  2818, 3008, 3063) and the slot checks assert the markers land at the
  mapped target offsets.
- The defaulted-section counts match the merged report (see §2): K→O
  factory 9 (Programs + Combis + Set lists + 4 DBK1 + 2 WBK1 on OS 2),
  O→K factory 4, synthetic 4 both ways.

Result: the CI filter (`.github/workflows/build.yml` `--Tests:` list)
is green again — **68/68 passed** locally (67 names; one name,
`ConvertedSlotsPreserveVerifiedFields`, exists in both OASYS classes and
matches two tests), was 51/60 on v1.6.2. On CI the fixture-dependent
tests are Inconclusive; the 3 synthetic failures that made the CI test
step red (`SyntheticKronosPcgConvertsToOasys`,
`SyntheticOs2KronosPcgConvertsToOasys`, `SyntheticOasysPcgConverts`) now
pass. Locally the two classes run **15/15** (9 + 6; they include the 9
former failures). The CI list gained 8 tests with this release: 3 for
the K→N drum-track mirror, 2 stale-since-1.6.2 N→K tests
(`NautilusWaveSequenceBankBeyondKronosSpaceTakesFreeUserBank`,
`NautilusWaveSequenceBanksWithoutFreeKronosTargetAreDropped`) and 3 for
the skipped-bank / v1-combi robustness work.

## 2. One "Programs:" defaulted section (both converters + python port)

The conversion reports listed the defaulted program sections as two
separate notes ("Programs (HD-1): …" + "Programs (EXi…): …").
`KronosToOasysConverter` and `OasysToKronosConverter` now emit ONE
"Programs:" note covering both engines (HD-1 first, then EXi), and the
python port (`docs/python-script/pcglib_convert.py`) mirrors it. The
reports are verified identical between the C# CLI and the python port on
all three conversions (see §5) — including the merged notes.

## 3. The latent wave-sequence model bugs (fixed; was fix doc §7)

The converters do not use these model paths, so the conversion output was
never affected; they affected the WPF app's "used wave sequence"
resolution. All four are fixed in `NautilusProgram.cs` and
`KronosProgram.cs`:

- `NautilusProgram.GetZoneMsType` / `GetZoneMsByteOffset`
  (`src/KorgKronosTools/Model/Nautilus/Synth/NautilusProgram.cs:156-171,
  198-204`): the record base was the **KRONOS v5** fiche base 2774; the
  NAUTILUS v6 records sit at **2768** (strides unchanged: 466 per osc,
  22 per zone). The type byte was read 6 bytes high. Fixed: base 2768.
- `GetUsedWaveSequence` (both classes; `NautilusProgram.cs:212-234`,
  `KronosProgram.cs` OS 2.x/3.x branch): the index was read as a
  **3-bit value from the single byte at +16**
  (`IntParameter.Set(..., +16, 2, 0, ...)`) — inside the MS Bank UUID
  field, always 0 in practice, so every zone resolved to INT WS 0. The
  byte-verified layout (and the v5 fiche tables: "Zone1 MS Number" at
  2792..2793) puts the global wave sequence index at **+18..19** as a
  little-endian 16-bit value (the zone record's MS number). Fixed:
  `SetMultiBytes(..., +18, 2, ...)` reads the LE16.
- `GetWaveSequenceIndices` (both classes): the bank walk decremented
  `patchIndex` but never `waveSequenceIndex`, so any global index ≥ 150
  (any reference into a user bank) ran the bank index off the end of the
  bank collection and threw. Masked until now because every index read
  as 0. Fixed: the walk decrements the index by each bank's patch count
  and keeps the patch index.
- `SetWaveSequence` (both classes; `KronosProgram.cs` OS 2.x/3.x branch
  only — live code, called from `Program.cs`): wrote the little-endian
  16-bit index at record **+0..1**, clobbering the MS type byte. Fixed:
  writes at +18..19. The KRONOS OS 1.x/1.5/1.6 branch (bank/number
  bytes at +1/+2 — a different zone-record layout) is deliberately
  untouched.

Regression tests — `src/PCG Tools Unittests/WaveSequenceResolutionTest.cs`
(new, registered in the csproj), 4 tests:

- `KronosWaveSequenceZonesResolveThroughTheMsNumberIndex` /
  `NautilusWaveSequenceZonesResolveThroughTheMsNumberIndex`: the getter
  resolution against the raw LE16 at +18 (skipping EXi slots via the
  osc-mode byte and GM/unloaded banks; the expected bank/patch decoded
  with the same bank walk; asserts the resolved bank is the patch's
  parent and the index matches).
- `KronosSetWaveSequenceWritesTheMsNumberAtRecordPlus18` /
  `NautilusSetWaveSequenceWritesTheMsNumberAtRecordPlus18`: setter round
  trips are byte-identical, and a cross-bank write of global index 3
  lands at +18 with the MS type byte preserved.

`docs/NAUTILUS_TO_KRONOS_V162_FIX.md` §7 is retitled accordingly (its
first edition described the index read as "the LE16 index at +16" — the
pre-fix code did a 3-bit single-byte read — and listed only two of the
four bugs).

## 4. Version bump 1.6.2 → 1.6.3

Every version surface: `src/pcglib/Program.cs` (CLI `ToolVersion`),
`src/pcglib/pcglib.csproj`, `src/PcgLib.Core/PcgLib.Core.csproj`,
`src/KorgKronosTools/Properties/AssemblyInfo.cs` (`AssemblyVersion` +
`AssemblyFileVersion` 1.6.3.0), `src/KorgKronosTools/ViewModels/MainViewModel.cs`
(the `Version` const + the two convert-command doc comments),
`installer/pcglib.iss` (`MyAppVersion`; `MyAppVersion4` stays 1.5.0.0),
`src/PcgLib.Core.Tests/CliSmokeTests.cs` (the banner assert, now
"pcglib 1.6.3 (core"), `docs/python-script/pcglib_convert.py`
(`PCGLIB_VERSION`), and the current-version header comments of
`OasysKronosHd1ProgramMap.cs`, `OasysToKronosConverter.cs`,
`KronosToOasysConverter.cs`, plus the doc stamps (`docs/OASYS_PARAMETER_MAP.md`
"v1.6.3 working document", `docs/OASYS_SQZ_ANALYSIS.md` "the v1.6.3
converter"). Historical 1.6.2 references (the N→K fix notes, the
"not re-derived for 1.6.2" comments, the v1.6.2 docs) are unchanged.
The CLI banner now prints `pcglib 1.6.3 (core 1.6.3.0)`.

## 5. The KRONOS → OASYS conversion completion

The v1.6.2 K→O conversion zeroed the EXi engine payload, zeroed the combi
KARMA region and would have mis-converted any bank whose slot size had
no verified map. v1.6.3 completes it in four steps (full derivation in
`docs/OASYS_PARAMETER_MAP.md` §9/§10/§14):

1. **EXi engine payload partial map** (`OasysKronosHd1ProgramMap`, used
   by both OASYS converters). Three byte-verified verbatim copy regions
   replace the v1.6.1 zeroing: the common tail (2718..2851 ↔ 2676..2809,
   shift 42, 134 B), the EXi 1 engine head (2908..3235 ↔ 2848..3175,
   shift 60, 328 B) and the EXi 2 engine head (3960..4287 ↔ 3636..3963,
   shift 324, 328 B). Verified by exact byte comparison on the
   name-matched factory pairs (580 pairs KRONOS OS 3.2 PRELOAD MBK1 ↔
   the `.sqz` ALLBANKS MBK1, 6174-B v2 slots; 201 pairs ↔ PRODUCER MBK1,
   4386-B v0 slots): 0 differing bytes on E1/E3 and on E2 for the v0
   pairs (4 differing bytes total on the v2 pairs). Round trips with the
   converter itself: 0 differing bytes on the copied regions — 154,833 +
   66,547 + 226,567 = **447,947 EXi payload bytes** preserved (the v1.6.1
   zeroing lost all of them). The unmapped gaps (K 2852..2907 /
   3236..3959 / 4288..4959; O 2810..2847 / 3176..3635 / 3964..4385) stay
   zero and are reported in the defaulted sections ("the EXi engine
   payload is partially preserved/partially copied (…)").
2. **Combi KARMA map re-derivation**. The combi slot map is now
   byte-verified (`tables/Oasys_Combi_blocks.csv`): zone A 0..1291
   identity; KRONOS Drum Track Common 1292..1303 dropped K→O (O→K
   writes the combi factory default `CombiDrumTrackCommonDefault`
   `00 00 00 0B 00 7F 01 7F 00 09 10 00`); KARMA Common + Modules A..D
   1304..4789 ↔ 1292..4777 (shift 12); the Common/assignable tail
   4790..4801 ↔ 4778..4789; 16 timbres 188 ↔ 186 B. **Combi KARMA now
   survives the conversion.** Verified: K→O→K on the KRONOS OS 3.2
   factory (768 combis: zone A and KARMA 0 mismatches, DTC defaulted
   768/768 as expected); O→K→O on PRODUCER (384 combis byte-identical).
3. **Skipped-bank reporting + OASYS v1 combi acceptance.** A bank whose
   slot size matches no verified map is dropped and reported
   (`PBK1 0x20000 bank U-A (128 slots, 4386-byte fiche): dropped -
   unexpected KRONOS/OASYS slot size (no verified map)`) instead of
   being silently mis-converted. O→K now accepts the OASYS v1 combi
   slots (11288 B, verified on the `.sqz` ALLBANKS.OASYS.PCG;
   `OasysCombiSlotSizes = {7766, 11288}`) and drops the 3522-B extension,
   reported per bank; the v1/v2 program engine extension bytes (6174-B
   slots, 1788 extra) were already accepted and are reported per bank.
4. **Set lists — investigated, unconvertible.** None of the 8 available
   OASYS files (7 factory + the `.sqz` ALLBANKS) carries SLS1/SBK1
   chunks, and the MIDI Quest `.sqz` documents the set list entry
   *semantics* (program/combi/song references + delay) but not the
   on-disk layout. Both directions keep dropping them, now with the
   evidence in the report ("none of the 8 available OASYS files carries
   SLS1 chunks").

Tests: the EXi assertion blocks in `KronosOasysConversionTest` and
`OasysKronosConversionTest` were rewritten against the partial map (3
region compares + 3 zero-gap asserts per slot, using the map constants);
3 new synthetic tests cover the skipped-bank reporting and the v1 combi
acceptance (`SyntheticKronosUnexpectedSlotSizeBankIsDroppedAndReported`,
`SyntheticOasysV1CombiSlotsConvertWithExtensionDropped`,
`SyntheticOasysUnexpectedSlotSizeBankIsDroppedAndReported`); the
"Programs:"/"Combis:" defaulted-section counts updated. All registered
in the CI filter.

## 6. The KRONOS → NAUTILUS drum-track mirror

The v1.6.2 N→K fix rebuilds the KRONOS Drum Track Common from the
NAUTILUS zone B scene data, but the K→N direction defaulted the scene
data, so K→N→K round trips did not preserve the DTC
(`docs/NAUTILUS_TO_KRONOS_V162_FIX.md` §6, limitation removed in 1.6.3).
v1.6.3 mirrors it:

- `KronosToNautilusConverter.MirrorDrumTrackCommon` writes the KRONOS
  Drum Track Common (1292..1303) into the NAUTILUS zone B scene data —
  the exact inverse of the N→K `RebuildDrumTrackCommon`: the scene
  selected by the default block's scene select carries the drum track;
  on/off, pattern number (fits the NAUTILUS 0..1999 range unclamped),
  pattern bank, trigger sync, latch, key/velocity zones, out/in
  channels; the step sequence select bit is cleared (the KRONOS has no
  step sequences); the undocumented flag bits 7~5 are carried through
  the scene common byte's reserved bits.
- `RestoreRtController` writes the NAUTILUS RT Controller factory
  default at 1292..1302 (the NAUTILUS bytes the KRONOS DTC occupies) and
  carries byte 1303.
- The N→K rebuild now also carries the undocumented flag bits 7~5 and
  byte 1303 back.
- Report: one line per converted drum track (`Program '…' (bank 0x…
  slot n): drum track on -> NAUTILUS scene data (pattern P708, trigger
  Wait KBD Trig, latch On)`), user-pattern warnings, and a summary line
  (`Drum tracks: 175 on (22 program(s), 153 combi(s)), 0 user pattern(s)
  not converted` on the KRONOS factory file).

Verified: **K→N→K preserves the Drum Track Common byte-identically**
(new test `KronosNautilusKronosRoundTripPreservesDrumTrackCommon`), the
mirror lands in the scene data
(`KronosDrumTrackCommonIsMirroredIntoZoneBSceneData`), the N→K rebuild
carries it back
(`NautilusDrumTrackCommonIsRebuiltFromZoneBSceneData`), and the xUnit
K→N oracle (`SyntheticPcg.VerifyProgramZoneRulesKronosToNautilus`) was
updated to the new zone A layout (0..1291 identity + the RT Controller
default at 1292..1302 + byte 1303 carried).

## 7. Verification

- Builds: `src/pcglib-net8.sln` (core + core tests + CLI) 0 warnings /
  0 errors; `src/PCG Tools Unittests` (+ the WPF app project it
  references) 0 warnings / 0 errors.
- MSTest on the CI filter (`.github/workflows/build.yml` `--Tests:`
  list, 67 names / 68 tests): **68/68 passed** (was 51/60 on v1.6.2).
- MSTest targeted, the four conversion classes **34/34**: K→O
  `KronosOasysConversionTest` **9/9**, O→K `OasysKronosConversionTest`
  **6/6**, K→N `KronosNautilusConversionTest` **11/11**, N→K
  `NautilusKronosConversionTest` **8/8**; `WaveSequenceResolutionTest`
  **4/4** (fixture-dependent — not in the CI filter, Inconclusive on
  CI; run locally).
- xUnit `PcgLib.Core.Tests`: **11/11** (the banner test expects
  "pcglib 1.6.3 (core" and runs against the freshly built CLI).
- Python port: `py_compile` OK; `--version` reports 1.6.3; **10/10
  conversions byte-identical** to the C# CLI (6 single-hop: N→K the beta
  tester's file, N→K factory, K→N factory, O→K ALLBANKS, O→K PRODUCER,
  K→O factory; 4 round trips: K→N→K, O→K→O ×2, K→O→K) and **10/10
  reports identical** (modulo the Source:/Output: file names and line
  endings) — including the merged "Programs:" defaulted notes, the EXi
  partial-map wording, the combi KARMA wording and the skipped-bank /
  v1-extension lines.
- Round-trip spot checks with the built CLI: K→O on the KRONOS OS 3.2
  factory (18 banks mapped, 5 dropped, 10 defaulted entries — the new
  Programs/Combis/Set-lists notes verified verbatim); O→K on the `.sqz`
  ALLBANKS (27 banks mapped, 0 dropped, 45 defaulted entries — 14
  v1/v2 engine-extension lines + 14 v1 combi-extension lines + the
  drum kit / wave sequence sound-defaults).

## 8. Still open (not 1.6.3)

- **Set lists** — unconvertible (no OASYS file carries SLS1/SBK1; the
  MIDI Quest `.sqz` documents the semantics, not the on-disk layout);
  dropped and reported in both directions.
- **Drum kits and wave sequences** — no verified map in either direction
  (KRONOS 38424-byte drum kit fiche vs OASYS 11288-byte; KRONOS
  2216-byte wave sequence fiche vs OASYS 1192-byte); sound-defaulted
  (Init-filled, names preserved) and reported.
- **The unmapped EXi engine gaps** (`docs/OASYS_PARAMETER_MAP.md` §9) —
  stay zero and are reported; mapping them needs a larger name-matched
  EXi sample.
- **Multisample correspondence table** — none available; zone conversion
  preserves (bank, number) structurally only.
- **Per-parameter SysEx address extraction** from the 214
  `SysXMap.ID*.bin` files, the MQ 8277 common-tail anomaly, the OASYS
  step-sequencer location, the MOD-7 slot-size discrepancy (4386 vs
  6174 B) — see `docs/OASYS_PARAMETER_MAP.md` §14.
- **The NAUTILUS/KRONOS pattern correspondence below 999** and the
  NAUTILUS user patterns / step sequences (no KRONOS equivalent) —
  see `docs/NAUTILUS_TO_KRONOS_V162_FIX.md` §6.
- **The Avalonia GUI** (macOS/Linux port) — the next project phase.
- The maintainer tests the 1.6.3 build (tag `v1.6.3` to publish).

## 9. Files changed

- `src/PCG Tools Unittests/KronosOasysConversionTest.cs`,
  `src/PCG Tools Unittests/OasysKronosConversionTest.cs` (the test
  rewrite + the EXi partial-map assertion blocks + the 3 new
  skipped-bank / v1-combi tests),
  `src/PCG Tools Unittests/KronosNautilusConversionTest.cs`,
  `src/PCG Tools Unittests/NautilusKronosConversionTest.cs` (the 3
  drum-track mirror tests), `src/PCG Tools Unittests/WaveSequenceResolutionTest.cs`
  (new + the csproj registration).
- `src/KorgKronosTools/Model/Nautilus/Synth/NautilusProgram.cs`,
  `src/KorgKronosTools/Model/KronosSpecific/Synth/KronosProgram.cs` (the
  model fixes).
- `src/KorgKronosTools/Model/Kronos/Conversion/OasysToKronosConverter.cs`,
  `src/KorgKronosTools/Model/OasysSpecific/Conversion/KronosToOasysConverter.cs`,
  `src/KorgKronosTools/Model/Common/Conversion/OasysKronosHd1ProgramMap.cs`
  (the merged Programs note + the header stamps; the EXi partial-map
  constants, the combi KARMA map, the skipped-bank collection, the
  `CombiDrumTrackCommonDefault`, the 11288-B v1 combi acceptance).
- `src/KorgKronosTools/Model/Nautilus/Conversion/KronosToNautilusConverter.cs`
  (the drum-track mirror + the RT Controller default + the report),
  `src/KorgKronosTools/Model/Kronos/Conversion/NautilusToKronosConverter.cs`
  (the N→K carries), `src/KorgKronosTools/ViewModels/MainViewModel.cs`,
  `src/pcglib/Program.cs` (the report plumbing).
- `src/PcgLib.Core.Tests/SyntheticPcg.cs` (the xUnit K→N oracle updated
  to the new zone A layout).
- `.github/workflows/build.yml` (the CI `--Tests:` list +8 tests).
- `docs/python-script/pcglib_convert.py` (the merged notes + the version
  + the 1:1 mirror of everything above).
- Every version surface (§4), `docs/OASYS_PARAMETER_MAP.md` (the new §9
  EXi partial map + §10 combi map, renumbered, the open points updated),
  `docs/OASYS_SQZ_ANALYSIS.md` (the doc stamps),
  `docs/NAUTILUS_TO_KRONOS_V162_FIX.md` §6/§7/§8 (the fixed limitation),
  `docs/ABOUT_DRUM_TRACKS_WAVE_SEQUENCES_NAUTILUS_TO_KRONOS.md` (the
  K→N mirror), `docs/ABOUT_THE_CONVERSION_FROM_KRONOS_TO_OASYS.md` (the
  completed conversion), this file, `tables/Oasys_EXi_blocks.csv` +
  `tables/Oasys_Combi_blocks.csv` (new).
- `STATUS.md`, `ROADMAP.md`, `RESUME.md` (the 1.6.3 entries).
