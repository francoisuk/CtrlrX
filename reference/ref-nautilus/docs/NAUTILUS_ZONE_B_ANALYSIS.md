# NAUTILUS zone-B analysis — the ARP/Drum Track/Step Sequencer/Scenes block

_October 17, 2026. Empirical analysis of the NAUTILUS (v6) program and
combi "zone B" — the block that replaces the KRONOS (v5) KARMA block —
against the NAUTILUS factory PRELOAD.PCG (1,920 programs, 256 combis) and
the NAUTILUS Parameter Guide (docs/nautilus/Nautilus Parameters Guide E4)._

## Summary

The NAUTILUS zone B is the **Arpeggiator / Drum Track / Step Sequencer /
Scenes** configuration (Parameter Guide PROGRAM mode pages 0-6a..0-6f; the
KRONOS dedicates the same fiche region to KARMA, which the NAUTILUS does not
have). Layout of the **program** fiche (slot 4,954, bytes 1304..2551,
1,248 bytes):

| Bytes | Size | Content | PG page |
|---|---|---|---|
| 1304–1331 | 28 | Header records: five 6-byte records with ids 0x11..0x15 (`11 08 02 00 01 00`, `12 08 04 00 01 00`, `13 01 07 00 01 00`, `14 03 07 00 01 00`, `15 04 07 00 00 00`) + zero padding (semantics still open) | 0-6a |
| 1332–1347 | 16 | ARP / DRUM / LATCH switches and flags (mostly 00/01 toggles; byte 1334: 0x01 = 88% of programs; bit assignment not fully decoded) | 0-6b |
| 1348 | 1 | **Scene Select (bits 2~0, 00~03)** + Cue Mode (bits 5~4, Immediately~Measure) — Prog_HD-1.txt | 0-6a |
| 1349 | 1 | Switches: bit0 **Latch**, bit1 **Arp**, bit2 **Drum** (Off~On) — Prog_HD-1.txt | 0-6b |
| 1350–1351 | 2 | **Tempo, LE16 in centi-BPM** (0FA0~7530 = 40.00~300.00; verified: 0x2134 = 85.00 BPM, 0x2EE0 = 120.00 BPM, 0x2AF8 = 110.00) | 0-6a |
| 1352–1356 | 5 | Arp Gate / Arp Velocity / Arp+Drum Length / Arp+Drum Swing (biased: 0x40 = 0 for the [-64..+63] parameters, 0x7F = 127 for Length [0..127]) + Drum SD | 0-6c |
| 1357–1359 | 3 | reserved | |
| 1360–1373 | 14 | **Drum Output Channel** (1360) + Drum Inst. Select 01..12 note table (1361..1372, a constant 12-byte table across 99.9% of all programs: `30 34 33 36 3A 3D 41 35 3B 4C 4B 6B`) + **Drum Input Channel** (1373) | 0-6d |
| 1374–1378 | 5 | **Drum trigger zones / modes**: Key Zone Bottom/Top (1374/1375, 00~7F), Velocity Zone Bottom/Top (1376/1377, 01~7F); byte 1378: bit0 **Drum Trigger Mode** (Start Immediately~Wait KBD Trig), bits 2~1 **Drum Latch Mode** (Off~Use Scene Latch) | 0-6d |
| 1379 | 1 | reserved | |
| 1380–2435 | 4 x 264 | **The four Step Sequences (A–D)**, 264-byte blocks at 1380 / 1644 / 1908 / 2172 (Prog_HD-1.txt "Step Seq. A..D": Resolution/Accent/Length/Steps-per-beat header, then 64 steps x 12 tones + accent). In the factory file they are near-identical to each other (261/264 bytes equal); a block's non-zero content is a handful of defaults (`01 7F 03 0C 40 10 13` at +0/+1/+2/+4/+5/+8/+10; block A carries the extra `01 7F 03` prefix) | 0-6e |
| 2436–2439 | 4 | zero padding | |
| 2440–2551 | 4 x 28 | **The four Scene records (Scene 1–4)**, 28 bytes each at 2440 / 2468 / 2496 / 2524: ARP Pattern Number LE16 at +0..1 (0..2180), ARP Octave/Resolution/Sort/Latch/KeySync/Keyboard/Run/Loop at +2..3, ARP Gate/Velocity/Swing at +4..6, ARP Output/Input Channel at +12..13; **drum track fields: Drum Select at +16 (bit0 select 0~1, bit1 Drum Run, bits 3~2 Step Seq. Select A~D), Drum Track Pattern Number LE16 at +20..21 (0..1999), Pattern Bank bits 3~0 + Trigger Sync Mode bit4 + Swing Resolution bits 7~5 at +22, Drum Track Shift at +23 (-24..+24)** — Prog_HD-1.txt | 0-6d |

Exactly: 76 (head, 1304..1379) + 4 x 264 (step sequences) + 4 (pad) + 4 x 28
(scene records) = 1,248.

_Layout correction (v1.6.2, from the MIDI-implementation SysEx dumps
Prog_HD-1.txt / Prog_EXi_Common.txt / CombiAndSongTimbreSet.txt): the first
edition of this document swapped the two 4-block regions — the 264-byte
blocks at 1380..2435 are the **Step Sequences A–D** (not the Scenes), and
the 28-byte records at 2440..2551 are the **Scene records 1–4** (not step
sequences). The scene-common block extends to 1378 (drum trigger modes),
not 1347; there is no tempo-source byte at 1349 (bit0 is the Latch
switch)._

The **combi** fiche zone B (slot 5,640, bytes 1304..2619, 1,316 bytes) has
the same layout — the step-sequence blocks at the identical offsets
(constant across all 256 factory combis) — but the scene records are 44
bytes each (two 16-byte ARP blocks A+B, then the drum track fields at
+32..+39: Drum Select at 2472, Pattern Number LE16 at 2476..2477, bank /
trigger-sync / swing at 2478, Shift at 2479, reserved 2480..2483;
Scene 2 starts at 2484 — CombiAndSongTimbreSet.txt), followed by a 4-byte
ARP B key/velocity-zone tail at 2616..2619: 76 + 4 x 264 + 4 + 4 x 44 + 4
= 1,316. The combi head (1304..1331) differs from the program head: the
6-byte record payloads carry timbre-zone masks (values such as
`00 3C 01 00`, `FF 3F 01 00`, `FF 3F 00 00`) instead of the program's
`07 00 01 00` defaults.

## Per-byte variability (factory statistics)

Across all 1,920 factory programs, only **124 of 1,248** zone-B bytes vary
(all statistics in build/zoneb_stats.txt — script in this session's
history, see RESUME):

- 1350/1351 (tempo): 64/51 distinct values, mode 0xE0/0x2E (= 120.00 BPM,
  17-19%) — the only "musical" parameter that really varies.
- 1352/1353 (gate/velocity): 63/81 distinct values, mode 0x40 (0).
- 2440..2551 (step records): the high-entropy region — note/velocity
  data of the factory step sequences.
- Everything else is either constant or a two-value toggle (e.g. 1380/1381/
  1384 = `0C`/`40`/`10` vs 00/00/01 in 2.3% of programs).

Across all 256 factory combis, **163 of 1,316** bytes vary (tempo at
1350/1351 again, combi-head zone masks at 1305..1331, step records at
2440..2619).

## Impact on the converters

- **KRONOS -> NAUTILUS** (`KronosToNautilusConverter`): the embedded
  `NautilusProgramDefaultBlock` (most common 1,248-byte block across the
  factory HD-1 programs) and `NautilusCombiDefaultBlock` are REAL factory
  blocks — i.e. valid ARP/Scenes/StepSeq states: tempo 110.00 BPM,
  gate/velocity 0, all four scenes at their default record, default step
  records. The hardware-validated default stays unchanged (field-proven by
  the beta testers); this analysis confirms it is semantically a sane
  "default" state rather than arbitrary bytes.
- **NAUTILUS -> KRONOS** (`NautilusToKronosConverter`): the embedded
  KARMA default blocks (most common KARMA zone across the KRONOS factory,
  per engine) are equally real factory states.
- **Since v1.6.2** the NAUTILUS -> KRONOS converter also **rebuilds the
  KRONOS Drum Track Common** (bytes 1292..1303 of the KRONOS fiche, where
  the NAUTILUS keeps its RT Controller) from the zone B scene data
  decoded above: scene common 1348 (Scene Select) / 1349 bit2 (Drum
  Switch) / 1360 (Drum Output Channel) / 1373 (Drum Input Channel) /
  1374..1377 (trigger key/velocity zones) / 1378 (trigger + latch
  modes), and the selected scene's record drum fields (Pattern Number
  clamped to the KRONOS 0..999 range, Pattern Bank, Trigger Sync, Shift).
  Full mapping table, verification and limitations:
  docs/NAUTILUS_TO_KRONOS_V162_FIX.md.
- A synthetic "ARP off" default would require decoding the 1332..1347
  switch bytes 1:1 to the PG parameters — not attempted; the current
  defaults are field-validated and there is no evidence they misbehave.

## Open items

- The exact bit assignment of the ARP/DRUM/LATCH switch bytes (1332..1347)
  is not decoded 1:1; the variability map above constrains them.
- The five header records (ids 0x11..0x15) have unknown semantics; their
  payloads are constant defaults (programs) or zone masks (combis).
- The internal layout of the 264-byte Step Sequence blocks beyond the
  decoded header (64 steps x 12 tones + accent) and of the scene-record
  ARP fields +7..+11 / +14..+15 is not needed for the drum track rebuild
  and was not decoded further.

_Answered since the first edition (v1.6.2, from the MIDI-implementation
SysEx dumps): the scene-common block is 1348..1378 (Scene Select,
Latch/Arp/Drum switches, tempo, ARP gate/velocity/length/swing, drum
output/input channels, drum trigger key/velocity zones, drum trigger
mode + latch mode), and the 28-byte records at 2440..2551 are the Scene
1–4 records carrying the per-scene ARP + drum track settings (the former
"step records" interpretation was wrong — see the layout correction
above)._
