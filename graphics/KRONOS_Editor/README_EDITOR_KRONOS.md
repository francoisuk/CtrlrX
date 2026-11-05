# KRONOS KONTROL — EDITOR window artwork

Artwork for the **EDITOR** window of the Kronos Kontrol CTRLR panel (opened by the EDITOR button of the Main panel),
and the same window for the OASYS (OASYS OMNI) and the NAUTILUS (NAUTILUS NAVIGATOR). Same size, look and fonts as
the Main panels: **1500 × 432** px (1 unit = 1 px; 1500 × 414 until 3 Nov 2026), @2x versions at 3000 × 864.

There are two sets of pages:

| Set | Folder | What it is for |
|---|---|---|
| **0.97i** | `0.97i\Program`, `0.97i\Combi` | Redesign of the editor **as panel complet-0.97i is today** (`..\EDITOR_WINDOW.md`): same modulators (`kkF_…`, `kkC_…`), hand-designed pages. Use it to re-skin the current Lua code. |
| **Full** | `Full\…` (one zip per object) | The **complete editor**: every parameter of every object of the instrument, generated from Korg's MIDI Implementation tables, with the address of each parameter in the dump. Use it to build the editor that covers everything. |

Why two sets, and what 0.97i is missing: see **`GAPS_0.97i_vs_KRONOS.md`**. How every page is drawn, and how to
regenerate or extend them: see **`RECIPES_GUI_DRAWING.md`** and the scripts in **`sources_Editor\`**.

## 1. The 0.97i set

### Program (24 tabs, 14 drawings)

When two tabs have exactly the same parameters, they share one drawing; only the dynamic text changes (written by the
Lua code, not part of the background).

| Drawing (`KRONOS_KONTROL_EDITOR_<page>`) | Tabs it serves | What changes between the tabs |
|---|---|---|
| `GENERAL` | General | — |
| `COMMON` | Common | — |
| `OSC` | OSC1, OSC2 | the lit tab; `param` = OSC1 modulators (`kkF_02_…`), `param_alt` = OSC2 (`kkF_03_…`) |
| `EXI_MIX` | EXi1 Mix, EXi2 Mix | **same drawing, only the EXi name changes** (display `kkEdExiName`, e.g. "EXi 1 : AL-1" / "EXi 2 : …"); `param` = EXi1 (`kkF_04_…`), `param_alt` = EXi2 (`kkF_05_…`) |
| `E_AL1` … `E_EP1` (8) | Engine 1 and Engine 2 of each EXi engine | the ENGINE display (`kkEdEngine`: "ENGINE 1" / "ENGINE 2"); `param` = Engine 1 (`kkF_06_…` to `kkF_13_…`), `param_alt` = Engine 2 (`kkF_14_…` to `kkF_21_…`) |
| `IFX` | IFX 1-12 | — |
| `MFX_TFX` | MFX·TFX | — |

The `_fond` backgrounds have no lit tab and no display text, so a single background works for both tabs.
Correction from Korg's tables: the parameter `kkF_04_012` / `kkF_05_012` (labelled "Amount A" a second time in the
specification) is **"Offset: Amount"**; it is labelled OFFSET AMOUNT.

### Combi (43 tabs, 9 drawings)

The 43 tabs do not fit on one line: one line of pages (GENERAL, VECTOR, DRUM TRACK, IFX 1-4, IFX 5-8, IFX 9-12,
MFX·TFX, AUDIO IN, LFO & CTRL) + a **timbre selector 1-16** + **PAGE 1 / 2**. `kkEdTabsC` keeps its 43 tabs with its tab
strip hidden: timbre t, page p → tab 9 + 2t + (p − 1). One TIMBRE page 1 and one TIMBRE page 2 serve the 16 timbres;
the timbre parameters are regrouped by function between the two pages. GENERAL shows tabs 0 and 1, LFO & CTRL tabs 9
and 10, IFX one drawing for tabs 4, 5 and 6 (`param_alt` = [IFX 5-8, IFX 9-12]; IFX 11 has no Chain To, IFX 12 no
Chain). The TIMBRES table on GENERAL (program of each timbre) is a proposal: it is not in 0.97i.

## 2. The complete editor (`Full`)

| Object | Folder / zip | Navigation (areas · index · pages) |
|---|---|---|
| Program | `Program` | GENERAL, OSC, FILTER, AMP, LFO·MIX (OSC 1-2), COMMON MOD, EXi (EXi 1-2), STEP SEQ, ENGINE ▸, EFFECTS, FX EDIT ▸, VECTOR, CONTROL (controllers, Tone Adjust), DRUM TRACK, AUDIO IN, KARMA, KARMA GE |
| EXi engines | `Engine_<name>` | MAIN, OSC, FILTER, AMP·MIX, EG, LFO, MOD, FX (by engine) — `◀ PROGRAM` returns to the program |
| Combi | `Combi` | GENERAL, TIMBRE (1-16), EFFECTS, FX EDIT ▸, VECTOR, CONTROL, DRUM TRACK, AUDIO IN, KARMA, KARMA MODULE (A-D) |
| Song | `Song` | SONG, MIDI TRACKS (1-16), AUTOMATION, AUDIO TRACKS, PATTERNS, RPPR, TIMBRE SET ▸ (= Combi pages) |
| Global | `Global` | BASIC, CONTROLLER, MIDI, EXT SETS (1-128), AUDIO IN, OCTAVE SCALES (1-16), ALL NOTE SCALE, CATEGORIES |
| Drum Kit | `DrumKit` | GENERAL, NOTE (1-128) |
| Wave Seq | `WaveSeq` | GENERAL, STEP (1-64) |
| Set List | `SetList` | SET LIST, SLOT (0-127) |
| Effects | `Effects` | FX EDIT: one background (`…_FX_TEMPLATE_fond`) and one mock-up (`…_FX_TEMPLATE_maquette`) for the 16 effect slots; `FX_LAYOUTS.json` gives, for each of the 197 effect types, its name and the parameter of each of the 40 cells (label, type, range): the editor writes the effect name in the name field and fills the cells from it — no image per effect |

▸ = link to another set of pages.

- **Header** (all pages of the complete editor): the 0.97i header + **WRITE TO** (destination bank + number) and
  **COMPARE**, which 0.97i does not have.
- **Index selector**: only the first instance is drawn (OSC 1, TIMBRE 1, NOTE 1…); the others use the same layout.
  The `index` block of each `_layout.json` gives the instances and `stride_bytes`: OFS(instance n) = OFS(instance 1) +
  (n − 1) × stride. Where Korg lists only a few instances (Drum Kit notes, Wave Seq steps, Set List slots), the
  structure is the same for all.
- **Every control** of a `_layout.json` has a `korg` block: source file, OFS, bit field, SysEx fields
  (TYP / SOC / SUB / PID / IDX when Korg gives them), data range (hex) and value range.
- **Visibility** (`apply`): `hd1` / `exi` for program areas, `exi:<engine>` for engine pages, as in 0.97i.
- **INDEX.json** in each object folder lists the areas, their pages, instances and rules.
- **Planches** (`PLANCHE_FULL_<object>_<n>.png`): contact sheets of the pages, in navigation order, for review.

## 3. Files per page

| File | Content |
|---|---|
| `<page>_maquette.png` (`.jpg` for OASYS and NAUTILUS) | one mock-up per page, with example values (for review only) |
| `<page>_fond.png`, `_fond@2x.png` | background for the editor: no knobs, no lit bars, no display text |

Only what the editor needs is kept. SVG files and @2x mock-ups can be regenerated with the scripts (`GFX_EXTRAS=1`).
| `<page>_layout.json` | position, type, range, visibility and source of every control |

Example values (names, effects, numbers) are only examples.

## 4. Other instruments

`OASYS_Editor\` and `NAUTILUS_Editor\` hold the same complete editor in the OASYS OMNI and NAUTILUS NAVIGATOR skins,
each with a README giving its differences (structure of the instrument, missing or extra objects).
