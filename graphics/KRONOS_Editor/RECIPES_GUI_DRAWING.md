# Kronos Kontrol EDITOR — drawing recipes

How every page of the EDITOR window is drawn, so that a programmer (CTRLR / Lua, JUCE / VST3) or a designer can
redraw, extend or re-skin it. All the pages are produced by the scripts in `sources_Editor\`; this document gives the
rules those scripts follow. Units are pixels of the 1x PNG (1500 × 432; 414 until 3 Nov 2026), origin top-left; multiply by 2 for @2x.

## 1. Canvas and chassis (same as the Main panel)

| Element | Recipe |
|---|---|
| Canvas | 1500 × 432, rounded rect rx 4, face = vertical gradient `face` of the theme, 2 px black outline |
| Rack ears | x 0-46 and 1454-1500, gradient `ear`; 3 oval holes per ear (22 × 12, rx 6) at y 40, 207, 374, fill `hole` |
| Ear joints | 2 px lines at x 46 and 1454 |
| Logo | Kronoscopie logo (`logo_kronoscopie.svg`) 40 × 40 at x 1397, y 17 |
| Useful width | x 60 → 1440 (1,380 px) |
| No vertical dividers | the Main panel's two section dividers (x 468, 948) are removed on the EDITOR pages |

## 2. Theme tokens (`themes.py`)

Every colour comes from the theme, so the same page re-skins for OASYS OMNI and NAUTILUS NAVIGATOR by changing the
theme only. KRONOS KONTROL values:

| Token | Value | Used for |
|---|---|---|
| `face` | `#262628` → `#1b1b1d` → `#141415` | face gradient |
| `hline` | `#2e2e31` | frames of sections, rules |
| `title`, `title_font` | `#e0e0e0`, Inter 700, 10.5, spacing 1 | section titles (9.5 on EDITOR pages) |
| `btn` | `#3a3a3d` → `#1e1e20`, stroke `#000`, text `#f2f2f2`, rx 2.5 | buttons |
| `lit` / `lit_mode` | `#3fb6ff` / `#ffd23f` | lit bar: blue = on, yellow = current page / mode |
| `oled` | `#36b6ff` → `#0f86e0`, text `#04203a`, frame `#050608`, glow | displays, menus, value boxes |
| `knobg`, `knobtop` | radial `#3c3c3f` → `#09090a`, `#4a4a4e` → `#151517` | knob body and cap |
| `ring_on` / `ring_off` | `#1ea7ff` / `#0e2a40`, width 3.2 | knob ring |
| `msg` | `#fff8d6` → `#f4e7a8`, text `#3a3000` DejaVu Sans Mono | status line (same as the Main SysEx / Lua field) |
| Captions | `#b9c0c7` (labels), `#8a96a3` (secondary notes) | small labels |

Fonts: **Inter** (Light 300 logo, SemiBold 600 labels, Bold 700 buttons / titles, ExtraBold 800 big displays),
**DejaVu Sans Mono** (status line), and for the other themes **Michroma** (OASYS) and **Montserrat** (NAUTILUS).
In the SVG files all text is converted to paths (`txt2path_ext.py`), so no font is needed to display them.

## 3. Primitives

| Primitive | Function | Geometry |
|---|---|---|
| Button | `kt.bt(x, y, w, h, label, lit)` | shadow (y + 1.2), body gradient `btn`, 0.8 px highlight line, lit bar = rect (x + 3, y + 2.2, w − 6, 2) with glow; label Inter 700, centred, size 7-8.5 |
| Display | `kt.oled(x, y, w, h)` | frame rect (x − 3, y − 3, w + 6, h + 6) rx 2, inner gradient `oled` with glow |
| Menu | display + `▼` | ▼ in Inter 6.5 at the right edge (x + w − 4) |
| Knob | `kt.knob(cx, cy, r)` | ring radius r + 7, 270° arc from 135°, value arc in `ring_on`; body r, cap 0.72 r, white index line |
| Knob cell | `ked.knobcell` | 2-line label (Inter 600, 7 pt, uppercase) at y + 7 / y + 15; knob r 12 centred at y + 38 (r 17 at y + 46 on engine pages); value box 38 × 11 under it |
| Menu cell | `ked.menucell` | label at y + 7, menu 16 px high at y + 12 |
| Toggle | `ked.toggle` | button 18 px high; lit bar = On (Off / On parameters of Korg) |
| Section box | `ked.box(x, y, w, h, title)` | rounded rect rx 5, black 16 %, 1 px `hline`; title Inter 700 9.5 spacing 1 at (x + 10, y + 15); optional note right-aligned, 7 pt `#8a96a3` |
| Table | `kfull.draw_T` | label column 150 px; column headers at y + 30; rows every 21 px from y + 36; cells 16 px high, 4 px apart |
| Table cell | `kfull.cell` | toggle = small button; menu = display with ▼; number = **value box** (display, drag to change) |
| Matrix | `kfull.draw_M`, `draw_M2` | 16 cells per row with their own small label; 2-D matrices: rows = first index (e.g. scene), columns = second (switch) |

## 4. Page frame (every EDITOR page)

| Zone | Content | Coordinates |
|---|---|---|
| Title | `EDITOR`, Inter 700 12, spacing 2.2 | x 60, baseline 34 |
| Object menu | `OBJECT` caption + menu 112 × 16 (`kkObjSel`) | x 140, y 29 |
| Title display | 300 × 16 (`kkEdTitle`) | x 266, y 29 |
| Action buttons | READ SOUND, APPLY → 0x4B, WRITE → 0x49, STORE 0x4C, READ BANK 0x4D, 20 px high, 6 px apart | from x 586, y 27 |
| WRITE TO (complete editor) | caption, bank menu 58 × 16, number box 36 × 16, COMPARE 70 × 20 | after the action buttons |
| ◀ RACK | 76 × 20 | x 1306, y 27 |
| Status line | 506 × 13, pale yellow, ends at the right edge of the title display | x 60, y 54 |
| Navigation bar | captions at y 79 (7 pt grey + rule), buttons 18 px high at y 84; bottom rule at y 108 | x 60 → 1440 |
| Content | two rows of 138 px (y 114 and 260) or one row of 284 px | x 60 → 1440, gaps 8 |

### Navigation bar
- **0.97i pages (Program, Combi):** see `README_EDITOR_KRONOS.md` (24-tab bar for the Program; pages + timbre selector
  1-16 + page 1 / 2 for the Combi).
- **Complete editor:** three groups on one line, stretched to the full width:
  `AREAS` (one button per area of the object) · `INDEX` (instance selector: OSC 1-2, TIMBRE 1-16, MODULE A-D…;
  buttons up to 16 instances, otherwise ◀ display ▶) · `PAGE` (buttons up to 8 pages, otherwise ◀ n / N ▶).
  The current area, instance and page have the yellow lit bar. Engine pages start with a `◀ PROGRAM` button,
  FX EDIT pages with `◀ BACK` and the 16 effect slots.

## 5. How a page of the complete editor is built (`kmodel.py`, `kfull.py`)

1. **Read the Korg table** (`kdata.parse`): group, name, data range, value range, OFS, bit, SysEx fields.
2. **Choose the control** (`kdata.kind`): `Off~On` → toggle; numeric range or more than 24 steps → knob (value box in
   tables); anything else → menu; names → text field; UUIDs, `(fixed)` and reserved bytes are not drawn.
3. **Areas**: each object has a list of areas (regular expressions on Korg group names). An area may have an
   **index**: the instance number is taken out of the group name (`OSC1` → `OSC#`), only the first instance is drawn,
   and the layout says how to reach the others (`index.instances`, `stride_bytes`).
4. **Sections**: one per Korg group, split by the `(…)` prefix of the parameter names (e.g. `KARMA Common · Dynamic MIDI`).
5. **Blocks**, inside a section:
   - repeated names (`Zone1 MS Level`, `Step Value12`, `(Scene3) Switch5`) become a **table** (one column per
     instance, up to 16 columns, up to 11 rows) or a **2-D matrix**;
   - knobs go in a **K block** (one line of menus / toggles + one row of knobs, up to 22 knobs);
   - menus, toggles and texts that do not fit go in a **G block** (grid of up to 3 lines);
   - many single values of the same kind (note map, category names) go in an **M block** (16 per row).
6. **Pagination**: half-height blocks first, two rows per page, each row stretched to the full width (stretch
   factor capped at 1.6; narrower rows are centred); full-height blocks (tables of more than 4 rows, matrices)
   then share full-height pages.
7. **Labels**: Korg names in capitals, on 1 or 2 lines of 11 characters, with standard abbreviations
   (Intensity → Int, Source → Src, Frequency → Freq, Velocity → Vel…).
8. **Example values**: the first value of the range, or 0 when the range crosses 0. They are only examples.

## 6. FX EDIT (`kfx.py`)

One background for all 197 effect types: an EFFECT strip (type menu, ON) and a grid of **40 cells** (10 × 4,
132.6 × 58, 6 px apart, from x 60, y 162). Each cell: label (dynamic) at the top; knob r 10 + value box, or menu, or
button. `FX_LAYOUTS.json` lists, for each type, the parameter of each cell: `pid` (parameter ID in Effect.txt),
name, control kind, data and value range. Effects with more than 40 parameters use page 2 (one type has 68).

## 7. Files and backgrounds

| File | Content |
|---|---|
| `<page>_maquette.png` | one mock-up per page, with example values (1x) |
| `<page>_fond.png`, `_fond@2x.png` (`_fond.svg` with `GFX_EXTRAS=1`) | background for the editor: frames, labels and button bodies stay; knobs, lit bars and the text of every display are removed (the editor draws them) |
| `<page>_layout.json` | one entry per control: `id`, `type`, `kind`, `x, y, w, h` (knobs: `cx, cy, r`), `range`, `apply`, and in the complete editor `korg` (file, OFS, bit, SysEx fields, data, value) |
| `INDEX.json` (one per object) | areas, number of pages, instance selector and visibility rule of each area |
| `FX_LAYOUTS.json` | cell → parameter map of the 197 effect types |

## 8. Regenerating and extending

Requirements: Python 3, `cairosvg`, `fonttools`, `brotli`, `numpy`, `Pillow`; Inter and DejaVu Sans Mono installed
(or `FONT_DIR`), Michroma / Montserrat in `sources_Editor\fonts`; Korg's MIDI Implementation tables in a folder given by
`KRONOS_MIDIIMP` (for the NAUTILUS: its own `SysExDumps` folder).

```
python ked.py <out>                 # 0.97i Program pages (14 drawings)
python ked_combi.py <out>           # 0.97i Combi pages (9 drawings)
python kfull.py <out> [PROGRAM ENGINES COMBI SONG GLOBAL DRUMKIT WAVESEQ SETLIST]   # complete editor
python kfx.py <out>\Effects         # FX EDIT background + 197 effect layouts
set KFULL_THEME=OASYS_OMNI          # or NAUTILUS_NAVIGATOR: same pages in another skin
set KFULL_FAST=1                    # 1x PNG only (quick proofs)
```

- **New area or new grouping**: edit the area list of the object in `kfull.py` (`program_areas`, `combi_areas`…);
  regular expressions are matched on Korg group names.
- **Hand-made page**: write a function that draws into `s` with the primitives above (see `ked.page_general`) and
  render it with `kfull.render_page`.
- **New skin**: add a theme to `themes.py` (same tokens) and select it with `KFULL_THEME`.
