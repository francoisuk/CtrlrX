# About the conversion from Kronos to Oasys

_What is bigger on the KRONOS than on the OASYS, how pcglib converts it,
and what the conversion report tells you. Applies to pcglib 1.6.1 and
later; the conversion follows the byte-verified HD-1 parameter map
(`docs/OASYS_PARAMETER_MAP.md`). Since v1.6.3 the combi KARMA map is
re-derived (combi KARMA survives), the EXi engine payload converts
through a partial byte-verified map, and banks with an unexpected slot
size are dropped and reported instead of silently mis-converted._

## In short

- The KRONOS has **more banks than the OASYS**: 20 program banks vs 13
  (the U-AA..U-GG user banks have no OASYS target), 15 drum kit and 15
  wave sequence banks vs 8 each, and set lists the OASYS layout does not
  verify. Combinations are 14 vs 14.
- Bank ids map **identity** over the shared id space; KRONOS-only banks
  are **dropped and reported**; drum kits and wave sequences have no
  verified map, so their banks are emitted **Init-filled with the names
  preserved** and reported as defaulted.
- Programs are converted per the byte-verified map: the OASYS has KARMA
  too (the block moves by 12 bytes), but the KRONOS-only sections — drum
  track, gate params, crossfade pairs 4..7, and **oscillator zones
  5..8** (the KRONOS stores 8 zones per oscillator, the OASYS 4) — are
  dropped and reported. EXi (MOD-7) programs convert through a **partial**
  byte-verified map: three engine regions copy verbatim, the rest is
  zeroed and reported.
- Combinations convert per a re-derived map (v1.6.3): the combi **KARMA
  block survives** (shift −12), only the KRONOS Drum Track Common is
  dropped. Combi timbres that reference a KRONOS-only program bank
  (U-AA..U-GG) are **set to Off** and reported.
- A bank whose slot size matches no verified map is **dropped and
  reported** (never silently mis-converted).
- Every conversion writes a **text report** (`<name>-OASYS.txt` next to
  the converted PCG) listing every mapped bank, every dropped bank,
  every dropped reference and every defaulted section.

## 1. The two instruments side by side

The OASYS is the KRONOS' predecessor and shares its HD-1 program family,
but it is the smaller instrument: fewer user banks, smaller records, no
drum track.

| | KRONOS (OS 2.x/3.x) | OASYS |
|---|---|---|
| Program banks | **20**: I-A..I-F, U-A..U-G, U-AA..U-GG (128 slots each) | **13**: I-A..I-F, U-A..U-G (the GM bank is ROM, not stored, on both) |
| Combi banks | 14: I-A..I-G, U-A..U-G (128 slots each) | 14: I-A..I-G, U-A..U-G |
| Drum kit banks | **15**: INT (40 slots), U-A..U-G, U-AA..U-GG (16 slots each) | **8**: INT (40), U-A..U-G (16) |
| Wave sequence banks | **15**: INT (150 slots), U-A..U-G, U-AA..U-GG (32 slots each) | **8**: INT (150), U-A..U-G (32) |
| Set lists | 128 | layout unverified — not converted |
| Program record | 4960 bytes, PBK1/MBK1 version 5 | 4386 bytes, version 0 |
| Oscillator zones | **8 zones × 22 bytes per OSC** | **4 zones × 6 bytes per OSC** |
| Drum track | Drum Track Common (1292..1303) + Drum Track (2688..2717) | none |
| Combi record | 7810 bytes, 16 timbres × 188 bytes | 7766 bytes, 16 timbres × 186 bytes |
| Drum kit / wave sequence fiche | 38,424 / 2,216 bytes | 11,288 / 1,192 bytes |
| KARMA | yes (programs and combis) | yes (programs and combis; the combi KARMA map is re-derived since v1.6.3) |

The file bank-id spaces are shared, so banks map **identity** wherever
the OASYS has the bank; the KRONOS-only user banks U-AA..U-GG (bank ids
0x20007..0x2000D) exist for programs, drum kits and wave sequences alike
and have no OASYS target.

## 2. How the conversion works

The source gate: **KRONOS OS 2.x/3.x files only** — an OS 1.x file is a
different family and is rejected with a clear message.

### Programs (4960 → 4386 bytes per slot)

- **Zone A** (bytes 0..1291: name, Common, IFX/MFX/TFX, effect LFOs,
  vector, controllers, audio input): identity.
- **KARMA + Common** (1304..2687 → 1292..2675, shift −12): one
  continuous copy — **the OASYS has KARMA too** (at 1292..2545), so the
  program's KARMA data survives the conversion.
- **Common tail** (2718..2773 → 2676..2731, shift −42): Pitch EG, Common
  LFO, Common Keyboard Track 1-2.
- **OSC blocks** (KRONOS stride 466 @2774 ↔ OASYS stride 288 @2732):
  zones 1..4 converted (22 bytes → 6 bytes; the bank byte is read from
  the KORG-MS UUID — non-KORG-MS UUIDs read as bank 0); the trigger tails
  (crossfade pairs 1..3, damper, velocity zone), the 238-byte parameter
  payloads and the Mod.Mixer2 records are copied.
- **Zones 5..8** (per OSC) have no OASYS equivalent: dropped, and
  reported per program when they are actually used.
- **Dropped (no OASYS equivalent)**, reported in the defaulted sections:
  the Drum Track Common, the Drum Track, the Mod.Mixer Gate params,
  crossfade pairs 4..7, the display byte, the tail padding.
- **EXi (MOD-7) programs** (since v1.6.3): zone A and KARMA + Common are
  copied, and the EXi engine payload converts through a **partial
  byte-verified map** (`docs/OASYS_PARAMETER_MAP.md` §9): the common tail
  (2718..2851 → 2676..2809), the EXi 1 engine head (2908..3235 →
  2848..3175) and the EXi 2 engine head (3960..4287 → 3636..3963) copy
  verbatim; the remaining EXi engine regions have no verified OASYS map
  and are zeroed (and reported in the defaulted sections). On the KRONOS
  factory file a K→O→K round trip preserves 226,567 EXi payload bytes with
  zero differences on the copied regions.

### Combinations (7810 → 7766 bytes per slot, map re-derived in v1.6.3)

- **Zone A** (0..1291): identity (verified).
- **KARMA Common + Modules A..D** (1304..4789 → 1292..4777, shift −12):
  one continuous copy — **combi KARMA survives the conversion**
  (`docs/OASYS_PARAMETER_MAP.md` §10).
- **Drum Track Common** (1292..1303): no OASYS equivalent — dropped and
  reported in the defaulted sections.
- **Common/assignable block** (4790..4801 → 4778..4789, shift −12):
  category, favorite, auto load, scale, assignable switches/knobs
  (verified against Korg's HD-1 tables).
- **16 timbres** (4802 → 4790): 188 → 186 bytes each (the field offsets
  are shared; two KRONOS tail bytes are dropped). A timbre that
  references a KRONOS-only user bank (U-AA..U-GG) is **set to Off** — the
  native OASYS representation of an unused timbre — and reported.

### Drum kits and wave sequences

The layouts differ too much for a verified map (38,424 vs 11,288 bytes
per drum kit; 2,216 vs 1,192 per wave sequence). The banks are emitted
**Init-filled with the kit/sequence names preserved** (the 24-byte name
at slot offset 0 is shared) and reported as defaulted. KRONOS-only banks
(U-AA..U-GG) are dropped and reported.

### Set lists

Dropped and reported — the OASYS set list layout is unverified: **none of
the 8 available OASYS files** (7 factory files + the complete bank set
inside the MIDI Quest `.sqz`) **carries set list chunks** (SLS1/SBK1),
and the MIDI Quest config documents the set list entry *semantics*
(program/combi/song references + delay) but not the on-disk layout.

### Banks with an unexpected slot size (since v1.6.3)

Every bank is converted only through a slot size with a verified map.
A bank whose slot size matches none (a corrupt file, a future OS layout)
is **dropped and reported**, never silently mis-converted:

```
PBK1 0x20000 bank U-A (128 slots, 4386-byte fiche): dropped - unexpected KRONOS slot size (no verified map)
```

The OASYS → KRONOS direction accepts the OASYS v1/v2 layouts it has
verified maps for: program slots of 4386 B (v0) **and** 6174 B (v2), and
combi slots of 7766 B (v0) **and** 11288 B (v1, verified on the `.sqz`
ALLBANKS file). The extension bytes beyond the v0 layout have no verified
KRONOS map and are dropped, reported per bank:

```
MBK1 0x8000 -> 0x8000 bank I-F (128 slots): v1/v2 engine extension bytes (1788 extra vs the v0 layout) dropped (no verified KRONOS map)
CBK1 0x0 -> 0x0 bank I-A (128 slots): v1 combi extension bytes (3522 extra vs the v0 layout) dropped (no verified KRONOS map)
```

### The output

A complete OASYS file: model byte 0x70, `PCG1 { DIV1, PRG1, CMB1, DKT1,
WSQ1 }` with the full OASYS bank structures (13 program banks, 14 combi
banks, 8 drum kit and 8 wave sequence banks); banks without a source are
Init-filled. OASYS chunk checksums are version-only, so every chunk
validates.

## 3. What the output text mentions

Every KRONOS → OASYS conversion writes a **conversion report** next to
the converted PCG: same folder, same base name, `.txt` extension
(`MySet-OASYS.txt` for `MySet-OASYS.PCG`). The application
(**File > Convert to OASYS...**), the command line
(`pcglib convert <in.PCG> -t oasys`) and the standalone Python port
(`docs/python-script/pcglib_convert.py`) all write the same report.

The report contains:

1. **Header** — pcglib version, source file, output file.
2. **Summary** — `Converted: N banks mapped, M banks dropped (no OASYS
   target bank), K defaulted entries.`
3. **Mapped banks** — one line per bank:
   `PBK1 0x1 -> 0x1 bank I-B (128 slots)`.
4. **Dropped banks** — one line per bank that had no OASYS target, plus
   one line per bank with an unexpected slot size (no verified map):
   `Dropped PBK1 0x20007 bank U-AA (128 slots): no OASYS equivalent (program banks end at U-G)`
   `PBK1 0x20000 bank U-A (128 slots, 4386-byte fiche): dropped - unexpected KRONOS slot size (no verified map)`
5. **Dropped references** — one line per reference that could not be
   converted:
   `Dropped Program 'Expressive Horns EXs18  ' (bank I-B slot 6): zones 5..8 have no OASYS equivalent (4 zones per OSC) - dropped`
   `Dropped Combi 'K-Lab: Katja's House' (bank I-A slot 1) timbre 4: program bank U-AA (pcgId 24) has no OASYS equivalent - timbre set to Off`
6. **Defaulted sections** — what is emitted defaulted, and why:
   `Defaulted Programs: HD-1 slots - zone A (0..1291), KARMA + Common (1304..2687 -> 1292..2675), the common tail (2718..2773 -> 2676..2731) and the OSC blocks (zones 1..4 with KORG-MS UUIDs, trigger tails, the 238-byte parameter payloads, Mod.Mixer2) are preserved; Drum Track Common, Drum Track, the Mod.Mixer Gate params, crossfade pairs 4..7, the display byte, the tail padding and KRONOS zones 5..8 are dropped (no OASYS equivalent); EXi slots - zone A and KARMA + Common are preserved, the EXi engine payload is partially preserved (the common tail 2718..2851 -> 2676..2809, the EXi 1 engine head 2908..3235 -> 2848..3175, the EXi 2 engine head 3960..4287 -> 3636..3963; the remaining EXi engine regions have no verified OASYS map and are zeroed)`
   `Defaulted Combis: KARMA Common + Modules A..D (1304..4789 -> 1292..4777, shift -12) are preserved; the Drum Track Common (1292..1303) is dropped (no OASYS equivalent); zone A (0..1291), the Common/assignable block (4790..4801 -> 4778..4789) and the 16 timbres are preserved`
   `Defaulted Set lists (128 set lists): dropped - the OASYS set list layout is unverified (none of the 8 available OASYS files carries SLS1 chunks)`
   and one line per defaulted bank:
   `Defaulted DBK1 0x20000 -> 0x20000 bank U-A (16 slots): sound defaulted (KRONOS 38424-byte fiche vs OASYS 11288-byte; no verified map); names preserved`

   The OASYS → KRONOS direction reports the same sections with the
   direction flipped, plus one line per bank whose v1/v2 extension bytes
   were dropped:
   `Defaulted MBK1 0x8000 -> 0x8000 bank I-F (128 slots): v1/v2 engine extension bytes (1788 extra vs the v0 layout) dropped (no verified KRONOS map)`
   `Defaulted CBK1 0x0 -> 0x0 bank I-A (128 slots): v1 combi extension bytes (3522 extra vs the v0 layout) dropped (no verified KRONOS map)`

### Real example — the KRONOS OS 3.2 factory preload

The 30 MB factory file carries 17 program banks (12 with an OASYS
target, 5 KRONOS-only), 6 combi banks, 4 drum kit and 3 wave sequence
banks:

```
Converted: 18 banks mapped, 5 banks dropped (no OASYS target bank), 10 defaulted entries.
PBK1 0x1 -> 0x1 bank I-B (128 slots)
MBK1 0x0 -> 0x0 bank I-A (128 slots)
CBK1 0x0 -> 0x0 bank I-A (128 slots)
...
Dropped MBK1 0x20009 bank U-CC (128 slots): no OASYS equivalent (program banks end at U-G)
Dropped PBK1 0x20007 bank U-AA (128 slots): no OASYS equivalent (program banks end at U-G)
...
Dropped Program 'Expressive Horns EXs18  ' (bank I-B slot 6): zones 5..8 have no OASYS equivalent (4 zones per OSC) - dropped
Dropped Combi 'K-Lab: Katja's House' (bank I-A slot 1) timbre 4: program bank U-AA (pcgId 24) has no OASYS equivalent - timbre set to Off
...
Defaulted Programs: HD-1 slots - zone A (0..1291), KARMA + Common (1304..2687 -> 1292..2675), the common tail (2718..2773 -> 2676..2731) and the OSC blocks ... are preserved; Drum Track Common, Drum Track, ... and KRONOS zones 5..8 are dropped (no OASYS equivalent); EXi slots - zone A and KARMA + Common are preserved, the EXi engine payload is partially preserved (the common tail 2718..2851 -> 2676..2809, the EXi 1 engine head 2908..3235 -> 2848..3175, the EXi 2 engine head 3960..4287 -> 3636..3963; the remaining EXi engine regions have no verified OASYS map and are zeroed)
Defaulted Combis: KARMA Common + Modules A..D (1304..4789 -> 1292..4777, shift -12) are preserved; the Drum Track Common (1292..1303) is dropped (no OASYS equivalent); zone A (0..1291), the Common/assignable block (4790..4801 -> 4778..4789) and the 16 timbres are preserved
Defaulted Set lists (128 set lists): dropped - the OASYS set list layout is unverified (none of the 8 available OASYS files carries SLS1 chunks)
Defaulted DBK1 0x20000 -> 0x20000 bank U-A (16 slots): sound defaulted (KRONOS 38424-byte fiche vs OASYS 11288-byte; no verified map); names preserved
Defaulted WBK1 0x0 -> 0x0 bank INT (150 slots): sound defaulted (KRONOS 2216-byte fiche vs OASYS 1192-byte; no verified map); names preserved
```

In this file the 2199 dropped references are 11 programs that use
oscillator zones 5..8 and 2188 combi timbres that reference a KRONOS-only
U-AA..U-GG program bank (each timbre is set to Off). The 10 defaulted
entries are the Programs, Combis and Set lists notes plus 4 drum kit and
3 wave sequence banks.

### Real example — the KRONOS OS 2 factory preload

The OS 2 factory file has no KRONOS-only banks, so nothing is dropped at
bank level; one program uses zones 5..8:

```
Converted: 16 banks mapped, 0 banks dropped (no OASYS target bank), 9 defaulted entries.
...
Dropped Program 'Timpani Splits SW2 Roll2' (bank U-A slot 52): zones 5..8 have no OASYS equivalent (4 zones per OSC) - dropped
Defaulted Programs: HD-1 slots - ... (same note as above, incl. the EXi partial map)
Defaulted Combis: KARMA Common + Modules A..D (1304..4789 -> 1292..4777, shift -12) are preserved; the Drum Track Common (1292..1303) is dropped (no OASYS equivalent); ...
Defaulted Set lists (128 set lists): dropped - the OASYS set list layout is unverified (none of the 8 available OASYS files carries SLS1 chunks)
Defaulted DBK1 0x20000 -> 0x20000 bank U-A (16 slots): sound defaulted ...
```

## 4. Limitations

- **Oscillator zones 5..8** are dropped (the OASYS stores 4 zones per
  OSC); programs that use them are reported, and their zones 1..4 still
  convert.
- **Drum track** has no OASYS equivalent: the Drum Track Common and Drum
  Track sections are dropped and reported in the defaulted sections.
- **Combi KARMA** survives since v1.6.3 (the combi map is re-derived,
  shift −12); only the combi Drum Track Common is dropped.
- **EXi (MOD-7) engine data** is partially preserved (the three
  byte-verified regions of `docs/OASYS_PARAMETER_MAP.md` §9); the
  unmapped engine regions are zeroed and reported. Zone A and KARMA +
  Common are preserved.
- **Drum kits and wave sequences** are sound-defaulted (Init-filled,
  names preserved) — no verified map between the 38,424/2,216-byte KRONOS
  fiches and the 11,288/1,192-byte OASYS ones.
- **Set lists** are dropped (the OASYS layout is unverified — none of
  the 8 available OASYS files carries set list chunks).
- **Banks with an unexpected slot size** are dropped and reported (no
  verified map); the OASYS → KRONOS direction additionally drops the
  v1/v2 engine extension bytes (reported per bank).
- **Round trips**: OASYS → KRONOS → OASYS returns every HD-1 program
  **byte-for-byte identical** (program KARMA data survives; since v1.6.3
  the EXi payload's three copied regions survive too, and every combi is
  byte-identical, combi KARMA included). KRONOS → OASYS → KRONOS is not
  byte-identical: the KRONOS-only sections dropped on the way out are
  re-defaulted on the way back.

## Further reading

- `docs/OASYS_PARAMETER_MAP.md` — the byte-verified HD-1 program
  parameter map (with `tables/Oasys_HD1_blocks.csv` and
  `tables/Oasys_HD1_param_offsets.csv`), the EXi engine payload partial
  map (§9, `tables/Oasys_EXi_blocks.csv`) and the combi slot map (§10,
  `tables/Oasys_Combi_blocks.csv`).
- `docs/KRONOS_OASYS_V163_FIX.md` — the v1.6.3 OASYS test fixes.
- The user manual (`pcglib_manual.md`), chapter 9 "Converting between
  the instruments", section 9.5.
