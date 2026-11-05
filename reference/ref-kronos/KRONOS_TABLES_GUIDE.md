# Kronos — how to read the bit-level tables

**Rewritten for the ctrlr-project from pcglib knowledge (v1.6.3).** The Kronos
parameter knowledge exists in three shapes: Korg's original text tables
(`midi/*.txt`), and the same content restructured as CSV and JSON (`tables/`).
This document explains all three so the panel can be driven from data, not
hand-coded constants.

**Hardware-verified states.** For what the Kronos actually accepts and
transmits per SysEx function (T/D states, tested 16 oct. 2026), see
[`docs/SYSEX_KRONOS.md`](docs/SYSEX_KRONOS.md) — it wins over the tables
where the two disagree (e.g. Drum Track On is marked T there, but the device
never validated it; the panel uses fn 6E instead, see
`KRONOS_SYSEX_PARAMETER_CONTROL.md` §12b).

## 1. The Korg text tables (`midi/*.txt`)

Fixed-width tables, one row per parameter:

```
| OFS  | bit | parameter    | parameter        | data(hex) | value      |TYP|SOC|SUB|PID|IDX|
| 2586 |     | Tone Adjust  | Knob1 Assign     | 00~FF     | Off~       | 29|  0|  0|  1|  0|* SUB = (Assign >> 7) & 0x01, Value = Assign & 0x7f
```

- `OFS` — byte offset in the object (decimal). For engine blocks, the offset is
  relative to the block base (EXi 1 = 2908, EXi 2 = 3960).
- `bit` — bit span within the byte(s), **LSB first** (`0:0-7`, `1:5-7 + 2:0-3`
  for a field crossing two bytes).
- `data(hex)` — raw data range; `value` — display range (`00~61`) or value list
  (`Triangle~Random6`, `0~Off`).
- `TYP|SOC|SUB|PID|IDX` — the SysEx fn 43 parameter id (see
  `KRONOS_SYSEX_PARAMETER_CONTROL.md` §2). Empty for parameters with no SysEx
  id (e.g. the 24 name bytes). Footnotes (`* …`) give the packing formulas
  when an id byte is derived from the parameter's own bits.
- `SysExParams/VoiceModels/` holds per-engine variants of the same tables
  (AL-1, CX-3, EP-1, HD-1, MOD-7, MS-20EX, Off, PolysixEX, SGX-1, STR-1).

These files are byte-identical to `docs/MIDI implementation/` in this project.

## 2. The CSV tables (`tables/*.csv`)

The same content, semicolon-separated, French column names (Korg-table origin):

```
octet;bits (octet:bas-haut, poids faible d'abord);largeur;section;paramètre;données (hex);valeurs;note
0;0:0-7;8;Common;Name;00~FF;~;offset dans la fiche (3706 octets utiles, 4960 dans le PCG)
1;1:5-7 + 2:0-3;7;;[LFO1] Start Phase;DC~25;-180~RND;offset dans le bloc moteur : EXi 1 = 2908 + offset, EXi 2 = 3960 + offset
```

- `octet` — byte offset (relative to the object, or to the engine block base).
- `bits` — bit span, LSB first within each byte; multi-byte fields are written
  as spans joined by ` + `.
- `largeur` — field width in bits.
- `valeurs` — display range or value list, as above.
- `note` — free text; for engine tables it carries the block base
  (EXi 1 = 2908 + offset, EXi 2 = 3960 + offset).

## 3. The JSON tables (`tables/*.json`)

Machine-readable, one array of entries:

```json
[{"sec": "Common", "name": "Name", "pieces": [[0, 0, 7]], "data": "00~FF", "value": "~", "ids": ["", "", "", "", "", ""]},
 {"sec": "[LFO1]", "name": "Start Phase", "pieces": [[1, 5, 7], [2, 0, 3]], "data": "DC~25", "value": "-180~RND", "ids": ["11/12", "6", "0", "0", "0", ""]}]
```

- `pieces` — bit spans as `[octet, bitLo, bitHi]`, same LSB-first convention.
- `ids` — the **fn 43 parameter id in byte order (TYP, SOC, SUB, PID, IDX)**
  plus a spare slot. `"11/12"` = the parameter exists under two TYP values
  (e.g. EXi engine 1 / engine 2); `"?"` = not yet mapped; empty = no SysEx id.
- Same caveat as the text tables: where a footnote formula exists, the text
  table is authoritative.

## 4. Which table covers what

| File(s) | Object | Size | Notes |
|---|---|---|---|
| `Programme_HD-1.csv/.json` | HD-1 program | 4,960 B slot, 3,706 useful | oscillators at 2774 / 3240, 8 zones × 22 B; the last 1,254 B of the slot are not read (recopied verbatim) |
| `Programme_EXi_commun.csv/.json` | EXi program, common part | same offsets as HD-1 up to 2773 | engine selector at 2857 / 3909 |
| `Moteur_<engine>.csv/.json` (8 engines) | EXi engine block | 1,000 B | base 2908 (EXi 1) / 3960 (EXi 2); engine codes: 0 Off, 2 AL-1, 3 CX-3, 4 STR-1, 5 MS-20EX, 6 PolysixEX, 7 MOD-7, 8 SGX, 9 EP-1 |
| `Combinaison.csv/.json` | combination | 7,810 B | 16 timbres × 188 B from offset 4802 |
| `Effets.json` | effect blocks | 64 B per block | 198 effect types |
| `Effets_liste.csv` | effect type list | — | type number → name + parameter count |
| `FACTORY_NAMES.csv` | factory names | — | columns: instrument;object_type;bank_bid;bank_index;slot_index;name;engines |
| `HD1_param_offsets_v5_v6.csv` | HD-1 OS 3.1 ↔ 3.2 | — | per-parameter offsets, min/max per OS, verdict |
| `HD1_v5_to_v6_zone_map.csv` | HD-1 zone map | — | v5 → v6 zone record mapping |

## 5. Reading rules (from the consolidated knowledge, `docs/CONNAISSANCES_KRONOS_PCG.md` §4)

- Bit fields are **LSB first** within each byte; multi-byte fields are packed
  little-endian on the field width.
- 16-bit values are **little-endian**; negatives are **two's complement on the
  field width**.
- Values are **raw** — the table's value column gives the display mapping.
- Drum Track Program reference: offset **2688/2689** (number / bank number);
  Drum Track On: offset **1295 bit 4**; KARMA GE number: **1814–1815** (0–3583);
  oscillator mode (HD-1): **2558 bits 0–2** (0 Single, 1 Double, 2 Drums,
  3 Double Drums).

## 6. Caveats

- The `ids` mapping is partial. Generate panel controls from the tables, but
  verify each generated control against the hardware before shipping it
  (the project rule: every vertical slice is hardware-verified).
- PCG Tools (upstream) has three known errors — wave sequence OS 1 indexing,
  drum-kit zone offset (`zone + 18`, not `+2`), and gaps in its V2→V3 rules.
  Do not port its logic; the tables here are the corrected knowledge.
- The tables describe **OS 2/3 (v5/v3)** objects. OS 1 objects (v4/v3/v2/v0)
  differ (single-byte sample references, smaller zones); OS 1.5/1.6
  two-part format is not covered.
