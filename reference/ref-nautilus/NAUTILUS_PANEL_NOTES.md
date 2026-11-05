# Nautilus — what a future Ctrlr panel would need

**Rewritten for the ctrlr-project from pcglib knowledge (v1.6.3, commit
`c2af0f2`).** Notes for building a Nautilus panel like Kronos Kontrol, after
the Kronos one. The load-bearing documents are `docs/NAUTILUS_SYSEX_PROTOCOL_ANALYSIS.md`
(the SysEx differences from the Kronos) and the format analyses in `docs/`.

## 1. The instrument in one paragraph

The Nautilus (2021) is the Kronos's smaller sibling: the **same HD-1 and EXi
engines** (verified — Finding #6 of `docs/MASTER_NAUTILUS_ANALYSIS_SUMMARY.md`),
but **KARMA is replaced by a Scene system**, and the PCG file and SysEx header
differ. pcglib converts Nautilus ↔ Kronos PCG files (v1.6.2 fixed wave
sequences and drum tracks; v1.6.3 mirrored drum tracks K→N), which is how its
format is known.

## 2. The SysEx header is different

```
KRONOS:   F0 42 3g 68        [function] [data...] F7
NAUTILUS: F0 42 3g 00 01 5D  [function] [data...] F7
```

The Nautilus uses a **3-byte series identifier** `00 01 5D` (0x5D01 little-endian)
instead of the Kronos family byte `68`. `3g` is still global channel − 1. The
device inquiry reply differs accordingly (analysis §1.3).

## 3. Function codes: almost identical, two critical differences

Full matrix in `docs/NAUTILUS_SYSEX_PROTOCOL_ANALYSIS.md` §2.1. Everything the
Kronos panel would use exists on the Nautilus — 72/73/74/75/76/77 object dumps,
37/38/39/3A bank digests, 32/33 current performance id, 34/35/36 piano types,
43/44 parameter change, 53/54/55/56 kit/wave-seq parameter change, 12/42/4E
mode, 60/61/7C bank types — **except**:

| Fn | Kronos | Nautilus |
|----|--------|----------|
| 6D | KARMA Parameter Change | **Scene Parameter Change** |
| 6E | Drum Track Parameter Change | **Arp/Drum Track Parameter Change** |

So a Nautilus panel maps KARMA sliders/switches onto the Scene system, and the
drum-track controls onto the combined Arp/Drum Track function.

## 4. Parameter change grammar: identical

```
F0 42 3g 00 01 5D  43  TYP SOC SUB PID IDX  valueH valueM valueL  F7
```

Same 5-byte parameter id and same 21-bit value (valueH = bits 14–20,
valueM = 7–13, valueL = 0–6). Function 44 (binary, UUID) is identical too.
**The parameter databases differ** between the two instruments (instrument-
specific parameters, Scene vs KARMA, different feature sets) — the Nautilus
tables below are the Nautilus truth.

## 5. The Nautilus parameter tables (midi/)

`midi/NAUTILUS_MIDIimp/` is Korg's Nautilus MIDI implementation, copied whole:

- `NAUTILUS_MIDI_SysEx.txt` — the function-code table.
- `NAUTILUS_MIDI_MIDI_Implentaion.txt` — Korg's filename, sic.
- `SysExDumps/` — the **Nautilus bit-level parameter tables** (one row per
  parameter, carrying TYP/SOC/SUB/PID/IDX like the Kronos ones):
  `Prog_HD-1.txt` (783 KB), `Prog_EXi.txt` (777 KB), `Prog_EXi_Common.txt`
  (654 KB), `Global.txt` (1.4 MB), `Effect.txt` (853 KB),
  `CombiAndSongTimbreSet.txt` (1.1 MB), `SongControl.txt` (842 KB),
  `ArpPattern.txt` (174 KB), `WaveSequence.txt` (11 KB — wave seq 2,216 B,
  object version 1), `DrumKit.txt`, `DrumTrackPattern.txt`, `SetList.txt`,
  `Song.txt`, `SongEvent.txt` — 14 files, covering every editable object.

## 6. Banks: same spaces, different letters (verified 2026-10-21)

From `../ref-kronos/docs/KRONOS_PCG_FORMAT_FACTS.md` §5 (verified on real user
files and the Nautilus Parameter Guide E4):

| Type | Banks | Bank ids (bids) | Contents |
|---|---|---|---|
| Programs | **A..T** (20) | A..E = 0..4 (EXi INT), F = 0x8000 (HD-1 INT), G..T = 0x20000..0x2000D | OS 1.1.1 expanded 20 → 40 (extra banks a..t, bids unverified) |
| Combis | **A..N** (14) | A..G = 0..6 (INT), H..N = 0x20000..0x20006 | 7 INT + 7 user, same bid space as Kronos |
| Drum kits | **A..O** (15) | A = 0 (INT, 40 kits), B..O = 0x20000..0x2000D (16 each) | GM kits sit between H and I in linear addressing |
| Wave sequences | **A..T** (20) | A = 0 (INT, 150), B..T = 0x20000..0x20012 (32 each) | A **includes** the INT bank; factory fills A..I; OS 1.1.1 expanded 15 → 20 |

- Combi bank select: CC0 = 0, **CC32 = 0..6 (INT A..G), 8..14 (user H..N)**.
- The official Kronos ↔ Nautilus mapping (Parameter Guide E4, "Loading KRONOS
  .PCG files") is **by list position**: Kronos I-A..I-F → Nautilus A..F,
  U-A..U-GG → G..T; combis positionally over the full 14-bank lists. The bid
  spaces are identical; only the letters differ.
- Set list slot semantics (both instruments, verified): slot byte 24 bits 1–0
  = type (**0 = combi, 1 = program, 2 = song**), byte 25 bits 4–0 = bank
  (bits 7–5 = transpose MSB), byte 26 = index.

## 7. Nautilus PCG format differences (verified on the factory PRELOAD)

From `../ref-kronos/docs/KRONOS_PCG_FORMAT_FACTS.md` §2 and the docs in
`docs/`:

- **Set list**: one set list = **69,544 B**, slots **543 B** (the Kronos layout
  with one new byte — always 0 in the factory file — inserted at slot offset
  30, so the 512-byte comment starts at 31). STL1/SBK1 are **v1**
  (SLS1/SLD1/SDB1 stay v0). SDB1 record = 3,612 B.
- **HD-1 object version differs** from the Kronos v5 (Finding #5 of the master
  summary); **DIV1 chunk size differs** (Finding #4).
- **PCG header model byte: `0xDD`** (Kronos = `0x68`, Oasys = `0x70`).
- **Wave sequences: 19 banks** on the Nautilus vs **14 on the Kronos** — the
  conversion drops banks beyond the Kronos space and says so in its report
  (see `docs/ABOUT_DRUM_TRACKS_WAVE_SEQUENCES_NAUTILUS_TO_KRONOS.md`).
- **Drum tracks** exist and are converted both ways since v1.6.2/v1.6.3. Note
  the v1.6.2 bug root: the Drum Track Common is **not** at 1292..1303 on the
  Nautilus (`docs/NAUTILUS_TO_KRONOS_V162_FIX.md` §3).
- KARMA → **Scene** (Finding #2 of the master summary).

## 8. Factory names (names/)

`names/` holds the name lists extracted from Nautilus factory PCGs during the
pcglib work: per-chunk CSVs (`nautilus_mbk1_names.csv`, `nautilus_pbk1_names.csv`
= programs, `nautilus_cbk1_names.csv` = combis, `nautilus_dkt1_names.csv` =
kits, `nautilus_wsq1_names.csv` = wave sequences, `nautilus_abk1_names.csv` =
arp banks; columns `Index,Name,Bank,Offset`) plus whole-list variants
(`nautilus_factory_names.txt`, `nautilus_all_names.txt`,
`nautilus_program_names*.txt`, and the `*_clean*` / `*_final*` cleaned
versions). **Caveat:** some per-chunk CSV names carry raw non-UTF-8 bytes —
use the cleaned variants for display.

## 9. Where the rest lives

- pcglib `docs/nautilus/` — `Nautilus Parameters Guide E4` (folder of
  per-section PDFs), `Nautilus Operation Guide E3`, `NAUTILUS_VNL_EFGSJ6.pdf`,
  `NAUTILUS_QSG_EFGSJ7.pdf`, release notes and update/restore PDFs.
- `docs/NAUTILUS_KRONOS_COMPARISON.md` — in-depth file-format comparison.
- `docs/MASTER_NAUTILUS_ANALYSIS_SUMMARY.md` — the six critical findings
  (SysEx header, KARMA vs Scene, PCG header, DIV1 size, HD-1 version, same
  EXi engines) plus comparison tables.
- `docs/NAUTILUS_TO_KRONOS_V162_FIX.md` — the wave-sequence + drum-track bug
  report, root causes and fix (format facts about the Nautilus WS index spaces
  and Drum Track Common offset).
- `docs/CHUNK_INVENTORY_NAUTILUS.md`, `docs/NAUTILUS_CHUNK_INVENTORY_COMPLETE.txt`,
  `docs/INTERIM_REPORT_1/2/3_*.md`, `docs/MASTER_CHUNK_INVENTORY.md`,
  `docs/CHUNK_ANALYSIS_FULL.txt`, `docs/NAUTILUS_ZONE_B_ANALYSIS.md` — the Nautilus
  PCG format discovery (chunk grammar, parameter structure, HD-1 v5 vs v6).
