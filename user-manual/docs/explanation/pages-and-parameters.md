# Pages and parameters model

How the 215 numbered pages plus the FX EDIT template (216 page views in all)
and the 7 247 parameters are organised, and how a page's controls map to
KRONOS bytes.

## Page sets per object

Pages are generated from Korg parameter tables at build time and embedded as Lua
data (`KRONOS_FULL`). Each object has its own page set; page titles follow the
pattern `AREA · n/m`:

| Object | Pages | Areas (grouped) |
|---|---|---|
| Program | 156 | GENERAL; OSC 1–3; FILTER 1–4; AMP 1–3; LFO·MIX; COMMON MOD; EXi; STEP SEQ; EFFECTS; VECTOR; CONTROL; DRUM TRACK; AUDIO IN; KARMA 1–8; KARMA GE 1–4; then per engine (AL-1 18, CX-3 5, STR-1 22, MS-20EX 17, PolysixEX 11, MOD-7 36, SGX-2 1, EP-1 6) |
| Combi | 33 | GENERAL; TIMBRE 1–3; EFFECTS; VECTOR; CONTROL; DRUM TRACK; AUDIO IN; KARMA 1–8; KARMA MODULE 1–13 |
| Drum Kit | 3 | GENERAL; NOTE 1–2 |
| Wave Sequence | 2 | GENERAL; STEP |
| Global | 13 | BASIC 1–3; CONTROLLER; MIDI; EXT SETS; AUDIO IN; OCTAVE SCALES; ALL NOTE SCALE; CATEGORIES |
| Set List | 2 | SET LIST; SLOT |
| Song | 6 | SONG; MIDI TRACKS; AUTOMATION; AUDIO TRACKS; PATTERNS; RPPR |

Pages with an **instance** (OSC 1/2, TIMBRE 1–16, NOTE 1–128, EXi slot) store a
`base` + `stride`: the panel computes the byte offset of the instance
(`KK.edOff`) and reads/writes the same parameter fields at that offset. The
INDEX part of the navigation bar switches instances.

The complete directory with every page index, title and area:
[Editor page directory](../reference/pages.md).

## Parameter model

Each of the **7 247 parameters** is a table entry with:

| Field | Meaning |
|---|---|
| `nm` | display name (e.g. *Chord Mode*) |
| `sec` | section (page title) |
| `kind` | `slider` (continuous) or `combo` (list) — 4 657 sliders, 2 590 combos |
| `pcs` | bit-level location: absolute byte offset(s) + bit range, least-significant first |
| `w` | width in bits |
| `rmin`, `fr` | raw range (`rmin`…`rmin+2^w−1`, display steps `0…fr`) |
| `dmin`, `f` | display value = `dmin + idx × f` |
| `labels` | combo item names |
| `inv` | inverted polarity (bit set = On) |
| `set` | object set: prog / combi / kit / wsq / global / setlist / song |
| `apply` | applicability: `all`, `hd1`, `exi`, `engineN`, `engine2N`, `exi:<ENGINE>` |
| `sx` | present on 528 parameters: live *Parameter Change* (`0x43`) address (TYP/SOC/SUB/PID/IDX) — sent immediately on edit instead of patching the dump |

Distribution by set: prog 5 080, combi 1 448, kit 145, global 471,
setlist 22, song 49, wsq 32.

## Read / write mechanics

- The panel reads a field with pure arithmetic on the dump bytes (Lua 5.1 has no
  bit operators): each `pcs` piece contributes its bits, little-endian across
  the width. Truncated dumps yield "hidden parameter" instead of errors.
- Writing patches the same bits in the local dump (`kkEdWriteField`); **Apply**
  sends the whole dump (`0x4B`). Parameters with `sx` bypass the dump and are
  sent at once as Parameter Change.
- Display index ↔ raw value conversion honours `inv`, `rmin`, `fr`.

## Why controls appear/disappear

When a page is shown, each pooled control is bound to a parameter; if the
parameter is not applicable to the current object/program type
(`kkEdApplyOk`: wrong set, HD-1 vs EXi, wrong engine), the control is hidden
and edits are refused with an explanatory status message. The GENERAL page
switches between its HD-1 and EXi variants automatically based on the current
program.
