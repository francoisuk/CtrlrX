# Oasys — what a future Ctrlr panel would need

**Rewritten for the ctrlr-project from pcglib knowledge (v1.6.3, commit
`c2af0f2`).** Notes for building an Oasys panel like Kronos Kontrol, after the
Kronos one. Everything stated here is sourced from the copies in this folder;
the two load-bearing documents are `docs/OASYS_SQZ_ANALYSIS.md` (the SysEx
address tables) and `docs/OASYS_PARAMETER_MAP.md` (the byte-level Oasys↔Kronos
map).

## 1. The instrument in one paragraph

The Oasys (2007) is Korg's PCI workstation: HD-1 + the eight EXi engines
(AL-1, CX-3, EP-1, MOD-7, MS-20EX, PolysixEX, SGX-1, STR-1) and KARMA — the
same engine families as the Kronos, at different byte offsets. pcglib converts
Kronos ↔ Oasys PCG files (v1.6.3), which is how its format is known byte-exactly.

## 2. The key discovery: the SysXMap tables

**Korg never published the Oasys SysEx parameter addresses.** The MIDI Quest
`Korg OASYS.sqz` config contains 214 `SysXMap.ID*.bin` files that are the raw
parameter → SysEx address tables. pcglib extracted and summarised them:

- `tables/Oasys_SysXMap_summary.csv` — one row per SysXMap file (214 rows):
  record count/size, base addresses, the record-0 SysEx frame, DESC value.
- `docs/OASYS_SQZ_ANALYSIS.md` §5 — the full grammar.

### Frame grammar (analysis §5.2)

- Editor/global records (68 B): `F0 42 <fam> 75 <ed> <pg> F7`
  (e.g. editor 5052: `f0 42 68 75 00 04 f7`).
- Parameter records (82 B): `F0 42 <fam> 73 <addr_hi> <addr_lo> 00 <slot> <page> F7`
  (e.g. ID5036 record 0: `f0 42 68 73 01 40 00 00 03 f7`).
- `<fam>`: **0x68** = program/timbre family, **0x70** = combi/global family.
- `<slot>` increments 0..127 across a file's 128 records: **one SysXMap file =
  one parameter, one record per program slot** — record k addresses that
  parameter in slot k. A parameter read/write is therefore a single frame:
  `F0 42 68 73 <addr_hi> <addr_lo> 00 <slot> <page> F7`.
- Consecutive IDs = consecutive SysEx addresses; the base address (4-byte BE at
  record +1..+4) is constant per file; editor files sit at group base − 3.

### What the record counts mean (analysis §5.3)

| records | rec size | meaning |
|---|---|---|
| 0 | — | empty placeholders (bank data lives in `DataForID*.Bnk`) |
| 1 | 68 | editors / block setups / globals |
| 2 | 68 | pair (with 5051) |
| 16 | 82 | 16-slot parameters (KARMA pads / scenes) |
| 32 | 82 | 32-slot parameters (step-seq steps) |
| 40 | 82 | drum-kit bank (DBK1 = 40 kits) |
| 128 | 82 | program/combi bank parameters, one per slot |
| 128 | 7052–7992 | per-slot **full dumps** (name + program data) |
| 150 | 82 | wave-sequence bank (WBK1 = 150) |
| 256 | 78 | 2×128 — combi INT+USER pairs (inferred) |
| 400 / 1000 | 82 | unidentified (multisamples / samples?) |

### ID-space structure (analysis §5.4)

214 IDs, range 5035..8331: **5035–5356** HD-1 program + EXi + effect + KARMA
families, **5825–5888** EXi editor family, **8189–8331** combi/global
families. There is **no `SysXMap.ID8277.bin`** — the Oasys program editor
(8277) has no SysXMap file; Oasys program parameters live under the 50xx/53xx
IDs.

## 3. Banks and factory names

- 11 MIDI banks (`Korg OASYS.ini` `[BankKey] NumBanks=11`): MSB121 LSB0–9 (ROM,
  GM-organised: `I-G (GM)`, `I-G (GM1)` … `I-G (GM9)`, `I-G (GMd)`) +
  MSB120 LSB0 (user).
- `tables/Oasys_factory_names.csv` — the **1408 factory slot names**, extracted
  from the per-slot dump records and cross-validated against the ini
  (1407/1408 exact). Columns: `sysxmap_id, midi_bank, bank_name, slot, name`.
  These are the synth's own 21-character display names.

## 4. Oasys PCG format essentials (for a librarian/editor part)

From `docs/OASYS_SQZ_ANALYSIS.md` §7–8 and `docs/OASYS_PARAMETER_MAP.md` §5:

- `PRODUCER.PCG` (7,568,270 B): program slots **4,386 B**, combi **7,766 B**,
  drum kit **11,288 B**, wave seq **1,192 B**, Global 24,618 B.
- `ALLBANKS.OASYS.PCG` (32,694,610 B): 43 banks, program slots **6,174 B**
  (the "big" EXi-era slot), combis padded to 11,288 B.
- Chunk grammar: 16-byte file header (`KORG` + model byte **0x70** + `00 02 00`),
  12-byte chunk header `id(4) + size(4 BE) + stored(4 BE)`, bank chunks with a
  24-byte header `id + size + bankId + count + slotSize + subId`; `subId`
  carries the bank letter (INT 0..6 = I-A..I-G; USER 0x00020000.. = U-A..U-G).
  Containers: PCG1, PRG1, CMB1, DKT1, WSQ1, SLS1, SLD1, STL1, ARP1.

## 5. Oasys ↔ Kronos parameter map (docs/OASYS_PARAMETER_MAP.md, 15 sections)

The byte-verified correspondences a panel/converter needs:

- HD-1 program slot: Oasys **4,386 B** ↔ Kronos **4,960 B**.
- Per-oscillator block: **288 B** ↔ **466 B**; zone record **6 B** ↔ **22 B**.
- Combi slot: **7,766 B** ↔ **7,810 B**; trigger tail **12 B** ↔ **26 B**.
- EXi section: **Oasys offsets = Kronos offsets − 42** exactly.
- Editor cross-validation anchor: MQ editor **5052 = Kronos HD-1 layout**,
  **8277 = Oasys layout**, **5825 = Kronos EXi layout**.
- KRONOS-only sections are injected with factory defaults on O→K.

## 6. Editors and templates (analysis §9)

Six `[Patch Init]` editors (ControlID 4499): 5052 HD-1, 5825 HD-1, 5052 EXi,
5825 EXi, 8277 HD-1, 8277 EXi. Parameter counts per template (from
`[Parameter Select List]` comments): HD-1 = 1450, EXi = 550, Effect = 4100,
Karma Common = 700, Karma Parts = 3900, Patch Common = 600, AL-1 = 750,
CX-3 = 200, STR-1 = 850, MS-20 = 700, Poly-6 = 450, MOD-7 = 1400, SGX-1 = 100,
EP-1 = 400.

## 7. Open points (analysis §10 — do not treat as solved)

1. The **parameter name ↔ SysXMap ID** mapping is not in the `.bin` files — it
   lives in the `.sqt` editor templates (BLCK panels), not yet parsed.
2. ID5051 (400 records) and ID5280 (1000 records) are unidentified.
3. The 256-record files (5843–5856) are presumably combi INT+USER pairs.
4. The base-address clusters' meaning (bank-dump vs current-parameter space)
   is not fully resolved.
5. The MQ 8277 common-tail anomaly stands (the 8277 offsets address a
   SysEx-dump layout, not the PCG file bytes).

## 8. Licensing

The `.sqz` is a Sound Quest / MIDI Quest commercial product. The analysis was
for personal, non-commercial use; **only facts** (offsets, sizes, names,
addresses) are recorded here. The `.sqz` itself is not in this folder and must
not be redistributed. If this document is shared, `docs/OASYS_SQZ_ANALYSIS.md`
§1 must travel with it.

## 9. Where the rest lives

- `midi/OASYS_MIDI_implementation.pdf` — Korg's Oasys MIDI implementation (the
  SysEx authority; copied here).
- pcglib `docs/oasys/` — `OASYS_Param_Guide_v1_3_E5.pdf`,
  `OASYS_Op_Guide_v1_3_E5.pdf`, `OASYS_VNL_v1_2_EJ3.pdf`,
  `OASYS_VNL_v1_3_EJ4.pdf`, `OASYS_Introductory_Tour.pdf`, `CX3_EXi_GT.pdf`,
  `Classic_EX_ST_M3_OASYS_ Loading_Saving_SEQ.pdf`.
- pcglib `factory/OASYS/KORG Factory New/PRODUCER.PCG` — reference file.
- `docs/KRONOS_OASYS_V163_FIX.md` — the v1.6.3 conversion fixes (what was
  wrong, what is still open).
- `docs/ABOUT_THE_CONVERSION_FROM_KRONOS_TO_OASYS.md` — the user-facing
  overview of the K→O conversion and its report text.
