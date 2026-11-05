# OASYS `.sqz` analysis — the MIDI Quest `Korg OASYS` config, re-derived

**Status:** 2026-10-23 redo of the analysis behind `docs/OASYS_PARAMETER_MAP.md`. The
previous session's scratchpad (extracted config + scripts) was lost in a computer
restart; the `.sqz` itself survives at `docs/oasys/Korg OASYS.sqz` (now gitignored).
This document reports the fresh extraction, everything it yields, and cross-checks
the earlier doc. Claims of the earlier doc that are confirmed are marked ✓;
corrections are marked **CORRECTION**.

**Companion tables (generated, do not edit by hand):**

- `tables/Oasys_SysXMap_summary.csv` — one row per `SysXMap.ID*.bin` (214 rows):
  record count/size, base addresses, the record-0 SysEx frame, DESC value.
- `tables/Oasys_factory_names.csv` — the 1408 factory slot names extracted from the
  per-slot dump records (§6).

---

## 1. Provenance and licensing

The primary source analysed here is `docs/oasys/Korg OASYS.sqz`, a **Sound Quest / MIDI Quest
commercial product** (the config users load into MIDI Quest to use it as an OASYS
librarian/editor), analysed here **for personal, non-commercial use only**. Nothing extracted
from it (ini/bin/sqt/png content) is redistributed or committed to this repository; only facts
derived from it (offsets, sizes, names, addresses) are recorded in this document and the two
companion CSVs. If this document is shared, this section must travel with it.

Other sources: `factory/OASYS/KORG Factory New/PRODUCER.PCG` (reference OASYS file),
`factory/OS3.2/FACTORY/PRELOAD.PCG` (reference KRONOS file), `tables/Programme_HD-1.csv`
(KRONOS HD-1 program parameter table).

---

## 2. The `.sqz` container (verified)

`Korg OASYS.sqz`: 90,224,161 bytes, dated Oct 24 2021.

```
+0   "SQZ "                    magic
+4   entry count               u32 LE = 1810
+8   entries, repeated:
     nameLen                   1 byte
     name                      nameLen bytes (UTF-8, '/'-separated paths)
     blobLen                   u32 LE
     blob                      blobLen bytes, gzip-compressed
```

The parse consumes the file exactly (90,224,161 / 90,224,161 bytes); all 1810 entry
names are unique. Extraction yields 1810 files, 193,663,006 bytes raw (~184.6 MB), under
a top folder `Korg OASYS/`.

**CORRECTION (clarification):** the earlier doc's phrasing "`len(1) name len(4 LE) blob`"
is correct but easy to misread as `nameLen + blobLen + name + blob` — the blob length
comes **after** the name: `nameLen(1) + name + blobLen(4 LE) + blob`.

Inventory by category:

| category | count | content |
|---|---|---|
| `.png` | 970 | editor panel bitmaps |
| `SysXMap.ID*.bin` | 214 | raw parameter → SysEx address tables (§5) |
| `.ini` | 128 | 9 Block Setup files, 14 Combi Bank files, `Korg OASYS.ini`, `Patch.ini`, string lists |
| `.dll` | 114 | Win32 (57) + Win64 (57) MIDI Quest OASYS editor modules (`OASYS*.dll`) |
| `.dylib` | 55 | MacOSXCocoa editor modules |
| `.sqt` | 23 | editor templates (Patch.sqt 844,928 B, Combi.sqt 3,050,822 B, Wavesequence.sqt 2,217,443 B, …) |
| `.Bnk` | 41 | `DataForID<nnnn>.Bnk` bank-level editor data (one per editor/block-setup ID) |
| `.PCG` | 1 | `ALLBANKS.OASYS.PCG` (32,694,610 B) — the complete factory bank set (§7) |
| no extension | 10 | `Combi`, `DRUMS`, `Effect`, `GLOBAL`, `KarmaGE`, `Multi`, `Patch`, `SEQUENCE`, `SetList`, `WaveSeq` (editor data) |
| other | ~90 | `Patch.BkA..GG` / `Patch.IntA..` / `Patch.UserA..G`, `Combi.OASYS.*`, `*.UserA..G`/`IntA..G`/`OASYS` bank data, `Build Bank INI Files.bat` (a destructive MQ utility — "THIS WILL DESTROY THE BANK INIT INFORMATION" — not needed) |

---

## 3. `Korg OASYS.ini` — MIDI banks and program names (verified)

- `[BankKey]`: `NumBanks=11` — MSB121 LSB0–9 (ROM) + MSB120 LSB0 (user).
- Bank display names: `I-G (GM)`, `I-G (GM1)` … `I-G (GM9)`, `I-G (GMd)` — the ROM banks
  are GM-organized.
- 128 numbered program names per bank (`slot=N Name`), 1408 names total.

---

## 4. `Block Setup ID0.ini` — verified, with two corrections

- `Count=519`, 519 `BlockName` entries, 228 distinct names, 3 driver IDs — **all ✓**
  (earlier doc §4).
- Driver **5052** (KRONOS HD-1): 67 blocks, offsets 24..2774 (zone A + common only).
  Driver **5825** (KRONOS EXi): 227 blocks, 24..4961. Driver **8277** (OASYS): 225
  blocks, 24..4915.
- **CORRECTION:** the earlier doc's §4.1 table lists `EXi1 @2857 (1052 B)` under the
  5052 column — EXi1 is a **driver-5825** block; driver 5052 has no blocks beyond 2774
  (OSC1 zones). The offset/size themselves are correct.
- Driver 5825's EXi sub-block map = driver 8277's **+ 42 exactly** (e.g. Mod Mixer 1
  2868 vs 2826, MOD-7 EG1 3036 vs 2994, AL-1 OSC1 Pitch 3250 vs 3208) — the earlier
  doc's §4.3 table **✓** confirmed in full.
- All §4.1/§4.2 spot checks pass: Track EQ 2580/2568 (6 B), Tone Adjust 2586 (97 B),
  Drum Track Common 1292 (11 B), Drum Track 2688 (30 B), Pitch EG 2718 (26 B),
  Common LFO 2744/2676 (15 B), KARMA Common 1292 (510 B), KARMA Module 1802 (744 B),
  EXi1 2815 (1052 B). The KARMA cross-validation stands: MQ KARMA Module ends at 2545,
  exactly the byte-verified KARMA end.
- Other block setups: `ID5825.exi` = 294 ✓, `ID5825.old` = 200 ✓, `ID5857` = **383
  defined blocks** (header `Count=384` — off by one in the file itself), `ID5873` = 130 ✓,
  `ID8262` = 331 ✓, `ID8277` = 297 ✓, `ID8302` = 256 ✓, `ID8311` = 129 ✓.
  **CORRECTION:** the earlier doc said 384 blocks for ID5857; the actual defined-block
  count is 383.

---

## 5. `SysXMap.ID*.bin` — the raw parameter → SysEx address tables

Korg never published the OASYS SysEx parameter addresses; these 214 files are MIDI
Quest's own address tables. Format **✓** as documented earlier: IFF container
`FORM` + size + type `SYSX`, chunks `DESC` (4 B) + N × `DATA`. New findings below.

### 5.1 DESC = the DATA record count

Verified across all 214 files: the DESC value equals the number of DATA records
(128, 16, 32, 1, 256, 0, 40, 150, 2, 400, 1000 — see §5.3; 0 for the 11 empty files).

### 5.2 The SysEx frame grammar (precise)

- **Editor/global records** (68 B): `F0 42 <fam> 75 <ed> <pg> F7`
  — e.g. ID5052 (editor 5052): `f0 42 68 75 00 04 f7`; ID8262: `f0 42 70 75 01 02 f7`.
- **Parameter records** (82 B): `F0 42 <fam> 73 <addr_hi> <addr_lo> 00 <slot> <page> F7`
  — e.g. ID5036 record 0: `f0 42 68 73 01 40 00 00 03 f7`.
- `<fam>`: **0x68** = program/timbre family (editors 5035, 5052, 5087, 5825, 8189,
  5279–5281, …), **0x70** = combi/global family (8261, 8262, 8302, 8311 and their
  parameter files).
- **The `<slot>` byte increments 0..127 across a file's 128 records** — confirming the
  earlier doc's reading ("each `SysXMap.ID` file = one parameter, one record per program
  slot"): record k carries the SysEx frame addressing that parameter in slot k. Only 3
  bytes differ between consecutive records of ID5036: two index-table bytes and the slot
  byte (record offset 73).
- The 2-byte `<addr>` increments across consecutive IDs with wraparound (ID5036..5042 →
  0x0140..0x0146; ID5043..5049 → 0x0100..0x0106): **consecutive IDs = consecutive SysEx
  parameter addresses**.
- The base address (record +1..+4, 4-byte BE) is **constant per file** (187 files: 1
  distinct base; 16 files: 2). Clusters (files): 2919 (24), 1374 (23), 3954 (19),
  5680 (16), 8937 (15), 25200 (15), 43925 (15), 2544 (15), 12907 (14), 4244 (12),
  12912 (8), 4247 (5), 5253 (5), and singletons 48, 1371, 2541, 3951, 5632, 8934,
  12904, 12909, 25197, 28143, 28146, 28246, 43922, 79341, 79344.
  Editor files sit at **group base − 3**: 5052: 3951 = 3954−3; 5825: 4244 = 4247−3;
  5857: 43922 = 43925−3; 5873: 2541 = 2544−3; 8262: 12904 = 12907−3;
  8302: 12909 = 12912−3; 8311: 1371 = 1374−3; 5035: 8934 = 8937−3; 5281: 79341 = 79344−3.
- The worked example of the earlier doc §3 (ID5036: base 0x22E9, sub-address 0x22E8,
  index table 1,3,4,5,6,7,8,9,&lt;base−1&gt;,10, frame `F0 42 68 73 01 40 00 00 03 F7`) **✓**.

### 5.3 Record-count classes — what the N records mean

| records | rec size | files | IDs | meaning (identification) |
|---|---|---|---|---|
| 0 | — | 11 | 5066, 5322–5331 | empty placeholders (DESC=0; their bank data lives in `DataForID*.Bnk`) |
| 1 | 68 | 14 | 5035 5052 5067 5076 5087 5281 5825 5857 5873 8189 8261-8262 8302 8311 | editors / block setups / globals |
| 2 | 68 | 1 | 5050 | pair (with 5051) |
| 16 | 82 | 35 | 5069-5075 5343-5349 5859-5872 8304-8310 | 16-slot parameters (KARMA pads / scenes) |
| 32 | 82 | 35 | 5078-5084 5350-5356 5875-5888 8313-8319 | 32-slot parameters (step-seq steps) |
| 40 | 82 | 3 | 5068 5858 8303 | drum-kit bank (DBK1 = 40 kits ✓) |
| 128 | 82 | 85 | 5036-5049 5053-5065 5086 5267-5277 5279 5336-5342 5826-5831 8263-8276 8285-8290 8320-8331 | program/combi bank parameters, one per slot |
| 128 | 7052–7992 | 11 | 5832–5842 | per-slot **full dumps** (name + program data) — §6 |
| 150 | 82 | 3 | 5077 5874 8312 | wave-sequence bank (WBK1 = 150 ✓) |
| 256 | 78 | 14 | 5843–5856 | 2×128 — combi INT+USER pairs (ALLBANKS has 14 combi banks ✓, inferred) |
| 400 | 82 | 1 | 5051 | 400 — unidentified (multisamples?) |
| 1000 | 82 | 1 | 5280 | 1000 — unidentified (samples? base 48) |

### 5.4 ID-space structure

214 IDs, range 5035..8331: **5035–5356** (HD-1 program + EXi + effect + KARMA
families), **5825–5888** (EXi editor family), **8189–8331** (combi/global families).
Gaps: 5085, 5088–5266, 5278, 5282–5321, 5332–5335, 5357–5824, 5889–8188, 8190–8260,
8277–8284, 8291–8301.

**New finding: there is no `SysXMap.ID8277.bin`.** The OASYS program editor (8277) has
no SysXMap file, while both KRONOS editors (5052, 5825) do. The OASYS program
parameters live under the 50xx/53xx IDs (base clusters 3954, 5680, 8937, …). The
block-setup IDs with SysXMap files are 5825, 5857, 5873, 8262, 8302, 8311 (✓ as the
earlier doc said).

---

## 6. The per-slot dump records (ID5832..5842) — the factory names, cross-validated

11 files × 128 records of 7052–7992 B. Each record is the **complete SysEx dump of one
slot**: a name frame `F0 42 68 75 00 05 00 <21-byte space-padded name> …` followed by
the program data — including the zone records with ASCII `KORGMS` markers (the OASYS
SysEx dump carries the same KORG-MS family markers as the KRONOS; consistent with the
v1.6.3 converter's KORG-MS UUID zone mapping).

- The 11 files map 1:1, **in order**, to the 11 MIDI banks of `Korg OASYS.ini`:
  ID5832 = MSB121:LSB0 `I-G (GM)` … ID5841 = MSB121:LSB9, ID5842 = MSB120:LSB0
  `I-G (GMd)` (the GM drum bank — all kit names).
- The extracted names match the ini's program names **128/128 per bank** (1407/1408
  exact; one slot in `I-G (GM2)` differs) — a full internal cross-validation of the MQ
  config, and the names are the synth's own 21-character display names.
- Artifact: `tables/Oasys_factory_names.csv` (1408 rows: sysxmap_id, midi_bank,
  bank_name, slot, name).
- Note: the dump layout ≠ the PCG file layout (the earlier doc's §4.2 anomaly — the MQ
  8277 offsets address a SysEx-dump layout, not the file bytes). The dumps are still the
  authoritative per-slot content as the synth itself reports it.

---

## 7. `ALLBANKS.OASYS.PCG` — the complete factory bank set

32,694,610 B (the earlier doc's size ✓). Parses cleanly end-to-end with the chunk
grammar of §8. **43 banks:**

| chunk | banks | slots | slot size |
|---|---|---|---|
| PRG1 | 13 program banks — INT I-A..I-F + USER U-A..U-G | 128 each | **6174** |
| CMB1 | 14 combi banks (7 INT + 7 USER) | 128 each | **11288** |
| DKT1 | 8 drum-kit banks (1 INT × 40 + 7 USER × 16) | 40 / 16 | **11288** |
| WSQ1 | 8 wave-sequence banks (1 INT × 150 + 7 USER × 32) | 150 / 32 | **1192** |
| GLB1 | global | — | 24,618 B |

Plus `INI2` (3076 B) and `INI1` (2500 B) — PRODUCER.PCG has INI1 only.

Key contrasts with PRODUCER.PCG (slot sizes 4386 / 7766 / 11288 / 1192):

- ALLBANKS uses the **"big" (EXi-era) program slot of 6174 B** for all programs and pads
  combis to 11288 B. This corroborates the earlier doc's §12 open point (KNMOD7.PCG's
  6174-B MOD-7 slots): 6174 is a real OASYS slot size, not a KNMOD7 quirk.
- The bank header's bankId field reads **0x00020000** in ALLBANKS vs 0 in PRODUCER
  (a format/flags difference between the two files).
- Testing goldmine: 13 × 128 = 1664 programs (vs PRODUCER's 640 HD-1 + 256 MOD-7),
  14 combi banks, 8 wave-sequence banks. Note its program slots are 6174 B, so it is
  **not** slot-for-slot comparable with PRODUCER's 4386 B slots.

---

## 8. `PRODUCER.PCG` — verification + the precise chunk grammar

Every offset/size in the earlier doc §5 **✓** confirmed exactly:

| chunk | offset | contents |
|---|---|---|
| DIV1 | 0x1C | division header (size 44) |
| INI1 | 0x54 | init (size 888) |
| PRG1 | 0x3D8 | 5 × PBK1 (I-A..I-E) + 2 × MBK1 (I-F, U-F), 128 × 4386 B |
| CMB1 | 0x3BFB8C | 3 × CBK1, 128 × 7766 B |
| DKT1 | 0x697CE0 | 1 × DBK1, 40 × 11288 B |
| WSQ1 | 0x7060C4 | 1 × WBK1, 150 × 1192 B |
| GLB1 | 0x731B58 | global, 24,618 B |

The precise grammar (the earlier doc gave the bank-level layout only):

- **16-byte file header:** `KORG` + model byte (0x70 = OASYS) + version bytes
  (`00 02 00`) + zero padding.
- **12-byte chunk header:** `id(4) + size(4 BE) + stored(4 BE)`; the walk starts at 0x10
  with the `PCG1` container (its size covers the rest of the file; stored = 0x400);
  stride = 12 + size.
- **Containers:** PCG1, PRG1, CMB1, DKT1, WSQ1, SLS1, SLD1, STL1, ARP1 (children at +12).
- **Bank chunks:** 24-byte header `id(4) + size(4 BE) + bankId(4) + count(4) +
  slotSize(4) + subId(4)`; slots begin at chunk + 24; stride = 24 + count × slotSize;
  the size field reads stride − 12. `subId` carries the bank letter (INT: 0..6 =
  I-A..I-G; USER: 0x0002_0000.. = U-A..U-G).

---

## 9. `Patch.ini` — editors and templates (verified)

- Six `[Patch Init]` editors, all ControlID 4499: **5052 HD-1** (TableID 2), **5825 HD-1**
  (3), **5052 EXi** (1), **5825 EXi** (1), **8277 HD-1** (4), **8277 EXi** (5).
- `[Template List]`: 13 editor templates (`Patch.exi`, `Effect`, `Karma.Common`,
  `Karma.Parts`, `Patch.Common`, `Patch.AL-1/CX-3/STR-1/MS-20/Poly6/MOD-7/SGX-1/EP-1`
  .sqt); the HD-1 editor uses 4 of them, the EXi editor 12.
- `[Parameter Select List]` comments give per-template numbers (HD-1=1450, EXi=550,
  Effect=4100, Karma Common=700, Karma Parts=3900, Patch Common=600, AL-1=750, CX-3=200,
  STR-1=850, MS-20=700, Poly-6=450, MOD-7=1400, SGX-1=100, EP-1=400) — likely parameter
  counts per template; not yet tied to SysXMap IDs.

---

## 10. What this yields for pcglib

- **The SysXMap tables are the raw OASYS SysEx parameter addresses Korg never
  published** — the path to SysEx-level features (OASYS parameter display, MIDI remote
  control). The frame grammar (§5.2) is enough to build a parameter read/write:
  `F0 42 68 73 <addr_hi> <addr_lo> 00 <slot> <page> F7` per slot.
- **The name-dump records give the complete factory name list** (1408 names,
  cross-validated against the ini) — saved as `tables/Oasys_factory_names.csv`.
- **ALLBANKS.OASYS.PCG is a much larger test corpus than PRODUCER.PCG** (43 banks,
  big-slot format) — for converter testing, keeping in mind its 6174-B program slots.
- The OASYS SysEx dumps carry `KORGMS` zone markers — consistent with the KRONOS
  KORG-MS UUID family used by the v1.6.3 converter map.
- **Corrections to the earlier doc:** EXi1 is a 5825-driver block (not 5052); ID5857 has
  383 defined blocks (header Count=384); the .sqz entry layout is
  `nameLen + name + blobLen + blob`; no `SysXMap.ID8277` exists.
- **Open points:** (a) the parameter **name ↔ SysXMap ID** mapping is not in the .bin
  files — it lives in the .sqt editor templates (BLCK panels), not yet parsed; (b) the
  400- and 1000-record files (ID5051, ID5280) are unidentified (multisamples/samples?);
  (c) the 256-record files (5843–5856) are presumably combi INT+USER pairs; (d) the
  base-address clusters' meaning (bank-dump vs current-parameter space) is not fully
  resolved; (e) the MQ 8277 common-tail anomaly stands (earlier doc §4.2).

## 11. Files produced / reproducibility

- This document; `tables/Oasys_SysXMap_summary.csv`; `tables/Oasys_factory_names.csv`.
- The `.sqz` is gitignored (`*.sqz`, `docs/oasys/Korg OASYS/`). The extracted working
  copy lives in the session temp dir (`%TEMP%\pcglib-sqz\extracted`) — re-extract with
  the ~20-line parser of §2 if needed; the analysis scripts (block-setup parser, SysXMap
  parser, name extractor, PCG walker, table generators) live next to it.
