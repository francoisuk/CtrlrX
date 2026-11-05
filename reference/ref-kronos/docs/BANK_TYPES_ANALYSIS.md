# Bank Types Analysis — KRONOS OS 3.2 vs NAUTILUS

**Project:** kronos-pcglib
**Task:** Task 2 — Analyze other bank types (MBK1, CBK1, DKT1, ABK1, WBK1)
**Date:** October 17, 2026
**Status:** Complete
**Data sources:** `factory/OS3.2/FACTORY/PRELOAD.PCG`, `factory/NAUTILUS/PRELOAD.PCG`
**Scripts:** `scripts/analyze_bank_types.py`, `scripts/analyze_bank_types2.py`

---

## Executive summary

All bank chunks follow the same physical layout confirmed for PBK1 in Task 1:
**chunk data = 12-byte bank header (count, slot_size, bank_id) + count slots of
slot_size bytes, each slot starting with the object name.** The HD-1 v5/v6 zone
model (identical head / NAUTILUS block replacing KARMA / shifted tail) applies to
EXi programs with shift **−6** and to combinations with shift **−2170**.

| Chunk | Content | KRONOS 3.2 | NAUTILUS | Slot size v5 → v6 |
|---|---|---|---|---|
| PBK1 | HD-1 program banks | 9 banks × 128 | 10 banks × 128 | 4960 → 4954 |
| MBK1 | EXi program banks | 8 banks × 128 (1024) | 5 banks × 128 (640) | 4960 → 4954 |
| CBK1 | Combination banks | 6 banks × 128 (768) | 2 banks × 128 (256) | 7810 → 5640 |
| DBK1 (in DKT1) | Drum kit banks | 4 banks: 40 + 16+16+16 (88 kits) | 5 banks: 40 + 16×4 (104 kits) | 38424 (same) |
| WBK1 (in WSQ1) | Wave sequence banks | 3 banks: 150 + 32 + 32 | 9 banks: 150 + 32×8 | 2216 (same) |
| ABK1 (in ARP1) | Arpeggio patterns | — (no ARP1) | 1 bank: 2048 × 556 | — (NAUTILUS-only) |

**KARMA is absent from NAUTILUS in every object type.** Programs and combinations
both replace their KARMA sections with a NAUTILUS block; everything after it is
byte-identical to KRONOS, shifted earlier by the size difference.

---

## 1. Chunk tree (factory PRELOAD.PCG)

```
KRONOS OS 3.2                       NAUTILUS
PCG1                                PCG1
├── DIV1  (44 bytes)                ├── DIV1  (52 bytes)
├── SLS1  (set lists)               ├── SLS1  (set lists)
│   ├── SLD1 (462,360)              │   ├── SLD1 (462,360)
│   └── STL1 (8,885,272)            │   └── STL1 (8,901,656)
├── PRG1  (programs)               ├── PRG1  (programs)
│   ├── PBK1 ×9, MBK1 ×8            │   ├── MBK1 ×5, PBK1 ×10
├── CMB1  (combinations)            ├── CMB1  (combinations)
│   └── CBK1 ×6                     │   └── CBK1 ×2
├── DKT1  (drum kits)               ├── DKT1  (drum kits)
│   └── DBK1 ×4                     │   └── DBK1 ×5
├── WSQ1  (wave sequences)          ├── ARP1  (arpeggiator — NAUTILUS only)
│   └── WBK1 ×3                     │   └── ABK1 ×1 (2048 patterns)
└── GLB1  (global, 24,708)          ├── WSQ1  (wave sequences)
                                     │   └── WBK1 ×9
                                     └── GLB1  (global, 24,706)
```

---

## 2. Bank IDs (factory PRELOAD.PCG)

| Chunk | KRONOS OS 3.2 bids | NAUTILUS bids |
|---|---|---|
| PBK1 | 0x1, 0x20002, 0x20003, 0x20004, 0x20005, 0x20007, 0x20008, 0x2000A, 0x2000B | 0x8000, 0x20000–0x20008 |
| MBK1 | 0x0, 0x2, 0x3, 0x4, 0x8000, 0x20000, 0x20001, 0x20009 | 0x0, 0x1, 0x2, 0x3, 0x4 |
| CBK1 | 0x0–0x5 | 0x0, 0x1 |
| DBK1 | 0x0, 0x20000, 0x20001, 0x20002 | 0x0, 0x20000, 0x20001, 0x20002, 0x20003 |
| WBK1 | 0x0, 0x20000, 0x20005 | 0x0, 0x20000–0x20007 |
| ABK1 | — | 0x0 |

Bank ID semantics differ between instruments (e.g. NAUTILUS uses 0x8000 for its
first HD-1 bank where KRONOS uses 0x8000 for a user EXi bank). PCG Tools needs
per-instrument bank-id ↔ UI-bank mapping tables.

---

## 3. MBK1 — EXi programs (v5/v6 layout)

Slot 4960 (v5) / 4954 (v6), 128 per bank. Engine IDs at fiche bytes **2857 (EXi1)
and 3909 (EXi2)** in v5, and **2851 / 3903** in v6 (the −6 shift).

Engine histograms (factory): KRONOS 1024 EXi programs, NAUTILUS 640.

**The HD-1 zone rule applies unchanged to EXi programs:**

| Region | v5 offsets | v6 offsets | Verification |
|---|---|---|---|
| Zone A (Name, Common, IFX, MFX, TFX, LFO, Vector, Controller, Audio In, S/PDIF, Drum Track Common) | 0–1303 | 0–1303 (identity) | 98.9 % OK |
| Zone B (KARMA) | 1304–2557 | 1304–2551 (NAUTILUS block) | replaced (KARMA absent) |
| Zone C (Assignable Controller, Track EQ, Tone Adjust, EXi common, engine blocks) | 2558–4959 | 2552– (−6) | 99.4 % OK |

EXi common table verification: KRONOS @0 = 1235/1245 OK (99.2 %); NAUTILUS with the
zone rule = 629/634 OK (99.2 %).

### 3.1 Engine model blocks — layout confirmed, declared ranges outdated

Per-engine tables (`tables/Moteur_*.csv`) verify at only 56–77 % on **both**
instruments (NAUTILUS tracks KRONOS at the same −6 offsets, so the layout is
right). Failures are range overshoots of a consistent shape — e.g. AL-1
`LFO1 Frequency` declared 00~63 (0–99) observed to 119, `MIDI Sync Base Note`
declared 0–9 observed 0–15, mod source IDs declared 00~34 (0–52) observed to 247 —
i.e. **the engine tables predate OS 3.x parameter extensions**. They must be
rebuilt from the OS 3.2 MIDI documentation before use as validation; as offset
maps they appear correct.

---

## 4. CBK1 — Combinations (v5/v6 layout)

Slot 7810 (v5) / 5640 (v6), 128 per bank.

| Region | v5 offsets | v6 offsets | Content |
|---|---|---|---|
| Zone A | 0–1303 | 0–1303 (identity) | Name, Common, IFX, MFX, TFX, LFOs, Vector, Controller, Audio In, S/PDIF, Drum Track Common |
| Zone B | 1304–4789 (3486 B) | 1304–2619 (1316 B) | v5: KARMA Common + KARMA Modules A–D; v6: NAUTILUS block |
| Zone C | 4790–7809 | 2620–5639 (**shift −2170**) | Assignable Controller + Timbres 1–16 |

Verification: combi tail (rows ≥ 4790) — KRONOS @0 = 2753/2801 OK; NAUTILUS @−2170
= **2753/2801 OK** (identical). Timbre 1/8/16 sections each 171/174 on both.
Timbre 16 ends exactly at byte 5639, the last byte of the v6 slot.

Translation rule: **v6 offset = v5 offset − 2170 for v5 offsets ≥ 4790**; drop the
KARMA sections; NAUTILUS block initialised from a default combi (open item).

---

## 5. DKT1 / DBK1 — Drum kits

DKT1 is a **container**; inside are DBK1 bank chunks with the standard
header (count, slot_size, bank_id) and **slot size 38424 bytes** per kit.

- KRONOS: bank 0x0 (40 kits) + 0x20000–0x20002 (16 each) = **88 kits**
- NAUTILUS: bank 0x0 (40 kits) + 0x20000–0x20003 (16 each) = **104 kits**

Kit names sit at slot offset 0 (24 bytes). Kit record internals (38,424 bytes:
128 keys × samples/levels/tuning) are not yet mapped — open item.

---

## 6. ARP1 / ABK1 — Arpeggiator (NAUTILUS only)

The NAUTILUS PCG adds an **ARP1 container** with one **ABK1** bank:
**2048 patterns × 556 bytes**, bid 0x0, all slots non-empty, 24-byte name at
slot offset 0 ("OFF 4/4", "OFF 3/4", …, "Init Arp Pattern").

KRONOS has no ARP1 chunk — it uses KARMA instead. Pattern record internals
(556 bytes) are not yet mapped — open item.

---

## 7. WSQ1 / WBK1 — Wave sequences

Standard bank layout, **slot 2216 bytes** on both instruments:

- KRONOS: bid 0x0 (150 wave seqs) + 0x20000, 0x20005 (32 each)
- NAUTILUS: bid 0x0 (150) + 0x20000–0x20007 (32 each, 9 banks total)

Same format both instruments; factory content differs.

---

## 8. Implementation notes for PCG Tools

```csharp
// Every bank chunk: header (count, slotSize, bankId) then count slots of slotSize.
// Never hard-code slot sizes — read them from the bank header.
// v5 -> v6 translation shifts (zones after the NAUTILUS block):
//   HD-1 program:  -6   for v5 offsets >= 2558
//   EXi program:   -6   for v5 offsets >= 2558   (engine IDs at 2851/3903 in v6)
//   Combination:   -2170 for v5 offsets >= 4790
// KARMA data (all object types) is dropped: the function does not exist on NAUTILUS.
```

---

## 9. Open questions

1. DBK1 kit record layout (38,424 bytes per kit).
2. ABK1 arp pattern record layout (556 bytes per pattern).
3. NAUTILUS blocks at zone B of programs (1248 B) and combinations (1316 B) —
   decode (Arpeggiator-related).
4. Rebuild per-engine tables (`Moteur_*.csv`) from OS 3.2 MIDI documentation.
5. SLD1/STL1 (set list), GLB1 (global), DIV1 record layouts.
6. Per-instrument bank-ID ↔ UI bank mapping (needed for the UI layer).
