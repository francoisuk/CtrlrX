# About Drum Tracks & Wave Sequences from Nautilus to Kronos

_What is different between the two instruments, how pcglib converts it,
and what the conversion report tells you. Applies to pcglib 1.6.2 and
later — the NAUTILUS → KRONOS conversion was fixed in v1.6.2 after a
beta-tester report ("the Wave Sequences were not converted… the Drum
Tracks (DT) were not converted"); the KRONOS → NAUTILUS drum track
mirror described in §2 is v1.6.3._

## In short

- The NAUTILUS has **19 user wave sequence banks** (B..T); the KRONOS
  has **14** (U-A..U-GG). Both instruments have the same INT bank
  (150 factory wave sequences).
- Since v1.6.2 the NAUTILUS-only banks P..T are **not dropped**: they
  take the KRONOS user banks that no other bank claimed, and every wave
  sequence reference in the converted programs is remapped. A bank that
  finds no free KRONOS bank is dropped and reported.
- The **drum track survives** too: the KRONOS Drum Track Common is
  rebuilt from the NAUTILUS zone B scene data. Pattern numbers are
  clamped to the KRONOS 0..999 range; NAUTILUS user patterns and step
  sequences have no KRONOS equivalent and are reported.
- Every conversion writes a **text report** (`<name>-KRONOS.txt` next to
  the converted PCG) listing every mapped bank, every dropped bank,
  every remapped or reset wave sequence reference, and every drum track
  conversion, with summary lines.

## 1. The two instruments side by side

### Wave sequences

| | NAUTILUS | KRONOS |
|---|---|---|
| INT bank (150 factory wave sequences) | bank A (bank id 0x0) | INT (bank id 0x0) |
| User banks | **B..T = 19 banks** (bank ids 0x20000..0x20012) | **U-A..U-GG = 14 banks** (bank ids 0x20000..0x2000D) |
| Slots per user bank | 32 | 32 |
| Total banks | 20 (A..T) | 15 (INT + U-A..U-GG) |
| Wave sequence index space | 150 + 19 × 32 = **758** | 150 + 14 × 32 = **598** |

Notes:

- On the NAUTILUS the bank letters include the INT bank: A is the INT
  bank, B..T are the user banks (NAUTILUS Parameter Guide; expanded from
  15 to 20 banks in OS 1.1.1). The KRONOS shows INT plus U-A..U-GG.
- A wave sequence reference inside a program is a **global index**:
  0..149 is the INT bank; from 150 on, bank = (index − 150) / 32 and
  slot = (index − 150) % 32. The KRONOS index space stops at 597, so a
  NAUTILUS reference can point beyond anything the KRONOS can address.
- Wave sequences are the only bank type affected by the difference:
  programs (20 vs 20), combinations (14 vs 14) and drum kits (15 vs 15)
  have the same bank counts on both instruments. (The NAUTILUS-only
  arpeggiator has no KRONOS equivalent either and is dropped and
  reported.)

### Drum tracks

- On the KRONOS, bytes 1292..1303 of the program/combi record are the
  **Drum Track Common**: drum track on/off, pattern number, trigger
  mode, latch mode, key zone, velocity zone, output and input channels.
- On the NAUTILUS the **same bytes are the RT Controller**. The NAUTILUS
  drum track lives in **zone B** (scene common at bytes 1348..1378, and
  per-scene drum fields inside the scene records at 2440).
- The NAUTILUS drum track patterns go up to **1999** (the factory uses up
  to about 1271) and include **user patterns** (U bank) and **step
  sequences**. The KRONOS drum track accepts **preset patterns
  0..999** only.

## 2. How the conversion handles the difference

### Wave sequences (since v1.6.2)

1. The **INT bank is copied verbatim** (150 wave sequences).
2. User banks inside the shared bank-id space (NAUTILUS B..O, bank ids
   0x20000..0x2000D) **keep their bank id**: they land on the KRONOS
   U-A..U-GG banks position by position.
3. The NAUTILUS-only banks **P..T** (bank ids 0x2000E..0x20012) **take the
   KRONOS user banks that no identity bank claimed, in bank-id order**
   (lowest free bank first). Example: a file whose only user wave
   sequence bank is T converts T into KRONOS bank U-A.
4. A bank that finds **no free KRONOS user bank is dropped** (its content
   is lost) and reported. This can only happen when all 14 KRONOS user
   banks are already claimed — for example a full NAUTILUS file, or the
   Init-filled P..T banks that a KRONOS → NAUTILUS conversion creates.
5. Every wave sequence reference in the converted programs is remapped
   through this assignment:
   - a reference into a remapped bank is **remapped** to the new bank
     (same slot);
   - a reference into a dropped bank is **reset to 0** and reported;
   - a reference into a bank that is not in the source file is **kept**
     (the KRONOS bank exists and is Init-filled);
   - references into the INT bank are unchanged.
   - EXi (MOD-7) programs use no wave sequences and are not touched.

Before v1.6.2, banks P..T were simply dropped and the references were
left pointing beyond the KRONOS index space — the wave sequences were
lost. That was the beta-tester's report.

### Drum tracks (since v1.6.2)

- The KRONOS **Drum Track Common is rebuilt from the NAUTILUS zone B
  scene data**: on/off, pattern number, trigger mode ("Start
  Immediately" / "Wait KBD Trig"), latch mode (Off / On / Use Scene
  Latch), key zone, velocity zone, output and input channels. The
  section is rebuilt, not copied: on the NAUTILUS those bytes are the RT
  Controller, and copying them would write controller bytes into the
  drum track settings (the drum track came out off, with inverted trigger
  zones and a garbage pattern number — the second half of the
  beta-tester's report).
- The **pattern reference is kept**, clamped to the KRONOS 0..999 range
  when the NAUTILUS number is higher. The converter assumes the NAUTILUS
  and KRONOS preset patterns correspond by number up to 999.
- The **pattern data itself is not converted**: NAUTILUS user patterns
  (U bank) have no KRONOS equivalent, and neither do step sequences. Both
  are reported; the KRONOS keeps the pattern reference (with the clamped
  number and the bank flag).

The reverse direction (KRONOS → NAUTILUS, since v1.6.3) mirrors the
KRONOS Drum Track Common **into the NAUTILUS zone B scene data** — the
exact inverse of the rebuild above (the scene selected by the default
block's scene select carries the drum track; the pattern number fits the
NAUTILUS range unclamped; the KRONOS has no step sequences, so the step
sequence select bit is cleared; the undocumented flag bits 7~5 are carried
through the scene common byte's reserved bits). The NAUTILUS bytes
1292..1302 (the RT Controller on the NAUTILUS) get the NAUTILUS factory
default. The K→N report lists one line per converted drum track
(`Program '…' (bank 0x… slot n): drum track on -> NAUTILUS scene data
(pattern P708, trigger Wait KBD Trig, latch On)`) plus a summary line
(`Drum tracks: 175 on (22 program(s), 153 combi(s)), 0 user pattern(s)
not converted` on the KRONOS factory file). The result: a
KRONOS → NAUTILUS → KRONOS round trip preserves the Drum Track Common
**byte-identically**.

## 3. What the output text mentions

Every NAUTILUS → KRONOS conversion writes a **conversion report** next
to the converted PCG: same folder, same base name, `.txt` extension
(`MySet-KRONOS.txt` for `MySet-KRONOS.PCG`). The application
(**File > Convert to KRONOS...**), the command line (`pcglib convert`)
and the standalone Python port (`docs/python-script/pcglib_convert.py`)
all write the same report.

The report contains:

1. **Header** — pcglib version, source file, output file.
2. **Summary** — `Converted: N banks mapped, M banks dropped (no KRONOS
   target bank).`
3. **Mapped banks** — one line per bank:
   `WBK1 0x20012 -> 0x20000 bank U-A (32 slots)`.
4. **Dropped banks** — one line per bank that had no KRONOS target:
   `Dropped WBK1 0x2000E (32 slots)`.
5. **Dropped set list references** — set list slots whose referenced
   bank was not converted.
6. **Conversion notes** (since v1.6.2):
   - wave sequence reference remaps:
     `Program 'OB Epic PAD' (bank 0x2000D slot 36) osc 0 zone 0: wave sequence index 726 (bank T slot 0 '8Voice RR OBX') remapped to 150 (bank U-A slot 0)`
   - wave sequence reference resets (the warning for a wave sequence
     with no KRONOS home):
     `... wave sequence index N (bank T slot k 'name') has no KRONOS target bank - reference reset to 0`
   - drum track conversions:
     `Combi 'OB TRON' (bank 0x20006 slot 11): drum track on -> KRONOS Drum Track On (pattern U241, trigger Wait KBD Trig, latch On)`
   - drum track warnings:
     `Program 'OB Fat Filter SW1' (bank 0x2000D slot 20): drum track pattern 1262 clamped to 999 (KRONOS range 0..999)`
     `Combi 'OB TRON' (bank 0x20006 slot 11): drum track pattern U241 is a user pattern - user patterns are not converted`
     `... the selected scene uses a step sequence (no KRONOS equivalent)`
   - a drum track summary line:
     `Drum tracks: 17 on (1 program(s), 16 combi(s)), 8 pattern number(s) clamped to 999, 1 user pattern(s) not converted, 0 step sequence scene(s) without KRONOS equivalent`

### Real example

The beta tester's file (`N_EXs342 Kelfar Diamond Analog Synth.PCG` —
one program bank, one combi bank, one wave sequence bank T) converts
with:

```
Converted: 3 banks mapped, 0 banks dropped (no KRONOS target bank).
PBK1 0x2000D -> 0x2000D bank U-GG (128 slots)
CBK1 0x20006 -> 0x20006 bank U-G (128 slots)
WBK1 0x20012 -> 0x20000 bank U-A (32 slots)
Program 'OB Detuned Attack' (bank 0x2000D slot 3) osc 0 zone 0: wave sequence index 727 (bank T slot 1 '8Voice RR SuperSAW') remapped to 151 (bank U-A slot 1)
Program 'OB Epic PAD' (bank 0x2000D slot 36) osc 0 zone 0: wave sequence index 726 (bank T slot 0 '8Voice RR OBX') remapped to 150 (bank U-A slot 0)
...
Program 'OB Fat Filter SW1' (bank 0x2000D slot 20): drum track pattern 1262 clamped to 999 (KRONOS range 0..999)
Combi 'OB TRON' (bank 0x20006 slot 11): drum track on -> KRONOS Drum Track On (pattern U241, trigger Wait KBD Trig, latch On)
Combi 'OB TRON' (bank 0x20006 slot 11): drum track pattern U241 is a user pattern - user patterns are not converted
...
Drum tracks: 17 on (1 program(s), 16 combi(s)), 8 pattern number(s) clamped to 999, 1 user pattern(s) not converted, 0 step sequence scene(s) without KRONOS equivalent
```

Bank T landed on KRONOS bank U-A (the first free user bank), and all
nine wave sequence references in the programs were remapped to it —
nothing was lost.

### When a wave sequence bank is dropped

Converting a KRONOS file to NAUTILUS and back (KRONOS → NAUTILUS →
KRONOS) Init-fills the NAUTILUS-only banks P..T on the way out; on the
way back all 14 KRONOS user banks are already claimed, so the five
Init-filled banks have no free target and are reported:

```
Converted: 65 banks mapped, 5 banks dropped (no KRONOS target bank).
...
WBK1 0x2000D -> 0x2000D bank U-GG (32 slots)
Dropped WBK1 0x2000E (32 slots)
Dropped WBK1 0x2000F (32 slots)
Dropped WBK1 0x20010 (32 slots)
Dropped WBK1 0x20011 (32 slots)
Dropped WBK1 0x20012 (32 slots)
```

The same warning appears at reference level when a program points into a
dropped bank: `... has no KRONOS target bank - reference reset to 0`.

## 4. Limitations

- **Pattern numbers**: the converter assumes the NAUTILUS and KRONOS
  preset drum track patterns correspond by number up to 999; numbers
  above 999 are clamped (each clamp is reported). If the two preset sets
  diverge below 1000, a clamped reference would point at the wrong
  pattern on the KRONOS.
- **User patterns and step sequences** are not converted (reported per
  patch); the NAUTILUS pattern data has no KRONOS target.
- **EXi (MOD-7) programs** get the Drum Track Common rebuild but no wave
  sequence remap (they use no wave sequences).
- **KRONOS → NAUTILUS → KRONOS round trips** preserve the Drum Track
  Common byte-identically since v1.6.3 (the K→N direction mirrors it into
  the NAUTILUS scene data — see §2). What is still not converted is the
  pattern *data*: a KRONOS user drum track pattern (U bank) has no
  NAUTILUS equivalent, so the reference is kept and reported, same as in
  the N→K direction.

## Further reading

- `docs/NAUTILUS_TO_KRONOS_V162_FIX.md` — the byte-level root-cause
  analysis and the v1.6.2 fix (with the full zone B mapping table).
- `docs/NAUTILUS_ZONE_B_ANALYSIS.md` — the NAUTILUS zone B decode the
  drum track rebuild uses.
- The user manual (`pcglib_manual.md`), chapter 9 "Converting between
  the instruments", section 9.3.
