# HD-1 Parameter Offset Mapping — v5 (KRONOS) vs v6 (NAUTILUS)

**Project:** kronos-pcglib
**Task:** Task 1 — Parameter offset mapping for HD-1 v5 and v6
**Date:** October 17, 2026
**Status:** Complete
**Data sources:** `factory/OS3.2/FACTORY/PRELOAD.PCG`, `factory/OS3.1/PRELOAD.PCG`, `factory/NAUTILUS/PRELOAD.PCG`
**Scripts:** `scripts/check_bank_alignment.py`, `scripts/map_hd1_parameters.py`, `scripts/analyze_hd1_sections.py`, `scripts/test_hd1_shift.py`, `scripts/test_hd1_boundary.py`
**Machine-readable output:** `tables/HD1_param_offsets_v5_v6.csv`, `tables/HD1_v5_to_v6_zone_map.csv`

---

## Executive summary

The HD-1 program record ("fiche") of NAUTILUS (v6) is **identical to KRONOS (v5) for the
first 1292 bytes** (0–1291), then diverges. **KARMA is completely absent from NAUTILUS**
(it exists only on KRONOS): the 1254-byte KARMA block is replaced by a 1248-byte NAUTILUS
block, and **every section after that block sits exactly 6 bytes earlier** in v6 than in
v5. Each instrument also has its own undocumented tail block.

**Correction (v1.6.2):** bytes 1292–1303 are **not** identical. On the KRONOS they are the
Drum Track Common (tables/Programme_HD-1.csv); on the NAUTILUS they are the **RT
Controller** (Mode + Knob 1 settings, docs/nautilus/NAUTILUS_MIDIimp/SysExDumps/
Prog_HD-1.txt) — the NAUTILUS drum track lives in zone B instead (see §4.1 and
docs/NAUTILUS_TO_KRONOS_V162_FIX.md). The earlier "identical through 1303" claim came
from cross-checking the KRONOS fiche tables against NAUTILUS factory data whose RT
Controller bytes happen to satisfy the Drum Track Common constraints too.

| Zone | KRONOS v5 offset | NAUTILUS v6 offset | Content | v5/v6 status |
|---|---|---|---|---|
| A | 0–1291 | 0–1291 | Name, Common, IFX1–12, MFX1–2, TFX1–2, Effect LFOs, Vector Control, Controller, Audio Input 1–4, S/PDIF L/R | **Identical** (same offsets) |
| A' | 1292–1303 | 1292–1303 | v5: Drum Track Common. v6: RT Controller (Mode, Knob 1) | **Same offsets, different content** (v1.6.2 correction) |
| B | 1304–2557 | 1304–2551 | v5: KARMA Common + KARMA Module (1254 B). v6: NAUTILUS block (1248 B), Arpeggiator-related | **Incompatible** (different content, v6 block 6 B shorter) |
| C | 2558–3704 | 2552–3698 | Assignable Controller, Track EQ, Tone Adjust, OSC1 + OSC2 sections (incl. mod mixers) | **Identical, shifted −6** (v6 = v5 − 6) |
| D | 3705–3945 | — | Undocumented KRONOS tail (present in 384/1152 factory programs) | v5-only |
| E | — | 3699–4953 | Undocumented NAUTILUS tail (present in 512/1280 factory programs, max extent byte 4950) | v6-only |

Slot sizes: KRONOS 4960 bytes, NAUTILUS 4954 bytes (6-byte difference = zone B size
difference; padding absorbs the rest).

---

## 1. Corrections to earlier findings (IMPORTANT)

This document supersedes parts of `docs/HD1_PROGRAM_STRUCTURE_FINDINGS.md`. The
earlier analysis sliced PBK1 chunk data in fixed 4960-byte slots starting at offset 0,
which is misaligned by 12 bytes. What it interpreted as a program prefix was in fact the
**bank chunk header**:

- `00 00 00 80 00 00 13 60` (KRONOS) = count=128, slot_size=0x1360 (4960)
- `00 00 00 80 00 00 13 5A` (NAUTILUS) = count=128, slot_size=0x135A (4954)

Therefore:

1. The "7-byte prefix 00 00 00 80 00 00 13" is **not a program prefix** — bytes 0–3
   are the program count (0x80 = 128) and bytes 4–7 the slot size. The mysterious
   "0x13" byte is simply the high byte of the slot size (0x1360 / 0x135A).
2. The "instrument identifier byte 7" (0x60 KRONOS vs 0x5A NAUTILUS) is the **low
   byte of the slot size** (4960 vs 4954) — a format-version size difference, not an
   instrument flag.
3. "Byte 10 = 0x80" is part of the bank ID (NAUTILUS first PBK1 bank id = 0x8000).
4. The program name starts at **bank-data offset 12** (i.e. the first slot), and each
   slot begins with the 24-byte name — exactly the layout used by `scripts/pcg.py`
   and `scripts/kprog.py`.
5. The v6 record is **not** "3700 useful bytes": v6 content extends to byte 4950 in
   factory programs (zone E).

**Bank chunk layout (both instruments):**

```
PBK1 chunk data:
  bytes 0-3   : program count (uint32 BE, = 128)
  bytes 4-7   : slot size (uint32 BE; 4960 v5 / 4954 v6)
  bytes 8-11  : bank id (uint32 BE; see bank-id table below)
  bytes 12-   : count slots of slot_size bytes; each slot starts with the
                24-byte program name, parameters follow per
                tables/Programme_HD-1.csv (fiche offset = slot offset)
```

Factory bank IDs observed:

| Instrument | Chunk | Bank IDs |
|---|---|---|
| KRONOS OS 3.2 | PBK1 (HD-1) | 0x1, 0x20002–0x20005, 0x20007, 0x20008, 0x2000A, 0x2000B (9 banks) |
| KRONOS OS 3.1 | PBK1 (HD-1) | 0x1, 0x20002–0x20005, 0x20007, 0x20008 (7 banks) |
| NAUTILUS | PBK1 (HD-1) | 0x8000, 0x20000–0x20008 (10 banks) |

PCG headers: KRONOS `4B4F5247 68 00 02 02`, NAUTILUS `4B4F5247 DD 00 02 03` (KORG,
model byte 0x68/0xDD, then 00 02 0x?).

---

## 2. Method

All 2541 declared parameter rows of `tables/Programme_HD-1.csv` (Korg MIDI
implementation table for the HD-1 fiche, offsets 0–3704, bit-exact pieces, signed ranges
in two's complement) were verified against every HD-1 factory program:

- KRONOS OS 3.2: 1152 programs (9 banks)
- KRONOS OS 3.1: 896 programs (7 banks) — drift check
- NAUTILUS: 1280 programs (10 banks)

For each parameter the observed min/max across all programs was computed with the
declared bit extraction, converted to signed where the declared range is signed, and
compared to the declared range. Full results: `tables/HD1_param_offsets_v5_v6.csv`.

---

## 3. Results — KRONOS v5

**OS 3.1 vs OS 3.2: no layout drift.** Verification outcomes are near-identical; no
section moved between 3.1 and 3.2. The HD-1 fiche table applies to both.

Out of 2541 rows (per dataset): 1890 OK, 154 UNVERIFIED (declared range not
machine-parseable), 9 EXCEEDS, remainder fixed-value checks.

### 3.1 Declared-range issues found (table predates OS 3.x)

| Location | Declared | Observed (OS 3.1/3.2) | Note |
|---|---|---|---|
| IFX1–5, MFX1 Effect Type (fiche 88, 162, 236, 310, 384, 976) | 00~B9 (0–185) | up to 195 (0xC3) | OS 3.x added effect types; extend the range and cross-check `tables/Effets.json` |
| KARMA Common (Dynamic MIDI 3) Polarity (fiche 1352:3-4) | 00~01 | 0–2 | OS 3.x KARMA extension |
| KARMA Module Start Seed (fiche 1840:0-7 + 1841 + 1842 + 1843) | `80000000~7FFF` | — | Declared range is malformed in the source table (hi bound truncated to 4 digits) |
| Common Swing (fiche 2578:0-7 + 2579:0-1) | FED4~012C (−300..300) | exceeds | 10-bit field; verify against Drum Track swing documentation |

### 3.2 Uncovered fiche bytes

1354 of 3706 fiche bytes are not covered by `Programme_HD-1.csv`:

- **24–87**: undocumented gap between the name and IFX1.
- **Per-IFX parameter payload** (e.g. 97–161, 165, 171–235, …): the 32 effect
  parameters of each IFX are effect-type-dependent and are covered by
  `tables/Effets.json` keyed on effect type — not by the HD-1 fiche table.
- Scattered single bytes (reserved/padding) through the OSC sections.

---

## 4. Results — NAUTILUS v6

### 4.1 Zone A (bytes 0–1291): identical to KRONOS

All sections from Name through S/PDIF L/R verify at the same offsets with the
same declared constraints. Only exceptions are two Effect Type fields
(IFX10 at 754, TFX1 at 1116) whose observed values go up to 197 (0xC5) — NAUTILUS
effect list extends beyond KRONOS 3.2's observed maximum.

**Bytes 1292–1303 are the exception that proves the rule (v1.6.2 correction):**
the KRONOS keeps its **Drum Track Common** there (Pattern Number LE16 0..999,
Pattern Bank, Trigger Button/Latch/Sync modes, Drum Track On, trigger key/velocity
zones, Shift, Output/Input MIDI channel — tables/Programme_HD-1.csv,
Programme_EXi_commun.csv, Combinaison.csv), while the NAUTILUS keeps its **RT
Controller** there (Mode at 1292, Knob 1 Target/RT Control/Mixer Control at
1296/1298/1299, mixer channel enables at 1300–1301, Knob 2 Target at 1302 —
docs/nautilus/NAUTILUS_MIDIimp/SysExDumps/Prog_HD-1.txt, Prog_EXi_Common.txt,
CombiAndSongTimbreSet.txt). The NAUTILUS drum track itself lives in **zone B**
(scene common at 1348–1378, per-scene drum fields in the scene records at 2440,
stride 28 for programs / 44 for combis). An identity copy of 1292..1303 therefore
writes RT Controller bytes into the KRONOS Drum Track Common (inverted trigger
zones, garbage pattern number) — the beta-tester bug fixed in v1.6.2: the
NAUTILUS -> KRONOS converter now **rebuilds** the Drum Track Common from the zone B
scene data (docs/NAUTILUS_TO_KRONOS_V162_FIX.md). The NAUTILUS RT Controller
settings have no KRONOS equivalent at these offsets and are dropped.

### 4.2 Zone B (bytes 1304–2551): KARMA is absent — NAUTILUS block instead

The KARMA function **does not exist on NAUTILUS at all** (confirmed by the user; the
data agrees). The KRONOS KARMA Common (1304–1813) + KARMA Module (1814–2557) block —
1254 bytes — is replaced by a **1248-byte NAUTILUS block at 1304–2551**. Evidence:

- 416 parameter rows exceed their declared ranges when read at KRONOS offsets —
  all inside KARMA sections.
- 276 fixed-value parameters disagree (KARMA Module Control, Dynamic MIDI fixed
  fields, Chord Pad MIDI channel, KARMA Module I/O MIDI channels, Scene fader
  defaults, Run GE) — all inside KARMA sections. Zero such mismatches anywhere else.
- No shift of the KARMA region reprodu KARMA-compatible data (tested −1300..+1300);
  the block is genuinely different content, not moved KARMA data.
- Factory NAUTILUS content in this zone shows constant 16-bit values
  0x0810–0x0815 at 6-byte intervals — candidate: Arpeggiator/related settings
  (to be decoded in a follow-up; NAUTILUS arpeggiator patterns live in ABK1 chunks).

### 4.3 Zone C (bytes 2552–3698): KRONOS layout shifted by −6

A full shift scan (−1300..+1300, 834 constrained parameter rows in 2572–3704) gives:

| Shift | Rows within declared range |
|---|---|
| **−6** | **99.9 %** |
| next best (~−1277 etc.) | ≈96.9 % (coincidence from wide ranges) |

Seam check at the zone B/C boundary: per-byte value statistics of KRONOS 2560–2566
match NAUTILUS 2554–2560 exactly. **v6 offset = v5 offset − 6 for all of
KRONOS 2558–3704.**

### 4.4 Zones D and E: instrument-specific undocumented tails

- KRONOS: bytes 3705–3945 carry content in 384/1152 factory programs.
- NAUTILUS: bytes 3699–4953 carry content in 512/1280 factory programs
  (361 within 3707–3940, 80 within 3941–4500, 71 beyond 4500; deepest extent byte
  4950). The byte-activity patterns of the two tails do **not** correspond at −6 —
  they are different data. Candidates: per-program Drum Track pattern / Arpeggiator /
  Step Sequencer data (open question, see §7).

---

## 5. v5 → v6 translation rules (for PCG Tools)

```csharp
// HD-1 program conversion, KRONOS v5 fiche -> NAUTILUS v6 fiche
const int ZoneA_End = 1304;          // identical: copy v5[0..1303] -> v6[0..1303]
const int ZoneB_v5_End = 2558;       // v5 KARMA: drop entirely (function absent)
const int ZoneB_v6_End = 2552;       // v6 block: initialise from NAUTILUS default
const int ZoneC_v5_End = 3705;       // shifted: v6[i - 6] = v5[i] for 2558..3704
// v5 tail 3705..3945 (zone D): drop
// v6 tail 3699..slot_end (zone E): initialise from NAUTILUS default
```

- Slot sizes come from the **bank header**, never hard-coded (4960 v5 / 4954 v6 today).
- Checksums must be recomputed after any edit
  (`docs/CHECKSUM_ALGORITHM_VERIFICATION.md`).
- A NAUTILUS default program template (for zones B and E initialisation) should be
  extracted from a factory "Init HD-1" program — open item.

---

## 6. Effect type ranges

| Dataset | Max observed Effect Type |
|---|---|
| KRONOS OS 3.1 | 195 (0xC3) |
| KRONOS OS 3.2 | 195 (0xC3) |
| NAUTILUS | 197 (0xC5) |

The declared 00~B9 (185 effects) predates OS 3.x. The effect-type parameter ranges and
`tables/Effets.json` need extending; exact OS 3.2 / NAUTILUS effect lists to be
cross-checked against the Korg OS 3.2 MIDI documentation.

---

## 7. Open questions

1. Decode NAUTILUS zone B (1304–2551): presumed Arpeggiator settings block.
2. Identify KRONOS zone D (3705–3945) and NAUTILUS zone E (3699–4953) tail contents.
3. Fiche bytes 24–87 (undocumented gap after the name).
4. NAUTILUS bank-id semantics (0x8000 base vs KRONOS 0x1/0x20002+ scheme) — Task 2.
5. Effect type lists for OS 3.2 (to 0xC3+) and NAUTILUS (to 0xC5+).
6. Malformed declared ranges in the source table (Start Seed; verify Swing).

---

## 8. Reproducing

```bash
python scripts/check_bank_alignment.py     # bank layout verification
python scripts/map_hd1_parameters.py       # writes tables/HD1_param_offsets_v5_v6.csv
python scripts/analyze_hd1_sections.py    # section map + tail analysis
python scripts/test_hd1_shift.py          # shift scan (zone C = -6)
python scripts/test_hd1_boundary.py       # zone boundary checks
```
