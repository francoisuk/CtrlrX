# KRONOS PCG format facts — cross-validated against the Python reference implementation

**Project:** kronos-pcglib
**Date:** October 17, 2026
**Sources:** `scripts/kronos_pcg.py` (self-contained Python reference module,
ported from the hardware-validated `pcgconvert-core.js` of "Le grand livre du
KRONOS") and the public Korg MIDI implementation documents in
`docs/midi_korg/` (already tracked; policy update of October 17, 2026 allows
public Korg documentation in the repository).
**Cross-validation:** `kronos_pcg.py` parses and rebuilds **byte-identically**
the factory files of OS 1 (`PRELOAD.PCG`, `INIT.PCG`), OS 2
(`PRELOAD_V2.PCG`), OS 3.1 and OS 3.2 — an independent confirmation of the
checksum formats, bank layouts and object versions verified in Milestone 2.

---

## 1. PCG1 chunk size can be understated

Some PCG files written by the KRONOS announce a PCG1 size smaller than the
real file length. Readers must therefore **parse to end-of-file, not to the
PCG1 size field** (the pcglib C# reader already does this). The M3 writer
must write the **correct** size — and the round-trip test must accept that
a KRONOS-written input may have had a wrong size (rewriting then fixes it,
so byte-identity holds only for files whose size field was already correct).

## 2. Set list object layout (SBK1/STL1)

From `docs/midi_korg/SetList.txt` (public Korg doc, OS 2+, v1.01):

- One set list = **69,416 bytes**: 24-byte set list name at offset 0,
  then 128 slots of **542 bytes** each, then 16 trailing bytes
  ((69,416 − 24 − 16) / 128 = 542 exactly).
- Slot layout (offsets from slot start): 24-byte slot name, then
  Performance Type (program/combi/song), Color, Font, Performance Bank
  (00~1E = INT-A..U-GG), Performance Index, Hold Time, Volume, Keyboard
  Track, Transpose mod (−24~+24) — exact bitfields in the table.
- SDB1/SBK1 checksum format: `(version << 16) | 0x0100 | sum8` (KRONOS
  SBK1/SDB1 v0; NAUTILUS SBK1 v1) — already implemented in `PcgChecksum.cs`
  and documented in `docs/CHECKSUM_ALGORITHM_VERIFICATION.md`.

**NAUTILUS v1 differences (verified on the factory PRELOAD.PCG, Oct 17,
2026):** one set list = **69,544 bytes**; slots are **543 bytes** — the
KRONOS slot layout with **one new byte (always 0 in the factory file)
inserted at slot offset 30**, so the 512-byte comment starts at 31.
STL1/SBK1 are version 1 (SLS1/SLD1/SDB1 stay v0). The SBK1/SDB1 bank
catalog is count=128, slot=69,544 / 3,612, bid=0 like the KRONOS.

**Slot reference semantics (both instruments, verified against the factory
files):** slot bytes 24-26 = Performance Type bits 1-0 of byte 24
(**0 = combi, 1 = program, 2 = song** — the doc's "prog/combi/song" order is
misleading; the factory data is unambiguous), Performance Bank bits 4-0 of
byte 25 (bits 7-5 = transpose MSB), Performance Index byte 26. Program
bank byte -> file bank id: 0-4 = bids 0-4, 5 = 0x8000, 6-16 = GM/g banks
(ROM, no file bank), 17-30 = 0x20000+n. Combi bank byte: 0-6 = bids 0-6,
17-23 = 0x20000+n. The factory default empty slot = (program, bank 0,
index 0); fully-zero slot headers are untouched slots. The SDB1 record is
`24-byte set list name + LE32 record size + 128 x (24-byte slot name +
LE32 slot size)` = 3,612 bytes — the Disk-mode browser cache
(`PcgMemory.UpdateSdb1Chunk` rewrites only the names; the size fields
follow the SBK1 layout: 69,416/542 KRONOS, 69,544/543 NAUTILUS).

## 3. Drum kit record (DBK1) and wave sequence (WBK1)

- Drum kit: **38,424 bytes, Object Version 3** — layout in
  `docs/midi_korg/DrumKit.txt`. Note per-note structure in v3:
  24-byte name + 128 notes x 300 bytes (8 sample-reference zones of
  34 bytes + 28 bytes) — from the OS 2 -> OS 3 conversion path.
- Wave sequence: **2,216 bytes, Object Version 1** — layout in
  `docs/midi_korg/WaveSequence.txt` (40-byte head + 64 steps of 34 bytes
  sample references in v1).

## 4. Global section (GLB1) OS 2 -> OS 3 growth

Global v1 (OS 2.x) is 24,620 bytes; OS 3 appends an 88-byte tail
(`(0x10, 0xFF) x 39 + 10 zero bytes`) to reach **24,708** — the size
observed in the OS 3.2 factory file. M3 copies GLB1 verbatim; this tail is
only needed if a Global section is ever rebuilt for OS 3 from an OS 2 one.

## 5. Bank numbering maps (closes the ROADMAP parking-lot item)

All maps are implemented in `scripts/kronos_pcg.py`:

| Map | Meaning | Source of truth |
|---|---|---|
| `prog_bid` / `prog_index` | File bank id (0x0..0x4, 0x8000 = I-F, 0x20000+n = U-..) <-> DIV1 program bank index | PCG1/DIV1 |
| `combi_bid` / `combi_index` | Same for combinations (I-A..I-G, U-A..U-G) | PCG1/DIV1 |
| `kit_index` | Drum kits / wave sequences: 0 = INT, 0x20000+n = U-.. | PCG1/DIV1 |
| `BANK_ENUM` | Timbre "Bank Number" byte in a combi timbre, Drum Track (byte 2689) and set list slot: I-A..I-F = 0-5, GM/g(1)..g(d) = 6-16, U-A..U-GG = 17-30 | Korg MIDI doc |
| `CBANK_ENUM` | Set list slot performance bank (programs/combis): 0-6 = I-A..I-G, 17-23 = U-A..U-G | Korg MIDI doc |
| `BANKSEL_PROG` / `BANKSEL_COMBI` | MIDI Bank Select (CC0, CC32) per bank — KORG bank map, Parameter Guide p. 764 | Korg Parameter Guide |
| `PROG_BANKCODE` / `COMBI_BANKCODE` | SysEx bank codes: I-.. = 0..n, U-.. = 0x40+n | Korg SysEx doc |

The pcglib C# reader's bank-id mappings (verified in M2) agree with
`prog_index`/`combi_index`/`kit_index`.

**NAUTILUS bank space (verified October 21, 2026):** the NAUTILUS has the
same 20 program banks as the KRONOS — the NAUTILUS SysEx documentation
(`docs/nautilus/NAUTILUS_MIDIimp/SysExDumps/`: CombiAndSongTimbreSet,
Prog_EXi_Common, Prog_HD-1, SetList) gives Bank Number `00~1E` =
`INT-A~U-GG` for combi timbres, Drum Track and set list slots, and the
wave-seq/drum-kit mappings list user banks up to U-GG. Real user files
prove it: 5 of the 9 NAUTILUS PCGs in `docs/nautilus_pcg/` contain banks
at bids 0x20009..0x2000D (U-CC..U-GG). The factory preload only fills
bids 0x20000..0x20008 (U-A..U-BB).

**NAUTILUS bank letters (verified October 21, 2026, maintainer + NAUTILUS
Parameter Guide E4):** on the machine display and in PCG Tools the
NAUTILUS banks carry single letters, NOT the KRONOS I-A/U-A names:

| Type | Banks | Bids | Notes |
|------|-------|------|-------|
| Programs | A..T (20) | A..E = 0..4 (EXi INT), F = 0x8000 (HD-1 INT), G..T = 0x20000..0x2000D | OS 1.1.1 expanded programs 20 -> 40 (extra banks a..t, not modelled - unverified bids); "Remap MS/Sample Banks" dialog: Bank A...O, P...T, a...t |
| Combis | A..N (14) | A..G = 0..6 (INT), H..N = 0x20000..0x20006 | 7 INT + 7 user (same bid space as KRONOS) |
| Drum kits | A..O (15) | A = 0 (INT, 40 kits), B..O = 0x20000..0x2000D (16 each) | GM kits sit between H and I in linear addressing |
| Wave sequences | A..T (20) | A = 0 (INT, 150), B..T = 0x20000..0x20012 (32 each) | A INCLUDES the INT bank; factory fills A..I; OS 1.1.1 expanded 15 -> 20 |

**Official KRONOS <-> NAUTILUS bank mapping (NAUTILUS Parameter Guide
E4, "Loading KRONOS .PCG files"):** programs, drum kits and wave
sequences map by LIST POSITION = bank id (KRONOS I-A..I-F -> NAUTILUS
A..F, U-A..U-GG -> G..T; the bid spaces are identical); combinations map
positionally over the full 14-bank lists (KRONOS I-A..I-G -> NAUTILUS
A..G, U-A..U-G -> NAUTILUS H..N; both instruments have 7 INT + 7 user
combi banks - the bid spaces and the set list bank byte spaces are
identical, only the letters differ). Confirmed against the NAUTILUS MIDI
Implementation bank map (combi banks A..G at CC32 0..6, H..N at CC32 8..14)
and real user files (hardware bank N = bid 0x20006, L = 0x20004). Both
pcglib converters implement this table (October 21, 2026; corrected in
v1.3 - build 1.2 wrongly modelled the NAUTILUS as 6 INT + 8 user banks,
which shifted every user combi bank display one letter down: N showed as
M, L as K); set list bank bytes remap structurally through the same
correspondence.

## 6. Combi timbres layout (v5, slot 7,810)

16 timbres at slot offset **4,802 + 188 x timbre**; each timbre holds
(program number, bank byte via `BANK_ENUM`, MIDI channel 1-16/17 = Gch,
status). Timbre 16 ends exactly at byte 7,810 — consistent with the
M2-verified combi zone map (Zone C from 4,790).

## 7. SysEx Object Dump (KRONOS receive path)

From the Korg SysEx doc (`docs/midi_korg/KRONOS_MIDI_SysEx.txt`,
already tracked): banks can be sent to the KRONOS as Object Dumps —
header `F0 42 3x 68`, function 0x73 (Object Dump) with 7-bit packing
(7 data bytes + 1 high-bits byte per group, `to7`), per-object payload
sizes HD-1 **3,706**, EXi **4,960**, combi **7,810**, program/EXi object
version 5, combi version 3; function 0x7C (Change Program Bank Type)
and 0x76 (Store Bank Request) around the dumps. Relevant to M3's
hardware acceptance and the .syx file-reading path.

## 8. OS 1 <-> OS 2+ object conversions (reference, out of M3/M4 scope)

`kronos_pcg.py` also contains the tested OS 1 <-> OS 2+ conversions (sample
references: single ROM/EXs byte <-> 16-byte `KORG....MS.00` UUID; HD-1
program v4 -> v5 oscillator zones at fiche 2,774, 8 zones of 6 -> 22 bytes;
drum kit v2 22,040 -> v3 38,424; wave sequence v0 1,192 -> v1 2,216). These
are the basis for a possible future "load OS 1 PCG" feature; M4 remains
KRONOS v5 <-> NAUTILUS v6.

## 9. M3 impact checklist

- Writers must compute the true PCG1 size (readers stay tolerant).
- Set list / drum kit / wave sequence layouts are fully specified (see 2-3).
- Checksum write path already proven (null-writer round-trip, byte-identical).
- `scripts/kronos_pcg.py` is a second, independent implementation to use as
  a differential-testing oracle for the C# writers.
- Bank numbering maps available for reference updates (M3 edit operations)
  and future MIDI features.
