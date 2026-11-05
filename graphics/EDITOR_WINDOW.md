# Kronos Kontrol - EDITOR window specification

Version of the panel this spec describes: **`complet-0.97i`** (the screen captures, `editor_<n>_<page>.jpg` in `11_Graphics_ideas\ideas`, were taken
from the 0.97i build, so their on-screen strings are still partly French; the **target strings
below are the English ones** the 0.97j build ships). Coordinates are in panel pixels, origin
top-left of the panel, panel native size **1500 x 414**.

Sources of truth for this document:

- `panels/KronosKontrol/sources/editor_layout.json` - generated pages (idx, title, params with x/y/w/h/kind/range/labels).
- `panels/KronosKontrol/data/kronos_editor.lua` - the `p` table: SysEx mapping per parameter (`sec`, `nm`, `apply`, `set`, `pcs`, `w`, `rmin/fr`, `dmin/f`, `labels`).
- `panels/KronosKontrol/sources/build_panel.py` - the fixed (hand-placed) Editor controls: title, status, action buttons, object selector, tab bars, and the per-object "General" tab.
- `panels/KronosKontrol/scripts/gen_editor_lua.py` - generates the two files above.

---

## 1. When the Editor window appears

The main panel has two top-level tabs (`kkTabs`): tab 0 = **RACK** (the control surface), tab 1 = **EDIT**.
Clicking the **EDITOR** button on the RACK tab switches to tab 1, which is the Editor window. It is the
full panel area (1500 x 414). The **`< RACK`** button (top-right) switches back to tab 0.

The Editor edits the object currently held in the Kronos **edit buffer** (received via SysEx `0x4B` dump,
or loaded from a PCG file with **IMPORT >**). Five object types are supported, selected with the
**object selector** combo (see 2.4). Only one section-tab-bar is visible at a time, matching the
current object type (`kkEditShow` in `lua/kkEd.lua`):

| Object type | Selector idx | Tab bar modulator | Dump obj | Generated params | Pages |
|---|---|---|---|---|---|
| Program | 0 | `kkEdTabs` | 0x4B dump obj 01 (Program) | 404 | 24 |
| Combi | 1 | `kkEdTabsC` | 0x4B dump obj 02 (Combi) | 1930 | 43 |
| Drum Kit | 4 | `kkEdTabsK` | 0x4B dump obj 04 (Drum Kit) | 71 | 6 |
| Wave Seq | 5 | `kkEdTabsW` | 0x4B dump obj 05 (Wave Sequence) | 28 | 3 |
| Global | 3 | `kkEdTabsG` | 0x4B dump obj 03 (Global) | 591 | 15 |

> Total generated parameters across all object types: **3024**.

---

## 2. Window frame (common to every object type)

These controls sit above the tab bar and are identical for all five object types. They live on
panel tab 1 (`EDIT`), not inside any section tab.

### 2.1 Title row (y 14-36)

| Modulator | Type | Rect (x y w h) | Text | Font | Notes |
|---|---|---|---|---|---|
| `kkEdTitle` | label | `30 14 700 22` | `EDITOR - <Object> current (dump 0x4B)` | 15pt bold, light (`#e8e8e8`), centredLeft | Title; object name filled by `kkEditShow` |
| `kkBtnToRack` | button | `1390 14 90 22` | `<= RACK` | button text | Callback `kkClick`; switches back to RACK tab |

### 2.2 Status line (y 44-60)

| Modulator | Type | Rect (x y w h) | Text | Font | Notes |
|---|---|---|---|---|---|
| `kkEdStatus` | label | `30 44 1440 16` | (dynamic) | 10pt, grey (`#9aa4ad`), centredLeft | One-line status: dump obj/version/byte count, write progress, Reply 24 result, errors |

### 2.3 Action row (y 66-90)

Six action buttons. Each has a thin **lit bar** on top (the blue/yellow indicator) created by `lit()`.
The lit bar is the "on/active" indicator; it is driven from Lua.

| Modulator | Lit bar | Rect (x y w h) | Text | Callback | Meaning |
|---|---|---|---|---|---|
| `kkBtnGetProg` | `kkLitGetProg` | `30 66 170 24` | `Read sound` | `kkClick` | Request a `0x4B` dump of the current object from the Kronos into the edit buffer |
| `kkBtnApply` | `kkLitApply` | `210 66 180 24` | `Apply -> 0x4B` | `kkClick` | Send the (edited) local dump back to the edit buffer (`0x4B`). Edit-buffer only, non-destructive |
| `kkBtnWrite` | `kkLitWrite` | `400 66 170 24` | `Write -> 0x49` | `kkClick` | Copy the dump into the selected slot (`0x49`). Not yet saved to non-volatile memory |
| `kkBtnStore` | `kkLitStore` | `580 66 170 24` | `Store 0x4C` | `kkClick` | Save the bank to non-volatile memory (`0x4C`). Two-click confirm (armed window) |
| `kkBtnBankRead` | `kkLitBankRead` | `760 66 190 24` | `Read bank 0x4D` | `kkClick` | Read a whole bank (128 objects) from the Kronos (`0x4D`) |
| `kkObjSel` | - | `960 66 220 24` | combo | `kkObjChanged` | Object-type selector (see 2.4) |

Button style (from `button_text`): dark fill, light text, 10pt. Lit bar = 2px-high bar at the top
edge of the button rect (same x/y/w as the button).

### 2.4 Object selector `kkObjSel`

| Modulator | Type | Rect (x y w h) | Content | Callback |
|---|---|---|---|---|
| `kkObjSel` | combo | `960 66 220 24` | `0 : Program` / `1 : Combi` / `4 : Drum Kit` / `5 : Wave Seq` / `3 : Global` | `kkObjChanged` |

Selecting an object type switches which section-tab-bar is shown and re-runs `kkEditShow` (repopulates
the General tab and shows/hides the matching tab bar). It does **not** by itself request a dump; use
**Read sound** to fetch the object.

---

## 3. Section tab bars (y 92-116)

Each object type has its own `uiTabs` modulator occupying rect `0 92 1500 322` with `uiTabsDepth = 24`
(a 24px-tall tab strip at the top of that rect, content below). Only one of the five is visible at a
time. Tab 0 of each bar is always the **General** tab (hand-placed controls, see section 4.2-4.4);
tabs 1..N are the generated pages (see section 6). Tab background colour: `#1b1b1d`.

### 3.1 Program - `kkEdTabs` (24 tabs)

| Tab | Title | Params | Kinds |
|---|---|---|---|
| 0 | Général | 0 | - |
| 1 | Commun | 45 | combo=25, slider=20 |
| 2 | OSC1 | 52 | combo=12, slider=40 |
| 3 | OSC2 | 52 | combo=12, slider=40 |
| 4 | EXi1 Mix | 23 | combo=3, slider=20 |
| 5 | EXi2 Mix | 23 | combo=3, slider=20 |
| 6 | E1 AL-1 | 10 | combo=5, slider=5 |
| 7 | E1 CX-3 | 10 | combo=5, slider=5 |
| 8 | E1 STR-1 | 10 | combo=2, slider=8 |
| 9 | E1 MS-20EX | 10 | combo=3, slider=7 |
| 10 | E1 PolysixEX | 10 | combo=2, slider=8 |
| 11 | E1 MOD-7 | 10 | combo=5, slider=5 |
| 12 | E1 SGX-2 | 10 | combo=1, slider=9 |
| 13 | E1 EP-1 | 10 | combo=2, slider=8 |
| 14 | E2 AL-1 | 10 | combo=5, slider=5 |
| 15 | E2 CX-3 | 10 | combo=5, slider=5 |
| 16 | E2 STR-1 | 10 | combo=2, slider=8 |
| 17 | E2 MS-20EX | 10 | combo=3, slider=7 |
| 18 | E2 PolysixEX | 10 | combo=2, slider=8 |
| 19 | E2 MOD-7 | 10 | combo=5, slider=5 |
| 20 | E2 SGX-2 | 10 | combo=1, slider=9 |
| 21 | E2 EP-1 | 10 | combo=2, slider=8 |
| 22 | IFX 1-12 | 36 | combo=12, fxcombo=12, slider=12 |
| 23 | MFX·TFX | 13 | combo=6, fxcombo=4, slider=3 |

### 3.2 Combi - `kkEdTabsC` (43 tabs)

| Tab | Title | Params | Kinds |
|---|---|---|---|
| 0 | Général | 0 | - |
| 1 | Commun | 5 | combo=3, slider=2 |
| 2 | Vector | 42 | combo=18, slider=24 |
| 3 | Drum Track | 11 | combo=6, slider=5 |
| 4 | IFX 1-4 | 44 | combo=24, fxcombo=4, slider=16 |
| 5 | IFX 5-8 | 44 | combo=24, fxcombo=4, slider=16 |
| 6 | IFX 9-12 | 41 | combo=23, fxcombo=4, slider=14 |
| 7 | MFX·TFX | 18 | combo=10, fxcombo=4, slider=4 |
| 8 | Audio In | 48 | combo=18, slider=30 |
| 9 | LFO & In | 15 | combo=9, slider=6 |
| 10 | Contrôleurs | 14 | combo=10, slider=4 |
| 11 | Timbre 1 | 60 | combo=35, slider=25 |
| 12 | Timbre 1·2 | 43 | combo=29, slider=14 |
| 13 | Timbre 2 | 60 | combo=35, slider=25 |
| 14 | Timbre 2·2 | 43 | combo=29, slider=14 |
| 15 | Timbre 3 | 60 | combo=35, slider=25 |
| 16 | Timbre 3·2 | 43 | combo=29, slider=14 |
| 17 | Timbre 4 | 60 | combo=35, slider=25 |
| 18 | Timbre 4·2 | 43 | combo=29, slider=14 |
| 19 | Timbre 5 | 60 | combo=35, slider=25 |
| 20 | Timbre 5·2 | 43 | combo=29, slider=14 |
| 21 | Timbre 6 | 60 | combo=35, slider=25 |
| 22 | Timbre 6·2 | 43 | combo=29, slider=14 |
| 23 | Timbre 7 | 60 | combo=35, slider=25 |
| 24 | Timbre 7·2 | 43 | combo=29, slider=14 |
| 25 | Timbre 8 | 60 | combo=35, slider=25 |
| 26 | Timbre 8·2 | 43 | combo=29, slider=14 |
| 27 | Timbre 9 | 60 | combo=35, slider=25 |
| 28 | Timbre 9·2 | 43 | combo=29, slider=14 |
| 29 | Timbre 10 | 60 | combo=35, slider=25 |
| 30 | Timbre 10·2 | 43 | combo=29, slider=14 |
| 31 | Timbre 11 | 60 | combo=35, slider=25 |
| 32 | Timbre 11·2 | 43 | combo=29, slider=14 |
| 33 | Timbre 12 | 60 | combo=35, slider=25 |
| 34 | Timbre 12·2 | 43 | combo=29, slider=14 |
| 35 | Timbre 13 | 60 | combo=35, slider=25 |
| 36 | Timbre 13·2 | 43 | combo=29, slider=14 |
| 37 | Timbre 14 | 60 | combo=35, slider=25 |
| 38 | Timbre 14·2 | 43 | combo=29, slider=14 |
| 39 | Timbre 15 | 60 | combo=35, slider=25 |
| 40 | Timbre 15·2 | 43 | combo=29, slider=14 |
| 41 | Timbre 16 | 60 | combo=35, slider=25 |
| 42 | Timbre 16·2 | 43 | combo=29, slider=14 |

### 3.3 Drum Kit - `kkEdTabsK` (6 tabs)

| Tab | Title | Params | Kinds |
|---|---|---|---|
| 0 | Général | 0 | - |
| 1 | Note 1 · Commun | 24 | combo=12, slider=12 |
| 2 | Note 1 · Zone 1 | 16 | combo=3, slider=13 |
| 3 | Note 1 · Zones 2-8 | 21 | combo=7, slider=14 |
| 4 | Note 2 | 5 | combo=5 |
| 5 | Note 128 | 5 | combo=5 |

### 3.4 Wave Seq - `kkEdTabsW` (3 tabs)

| Tab | Title | Params | Kinds |
|---|---|---|---|
| 0 | Général | 0 | - |
| 1 | Commun | 12 | combo=1, slider=11 |
| 2 | Steps | 16 | combo=2, slider=14 |

### 3.5 Global - `kkEdTabsG` (15 tabs)

| Tab | Title | Params | Kinds |
|---|---|---|---|
| 0 | Général | 0 | - |
| 1 | Basic | 30 | combo=23, slider=7 |
| 2 | Controller | 34 | combo=3, slider=31 |
| 3 | MIDI | 21 | combo=18, slider=3 |
| 4 | MIDI Ext Set 1 | 60 | combo=30, slider=30 |
| 5 | Octave Scale | 60 | slider=60 |
| 6 | Octave Scale·2 | 60 | slider=60 |
| 7 | Octave Scale·3 | 60 | slider=60 |
| 8 | Octave Scale·4 | 12 | slider=12 |
| 9 | All Note Scale | 60 | slider=60 |
| 10 | All Note Scale·2 | 60 | slider=60 |
| 11 | All Note Scale·3 | 8 | slider=8 |
| 12 | Audio In | 48 | combo=18, slider=30 |
| 13 | Assignments | 60 | combo=30, slider=30 |
| 14 | Assignments·2 | 18 | combo=9, slider=9 |

---

## 4. Content area (y 116-414)

### 4.1 Generated-control pattern (tabs 1..N, all object types)

Every generated parameter occupies a **cell** of width `w` (usually 146px) and row height `h` = 47px,
laid out on a grid starting at x=5, y=116. Inside a cell at `(x, y)`:

| Element | Rect (relative to cell) | Style |
|---|---|---|
| Label `<name>L` | `(x, y, w, 11)` | 8pt, grey (`#9aa4ad`), centredLeft, not bold. Text = the param `label` (`Section - Name`) |
| Knob (slider) `<name>` | `(x+55, y+12, 36, 36)` | `RotaryVerticalDrag`; fill `#1ea7ff`, outline `#0b2233`, thumb `#e8e8e8`, track `#101012`; value text dark |
| Combo (combo) `<name>` | `(x, y+13, w, 20)` | dark fill `#2a2f36`, outline `#3a4150`, arrow/text light, 8pt centredLeft; content = param `labels` |
| FX combo (fxcombo) `<name>` | `(x, y+13, w, 20)` | same combo style; content = the shared FX-type list (331 entries, `0 : <name>` ... `330 : <name>`) |

All generated controls fire `luaModulatorValueChange = kkEdField` and send MIDI as CC (`midiMessageType = 9`).
Slider ranges come from `min/max/interval/decimals` in the layout; combos from `labels`.

### 4.2 General tab (tab 0) - Program (`kkEdTabs` tab 0)

Hand-placed. Two zones: a **read-only display** zone (top) and an **edit** zone (bottom).

Read-only display (E1):

| Modulator | Type | Rect (x y w h) | Caption | Font |
|---|---|---|---|---|
| `kkEdName` | label (editable on double-click) | `100 116 340 24` | `kkCapName` = `Name` at `30 122 60 14` | 14pt light |
| `kkEdVer` | label | `530 116 90 24` | `kkCapVer` = `Version` at `460 122 70 14` | 12pt light |
| `kkEdCat` | label | `140 150 220 24` | `kkCapCat` = `Category` at `30 156 100 14` | 12pt light |
| `kkEdScale` | label | `580 150 220 24` | `kkCapScale` = `Scale` at `510 156 65 14` | 12pt light |
| `kkEdExi1` | label | `100 184 240 24` | `kkCapExi1` = `EXi 1` at `30 190 60 14` | 12pt light |
| `kkEdExi2` | label | `430 184 240 24` | `kkCapExi2` = `EXi 2` at `360 190 60 14` | 12pt light |
| `kkEdIFX` | label | `120 218 1350 24` | `kkCapIFX` = `IFX 1-12` at `30 224 80 14` | 11pt light |
| `kkEdMFX` | label | `120 252 400 24` | `kkCapMFX` = `MFX 1-2` at `30 258 80 14` | 12pt light |
| `kkEdTFX` | label | `620 252 400 24` | `kkCapTFX` = `TFX 1-2` at `540 258 70 14` | 12pt light |

`kkEdName` is editable: double-click to edit (max 24 chars), callback `kkEdNameEdit` patches the name
into the local dump. Captions (`kkCap*`) are 10pt grey labels.

Edit zone (E2, y 292-360):

| Modulator | Type | Rect (x y w h) | Caption | Range | Callback |
|---|---|---|---|---|---|
| `kkEdTitle2` | label | `30 292 420 14` | `Edit (E2) - levels (real-time fn 43) & IFX1` | - | - |
| `kkEdP1` | knob | `40 322 36 36` | `kkCapP1` = `OSC1/EXi1 Level` at `30 308 105 12` | 0..127 | `kkEdP1` (real-time fn 43) |
| `kkEdP8` | knob | `160 322 36 36` | `kkCapP8` = `Master Vol` at `150 308 75 12` | 0..127 | `kkEdP8` (real-time fn 43) |
| `kkEdCatE` | combo | `370 152 120 22` | (in the read zone row) | category list | `kkEdCatEdit` |
| `kkEdScaleE` | combo | `810 152 90 22` | (in the read zone row) | scale list | `kkEdScaleEdit` |
| `kkEdIFX1` | combo | `270 324 180 22` | `kkCapIFX1` = `IFX1` at `270 308 50 12` | FX list | `kkEdIFX1Edit` |

`kkEdCatE` / `kkEdScaleE` sit on the Category/Scale rows (y 152) next to the read-only labels, and patch
the local dump. `kkEdP1`/`kkEdP8` are real-time level sends (SysEx fn 43), not dump patches.

Footer notes (y 366-410):

| Modulator | Rect (x y w h) | Text |
|---|---|---|
| `kkEdNote` | `30 366 1440 20` | E1 read-only note (name/version/category/scale/effect types) |
| `kkEdHint2` | `30 388 720 22` | Apply/Write/Store/Read-bank explanation |
| `kkEdHint` | `770 388 700 22` | "Controls outside the current program type are hidden" note |

### 4.3 General tab (tab 0) - Combi (`kkEdTabsC` tab 0)

Same idea, fewer fields (no EXi/IFX/MFX/TFX read rows, no E2 knobs):

| Modulator | Type | Rect (x y w h) | Caption | Font |
|---|---|---|---|---|
| `kkCEdName` | label (editable on double-click) | `100 116 340 24` | `kkCCapName` = `Name` at `30 122 60 14` | 14pt light |
| `kkCEdVer` | label | `530 116 90 24` | `kkCCapVer` = `Version` at `460 122 70 14` | 12pt light |
| `kkCEdCat` | label | `140 150 220 24` | `kkCCapCat` = `Category` at `30 156 100 14` | 12pt light |
| `kkCEdScale` | label | `580 150 220 24` | `kkCCapScale` = `Scale` at `510 156 65 14` | 12pt light |
| `kkCNote` | label | `30 366 1440 20` | E4 read-only note | 9pt grey |

Note: the Combi General tab currently has **no** edit combos for category/scale (read-only in v1).

### 4.4 General tab (tab 0) - Drum Kit / Wave Seq / Global

These three object types have **no editable fields** on their General tab - only a single explanatory
note label at `30 366 1440 20` (9pt grey):

| Object | Modulator | Note text (summary) |
|---|---|---|
| Drum Kit | `kkKNote` | obj 04, 38424 bytes, 71 params / 5 pages, edit buffer only (no slot write, no Store) |
| Wave Seq | `kkWNote` | obj 05, 2216 bytes, 28 params / 2 pages, edit buffer only |
| Global | `kkGNote` | obj 03, 24708 bytes, 591 params / 14 pages, edit buffer only |

---

## 5. Behavior, callbacks and guards

- **Populate**: `kkEditShow` (lua/kkEd.lua) runs when a dump arrives / object type changes. It fills the
  General-tab read labels from the dump, sets `kkEdTitle`, and calls `kkEdPopulateOne` for every generated
  control on the visible pages, writing each control's value from the dump via the `p` table mapping.
- **Edit a control**: `kkEdField(component, value)` patches the local dump in memory (byte/bit write per
  `pcs`/`w`) and, for the E2 real-time knobs, also sends SysEx fn 43. Nothing is sent to the Kronos until
  **Apply -> 0x4B** is pressed.
- **Visibility / guards**: generated controls whose `apply` does not match the current program type
  (HD-1 / EXi / engine N) are **hidden** (`kkEdPopulateOne`). The `apply` column in section 6 is that rule:
  `all` = always visible; `hd1` = HD-1 programs only; `exi` = EXi programs only; `engineN`/`engine2N` =
  a specific EXi engine on E1/E2. Combi/Kit/WSQ/Global params use `apply = combi`/`kit`/`wsq`/`global`.
- **Edit-buffer only (v1 safety)**: Apply uses `0x4B` (edit buffer). Write (`0x49`) and Store (`0x4C`) are
  gated: Write/Store are refused outside Program/Combi mode and on read-only/unknown banks; Store needs
  two clicks within a timeout. Drum Kit / Wave Seq / Global have **no** slot write and **no** Store.
- **Reply 24**: after Write/Store the panel watches for the Kronos `Reply 24` and reports OK / rejected
  (code) in `kkEdStatus`.
- **Tab change**: `kkEdTabChanged` repopulates the newly visible page (`kkEdPopulateOne` per control).

---

## 6. Per-page parameter tables (tabs 1..N)

Cell = `(x, y, w)` at row height 47. Label at `(x, y, w, 11)` (8pt grey). Control geometry and ranges per
the pattern in 4.1. `Apply` = visibility rule (see section 5). `Set` = which dump the param patches.

### 6.1 Program - `kkEdTabs` - 0x4B dump obj 01 (Program)

#### Tab 1 - Commun (45 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_01_001` | Common · Chord Mode | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Off \| 1 \| Advanced | all | prog |
| 2 | `kkF_01_002` | Common · Favorite | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | all | prog |
| 3 | `kkF_01_003` | Common · Hold | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Off \| On | all | prog |
| 4 | `kkF_01_004` | Common · Assign Mode | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Poly \| Mono | all | prog |
| 5 | `kkF_01_005` | Common · Single Trigger | `(601, 116, 146)` | combo `(601, 129)` 146x20 | Off \| On | all | prog |
| 6 | `kkF_01_006` | Common · Poly Legato | `(750, 116, 146)` | combo `(750, 129)` 146x20 | Normal \| Legato using | all | prog |
| 7 | `kkF_01_007` | Common · Key Priority | `(899, 116, 146)` | combo `(899, 129)` 146x20 | Low \| 1 \| Last | all | prog |
| 8 | `kkF_01_008` | Common · Legato | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | Normal \| Legato | all | prog |
| 9 | `kkF_01_009` | Common · Legato using S.Offset | `(1197, 116, 146)` | combo `(1197, 129)` 146x20 | Old Legato \| Legato u | all | prog |
| 10 | `kkF_01_010` | Common · Enable Half Damper | `(1346, 116, 146)` | combo `(1346, 129)` 146x20 | Off \| On | all | prog |
| 11 | `kkF_01_011` | Common · Unison Voices | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | 2..16 step 1.0 (0 dec) | all | prog |
| 12 | `kkF_01_012` | Common · Unison | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | all | prog |
| 13 | `kkF_01_013` | Common · Unison Detune | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..200 step 1.0 (0 dec) | all | prog |
| 14 | `kkF_01_014` | Common · Unison Thickness | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 | all | prog |
| 15 | `kkF_01_015` | Common · Chord Source | `(601, 165, 146)` | combo `(601, 178)` 146x20 | Pad 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| Pad 8 | all | prog |
| 16 | `kkF_01_016` | Common · Hold Bottom Key | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | all | prog |
| 17 | `kkF_01_017` | Common · Hold Top Key | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | all | prog |
| 18 | `kkF_01_018` | Common · Bus Select | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | all | prog |
| 19 | `kkF_01_019` | Common · Fx Control Bus | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| FX Control2 | all | prog |
| 20 | `kkF_01_020` | Common · Rec Bus | `(1346, 165, 146)` | combo `(1346, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | all | prog |
| 21 | `kkF_01_021` | Common · Max # of Notes | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Dynamic \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 | all | prog |
| 22 | `kkF_01_022` | Common · Stereo Spread | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..100 step 1.0 (0 dec) | all | prog |
| 23 | `kkF_01_023` | Common · Scale Key | `(303, 214, 146)` | combo `(303, 227)` 146x20 | C \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| B | all | prog |
| 24 | `kkF_01_024` | Common · Scale Random | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..7 step 1.0 (0 dec) | all | prog |
| 25 | `kkF_01_025` | Common LFO · Waveform | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Triangle \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| Random6(Co | all | prog |
| 26 | `kkF_01_026` | Common LFO · Stop | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | all | prog |
| 27 | `kkF_01_027` | Common LFO · Frequency | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..99 step 1.0 (0 dec) | all | prog |
| 28 | `kkF_01_028` | Common LFO · Frequency Fine | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..99 step 1.0 (0 dec) | all | prog |
| 29 | `kkF_01_029` | Common LFO · Shape | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | all | prog |
| 30 | `kkF_01_030` | Common LFO · Shape Mod.Source | `(1346, 214, 146)` | knob `(1401, 226)` 36x36 rotary | 0..40 step 1.0 (0 dec) | all | prog |
| 31 | `kkF_01_031` | Common LFO · Shape Mod.Intensity | `(5, 263, 146)` | knob `(60, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | all | prog |
| 32 | `kkF_01_032` | Common LFO · Offset | `(154, 263, 146)` | knob `(209, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | all | prog |
| 33 | `kkF_01_033` | Common LFO · Reset Source | `(303, 263, 146)` | knob `(358, 275)` 36x36 rotary | 0..40 step 1.0 (0 dec) | all | prog |
| 34 | `kkF_01_034` | Common LFO · MIDI Sync Base Note | `(452, 263, 146)` | combo `(452, 276)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | all | prog |
| 35 | `kkF_01_035` | Common LFO · MIDI Sync | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | all | prog |
| 36 | `kkF_01_036` | Common LFO · MIDI Sync Times | `(750, 263, 146)` | knob `(805, 275)` 36x36 rotary | 1..32 step 1.0 (0 dec) | all | prog |
| 37 | `kkF_01_037` | Common LFO · Frequency Mod.Source | `(899, 263, 146)` | knob `(954, 275)` 36x36 rotary | 0..40 step 1.0 (0 dec) | all | prog |
| 38 | `kkF_01_038` | Common LFO · Frequency Mod.Intensity | `(1048, 263, 146)` | knob `(1103, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | all | prog |
| 39 | `kkF_01_039` | Common LFO · Frequency Mod.Int.Mod.Source | `(1197, 263, 146)` | knob `(1252, 275)` 36x36 rotary | 0..40 step 1.0 (0 dec) | all | prog |
| 40 | `kkF_01_040` | Common LFO · Frequency Mod.Int.Mod.Intensity | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | all | prog |
| 41 | `kkF_01_041` | Common · Oscillator Mode | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Single \| 1 \| 2 \| 3 \| 4 \| Double Drums | hd1 | prog |
| 42 | `kkF_01_042` | Common · Use Drum.Inst Bus Select/Send | `(154, 312, 146)` | combo `(154, 325)` 146x20 | Off \| On | hd1 | prog |
| 43 | `kkF_01_043` | Common · Swing | `(303, 312, 146)` | knob `(358, 324)` 36x36 rotary | -300..300 step 1.0 (0 dec) | hd1 | prog |
| 44 | `kkF_01_044` | Common · Quantize Trigger | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Off \| On | hd1 | prog |
| 45 | `kkF_01_045` | Common · Key Sync | `(601, 312, 146)` | combo `(601, 325)` 146x20 | Off \| On | hd1 | prog |

#### Tab 2 - OSC1 (52 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_02_001` | OSC1 Output · Vector Center Level | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..100 step 25.0 (0 dec) | hd1 | prog |
| 2 | `kkF_02_002` | OSC1 Output · Panpot | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | hd1 | prog |
| 3 | `kkF_02_003` | OSC1 Output · Use Drum.Inst Panpot | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Off \| On | hd1 | prog |
| 4 | `kkF_02_004` | OSC1 Output · Panpot Mod.Source | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..48 step 1.0 (0 dec) | hd1 | prog |
| 5 | `kkF_02_005` | OSC1 Output · Panpot Mod.Intensity | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | hd1 | prog |
| 6 | `kkF_02_006` | OSC1 Output · Send1 | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | hd1 | prog |
| 7 | `kkF_02_007` | OSC1 Output · Send2 | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | hd1 | prog |
| 8 | `kkF_02_008` | OSC1 Output · Patch Level | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | hd1 | prog |
| 9 | `kkF_02_009` | OSC1 Pitch · Octave | `(1197, 116, 146)` | combo `(1197, 129)` 146x20 | 32' \| 255 \| 0 \| 4' | hd1 | prog |
| 10 | `kkF_02_010` | OSC1 Pitch · Transpose | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | -12..12 step 1.0 (0 dec) | hd1 | prog |
| 11 | `kkF_02_011` | OSC1 Pitch · Tune | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | hd1 | prog |
| 12 | `kkF_02_012` | OSC1 Pitch · Mod.Source | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | 0..48 step 1.0 (0 dec) | hd1 | prog |
| 13 | `kkF_02_013` | OSC1 Pitch · Pitch Slope | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | -1..2 step 0.1 (1 dec) | hd1 | prog |
| 14 | `kkF_02_014` | OSC1 Pitch · Pitch EG Int.Mod.Source | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..48 step 1.0 (0 dec) | hd1 | prog |
| 15 | `kkF_02_015` | OSC1 Filter A · Filter Type | `(601, 165, 146)` | combo `(601, 178)` 146x20 | Low Pass \| 1 \| 2 \| Band Rejec | hd1 | prog |
| 16 | `kkF_02_016` | OSC1 Filter A · Bypass | `(750, 165, 146)` | combo `(750, 178)` 146x20 | Off \| On | hd1 | prog |
| 17 | `kkF_02_017` | OSC1 Filter A · Trim | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 18 | `kkF_02_018` | OSC1 Filter A · Output | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 19 | `kkF_02_019` | OSC1 Filter A · Output Mod.Source | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..48 step 1.0 (0 dec) | hd1 | prog |
| 20 | `kkF_02_020` | OSC1 Filter A · Output Mod.Intensity | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | hd1 | prog |
| 21 | `kkF_02_021` | OSC1 Filter A · Cutoff | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 22 | `kkF_02_022` | OSC1 Filter A · Resonance | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 23 | `kkF_02_023` | OSC1 Filter B · Filter Type | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Low Pass \| 1 \| 2 \| Band Rejec | hd1 | prog |
| 24 | `kkF_02_024` | OSC1 Filter B · Bypass | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | hd1 | prog |
| 25 | `kkF_02_025` | OSC1 Filter B · Trim | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 26 | `kkF_02_026` | OSC1 Filter B · Output | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 27 | `kkF_02_027` | OSC1 Filter B · Output Mod.Source | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..48 step 1.0 (0 dec) | hd1 | prog |
| 28 | `kkF_02_028` | OSC1 Filter B · Output Mod.Intensity | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | hd1 | prog |
| 29 | `kkF_02_029` | OSC1 Filter B · Cutoff | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 30 | `kkF_02_030` | OSC1 Filter B · Resonance | `(1346, 214, 146)` | knob `(1401, 226)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 31 | `kkF_02_031` | OSC1 Amplifier EG · Start Level | `(5, 263, 146)` | knob `(60, 275)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 32 | `kkF_02_032` | OSC1 Amplifier EG · Attack Time | `(154, 263, 146)` | knob `(209, 275)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 33 | `kkF_02_033` | OSC1 Amplifier EG · Attack Level | `(303, 263, 146)` | knob `(358, 275)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 34 | `kkF_02_034` | OSC1 Amplifier EG · Decay Time | `(452, 263, 146)` | knob `(507, 275)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 35 | `kkF_02_035` | OSC1 Amplifier EG · Break Level | `(601, 263, 146)` | knob `(656, 275)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 36 | `kkF_02_036` | OSC1 Amplifier EG · Slope Time | `(750, 263, 146)` | knob `(805, 275)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 37 | `kkF_02_037` | OSC1 Amplifier EG · Sustain Level | `(899, 263, 146)` | knob `(954, 275)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 38 | `kkF_02_038` | OSC1 Amplifier EG · Release Time | `(1048, 263, 146)` | knob `(1103, 275)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 39 | `kkF_02_039` | OSC1 LFO1 · Waveform | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Triangle \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| Random6(Co | hd1 | prog |
| 40 | `kkF_02_040` | OSC1 LFO1 · Stop | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Off \| On | hd1 | prog |
| 41 | `kkF_02_041` | OSC1 LFO1 · Key Sync | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Off \| On | hd1 | prog |
| 42 | `kkF_02_042` | OSC1 LFO1 · Frequency | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 43 | `kkF_02_043` | OSC1 LFO1 · Frequency Fine | `(303, 312, 146)` | knob `(358, 324)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 44 | `kkF_02_044` | OSC1 LFO1 · Shape | `(452, 312, 146)` | knob `(507, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | hd1 | prog |
| 45 | `kkF_02_045` | OSC1 LFO1 · Shape Mod.Source | `(601, 312, 146)` | knob `(656, 324)` 36x36 rotary | 0..48 step 1.0 (0 dec) | hd1 | prog |
| 46 | `kkF_02_046` | OSC1 LFO2 · Waveform | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Triangle \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| Random6(Co | hd1 | prog |
| 47 | `kkF_02_047` | OSC1 LFO2 · Stop | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Off \| On | hd1 | prog |
| 48 | `kkF_02_048` | OSC1 LFO2 · Key Sync | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Off \| On | hd1 | prog |
| 49 | `kkF_02_049` | OSC1 LFO2 · Frequency | `(1197, 312, 146)` | knob `(1252, 324)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 50 | `kkF_02_050` | OSC1 LFO2 · Frequency Fine | `(1346, 312, 146)` | knob `(1401, 324)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 51 | `kkF_02_051` | OSC1 LFO2 · Shape | `(5, 361, 146)` | knob `(60, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | hd1 | prog |
| 52 | `kkF_02_052` | OSC1 LFO2 · Shape Mod.Source | `(154, 361, 146)` | knob `(209, 373)` 36x36 rotary | 0..48 step 1.0 (0 dec) | hd1 | prog |

#### Tab 3 - OSC2 (52 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_03_001` | OSC2 Output · Vector Center Level | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..100 step 25.0 (0 dec) | hd1 | prog |
| 2 | `kkF_03_002` | OSC2 Output · Panpot | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | hd1 | prog |
| 3 | `kkF_03_003` | OSC2 Output · Use Drum.Inst Panpot | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Off \| On | hd1 | prog |
| 4 | `kkF_03_004` | OSC2 Output · Panpot Mod.Source | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..48 step 1.0 (0 dec) | hd1 | prog |
| 5 | `kkF_03_005` | OSC2 Output · Panpot Mod.Intensity | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | hd1 | prog |
| 6 | `kkF_03_006` | OSC2 Output · Send1 | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | hd1 | prog |
| 7 | `kkF_03_007` | OSC2 Output · Send2 | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | hd1 | prog |
| 8 | `kkF_03_008` | OSC2 Output · Patch Level | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | hd1 | prog |
| 9 | `kkF_03_009` | OSC2 Pitch · Octave | `(1197, 116, 146)` | combo `(1197, 129)` 146x20 | 32' \| 255 \| 0 \| 4' | hd1 | prog |
| 10 | `kkF_03_010` | OSC2 Pitch · Transpose | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | -12..12 step 1.0 (0 dec) | hd1 | prog |
| 11 | `kkF_03_011` | OSC2 Pitch · Tune | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | hd1 | prog |
| 12 | `kkF_03_012` | OSC2 Pitch · Mod.Source | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | 0..48 step 1.0 (0 dec) | hd1 | prog |
| 13 | `kkF_03_013` | OSC2 Pitch · Pitch Slope | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | -1..2 step 0.1 (1 dec) | hd1 | prog |
| 14 | `kkF_03_014` | OSC2 Pitch · Pitch EG Int.Mod.Source | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..48 step 1.0 (0 dec) | hd1 | prog |
| 15 | `kkF_03_015` | OSC2 Filter A · Filter Type | `(601, 165, 146)` | combo `(601, 178)` 146x20 | Low Pass \| 1 \| 2 \| Band Rejec | hd1 | prog |
| 16 | `kkF_03_016` | OSC2 Filter A · Bypass | `(750, 165, 146)` | combo `(750, 178)` 146x20 | Off \| On | hd1 | prog |
| 17 | `kkF_03_017` | OSC2 Filter A · Trim | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 18 | `kkF_03_018` | OSC2 Filter A · Output | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 19 | `kkF_03_019` | OSC2 Filter A · Output Mod.Source | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..48 step 1.0 (0 dec) | hd1 | prog |
| 20 | `kkF_03_020` | OSC2 Filter A · Output Mod.Intensity | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | hd1 | prog |
| 21 | `kkF_03_021` | OSC2 Filter A · Cutoff | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 22 | `kkF_03_022` | OSC2 Filter A · Resonance | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 23 | `kkF_03_023` | OSC2 Filter B · Filter Type | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Low Pass \| 1 \| 2 \| Band Rejec | hd1 | prog |
| 24 | `kkF_03_024` | OSC2 Filter B · Bypass | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | hd1 | prog |
| 25 | `kkF_03_025` | OSC2 Filter B · Trim | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 26 | `kkF_03_026` | OSC2 Filter B · Output | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 27 | `kkF_03_027` | OSC2 Filter B · Output Mod.Source | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..48 step 1.0 (0 dec) | hd1 | prog |
| 28 | `kkF_03_028` | OSC2 Filter B · Output Mod.Intensity | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | hd1 | prog |
| 29 | `kkF_03_029` | OSC2 Filter B · Cutoff | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 30 | `kkF_03_030` | OSC2 Filter B · Resonance | `(1346, 214, 146)` | knob `(1401, 226)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 31 | `kkF_03_031` | OSC2 Amplifier EG · Start Level | `(5, 263, 146)` | knob `(60, 275)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 32 | `kkF_03_032` | OSC2 Amplifier EG · Attack Time | `(154, 263, 146)` | knob `(209, 275)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 33 | `kkF_03_033` | OSC2 Amplifier EG · Attack Level | `(303, 263, 146)` | knob `(358, 275)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 34 | `kkF_03_034` | OSC2 Amplifier EG · Decay Time | `(452, 263, 146)` | knob `(507, 275)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 35 | `kkF_03_035` | OSC2 Amplifier EG · Break Level | `(601, 263, 146)` | knob `(656, 275)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 36 | `kkF_03_036` | OSC2 Amplifier EG · Slope Time | `(750, 263, 146)` | knob `(805, 275)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 37 | `kkF_03_037` | OSC2 Amplifier EG · Sustain Level | `(899, 263, 146)` | knob `(954, 275)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 38 | `kkF_03_038` | OSC2 Amplifier EG · Release Time | `(1048, 263, 146)` | knob `(1103, 275)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 39 | `kkF_03_039` | OSC2 LFO1 · Waveform | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Triangle \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| Random6(Co | hd1 | prog |
| 40 | `kkF_03_040` | OSC2 LFO1 · Stop | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Off \| On | hd1 | prog |
| 41 | `kkF_03_041` | OSC2 LFO1 · Key Sync | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Off \| On | hd1 | prog |
| 42 | `kkF_03_042` | OSC2 LFO1 · Frequency | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 43 | `kkF_03_043` | OSC2 LFO1 · Frequency Fine | `(303, 312, 146)` | knob `(358, 324)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 44 | `kkF_03_044` | OSC2 LFO1 · Shape | `(452, 312, 146)` | knob `(507, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | hd1 | prog |
| 45 | `kkF_03_045` | OSC2 LFO1 · Shape Mod.Source | `(601, 312, 146)` | knob `(656, 324)` 36x36 rotary | 0..48 step 1.0 (0 dec) | hd1 | prog |
| 46 | `kkF_03_046` | OSC2 LFO2 · Waveform | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Triangle \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| Random6(Co | hd1 | prog |
| 47 | `kkF_03_047` | OSC2 LFO2 · Stop | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Off \| On | hd1 | prog |
| 48 | `kkF_03_048` | OSC2 LFO2 · Key Sync | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Off \| On | hd1 | prog |
| 49 | `kkF_03_049` | OSC2 LFO2 · Frequency | `(1197, 312, 146)` | knob `(1252, 324)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 50 | `kkF_03_050` | OSC2 LFO2 · Frequency Fine | `(1346, 312, 146)` | knob `(1401, 324)` 36x36 rotary | 0..99 step 1.0 (0 dec) | hd1 | prog |
| 51 | `kkF_03_051` | OSC2 LFO2 · Shape | `(5, 361, 146)` | knob `(60, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | hd1 | prog |
| 52 | `kkF_03_052` | OSC2 LFO2 · Shape Mod.Source | `(154, 361, 146)` | knob `(209, 373)` 36x36 rotary | 0..48 step 1.0 (0 dec) | hd1 | prog |

#### Tab 4 - EXi1 Mix (23 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_04_001` | EXi1 Output · Vector Center Level | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..100 step 25.0 (0 dec) | exi | prog |
| 2 | `kkF_04_002` | EXi1 Output · Panpot | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | exi | prog |
| 3 | `kkF_04_003` | EXi1 Output · Panpot Mod.Intensity | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | exi | prog |
| 4 | `kkF_04_004` | EXi1 Output · Send1 | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | exi | prog |
| 5 | `kkF_04_005` | EXi1 Output · Send2 | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | exi | prog |
| 6 | `kkF_04_006` | EXi1 Output · Patch Level | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | exi | prog |
| 7 | `kkF_04_007` | EXi1 Output · Mute | `(899, 116, 146)` | combo `(899, 129)` 146x20 | Off \| On | exi | prog |
| 8 | `kkF_04_008` | EXi1 Mod.Mixer1 · Type | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | A+B \| 1 \| 2 \| 3 \| 4 \| 5 \| Gate | exi | prog |
| 9 | `kkF_04_009` | EXi1 Mod.Mixer1 · Amount A | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | exi | prog |
| 10 | `kkF_04_010` | EXi1 Mod.Mixer1 · Amount B | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | exi | prog |
| 11 | `kkF_04_011` | EXi1 Mod.Mixer1 · Number Of Steps | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | 2..32 step 1.0 (0 dec) | exi | prog |
| 12 | `kkF_04_012` | EXi1 Mod.Mixer1 · Amount A | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | -199..199 step 1.0 (0 dec) | exi | prog |
| 13 | `kkF_04_013` | EXi1 Mod.Mixer1 · Offset | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | -199..199 step 1.0 (0 dec) | exi | prog |
| 14 | `kkF_04_014` | EXi1 Mod.Mixer1 · Attack | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | exi | prog |
| 15 | `kkF_04_015` | EXi1 Mod.Mixer1 · Decay | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | exi | prog |
| 16 | `kkF_04_016` | EXi1 Mod.Mixer2 · Type | `(750, 165, 146)` | combo `(750, 178)` 146x20 | A+B \| 1 \| 2 \| 3 \| 4 \| 5 \| Gate | exi | prog |
| 17 | `kkF_04_017` | EXi1 Mod.Mixer2 · Amount A | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | exi | prog |
| 18 | `kkF_04_018` | EXi1 Mod.Mixer2 · Amount B | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | exi | prog |
| 19 | `kkF_04_019` | EXi1 Mod.Mixer2 · Number Of Steps | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 2..32 step 1.0 (0 dec) | exi | prog |
| 20 | `kkF_04_020` | EXi1 Mod.Mixer2 · Amount A | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | -199..199 step 1.0 (0 dec) | exi | prog |
| 21 | `kkF_04_021` | EXi1 Mod.Mixer2 · Offset | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | -199..199 step 1.0 (0 dec) | exi | prog |
| 22 | `kkF_04_022` | EXi1 Mod.Mixer2 · Attack | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..99 step 1.0 (0 dec) | exi | prog |
| 23 | `kkF_04_023` | EXi1 Mod.Mixer2 · Decay | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..99 step 1.0 (0 dec) | exi | prog |

#### Tab 5 - EXi2 Mix (23 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_05_001` | EXi2 Output · Vector Center Level | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..100 step 25.0 (0 dec) | exi | prog |
| 2 | `kkF_05_002` | EXi2 Output · Panpot | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | exi | prog |
| 3 | `kkF_05_003` | EXi2 Output · Panpot Mod.Intensity | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | exi | prog |
| 4 | `kkF_05_004` | EXi2 Output · Send1 | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | exi | prog |
| 5 | `kkF_05_005` | EXi2 Output · Send2 | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | exi | prog |
| 6 | `kkF_05_006` | EXi2 Output · Patch Level | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | exi | prog |
| 7 | `kkF_05_007` | EXi2 Output · Mute | `(899, 116, 146)` | combo `(899, 129)` 146x20 | Off \| On | exi | prog |
| 8 | `kkF_05_008` | EXi2 Mod.Mixer1 · Type | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | A+B \| 1 \| 2 \| 3 \| 4 \| 5 \| Gate | exi | prog |
| 9 | `kkF_05_009` | EXi2 Mod.Mixer1 · Amount A | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | exi | prog |
| 10 | `kkF_05_010` | EXi2 Mod.Mixer1 · Amount B | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | exi | prog |
| 11 | `kkF_05_011` | EXi2 Mod.Mixer1 · Number Of Steps | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | 2..32 step 1.0 (0 dec) | exi | prog |
| 12 | `kkF_05_012` | EXi2 Mod.Mixer1 · Amount A | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | -199..199 step 1.0 (0 dec) | exi | prog |
| 13 | `kkF_05_013` | EXi2 Mod.Mixer1 · Offset | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | -199..199 step 1.0 (0 dec) | exi | prog |
| 14 | `kkF_05_014` | EXi2 Mod.Mixer1 · Attack | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | exi | prog |
| 15 | `kkF_05_015` | EXi2 Mod.Mixer1 · Decay | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | exi | prog |
| 16 | `kkF_05_016` | EXi2 Mod.Mixer2 · Type | `(750, 165, 146)` | combo `(750, 178)` 146x20 | A+B \| 1 \| 2 \| 3 \| 4 \| 5 \| Gate | exi | prog |
| 17 | `kkF_05_017` | EXi2 Mod.Mixer2 · Amount A | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | exi | prog |
| 18 | `kkF_05_018` | EXi2 Mod.Mixer2 · Amount B | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | exi | prog |
| 19 | `kkF_05_019` | EXi2 Mod.Mixer2 · Number Of Steps | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 2..32 step 1.0 (0 dec) | exi | prog |
| 20 | `kkF_05_020` | EXi2 Mod.Mixer2 · Amount A | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | -199..199 step 1.0 (0 dec) | exi | prog |
| 21 | `kkF_05_021` | EXi2 Mod.Mixer2 · Offset | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | -199..199 step 1.0 (0 dec) | exi | prog |
| 22 | `kkF_05_022` | EXi2 Mod.Mixer2 · Attack | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..99 step 1.0 (0 dec) | exi | prog |
| 23 | `kkF_05_023` | EXi2 Mod.Mixer2 · Decay | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..99 step 1.0 (0 dec) | exi | prog |

#### Tab 6 - E1 AL-1 (10 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_06_001` | OSC1 · Waveform | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Saw \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| Square/Triangle | engine2 | prog |
| 2 | `kkF_06_002` | OSC1 · Wave Morph | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..100 step 1.0 (0 dec) | engine2 | prog |
| 3 | `kkF_06_003` | OSC1 · Wave Morph Mod.Source | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..52 step 1.0 (0 dec) | engine2 | prog |
| 4 | `kkF_06_004` | OSC2 · Waveform | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Saw \| 1 \| 2 \| 3 \| 4 \| Detuned Saw 2 | engine2 | prog |
| 5 | `kkF_06_005` | OSC2 · Wave Morph | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..100 step 1.0 (0 dec) | engine2 | prog |
| 6 | `kkF_06_006` | Filter A · Bypass | `(750, 116, 146)` | combo `(750, 129)` 146x20 | Off \| On | engine2 | prog |
| 7 | `kkF_06_007` | Filter A · Filter Type | `(899, 116, 146)` | combo `(899, 129)` 146x20 | Low Pass \| 1 \| 2 \| 3 \| Multi Filt | engine2 | prog |
| 8 | `kkF_06_008` | Amplifier EG · Start Level | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine2 | prog |
| 9 | `kkF_06_009` | Amplifier EG · Attack Level | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine2 | prog |
| 10 | `kkF_06_010` | LFO1 · Waveform | `(1346, 116, 146)` | combo `(1346, 129)` 146x20 | Triangle \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| Random6(Co | engine2 | prog |

#### Tab 7 - E1 CX-3 (10 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_07_001` | Basic · Delay Start | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..97 step 1.0 (0 dec) | engine3 | prog |
| 2 | `kkF_07_002` | Basic · Wheel Type | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Vintage \| Clean | engine3 | prog |
| 3 | `kkF_07_003` | Basic · Overtone Level | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine3 | prog |
| 4 | `kkF_07_004` | Basic · Leakage Level | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine3 | prog |
| 5 | `kkF_07_005` | Drawbar · Drawbar Mode | `(601, 116, 146)` | combo `(601, 129)` 146x20 | Normal \| EX | engine3 | prog |
| 6 | `kkF_07_006` | Drawbar · Split Enable | `(750, 116, 146)` | combo `(750, 129)` 146x20 | Off \| On | engine3 | prog |
| 7 | `kkF_07_007` | Drawbar · Split Enable Mod.Source | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..40 step 1.0 (0 dec) | engine3 | prog |
| 8 | `kkF_07_008` | Amplifier · Amp Type | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | Type1 \| 1 \| Pre Amp | engine3 | prog |
| 9 | `kkF_07_009` | Amplifier · Amp Gain | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine3 | prog |
| 10 | `kkF_07_010` | Percussion · Enable | `(1346, 116, 146)` | combo `(1346, 129)` 146x20 | Off \| On | engine3 | prog |

#### Tab 8 - E1 STR-1 (10 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_08_001` | String · Decay | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..100 step 1.0 (0 dec) | engine4 | prog |
| 2 | `kkF_08_002` | String · Decay Mod.1 Source | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..59 step 1.0 (0 dec) | engine4 | prog |
| 3 | `kkF_08_003` | String · Decay Mod.2 Source | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..59 step 1.0 (0 dec) | engine4 | prog |
| 4 | `kkF_08_004` | Mixer · String Level | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine4 | prog |
| 5 | `kkF_08_005` | Mixer · String Level Mod.Source | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..59 step 1.0 (0 dec) | engine4 | prog |
| 6 | `kkF_08_006` | Filter A · Bypass | `(750, 116, 146)` | combo `(750, 129)` 146x20 | Off \| On | engine4 | prog |
| 7 | `kkF_08_007` | Filter A · Filter Type | `(899, 116, 146)` | combo `(899, 129)` 146x20 | Low Pass \| 1 \| 2 \| 3 \| Multi Filt | engine4 | prog |
| 8 | `kkF_08_008` | Amplifier EG · Start Level | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine4 | prog |
| 9 | `kkF_08_009` | Amplifier EG · Attack Level | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine4 | prog |
| 10 | `kkF_08_010` | Feedback · Feedback Distance | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0.23..10 step 0.01 (2 dec) | engine4 | prog |

#### Tab 9 - E1 MS-20EX (10 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_09_001` | VCO1 · Waveform | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Triangle \| 1 \| 2 \| Noise | engine5 | prog |
| 2 | `kkF_09_002` | VCO1 · Waveform Mod.Source | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..52 step 1.0 (0 dec) | engine5 | prog |
| 3 | `kkF_09_003` | VCO2 · Waveform | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Saw \| 1 \| 2 \| Ring Mod. | engine5 | prog |
| 4 | `kkF_09_004` | VCO2 · Waveform Mod.Source | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..52 step 1.0 (0 dec) | engine5 | prog |
| 5 | `kkF_09_005` | LPF · Cutoff | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..10 step 0.01 (2 dec) | engine5 | prog |
| 6 | `kkF_09_006` | LPF · Peak | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..10 step 0.01 (2 dec) | engine5 | prog |
| 7 | `kkF_09_007` | HPF · Cutoff | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..10 step 0.01 (2 dec) | engine5 | prog |
| 8 | `kkF_09_008` | Mixer · Mixer1 Input A Level | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -10..10 step 0.01 (2 dec) | engine5 | prog |
| 9 | `kkF_09_009` | EG1 · Delay Time | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..10 step 0.01 (2 dec) | engine5 | prog |
| 10 | `kkF_09_010` | MG · Key Sync | `(1346, 116, 146)` | combo `(1346, 129)` 146x20 | Off \| On | engine5 | prog |

#### Tab 10 - E1 PolysixEX (10 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_10_001` | VCO · PWM Speed | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..10 step 0.01 (2 dec) | engine6 | prog |
| 2 | `kkF_10_002` | VCO · PWM Speed Mod.Source | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..49 step 1.0 (0 dec) | engine6 | prog |
| 3 | `kkF_10_003` | Filter · Cutoff | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..10 step 0.01 (2 dec) | engine6 | prog |
| 4 | `kkF_10_004` | Filter · Cutoff Mod.Source | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..49 step 1.0 (0 dec) | engine6 | prog |
| 5 | `kkF_10_005` | EG · Attack Time | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..10 step 0.01 (2 dec) | engine6 | prog |
| 6 | `kkF_10_006` | EG · Attack Time Mod.Source | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..49 step 1.0 (0 dec) | engine6 | prog |
| 7 | `kkF_10_007` | MG · Key Sync | `(899, 116, 146)` | combo `(899, 129)` 146x20 | Off \| On | engine6 | prog |
| 8 | `kkF_10_008` | MG · Frequency | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..10 step 0.01 (2 dec) | engine6 | prog |
| 9 | `kkF_10_009` | VCA · Volume | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..10 step 0.01 (2 dec) | engine6 | prog |
| 10 | `kkF_10_010` | Arpeggiator · Enable | `(1346, 116, 146)` | combo `(1346, 129)` 146x20 | Off \| On | engine6 | prog |

#### Tab 11 - E1 MOD-7 (10 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_11_001` | OSC1 · OSC On/Off | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Off \| On | engine7 | prog |
| 2 | `kkF_11_002` | OSC1 · OSC Mode | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| Ring Mod. Only | engine7 | prog |
| 3 | `kkF_11_003` | Output Mixer · Mixer1 Level | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..100 step 1.0 (0 dec) | engine7 | prog |
| 4 | `kkF_11_004` | Output Mixer · Mixer2 Level | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..100 step 1.0 (0 dec) | engine7 | prog |
| 5 | `kkF_11_005` | Filter A · Bypass | `(601, 116, 146)` | combo `(601, 129)` 146x20 | Off \| On | engine7 | prog |
| 6 | `kkF_11_006` | Filter A · Filter Type | `(750, 116, 146)` | combo `(750, 129)` 146x20 | Low Pass \| 1 \| 2 \| 3 \| Multi Filt | engine7 | prog |
| 7 | `kkF_11_007` | Amplifier EG · Start Level | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine7 | prog |
| 8 | `kkF_11_008` | Amplifier EG · Attack Level | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine7 | prog |
| 9 | `kkF_11_009` | LFO1 · Waveform | `(1197, 116, 146)` | combo `(1197, 129)` 146x20 | Triangle \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| Random6(Co | engine7 | prog |
| 10 | `kkF_11_010` | Macro · Brightness | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | -100..100 step 1.0 (0 dec) | engine7 | prog |

#### Tab 12 - E1 SGX-2 (10 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_12_001` | User Param · Piano Type | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..255 step 1.0 (0 dec) | engine8 | prog |
| 2 | `kkF_12_002` | User Param · Patch Level | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | engine8 | prog |
| 3 | `kkF_12_003` | User Param · Transpose | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | -12..12 step 1.0 (0 dec) | engine8 | prog |
| 4 | `kkF_12_004` | User Param · Octave | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | -2..1 step 1.0 (0 dec) | engine8 | prog |
| 5 | `kkF_12_005` | User Param · Amp Vel. Int. | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | -100..100 step 1.0 (0 dec) | engine8 | prog |
| 6 | `kkF_12_006` | User Param · Release Time | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | -100..100 step 1.0 (0 dec) | engine8 | prog |
| 7 | `kkF_12_007` | User Param · Velocity Bias | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | -100..100 step 1.0 (0 dec) | engine8 | prog |
| 8 | `kkF_12_008` | User Param · Lid Position | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..100 step 1.0 (0 dec) | engine8 | prog |
| 9 | `kkF_12_009` | User Param · St. Perspective | `(1197, 116, 146)` | combo `(1197, 129)` 146x20 | Player \| Audience | engine8 | prog |
| 10 | `kkF_12_010` | User Param · Una Corda On | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..1 step 1.0 (0 dec) | engine8 | prog |

#### Tab 13 - E1 EP-1 (10 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_13_001` | Self · Voice Delay | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..97 step 1.0 (0 dec) | engine9 | prog |
| 2 | `kkF_13_002` | Self · Model Type | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Tine I Late \| 1 \| 2 \| 3 \| 4 \| 5 \| Early | engine9 | prog |
| 3 | `kkF_13_003` | Self · IFX Type | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| VOX Wah | engine9 | prog |
| 4 | `kkF_13_004` | Self · Tine Pre Amp Volume | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..100 step 1.0 (0 dec) | engine9 | prog |
| 5 | `kkF_13_005` | Osc · Pitch Slope | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | -1..2 step 0.01 (2 dec) | engine9 | prog |
| 6 | `kkF_13_006` | Osc · Pitch Ribbon | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | -60..60 step 1.0 (0 dec) | engine9 | prog |
| 7 | `kkF_13_007` | Osc · Pitch Bend Up | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | -60..12 step 1.0 (0 dec) | engine9 | prog |
| 8 | `kkF_13_008` | EP Amp · Level | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | engine9 | prog |
| 9 | `kkF_13_009` | EP Amp · AMS Source | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..41 step 1.0 (0 dec) | engine9 | prog |
| 10 | `kkF_13_010` | EP Amp · AMS Intensity | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | engine9 | prog |

#### Tab 14 - E2 AL-1 (10 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_14_001` | OSC1 · Waveform | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Saw \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| Square/Triangle | engine22 | prog |
| 2 | `kkF_14_002` | OSC1 · Wave Morph | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..100 step 1.0 (0 dec) | engine22 | prog |
| 3 | `kkF_14_003` | OSC1 · Wave Morph Mod.Source | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..52 step 1.0 (0 dec) | engine22 | prog |
| 4 | `kkF_14_004` | OSC2 · Waveform | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Saw \| 1 \| 2 \| 3 \| 4 \| Detuned Saw 2 | engine22 | prog |
| 5 | `kkF_14_005` | OSC2 · Wave Morph | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..100 step 1.0 (0 dec) | engine22 | prog |
| 6 | `kkF_14_006` | Filter A · Bypass | `(750, 116, 146)` | combo `(750, 129)` 146x20 | Off \| On | engine22 | prog |
| 7 | `kkF_14_007` | Filter A · Filter Type | `(899, 116, 146)` | combo `(899, 129)` 146x20 | Low Pass \| 1 \| 2 \| 3 \| Multi Filt | engine22 | prog |
| 8 | `kkF_14_008` | Amplifier EG · Start Level | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine22 | prog |
| 9 | `kkF_14_009` | Amplifier EG · Attack Level | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine22 | prog |
| 10 | `kkF_14_010` | LFO1 · Waveform | `(1346, 116, 146)` | combo `(1346, 129)` 146x20 | Triangle \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| Random6(Co | engine22 | prog |

#### Tab 15 - E2 CX-3 (10 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_15_001` | Basic · Delay Start | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..97 step 1.0 (0 dec) | engine23 | prog |
| 2 | `kkF_15_002` | Basic · Wheel Type | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Vintage \| Clean | engine23 | prog |
| 3 | `kkF_15_003` | Basic · Overtone Level | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine23 | prog |
| 4 | `kkF_15_004` | Basic · Leakage Level | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine23 | prog |
| 5 | `kkF_15_005` | Drawbar · Drawbar Mode | `(601, 116, 146)` | combo `(601, 129)` 146x20 | Normal \| EX | engine23 | prog |
| 6 | `kkF_15_006` | Drawbar · Split Enable | `(750, 116, 146)` | combo `(750, 129)` 146x20 | Off \| On | engine23 | prog |
| 7 | `kkF_15_007` | Drawbar · Split Enable Mod.Source | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..40 step 1.0 (0 dec) | engine23 | prog |
| 8 | `kkF_15_008` | Amplifier · Amp Type | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | Type1 \| 1 \| Pre Amp | engine23 | prog |
| 9 | `kkF_15_009` | Amplifier · Amp Gain | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine23 | prog |
| 10 | `kkF_15_010` | Percussion · Enable | `(1346, 116, 146)` | combo `(1346, 129)` 146x20 | Off \| On | engine23 | prog |

#### Tab 16 - E2 STR-1 (10 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_16_001` | String · Decay | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..100 step 1.0 (0 dec) | engine24 | prog |
| 2 | `kkF_16_002` | String · Decay Mod.1 Source | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..59 step 1.0 (0 dec) | engine24 | prog |
| 3 | `kkF_16_003` | String · Decay Mod.2 Source | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..59 step 1.0 (0 dec) | engine24 | prog |
| 4 | `kkF_16_004` | Mixer · String Level | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine24 | prog |
| 5 | `kkF_16_005` | Mixer · String Level Mod.Source | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..59 step 1.0 (0 dec) | engine24 | prog |
| 6 | `kkF_16_006` | Filter A · Bypass | `(750, 116, 146)` | combo `(750, 129)` 146x20 | Off \| On | engine24 | prog |
| 7 | `kkF_16_007` | Filter A · Filter Type | `(899, 116, 146)` | combo `(899, 129)` 146x20 | Low Pass \| 1 \| 2 \| 3 \| Multi Filt | engine24 | prog |
| 8 | `kkF_16_008` | Amplifier EG · Start Level | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine24 | prog |
| 9 | `kkF_16_009` | Amplifier EG · Attack Level | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine24 | prog |
| 10 | `kkF_16_010` | Feedback · Feedback Distance | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0.23..10 step 0.01 (2 dec) | engine24 | prog |

#### Tab 17 - E2 MS-20EX (10 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_17_001` | VCO1 · Waveform | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Triangle \| 1 \| 2 \| Noise | engine25 | prog |
| 2 | `kkF_17_002` | VCO1 · Waveform Mod.Source | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..52 step 1.0 (0 dec) | engine25 | prog |
| 3 | `kkF_17_003` | VCO2 · Waveform | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Saw \| 1 \| 2 \| Ring Mod. | engine25 | prog |
| 4 | `kkF_17_004` | VCO2 · Waveform Mod.Source | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..52 step 1.0 (0 dec) | engine25 | prog |
| 5 | `kkF_17_005` | LPF · Cutoff | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..10 step 0.01 (2 dec) | engine25 | prog |
| 6 | `kkF_17_006` | LPF · Peak | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..10 step 0.01 (2 dec) | engine25 | prog |
| 7 | `kkF_17_007` | HPF · Cutoff | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..10 step 0.01 (2 dec) | engine25 | prog |
| 8 | `kkF_17_008` | Mixer · Mixer1 Input A Level | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -10..10 step 0.01 (2 dec) | engine25 | prog |
| 9 | `kkF_17_009` | EG1 · Delay Time | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..10 step 0.01 (2 dec) | engine25 | prog |
| 10 | `kkF_17_010` | MG · Key Sync | `(1346, 116, 146)` | combo `(1346, 129)` 146x20 | Off \| On | engine25 | prog |

#### Tab 18 - E2 PolysixEX (10 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_18_001` | VCO · PWM Speed | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..10 step 0.01 (2 dec) | engine26 | prog |
| 2 | `kkF_18_002` | VCO · PWM Speed Mod.Source | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..49 step 1.0 (0 dec) | engine26 | prog |
| 3 | `kkF_18_003` | Filter · Cutoff | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..10 step 0.01 (2 dec) | engine26 | prog |
| 4 | `kkF_18_004` | Filter · Cutoff Mod.Source | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..49 step 1.0 (0 dec) | engine26 | prog |
| 5 | `kkF_18_005` | EG · Attack Time | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..10 step 0.01 (2 dec) | engine26 | prog |
| 6 | `kkF_18_006` | EG · Attack Time Mod.Source | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..49 step 1.0 (0 dec) | engine26 | prog |
| 7 | `kkF_18_007` | MG · Key Sync | `(899, 116, 146)` | combo `(899, 129)` 146x20 | Off \| On | engine26 | prog |
| 8 | `kkF_18_008` | MG · Frequency | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..10 step 0.01 (2 dec) | engine26 | prog |
| 9 | `kkF_18_009` | VCA · Volume | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..10 step 0.01 (2 dec) | engine26 | prog |
| 10 | `kkF_18_010` | Arpeggiator · Enable | `(1346, 116, 146)` | combo `(1346, 129)` 146x20 | Off \| On | engine26 | prog |

#### Tab 19 - E2 MOD-7 (10 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_19_001` | OSC1 · OSC On/Off | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Off \| On | engine27 | prog |
| 2 | `kkF_19_002` | OSC1 · OSC Mode | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| Ring Mod. Only | engine27 | prog |
| 3 | `kkF_19_003` | Output Mixer · Mixer1 Level | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..100 step 1.0 (0 dec) | engine27 | prog |
| 4 | `kkF_19_004` | Output Mixer · Mixer2 Level | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..100 step 1.0 (0 dec) | engine27 | prog |
| 5 | `kkF_19_005` | Filter A · Bypass | `(601, 116, 146)` | combo `(601, 129)` 146x20 | Off \| On | engine27 | prog |
| 6 | `kkF_19_006` | Filter A · Filter Type | `(750, 116, 146)` | combo `(750, 129)` 146x20 | Low Pass \| 1 \| 2 \| 3 \| Multi Filt | engine27 | prog |
| 7 | `kkF_19_007` | Amplifier EG · Start Level | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine27 | prog |
| 8 | `kkF_19_008` | Amplifier EG · Attack Level | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..99 step 1.0 (0 dec) | engine27 | prog |
| 9 | `kkF_19_009` | LFO1 · Waveform | `(1197, 116, 146)` | combo `(1197, 129)` 146x20 | Triangle \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| Random6(Co | engine27 | prog |
| 10 | `kkF_19_010` | Macro · Brightness | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | -100..100 step 1.0 (0 dec) | engine27 | prog |

#### Tab 20 - E2 SGX-2 (10 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_20_001` | User Param · Piano Type | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..255 step 1.0 (0 dec) | engine28 | prog |
| 2 | `kkF_20_002` | User Param · Patch Level | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | engine28 | prog |
| 3 | `kkF_20_003` | User Param · Transpose | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | -12..12 step 1.0 (0 dec) | engine28 | prog |
| 4 | `kkF_20_004` | User Param · Octave | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | -2..1 step 1.0 (0 dec) | engine28 | prog |
| 5 | `kkF_20_005` | User Param · Amp Vel. Int. | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | -100..100 step 1.0 (0 dec) | engine28 | prog |
| 6 | `kkF_20_006` | User Param · Release Time | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | -100..100 step 1.0 (0 dec) | engine28 | prog |
| 7 | `kkF_20_007` | User Param · Velocity Bias | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | -100..100 step 1.0 (0 dec) | engine28 | prog |
| 8 | `kkF_20_008` | User Param · Lid Position | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..100 step 1.0 (0 dec) | engine28 | prog |
| 9 | `kkF_20_009` | User Param · St. Perspective | `(1197, 116, 146)` | combo `(1197, 129)` 146x20 | Player \| Audience | engine28 | prog |
| 10 | `kkF_20_010` | User Param · Una Corda On | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..1 step 1.0 (0 dec) | engine28 | prog |

#### Tab 21 - E2 EP-1 (10 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_21_001` | Self · Voice Delay | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..97 step 1.0 (0 dec) | engine29 | prog |
| 2 | `kkF_21_002` | Self · Model Type | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Tine I Late \| 1 \| 2 \| 3 \| 4 \| 5 \| Early | engine29 | prog |
| 3 | `kkF_21_003` | Self · IFX Type | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| VOX Wah | engine29 | prog |
| 4 | `kkF_21_004` | Self · Tine Pre Amp Volume | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..100 step 1.0 (0 dec) | engine29 | prog |
| 5 | `kkF_21_005` | Osc · Pitch Slope | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | -1..2 step 0.01 (2 dec) | engine29 | prog |
| 6 | `kkF_21_006` | Osc · Pitch Ribbon | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | -60..60 step 1.0 (0 dec) | engine29 | prog |
| 7 | `kkF_21_007` | Osc · Pitch Bend Up | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | -60..12 step 1.0 (0 dec) | engine29 | prog |
| 8 | `kkF_21_008` | EP Amp · Level | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | engine29 | prog |
| 9 | `kkF_21_009` | EP Amp · AMS Source | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..41 step 1.0 (0 dec) | engine29 | prog |
| 10 | `kkF_21_010` | EP Amp · AMS Intensity | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | engine29 | prog |

#### Tab 22 - IFX 1-12 (36 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_22_001` | Insert Effect1 · Effect Type | `(5, 116, 146)` | fxcombo `(5, 129)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | all | prog |
| 2 | `kkF_22_002` | Insert Effect1 · Switch | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | all | prog |
| 3 | `kkF_22_003` | Insert Effect1 · Panpot | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | all | prog |
| 4 | `kkF_22_004` | Insert Effect2 · Effect Type | `(452, 116, 146)` | fxcombo `(452, 129)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | all | prog |
| 5 | `kkF_22_005` | Insert Effect2 · Switch | `(601, 116, 146)` | combo `(601, 129)` 146x20 | Off \| On | all | prog |
| 6 | `kkF_22_006` | Insert Effect2 · Panpot | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | all | prog |
| 7 | `kkF_22_007` | Insert Effect3 · Effect Type | `(899, 116, 146)` | fxcombo `(899, 129)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | all | prog |
| 8 | `kkF_22_008` | Insert Effect3 · Switch | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | Off \| On | all | prog |
| 9 | `kkF_22_009` | Insert Effect3 · Panpot | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | all | prog |
| 10 | `kkF_22_010` | Insert Effect4 · Effect Type | `(1346, 116, 146)` | fxcombo `(1346, 129)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | all | prog |
| 11 | `kkF_22_011` | Insert Effect4 · Switch | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Off \| On | all | prog |
| 12 | `kkF_22_012` | Insert Effect4 · Panpot | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | all | prog |
| 13 | `kkF_22_013` | Insert Effect5 · Effect Type | `(303, 165, 146)` | fxcombo `(303, 178)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | all | prog |
| 14 | `kkF_22_014` | Insert Effect5 · Switch | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | all | prog |
| 15 | `kkF_22_015` | Insert Effect5 · Panpot | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | all | prog |
| 16 | `kkF_22_016` | Insert Effect6 · Effect Type | `(750, 165, 146)` | fxcombo `(750, 178)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | all | prog |
| 17 | `kkF_22_017` | Insert Effect6 · Switch | `(899, 165, 146)` | combo `(899, 178)` 146x20 | Off \| On | all | prog |
| 18 | `kkF_22_018` | Insert Effect6 · Panpot | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | all | prog |
| 19 | `kkF_22_019` | Insert Effect7 · Effect Type | `(1197, 165, 146)` | fxcombo `(1197, 178)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | all | prog |
| 20 | `kkF_22_020` | Insert Effect7 · Switch | `(1346, 165, 146)` | combo `(1346, 178)` 146x20 | Off \| On | all | prog |
| 21 | `kkF_22_021` | Insert Effect7 · Panpot | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | all | prog |
| 22 | `kkF_22_022` | Insert Effect8 · Effect Type | `(154, 214, 146)` | fxcombo `(154, 227)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | all | prog |
| 23 | `kkF_22_023` | Insert Effect8 · Switch | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| On | all | prog |
| 24 | `kkF_22_024` | Insert Effect8 · Panpot | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | all | prog |
| 25 | `kkF_22_025` | Insert Effect9 · Effect Type | `(601, 214, 146)` | fxcombo `(601, 227)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | all | prog |
| 26 | `kkF_22_026` | Insert Effect9 · Switch | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | all | prog |
| 27 | `kkF_22_027` | Insert Effect9 · Panpot | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | all | prog |
| 28 | `kkF_22_028` | Insert Effect10 · Effect Type | `(1048, 214, 146)` | fxcombo `(1048, 227)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | all | prog |
| 29 | `kkF_22_029` | Insert Effect10 · Switch | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| On | all | prog |
| 30 | `kkF_22_030` | Insert Effect10 · Panpot | `(1346, 214, 146)` | knob `(1401, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | all | prog |
| 31 | `kkF_22_031` | Insert Effect11 · Effect Type | `(5, 263, 146)` | fxcombo `(5, 276)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | all | prog |
| 32 | `kkF_22_032` | Insert Effect11 · Switch | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | all | prog |
| 33 | `kkF_22_033` | Insert Effect11 · Panpot | `(303, 263, 146)` | knob `(358, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | all | prog |
| 34 | `kkF_22_034` | Insert Effect12 · Effect Type | `(452, 263, 146)` | fxcombo `(452, 276)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | all | prog |
| 35 | `kkF_22_035` | Insert Effect12 · Switch | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | all | prog |
| 36 | `kkF_22_036` | Insert Effect12 · Panpot | `(750, 263, 146)` | knob `(805, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | all | prog |

#### Tab 23 - MFX·TFX (13 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkF_23_001` | Master Effect1 · Effect Type | `(5, 116, 146)` | fxcombo `(5, 129)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | all | prog |
| 2 | `kkF_23_002` | Master Effect1 · Switch | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | all | prog |
| 3 | `kkF_23_003` | Master Effect2 · Effect Type | `(303, 116, 146)` | fxcombo `(303, 129)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | all | prog |
| 4 | `kkF_23_004` | Master Effect2 · Switch | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| On | all | prog |
| 5 | `kkF_23_005` | Total Effect1 · Effect Type | `(601, 116, 146)` | fxcombo `(601, 129)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | all | prog |
| 6 | `kkF_23_006` | Total Effect1 · Switch | `(750, 116, 146)` | combo `(750, 129)` 146x20 | Off \| On | all | prog |
| 7 | `kkF_23_007` | Total Effect2 · Effect Type | `(899, 116, 146)` | fxcombo `(899, 129)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | all | prog |
| 8 | `kkF_23_008` | Total Effect2 · Switch | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | Off \| On | all | prog |
| 9 | `kkF_23_009` | Master Effect · Return 1 | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | all | prog |
| 10 | `kkF_23_010` | Master Effect · Return 2 | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | all | prog |
| 11 | `kkF_23_011` | Master Effect · Chain Direction | `(5, 165, 146)` | combo `(5, 178)` 146x20 | M.Fx1 -> M.Fx2 \| M.Fx | all | prog |
| 12 | `kkF_23_012` | Master Effect · Chain Switch | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | all | prog |
| 13 | `kkF_23_013` | Master Effect · Chain Level | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | all | prog |


### 6.2 Combi - `kkEdTabsC` - 0x4B dump obj 02 (Combi)

#### Tab 1 - Commun (5 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_01_001` | Common · Favorite | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Off \| On | combi | combi |
| 2 | `kkC_01_002` | Common · Auto Load Program Tone Adjust | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | combi | combi |
| 3 | `kkC_01_003` | Common · Scale Type | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..26 step 1.0 (0 dec) | combi | combi |
| 4 | `kkC_01_004` | Common · Scale Key | `(452, 116, 146)` | combo `(452, 129)` 146x20 | C \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| B | combi | combi |
| 5 | `kkC_01_005` | Common · Scale Random | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..7 step 1.0 (0 dec) | combi | combi |

#### Tab 2 - Vector (42 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_02_001` | Vector Control · JS +X Assign | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..162 step 1.0 (0 dec) | combi | combi |
| 2 | `kkC_02_002` | Vector Control · JS -X Assign | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..162 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_02_003` | Vector Control · JS +Y Assign | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..162 step 1.0 (0 dec) | combi | combi |
| 4 | `kkC_02_004` | Vector Control · JS -Y Assign | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..162 step 1.0 (0 dec) | combi | combi |
| 5 | `kkC_02_005` | Vector Control · X Mode | `(601, 116, 146)` | combo `(601, 129)` 146x20 | Pos \| 1 \| 2 \| Split | combi | combi |
| 6 | `kkC_02_006` | Vector Control · Y Mode | `(750, 116, 146)` | combo `(750, 129)` 146x20 | Pos \| 1 \| 2 \| Split | combi | combi |
| 7 | `kkC_02_007` | Vector Control · Enable Vector | `(899, 116, 146)` | combo `(899, 129)` 146x20 | Off \| On | combi | combi |
| 8 | `kkC_02_008` | Vector Control · Enable Control Change | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | Off \| On | combi | combi |
| 9 | `kkC_02_009` | Vector Control · Enable Volume Control | `(1197, 116, 146)` | combo `(1197, 129)` 146x20 | Off \| On | combi | combi |
| 10 | `kkC_02_010` | Vector Control · Equal Power | `(1346, 116, 146)` | combo `(1346, 129)` 146x20 | Off \| On | combi | combi |
| 11 | `kkC_02_011` | Vector Control · Tempo Based | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Off \| On | combi | combi |
| 12 | `kkC_02_012` | Vector Control · Key Sync | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | combi | combi |
| 13 | `kkC_02_013` | Vector Control · (0) Position X | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | -127..127 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_02_014` | Vector Control · (0) Position Y | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | -127..127 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_02_015` | Vector Control · (1) Position X | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | -127..127 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_02_016` | Vector Control · (1) Position Y | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -127..127 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_02_017` | Vector Control · (2) Position X | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -127..127 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_02_018` | Vector Control · (2) Position Y | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -127..127 step 1.0 (0 dec) | combi | combi |
| 19 | `kkC_02_019` | Vector Control · (3) Position X | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | -127..127 step 1.0 (0 dec) | combi | combi |
| 20 | `kkC_02_020` | Vector Control · (3) Position Y | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | -127..127 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_02_021` | Vector Control · (4) Position X | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | -127..127 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_02_022` | Vector Control · (4) Position Y | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | -127..127 step 1.0 (0 dec) | combi | combi |
| 23 | `kkC_02_023` | Vector Control · (0to1) Hold Time Base Note | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 1/1 | combi | combi |
| 24 | `kkC_02_024` | Vector Control · (1to2) Hold Time Base Note | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 1/1 | combi | combi |
| 25 | `kkC_02_025` | Vector Control · (2to3) Hold Time Base Note | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 1/1 | combi | combi |
| 26 | `kkC_02_026` | Vector Control · (3to4) Hold Time Base Note | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 1/1 | combi | combi |
| 27 | `kkC_02_027` | Vector Control · (0to1) Hold Time Times | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_02_028` | Vector Control · (1to2) Hold Time Times | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_02_029` | Vector Control · (2to3) Hold Time Times | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 30 | `kkC_02_030` | Vector Control · (3to4) Hold Time Times | `(1346, 214, 146)` | knob `(1401, 226)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 31 | `kkC_02_031` | Vector Control · (0to1) Transition Time Base Note | `(5, 263, 146)` | combo `(5, 276)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 32 | `kkC_02_032` | Vector Control · (1to2) Transition Time Base Note | `(154, 263, 146)` | combo `(154, 276)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 33 | `kkC_02_033` | Vector Control · (2to3) Transition Time Base Note | `(303, 263, 146)` | combo `(303, 276)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 34 | `kkC_02_034` | Vector Control · (3toLoop) Transition Time Base Note | `(452, 263, 146)` | combo `(452, 276)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 35 | `kkC_02_035` | Vector Control · (3to4) Transition Time Base Note | `(601, 263, 146)` | combo `(601, 276)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 36 | `kkC_02_036` | Vector Control · (0to1) Transition Time Times | `(750, 263, 146)` | knob `(805, 275)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 37 | `kkC_02_037` | Vector Control · (1to2) Transition Time Times | `(899, 263, 146)` | knob `(954, 275)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 38 | `kkC_02_038` | Vector Control · (2to3) Transition Time Times | `(1048, 263, 146)` | knob `(1103, 275)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 39 | `kkC_02_039` | Vector Control · (3toLoop) Transition Time Times | `(1197, 263, 146)` | knob `(1252, 275)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 40 | `kkC_02_040` | Vector Control · (3to4) Transition Time Times | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 41 | `kkC_02_041` | Vector Control · Loop Direction | `(5, 312, 146)` | combo `(5, 325)` 146x20 | 0->3 \| 1 \| 2 \| 3 \| 1<->3 | combi | combi |
| 42 | `kkC_02_042` | Vector Control · Loop Repeat | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |

#### Tab 3 - Drum Track (11 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_03_001` | Drum Track Common · Pattern Bank | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Preset \| User | combi | combi |
| 2 | `kkC_03_002` | Drum Track Common · Trigger Button Mode | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Start Immediately \| W | combi | combi |
| 3 | `kkC_03_003` | Drum Track Common · Trigger Latch Mode | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Off \| 1 \| Use KARMA Latch | combi | combi |
| 4 | `kkC_03_004` | Drum Track Common · Trigger Sync Mode | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| Sequence | combi | combi |
| 5 | `kkC_03_005` | Drum Track Common · Drum Track On | `(601, 116, 146)` | combo `(601, 129)` 146x20 | Off \| On | combi | combi |
| 6 | `kkC_03_006` | Drum Track Common · Trigger Key Zone Bottom | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_03_007` | Drum Track Common · Trigger Key Zone Top | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_03_008` | Drum Track Common · Trigger Velocity Zone Bottom | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_03_009` | Drum Track Common · Trigger Velocity Zone Top | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_03_010` | Drum Track Common · Shift | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | -24..24 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_03_011` | Drum Track Common · Output MIDI Channel | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |

#### Tab 4 - IFX 1-4 (44 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_04_001` | Insert Effect1 · Effect Type | `(5, 116, 146)` | fxcombo `(5, 129)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | combi | combi |
| 2 | `kkC_04_002` | Insert Effect1 · Channel | `(154, 116, 146)` | combo `(154, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| All Routed | combi | combi |
| 3 | `kkC_04_003` | Insert Effect1 · Switch | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Off \| On | combi | combi |
| 4 | `kkC_04_004` | Insert Effect1 · Chain Switch | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Chain Off \| Chain On | combi | combi |
| 5 | `kkC_04_005` | Insert Effect1 · Chain To | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 2..12 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_04_006` | Insert Effect1 · Panpot | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_04_007` | Insert Effect1 · Bus Select | `(899, 116, 146)` | combo `(899, 129)` 146x20 | L/R \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| Off | combi | combi |
| 8 | `kkC_04_008` | Insert Effect1 · Fx Control Bus | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 9 | `kkC_04_009` | Insert Effect1 · Send1 | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_04_010` | Insert Effect1 · Send2 | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_04_011` | Insert Effect1 · Rec Bus | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 12 | `kkC_04_012` | Insert Effect2 · Effect Type | `(154, 165, 146)` | fxcombo `(154, 178)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | combi | combi |
| 13 | `kkC_04_013` | Insert Effect2 · Channel | `(303, 165, 146)` | combo `(303, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| All Routed | combi | combi |
| 14 | `kkC_04_014` | Insert Effect2 · Switch | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_04_015` | Insert Effect2 · Chain Switch | `(601, 165, 146)` | combo `(601, 178)` 146x20 | Chain Off \| Chain On | combi | combi |
| 16 | `kkC_04_016` | Insert Effect2 · Chain To | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 3..12 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_04_017` | Insert Effect2 · Panpot | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_04_018` | Insert Effect2 · Bus Select | `(1048, 165, 146)` | combo `(1048, 178)` 146x20 | L/R \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| Off | combi | combi |
| 19 | `kkC_04_019` | Insert Effect2 · Fx Control Bus | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 20 | `kkC_04_020` | Insert Effect2 · Send1 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_04_021` | Insert Effect2 · Send2 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_04_022` | Insert Effect2 · Rec Bus | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 23 | `kkC_04_023` | Insert Effect3 · Effect Type | `(303, 214, 146)` | fxcombo `(303, 227)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | combi | combi |
| 24 | `kkC_04_024` | Insert Effect3 · Channel | `(452, 214, 146)` | combo `(452, 227)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| All Routed | combi | combi |
| 25 | `kkC_04_025` | Insert Effect3 · Switch | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_04_026` | Insert Effect3 · Chain Switch | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Chain Off \| Chain On | combi | combi |
| 27 | `kkC_04_027` | Insert Effect3 · Chain To | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 4..12 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_04_028` | Insert Effect3 · Panpot | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_04_029` | Insert Effect3 · Bus Select | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | L/R \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| Off | combi | combi |
| 30 | `kkC_04_030` | Insert Effect3 · Fx Control Bus | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_04_031` | Insert Effect3 · Send1 | `(5, 263, 146)` | knob `(60, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 32 | `kkC_04_032` | Insert Effect3 · Send2 | `(154, 263, 146)` | knob `(209, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 33 | `kkC_04_033` | Insert Effect3 · Rec Bus | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 34 | `kkC_04_034` | Insert Effect4 · Effect Type | `(452, 263, 146)` | fxcombo `(452, 276)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | combi | combi |
| 35 | `kkC_04_035` | Insert Effect4 · Channel | `(601, 263, 146)` | combo `(601, 276)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| All Routed | combi | combi |
| 36 | `kkC_04_036` | Insert Effect4 · Switch | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Off \| On | combi | combi |
| 37 | `kkC_04_037` | Insert Effect4 · Chain Switch | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Chain Off \| Chain On | combi | combi |
| 38 | `kkC_04_038` | Insert Effect4 · Chain To | `(1048, 263, 146)` | knob `(1103, 275)` 36x36 rotary | 5..12 step 1.0 (0 dec) | combi | combi |
| 39 | `kkC_04_039` | Insert Effect4 · Panpot | `(1197, 263, 146)` | knob `(1252, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 40 | `kkC_04_040` | Insert Effect4 · Bus Select | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | L/R \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| Off | combi | combi |
| 41 | `kkC_04_041` | Insert Effect4 · Fx Control Bus | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 42 | `kkC_04_042` | Insert Effect4 · Send1 | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_04_043` | Insert Effect4 · Send2 | `(303, 312, 146)` | knob `(358, 324)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 44 | `kkC_04_044` | Insert Effect4 · Rec Bus | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |

#### Tab 5 - IFX 5-8 (44 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_05_001` | Insert Effect5 · Effect Type | `(5, 116, 146)` | fxcombo `(5, 129)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | combi | combi |
| 2 | `kkC_05_002` | Insert Effect5 · Channel | `(154, 116, 146)` | combo `(154, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| All Routed | combi | combi |
| 3 | `kkC_05_003` | Insert Effect5 · Switch | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Off \| On | combi | combi |
| 4 | `kkC_05_004` | Insert Effect5 · Chain Switch | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Chain Off \| Chain On | combi | combi |
| 5 | `kkC_05_005` | Insert Effect5 · Chain To | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 6..12 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_05_006` | Insert Effect5 · Panpot | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_05_007` | Insert Effect5 · Bus Select | `(899, 116, 146)` | combo `(899, 129)` 146x20 | L/R \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| Off | combi | combi |
| 8 | `kkC_05_008` | Insert Effect5 · Fx Control Bus | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 9 | `kkC_05_009` | Insert Effect5 · Send1 | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_05_010` | Insert Effect5 · Send2 | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_05_011` | Insert Effect5 · Rec Bus | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 12 | `kkC_05_012` | Insert Effect6 · Effect Type | `(154, 165, 146)` | fxcombo `(154, 178)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | combi | combi |
| 13 | `kkC_05_013` | Insert Effect6 · Channel | `(303, 165, 146)` | combo `(303, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| All Routed | combi | combi |
| 14 | `kkC_05_014` | Insert Effect6 · Switch | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_05_015` | Insert Effect6 · Chain Switch | `(601, 165, 146)` | combo `(601, 178)` 146x20 | Chain Off \| Chain On | combi | combi |
| 16 | `kkC_05_016` | Insert Effect6 · Chain To | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 7..12 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_05_017` | Insert Effect6 · Panpot | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_05_018` | Insert Effect6 · Bus Select | `(1048, 165, 146)` | combo `(1048, 178)` 146x20 | L/R \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| Off | combi | combi |
| 19 | `kkC_05_019` | Insert Effect6 · Fx Control Bus | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 20 | `kkC_05_020` | Insert Effect6 · Send1 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_05_021` | Insert Effect6 · Send2 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_05_022` | Insert Effect6 · Rec Bus | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 23 | `kkC_05_023` | Insert Effect7 · Effect Type | `(303, 214, 146)` | fxcombo `(303, 227)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | combi | combi |
| 24 | `kkC_05_024` | Insert Effect7 · Channel | `(452, 214, 146)` | combo `(452, 227)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| All Routed | combi | combi |
| 25 | `kkC_05_025` | Insert Effect7 · Switch | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_05_026` | Insert Effect7 · Chain Switch | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Chain Off \| Chain On | combi | combi |
| 27 | `kkC_05_027` | Insert Effect7 · Chain To | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 8..12 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_05_028` | Insert Effect7 · Panpot | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_05_029` | Insert Effect7 · Bus Select | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | L/R \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| Off | combi | combi |
| 30 | `kkC_05_030` | Insert Effect7 · Fx Control Bus | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_05_031` | Insert Effect7 · Send1 | `(5, 263, 146)` | knob `(60, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 32 | `kkC_05_032` | Insert Effect7 · Send2 | `(154, 263, 146)` | knob `(209, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 33 | `kkC_05_033` | Insert Effect7 · Rec Bus | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 34 | `kkC_05_034` | Insert Effect8 · Effect Type | `(452, 263, 146)` | fxcombo `(452, 276)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | combi | combi |
| 35 | `kkC_05_035` | Insert Effect8 · Channel | `(601, 263, 146)` | combo `(601, 276)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| All Routed | combi | combi |
| 36 | `kkC_05_036` | Insert Effect8 · Switch | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Off \| On | combi | combi |
| 37 | `kkC_05_037` | Insert Effect8 · Chain Switch | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Chain Off \| Chain On | combi | combi |
| 38 | `kkC_05_038` | Insert Effect8 · Chain To | `(1048, 263, 146)` | knob `(1103, 275)` 36x36 rotary | 9..12 step 1.0 (0 dec) | combi | combi |
| 39 | `kkC_05_039` | Insert Effect8 · Panpot | `(1197, 263, 146)` | knob `(1252, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 40 | `kkC_05_040` | Insert Effect8 · Bus Select | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | L/R \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| Off | combi | combi |
| 41 | `kkC_05_041` | Insert Effect8 · Fx Control Bus | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 42 | `kkC_05_042` | Insert Effect8 · Send1 | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_05_043` | Insert Effect8 · Send2 | `(303, 312, 146)` | knob `(358, 324)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 44 | `kkC_05_044` | Insert Effect8 · Rec Bus | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |

#### Tab 6 - IFX 9-12 (41 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_06_001` | Insert Effect9 · Effect Type | `(5, 116, 146)` | fxcombo `(5, 129)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | combi | combi |
| 2 | `kkC_06_002` | Insert Effect9 · Channel | `(154, 116, 146)` | combo `(154, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| All Routed | combi | combi |
| 3 | `kkC_06_003` | Insert Effect9 · Switch | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Off \| On | combi | combi |
| 4 | `kkC_06_004` | Insert Effect9 · Chain Switch | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Chain Off \| Chain On | combi | combi |
| 5 | `kkC_06_005` | Insert Effect9 · Chain To | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 10..12 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_06_006` | Insert Effect9 · Panpot | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_06_007` | Insert Effect9 · Bus Select | `(899, 116, 146)` | combo `(899, 129)` 146x20 | L/R \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| Off | combi | combi |
| 8 | `kkC_06_008` | Insert Effect9 · Fx Control Bus | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 9 | `kkC_06_009` | Insert Effect9 · Send1 | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_06_010` | Insert Effect9 · Send2 | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_06_011` | Insert Effect9 · Rec Bus | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 12 | `kkC_06_012` | Insert Effect10 · Effect Type | `(154, 165, 146)` | fxcombo `(154, 178)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | combi | combi |
| 13 | `kkC_06_013` | Insert Effect10 · Channel | `(303, 165, 146)` | combo `(303, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| All Routed | combi | combi |
| 14 | `kkC_06_014` | Insert Effect10 · Switch | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_06_015` | Insert Effect10 · Chain Switch | `(601, 165, 146)` | combo `(601, 178)` 146x20 | Chain Off \| Chain On | combi | combi |
| 16 | `kkC_06_016` | Insert Effect10 · Chain To | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 11..12 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_06_017` | Insert Effect10 · Panpot | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_06_018` | Insert Effect10 · Bus Select | `(1048, 165, 146)` | combo `(1048, 178)` 146x20 | L/R \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| Off | combi | combi |
| 19 | `kkC_06_019` | Insert Effect10 · Fx Control Bus | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 20 | `kkC_06_020` | Insert Effect10 · Send1 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_06_021` | Insert Effect10 · Send2 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_06_022` | Insert Effect10 · Rec Bus | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 23 | `kkC_06_023` | Insert Effect11 · Effect Type | `(303, 214, 146)` | fxcombo `(303, 227)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | combi | combi |
| 24 | `kkC_06_024` | Insert Effect11 · Channel | `(452, 214, 146)` | combo `(452, 227)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| All Routed | combi | combi |
| 25 | `kkC_06_025` | Insert Effect11 · Switch | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_06_026` | Insert Effect11 · Chain Switch | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Chain Off \| Chain On | combi | combi |
| 27 | `kkC_06_027` | Insert Effect11 · Panpot | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_06_028` | Insert Effect11 · Bus Select | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | L/R \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| Off | combi | combi |
| 29 | `kkC_06_029` | Insert Effect11 · Fx Control Bus | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 30 | `kkC_06_030` | Insert Effect11 · Send1 | `(1346, 214, 146)` | knob `(1401, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 31 | `kkC_06_031` | Insert Effect11 · Send2 | `(5, 263, 146)` | knob `(60, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 32 | `kkC_06_032` | Insert Effect11 · Rec Bus | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 33 | `kkC_06_033` | Insert Effect12 · Effect Type | `(303, 263, 146)` | fxcombo `(303, 276)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | combi | combi |
| 34 | `kkC_06_034` | Insert Effect12 · Channel | `(452, 263, 146)` | combo `(452, 276)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| All Routed | combi | combi |
| 35 | `kkC_06_035` | Insert Effect12 · Switch | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | combi | combi |
| 36 | `kkC_06_036` | Insert Effect12 · Panpot | `(750, 263, 146)` | knob `(805, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 37 | `kkC_06_037` | Insert Effect12 · Bus Select | `(899, 263, 146)` | combo `(899, 276)` 146x20 | L/R \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| Off | combi | combi |
| 38 | `kkC_06_038` | Insert Effect12 · Fx Control Bus | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 39 | `kkC_06_039` | Insert Effect12 · Send1 | `(1197, 263, 146)` | knob `(1252, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 40 | `kkC_06_040` | Insert Effect12 · Send2 | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 41 | `kkC_06_041` | Insert Effect12 · Rec Bus | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |

#### Tab 7 - MFX·TFX (18 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_07_001` | Master Effect1 · Effect Type | `(5, 116, 146)` | fxcombo `(5, 129)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | combi | combi |
| 2 | `kkC_07_002` | Master Effect1 · Channel | `(154, 116, 146)` | combo `(154, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 3 | `kkC_07_003` | Master Effect1 · Switch | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Off \| On | combi | combi |
| 4 | `kkC_07_004` | Master Effect2 · Effect Type | `(452, 116, 146)` | fxcombo `(452, 129)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | combi | combi |
| 5 | `kkC_07_005` | Master Effect2 · Channel | `(601, 116, 146)` | combo `(601, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 6 | `kkC_07_006` | Master Effect2 · Switch | `(750, 116, 146)` | combo `(750, 129)` 146x20 | Off \| On | combi | combi |
| 7 | `kkC_07_007` | Total Effect1 · Effect Type | `(899, 116, 146)` | fxcombo `(899, 129)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | combi | combi |
| 8 | `kkC_07_008` | Total Effect1 · Channel | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 9 | `kkC_07_009` | Total Effect1 · Switch | `(1197, 116, 146)` | combo `(1197, 129)` 146x20 | Off \| On | combi | combi |
| 10 | `kkC_07_010` | Total Effect2 · Effect Type | `(1346, 116, 146)` | fxcombo `(1346, 129)` 146x20 | FX type list (shared, 331 entries, idx 0..330) | combi | combi |
| 11 | `kkC_07_011` | Total Effect2 · Channel | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 12 | `kkC_07_012` | Total Effect2 · Switch | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | combi | combi |
| 13 | `kkC_07_013` | Master Effect · Return 1 | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_07_014` | Master Effect · Return 2 | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_07_015` | Master Effect · Chain Direction | `(601, 165, 146)` | combo `(601, 178)` 146x20 | M.Fx1 -> M.Fx2 \| M.Fx | combi | combi |
| 16 | `kkC_07_016` | Master Effect · Chain Switch | `(750, 165, 146)` | combo `(750, 178)` 146x20 | Off \| On | combi | combi |
| 17 | `kkC_07_017` | Master Effect · Chain Level | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_07_018` | Total Effect · Master Volume | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |

#### Tab 8 - Audio In (48 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_08_001` | Audio Input 1 · Level | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 2 | `kkC_08_002` | Audio Input 1 · Pan | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_08_003` | Audio Input 1 · Send1 | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 4 | `kkC_08_004` | Audio Input 1 · Send2 | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 5 | `kkC_08_005` | Audio Input 1 · Bus Select | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_08_006` | Audio Input 1 · Fx Control Bus | `(750, 116, 146)` | combo `(750, 129)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 7 | `kkC_08_007` | Audio Input 1 · Rec Bus | `(899, 116, 146)` | combo `(899, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 8 | `kkC_08_008` | Audio Input 1 · Mute | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | Off \| On | combi | combi |
| 9 | `kkC_08_009` | Audio Input 2 · Level | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_08_010` | Audio Input 2 · Pan | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_08_011` | Audio Input 2 · Send1 | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 12 | `kkC_08_012` | Audio Input 2 · Send2 | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 13 | `kkC_08_013` | Audio Input 2 · Bus Select | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_08_014` | Audio Input 2 · Fx Control Bus | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 15 | `kkC_08_015` | Audio Input 2 · Rec Bus | `(601, 165, 146)` | combo `(601, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 16 | `kkC_08_016` | Audio Input 2 · Mute | `(750, 165, 146)` | combo `(750, 178)` 146x20 | Off \| On | combi | combi |
| 17 | `kkC_08_017` | Audio Input 3 · Level | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_08_018` | Audio Input 3 · Pan | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 19 | `kkC_08_019` | Audio Input 3 · Send1 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 20 | `kkC_08_020` | Audio Input 3 · Send2 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_08_021` | Audio Input 3 · Bus Select | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_08_022` | Audio Input 3 · Fx Control Bus | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 23 | `kkC_08_023` | Audio Input 3 · Rec Bus | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 24 | `kkC_08_024` | Audio Input 3 · Mute | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | combi | combi |
| 25 | `kkC_08_025` | Audio Input 4 · Level | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 26 | `kkC_08_026` | Audio Input 4 · Pan | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 27 | `kkC_08_027` | Audio Input 4 · Send1 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_08_028` | Audio Input 4 · Send2 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_08_029` | Audio Input 4 · Bus Select | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 30 | `kkC_08_030` | Audio Input 4 · Fx Control Bus | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_08_031` | Audio Input 4 · Rec Bus | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 32 | `kkC_08_032` | Audio Input 4 · Mute | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | combi | combi |
| 33 | `kkC_08_033` | S/PDIF L · Level | `(303, 263, 146)` | knob `(358, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 34 | `kkC_08_034` | S/PDIF L · Pan | `(452, 263, 146)` | knob `(507, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 35 | `kkC_08_035` | S/PDIF L · Send1 | `(601, 263, 146)` | knob `(656, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 36 | `kkC_08_036` | S/PDIF L · Send2 | `(750, 263, 146)` | knob `(805, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 37 | `kkC_08_037` | S/PDIF L · Bus Select | `(899, 263, 146)` | knob `(954, 275)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 38 | `kkC_08_038` | S/PDIF L · Fx Control Bus | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 39 | `kkC_08_039` | S/PDIF L · Rec Bus | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 40 | `kkC_08_040` | S/PDIF L · Mute | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Off \| On | combi | combi |
| 41 | `kkC_08_041` | S/PDIF R · Level | `(5, 312, 146)` | knob `(60, 324)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 42 | `kkC_08_042` | S/PDIF R · Pan | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_08_043` | S/PDIF R · Send1 | `(303, 312, 146)` | knob `(358, 324)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 44 | `kkC_08_044` | S/PDIF R · Send2 | `(452, 312, 146)` | knob `(507, 324)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 45 | `kkC_08_045` | S/PDIF R · Bus Select | `(601, 312, 146)` | knob `(656, 324)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 46 | `kkC_08_046` | S/PDIF R · Fx Control Bus | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 47 | `kkC_08_047` | S/PDIF R · Rec Bus | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 48 | `kkC_08_048` | S/PDIF R · Mute | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Off \| On | combi | combi |

#### Tab 9 - LFO & In (15 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_09_001` | Effect LFO1 · Sync | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Off \| On | combi | combi |
| 2 | `kkC_09_002` | Effect LFO1 · Source | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..37 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_09_003` | Effect LFO1 · MIDI Channel | `(303, 116, 146)` | combo `(303, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 4 | `kkC_09_004` | Effect LFO1 · BPM | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..26001 step 1.0 (0 dec) | combi | combi |
| 5 | `kkC_09_005` | Effect LFO1 · MIDI Sync Base Note | `(601, 116, 146)` | combo `(601, 129)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 6 | `kkC_09_006` | Effect LFO1 · MIDI Sync | `(750, 116, 146)` | combo `(750, 129)` 146x20 | Off \| On | combi | combi |
| 7 | `kkC_09_007` | Effect LFO1 · MIDI Sync Base Times | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_09_008` | Effect LFO2 · Sync | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | Off \| On | combi | combi |
| 9 | `kkC_09_009` | Effect LFO2 · Source | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..37 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_09_010` | Effect LFO2 · MIDI Channel | `(1346, 116, 146)` | combo `(1346, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 11 | `kkC_09_011` | Effect LFO2 · BPM | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | 0..26001 step 1.0 (0 dec) | combi | combi |
| 12 | `kkC_09_012` | Effect LFO2 · MIDI Sync Base Note | `(154, 165, 146)` | combo `(154, 178)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 13 | `kkC_09_013` | Effect LFO2 · MIDI Sync | `(303, 165, 146)` | combo `(303, 178)` 146x20 | Off \| On | combi | combi |
| 14 | `kkC_09_014` | Effect LFO2 · MIDI Sync Base Times | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_09_015` | Audio Input · Use Global Setting | `(601, 165, 146)` | combo `(601, 178)` 146x20 | Off \| On | combi | combi |

#### Tab 10 - Contrôleurs (14 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_10_001` | Assignable Controller · Switch1 Assign | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| Chord Switch | combi | combi |
| 2 | `kkC_10_002` | Assignable Controller · Switch1 Mode | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Toggle \| Momentary | combi | combi |
| 3 | `kkC_10_003` | Assignable Controller · Switch1 Status | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Off \| On | combi | combi |
| 4 | `kkC_10_004` | Assignable Controller · Switch2 Assign | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| Chord Switch | combi | combi |
| 5 | `kkC_10_005` | Assignable Controller · Switch2 Mode | `(601, 116, 146)` | combo `(601, 129)` 146x20 | Toggle \| Momentary | combi | combi |
| 6 | `kkC_10_006` | Assignable Controller · Switch2 Status | `(750, 116, 146)` | combo `(750, 129)` 146x20 | Off \| On | combi | combi |
| 7 | `kkC_10_007` | Assignable Controller · Knob5 Assign | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..142 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_10_008` | Assignable Controller · Knob6 Assign | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..142 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_10_009` | Assignable Controller · Knob7 Assign | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..142 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_10_010` | Assignable Controller · Knob8 Assign | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..142 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_10_011` | Controller · Control Assign | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Timbre1-8 \| 1 \| 2 \| 3 \| 4 \| 5 \| Custom Mo | combi | combi |
| 12 | `kkC_10_012` | Controller · Knob Mode | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Channel Strip \| Indiv | combi | combi |
| 13 | `kkC_10_013` | Controller · Selected Timbre | `(303, 165, 146)` | combo `(303, 178)` 146x20 | Timbre1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| Timbre16 | combi | combi |
| 14 | `kkC_10_014` | Controller · Selected Audio | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Audio Input 1 \| 1 \| 2 \| 3 \| 4 \| S/PDI | combi | combi |

#### Tab 11 - Timbre 1 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_11_001` | Timbre1 · Program Number | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 2 | `kkC_11_002` | Timbre1 · Bank Number | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..30 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_11_003` | Timbre1 · MIDI Channel | `(303, 116, 146)` | combo `(303, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 4 | `kkC_11_004` | Timbre1 · Status | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| External2 | combi | combi |
| 5 | `kkC_11_005` | Timbre1 · Bank MSB | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_11_006` | Timbre1 · Bank LSB | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_11_007` | Timbre1 · Volume | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_11_008` | Timbre1 · Transpose | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -60..60 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_11_009` | Timbre1 · Detune | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_11_010` | Timbre1 · Delay Time | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..6001 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_11_011` | Timbre1 · Delay Tempo Base Note | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 12 | `kkC_11_012` | Timbre1 · Delay Mode | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | combi | combi |
| 13 | `kkC_11_013` | Timbre1 · Delay Tempo Times | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_11_014` | Timbre1 · Pan | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_11_015` | Timbre1 · Send1 | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_11_016` | Timbre1 · Send2 | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_11_017` | Timbre1 · Drum Kit Patch IFX1 | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_11_018` | Timbre1 · Drum Kit Patch IFX2 | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 19 | `kkC_11_019` | Timbre1 · Drum Kit Patch IFX3 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 20 | `kkC_11_020` | Timbre1 · Drum Kit Patch IFX4 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_11_021` | Timbre1 · Drum Kit Patch IFX5 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_11_022` | Timbre1 · Drum Kit Patch IFX6 | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 23 | `kkC_11_023` | Timbre1 · Drum Kit Patch IFX7 | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 24 | `kkC_11_024` | Timbre1 · Drum Kit Patch IFX8 | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 25 | `kkC_11_025` | Timbre1 · Drum Kit Patch IFX9 | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 26 | `kkC_11_026` | Timbre1 · Drum Kit Patch IFX10 | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 27 | `kkC_11_027` | Timbre1 · Drum Kit Patch IFX11 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_11_028` | Timbre1 · Drum Kit Patch IFX12 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_11_029` | Timbre1 · Bus Select | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 30 | `kkC_11_030` | Timbre1 · Fx Bus Select | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_11_031` | Timbre1 · Use Drum Kit Bus Setting | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_11_032` | Timbre1 · Rec Bus | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 33 | `kkC_11_033` | Timbre1 · Chord Source | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| Pad 8 | combi | combi |
| 34 | `kkC_11_034` | Timbre1 · Max # of Notes | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 16 | combi | combi |
| 35 | `kkC_11_035` | Timbre1 · Chord Mode | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Program \| 1 \| 2 \| Advanced | combi | combi |
| 36 | `kkC_11_036` | Timbre1 · (Filter) Program Change | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Disable \| Enable | combi | combi |
| 37 | `kkC_11_037` | Timbre1 · (Filter) After Touch | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Disable \| Enable | combi | combi |
| 38 | `kkC_11_038` | Timbre1 · (Filter) Damper | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Disable \| Enable | combi | combi |
| 39 | `kkC_11_039` | Timbre1 · (Filter) Portamento | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Disable \| Enable | combi | combi |
| 40 | `kkC_11_040` | Timbre1 · (Filter) JSX As Mod. | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Disable \| Enable | combi | combi |
| 41 | `kkC_11_041` | Timbre1 · (Filter) JS+Y | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Disable \| Enable | combi | combi |
| 42 | `kkC_11_042` | Timbre1 · (Filter) JS-Y | `(154, 312, 146)` | combo `(154, 325)` 146x20 | Disable \| Enable | combi | combi |
| 43 | `kkC_11_043` | Timbre1 · (Filter) Ribbon | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Disable \| Enable | combi | combi |
| 44 | `kkC_11_044` | Timbre1 · (Filter) Knob1 | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Disable \| Enable | combi | combi |
| 45 | `kkC_11_045` | Timbre1 · (Filter) Knob2 | `(601, 312, 146)` | combo `(601, 325)` 146x20 | Disable \| Enable | combi | combi |
| 46 | `kkC_11_046` | Timbre1 · (Filter) Knob3 | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Disable \| Enable | combi | combi |
| 47 | `kkC_11_047` | Timbre1 · (Filter) Knob4 | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Disable \| Enable | combi | combi |
| 48 | `kkC_11_048` | Timbre1 · (Filter) Knob5 | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Disable \| Enable | combi | combi |
| 49 | `kkC_11_049` | Timbre1 · (Filter) Knob6 | `(1197, 312, 146)` | combo `(1197, 325)` 146x20 | Disable \| Enable | combi | combi |
| 50 | `kkC_11_050` | Timbre1 · (Filter) Knob7 | `(1346, 312, 146)` | combo `(1346, 325)` 146x20 | Disable \| Enable | combi | combi |
| 51 | `kkC_11_051` | Timbre1 · (Filter) Knob8 | `(5, 361, 146)` | combo `(5, 374)` 146x20 | Disable \| Enable | combi | combi |
| 52 | `kkC_11_052` | Timbre1 · (Filter) Switch1 | `(154, 361, 146)` | combo `(154, 374)` 146x20 | Disable \| Enable | combi | combi |
| 53 | `kkC_11_053` | Timbre1 · (Filter) Switch2 | `(303, 361, 146)` | combo `(303, 374)` 146x20 | Disable \| Enable | combi | combi |
| 54 | `kkC_11_054` | Timbre1 · (Filter) Foot Switch | `(452, 361, 146)` | combo `(452, 374)` 146x20 | Disable \| Enable | combi | combi |
| 55 | `kkC_11_055` | Timbre1 · (Filter) Foot Pedal | `(601, 361, 146)` | combo `(601, 374)` 146x20 | Disable \| Enable | combi | combi |
| 56 | `kkC_11_056` | Timbre1 · (Filter) Other CC# | `(750, 361, 146)` | combo `(750, 374)` 146x20 | Disable \| Enable | combi | combi |
| 57 | `kkC_11_057` | Timbre1 · Use Program Scale | `(899, 361, 146)` | combo `(899, 374)` 146x20 | Off \| On | combi | combi |
| 58 | `kkC_11_058` | Timbre1 · Auto Load Program EQ | `(1048, 361, 146)` | combo `(1048, 374)` 146x20 | Off \| On | combi | combi |
| 59 | `kkC_11_059` | Timbre1 · Mute | `(1197, 361, 146)` | combo `(1197, 374)` 146x20 | Off \| On | combi | combi |
| 60 | `kkC_11_060` | Timbre1 · Osc Mode | `(1346, 361, 146)` | combo `(1346, 374)` 146x20 | Program \| 1 \| 2 \| Mono Legato | combi | combi |

#### Tab 12 - Timbre 1·2 (43 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_12_001` | Timbre1 · Osc Select | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Both \| 1 \| OSC2 | combi | combi |
| 2 | `kkC_12_002` | Timbre1 · Timbre Priority | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | combi | combi |
| 3 | `kkC_12_003` | Timbre1 · Osc On/Off By KARMA | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Normal \| 1 \| Osc Off by K | combi | combi |
| 4 | `kkC_12_004` | Timbre1 · (Filter) Waveform SysEx | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Disable \| Enable | combi | combi |
| 5 | `kkC_12_005` | Timbre1 · Key Window Top | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_12_006` | Timbre1 · Key Window Bottom | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_12_007` | Timbre1 · Vel.Window High | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_12_008` | Timbre1 · Vel.Window Low | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_12_009` | Timbre1 · Vel.Window High Slope | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 10 | `kkC_12_010` | Timbre1 · Vel.Window Low Slope | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 11 | `kkC_12_011` | Timbre1 · Quantize Trigger | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 12 | `kkC_12_012` | Timbre1 · Key Sync | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 13 | `kkC_12_013` | Timbre1 · (Track EQ) Trim | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_12_014` | Timbre1 · (Track EQ) Bypass | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_12_015` | Timbre1 · (Track EQ) Mid Frequency | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..165 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_12_016` | Timbre1 · (Track EQ) Low Gain | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 17 | `kkC_12_017` | Timbre1 · (Track EQ) Mid Gain | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 18 | `kkC_12_018` | Timbre1 · (Track EQ) High Gain | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 19 | `kkC_12_019` | Timbre1 · VJS Assign | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| -Y | combi | combi |
| 20 | `kkC_12_020` | Timbre1 · Volume Center | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..100 step 25.0 (0 dec) | combi | combi |
| 21 | `kkC_12_021` | Timbre1 · Program Vector Volume | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Off \| On | combi | combi |
| 22 | `kkC_12_022` | Timbre1 · Combi Vector CC | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| On | combi | combi |
| 23 | `kkC_12_023` | Timbre1 · Program Vector CC | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| On | combi | combi |
| 24 | `kkC_12_024` | Timbre1 · Switch1 Value | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | combi | combi |
| 25 | `kkC_12_025` | Timbre1 · Switch2 Value | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_12_026` | Timbre1 · Switch3 Value | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | combi | combi |
| 27 | `kkC_12_027` | Timbre1 · Switch4 Value | `(899, 214, 146)` | combo `(899, 227)` 146x20 | Off \| On | combi | combi |
| 28 | `kkC_12_028` | Timbre1 · Switch5 Value | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | Off \| On | combi | combi |
| 29 | `kkC_12_029` | Timbre1 · Switch6 Value | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| On | combi | combi |
| 30 | `kkC_12_030` | Timbre1 · Switch7 Value | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| On | combi | combi |
| 31 | `kkC_12_031` | Timbre1 · Switch8 Value | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_12_032` | Timbre1 · Switch9 Value | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | combi | combi |
| 33 | `kkC_12_033` | Timbre1 · Switch10 Value | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Off \| On | combi | combi |
| 34 | `kkC_12_034` | Timbre1 · Switch11 Value | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Off \| On | combi | combi |
| 35 | `kkC_12_035` | Timbre1 · Switch12 Value | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | combi | combi |
| 36 | `kkC_12_036` | Timbre1 · Switch13 Value | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Off \| On | combi | combi |
| 37 | `kkC_12_037` | Timbre1 · Switch14 Value | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Off \| On | combi | combi |
| 38 | `kkC_12_038` | Timbre1 · Switch15 Value | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| On | combi | combi |
| 39 | `kkC_12_039` | Timbre1 · Switch16 Value | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Off \| On | combi | combi |
| 40 | `kkC_12_040` | Timbre1 · EXi1 Input Source Bus | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 41 | `kkC_12_041` | Timbre1 · EXi1 Input Source Channel | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |
| 42 | `kkC_12_042` | Timbre1 · EXi2 Input Source Bus | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_12_043` | Timbre1 · EXi2 Input Source Channel | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |

#### Tab 13 - Timbre 2 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_13_001` | Timbre2 · Program Number | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 2 | `kkC_13_002` | Timbre2 · Bank Number | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..30 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_13_003` | Timbre2 · MIDI Channel | `(303, 116, 146)` | combo `(303, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 4 | `kkC_13_004` | Timbre2 · Status | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| External2 | combi | combi |
| 5 | `kkC_13_005` | Timbre2 · Bank MSB | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_13_006` | Timbre2 · Bank LSB | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_13_007` | Timbre2 · Volume | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_13_008` | Timbre2 · Transpose | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -60..60 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_13_009` | Timbre2 · Detune | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_13_010` | Timbre2 · Delay Time | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..6001 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_13_011` | Timbre2 · Delay Tempo Base Note | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 12 | `kkC_13_012` | Timbre2 · Delay Mode | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | combi | combi |
| 13 | `kkC_13_013` | Timbre2 · Delay Tempo Times | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_13_014` | Timbre2 · Pan | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_13_015` | Timbre2 · Send1 | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_13_016` | Timbre2 · Send2 | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_13_017` | Timbre2 · Drum Kit Patch IFX1 | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_13_018` | Timbre2 · Drum Kit Patch IFX2 | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 19 | `kkC_13_019` | Timbre2 · Drum Kit Patch IFX3 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 20 | `kkC_13_020` | Timbre2 · Drum Kit Patch IFX4 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_13_021` | Timbre2 · Drum Kit Patch IFX5 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_13_022` | Timbre2 · Drum Kit Patch IFX6 | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 23 | `kkC_13_023` | Timbre2 · Drum Kit Patch IFX7 | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 24 | `kkC_13_024` | Timbre2 · Drum Kit Patch IFX8 | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 25 | `kkC_13_025` | Timbre2 · Drum Kit Patch IFX9 | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 26 | `kkC_13_026` | Timbre2 · Drum Kit Patch IFX10 | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 27 | `kkC_13_027` | Timbre2 · Drum Kit Patch IFX11 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_13_028` | Timbre2 · Drum Kit Patch IFX12 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_13_029` | Timbre2 · Bus Select | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 30 | `kkC_13_030` | Timbre2 · Fx Bus Select | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_13_031` | Timbre2 · Use Drum Kit Bus Setting | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_13_032` | Timbre2 · Rec Bus | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 33 | `kkC_13_033` | Timbre2 · Chord Source | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| Pad 8 | combi | combi |
| 34 | `kkC_13_034` | Timbre2 · Max # of Notes | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 16 | combi | combi |
| 35 | `kkC_13_035` | Timbre2 · Chord Mode | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Program \| 1 \| 2 \| Advanced | combi | combi |
| 36 | `kkC_13_036` | Timbre2 · (Filter) Program Change | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Disable \| Enable | combi | combi |
| 37 | `kkC_13_037` | Timbre2 · (Filter) After Touch | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Disable \| Enable | combi | combi |
| 38 | `kkC_13_038` | Timbre2 · (Filter) Damper | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Disable \| Enable | combi | combi |
| 39 | `kkC_13_039` | Timbre2 · (Filter) Portamento | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Disable \| Enable | combi | combi |
| 40 | `kkC_13_040` | Timbre2 · (Filter) JSX As Mod. | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Disable \| Enable | combi | combi |
| 41 | `kkC_13_041` | Timbre2 · (Filter) JS+Y | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Disable \| Enable | combi | combi |
| 42 | `kkC_13_042` | Timbre2 · (Filter) JS-Y | `(154, 312, 146)` | combo `(154, 325)` 146x20 | Disable \| Enable | combi | combi |
| 43 | `kkC_13_043` | Timbre2 · (Filter) Ribbon | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Disable \| Enable | combi | combi |
| 44 | `kkC_13_044` | Timbre2 · (Filter) Knob1 | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Disable \| Enable | combi | combi |
| 45 | `kkC_13_045` | Timbre2 · (Filter) Knob2 | `(601, 312, 146)` | combo `(601, 325)` 146x20 | Disable \| Enable | combi | combi |
| 46 | `kkC_13_046` | Timbre2 · (Filter) Knob3 | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Disable \| Enable | combi | combi |
| 47 | `kkC_13_047` | Timbre2 · (Filter) Knob4 | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Disable \| Enable | combi | combi |
| 48 | `kkC_13_048` | Timbre2 · (Filter) Knob5 | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Disable \| Enable | combi | combi |
| 49 | `kkC_13_049` | Timbre2 · (Filter) Knob6 | `(1197, 312, 146)` | combo `(1197, 325)` 146x20 | Disable \| Enable | combi | combi |
| 50 | `kkC_13_050` | Timbre2 · (Filter) Knob7 | `(1346, 312, 146)` | combo `(1346, 325)` 146x20 | Disable \| Enable | combi | combi |
| 51 | `kkC_13_051` | Timbre2 · (Filter) Knob8 | `(5, 361, 146)` | combo `(5, 374)` 146x20 | Disable \| Enable | combi | combi |
| 52 | `kkC_13_052` | Timbre2 · (Filter) Switch1 | `(154, 361, 146)` | combo `(154, 374)` 146x20 | Disable \| Enable | combi | combi |
| 53 | `kkC_13_053` | Timbre2 · (Filter) Switch2 | `(303, 361, 146)` | combo `(303, 374)` 146x20 | Disable \| Enable | combi | combi |
| 54 | `kkC_13_054` | Timbre2 · (Filter) Foot Switch | `(452, 361, 146)` | combo `(452, 374)` 146x20 | Disable \| Enable | combi | combi |
| 55 | `kkC_13_055` | Timbre2 · (Filter) Foot Pedal | `(601, 361, 146)` | combo `(601, 374)` 146x20 | Disable \| Enable | combi | combi |
| 56 | `kkC_13_056` | Timbre2 · (Filter) Other CC# | `(750, 361, 146)` | combo `(750, 374)` 146x20 | Disable \| Enable | combi | combi |
| 57 | `kkC_13_057` | Timbre2 · Use Program Scale | `(899, 361, 146)` | combo `(899, 374)` 146x20 | Off \| On | combi | combi |
| 58 | `kkC_13_058` | Timbre2 · Auto Load Program EQ | `(1048, 361, 146)` | combo `(1048, 374)` 146x20 | Off \| On | combi | combi |
| 59 | `kkC_13_059` | Timbre2 · Mute | `(1197, 361, 146)` | combo `(1197, 374)` 146x20 | Off \| On | combi | combi |
| 60 | `kkC_13_060` | Timbre2 · Osc Mode | `(1346, 361, 146)` | combo `(1346, 374)` 146x20 | Program \| 1 \| 2 \| Mono Legato | combi | combi |

#### Tab 14 - Timbre 2·2 (43 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_14_001` | Timbre2 · Osc Select | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Both \| 1 \| OSC2 | combi | combi |
| 2 | `kkC_14_002` | Timbre2 · Timbre Priority | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | combi | combi |
| 3 | `kkC_14_003` | Timbre2 · Osc On/Off By KARMA | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Normal \| 1 \| Osc Off by K | combi | combi |
| 4 | `kkC_14_004` | Timbre2 · (Filter) Waveform SysEx | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Disable \| Enable | combi | combi |
| 5 | `kkC_14_005` | Timbre2 · Key Window Top | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_14_006` | Timbre2 · Key Window Bottom | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_14_007` | Timbre2 · Vel.Window High | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_14_008` | Timbre2 · Vel.Window Low | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_14_009` | Timbre2 · Vel.Window High Slope | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 10 | `kkC_14_010` | Timbre2 · Vel.Window Low Slope | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 11 | `kkC_14_011` | Timbre2 · Quantize Trigger | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 12 | `kkC_14_012` | Timbre2 · Key Sync | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 13 | `kkC_14_013` | Timbre2 · (Track EQ) Trim | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_14_014` | Timbre2 · (Track EQ) Bypass | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_14_015` | Timbre2 · (Track EQ) Mid Frequency | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..165 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_14_016` | Timbre2 · (Track EQ) Low Gain | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 17 | `kkC_14_017` | Timbre2 · (Track EQ) Mid Gain | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 18 | `kkC_14_018` | Timbre2 · (Track EQ) High Gain | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 19 | `kkC_14_019` | Timbre2 · VJS Assign | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| -Y | combi | combi |
| 20 | `kkC_14_020` | Timbre2 · Volume Center | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..100 step 25.0 (0 dec) | combi | combi |
| 21 | `kkC_14_021` | Timbre2 · Program Vector Volume | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Off \| On | combi | combi |
| 22 | `kkC_14_022` | Timbre2 · Combi Vector CC | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| On | combi | combi |
| 23 | `kkC_14_023` | Timbre2 · Program Vector CC | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| On | combi | combi |
| 24 | `kkC_14_024` | Timbre2 · Switch1 Value | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | combi | combi |
| 25 | `kkC_14_025` | Timbre2 · Switch2 Value | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_14_026` | Timbre2 · Switch3 Value | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | combi | combi |
| 27 | `kkC_14_027` | Timbre2 · Switch4 Value | `(899, 214, 146)` | combo `(899, 227)` 146x20 | Off \| On | combi | combi |
| 28 | `kkC_14_028` | Timbre2 · Switch5 Value | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | Off \| On | combi | combi |
| 29 | `kkC_14_029` | Timbre2 · Switch6 Value | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| On | combi | combi |
| 30 | `kkC_14_030` | Timbre2 · Switch7 Value | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| On | combi | combi |
| 31 | `kkC_14_031` | Timbre2 · Switch8 Value | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_14_032` | Timbre2 · Switch9 Value | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | combi | combi |
| 33 | `kkC_14_033` | Timbre2 · Switch10 Value | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Off \| On | combi | combi |
| 34 | `kkC_14_034` | Timbre2 · Switch11 Value | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Off \| On | combi | combi |
| 35 | `kkC_14_035` | Timbre2 · Switch12 Value | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | combi | combi |
| 36 | `kkC_14_036` | Timbre2 · Switch13 Value | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Off \| On | combi | combi |
| 37 | `kkC_14_037` | Timbre2 · Switch14 Value | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Off \| On | combi | combi |
| 38 | `kkC_14_038` | Timbre2 · Switch15 Value | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| On | combi | combi |
| 39 | `kkC_14_039` | Timbre2 · Switch16 Value | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Off \| On | combi | combi |
| 40 | `kkC_14_040` | Timbre2 · EXi1 Input Source Bus | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 41 | `kkC_14_041` | Timbre2 · EXi1 Input Source Channel | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |
| 42 | `kkC_14_042` | Timbre2 · EXi2 Input Source Bus | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_14_043` | Timbre2 · EXi2 Input Source Channel | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |

#### Tab 15 - Timbre 3 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_15_001` | Timbre3 · Program Number | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 2 | `kkC_15_002` | Timbre3 · Bank Number | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..30 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_15_003` | Timbre3 · MIDI Channel | `(303, 116, 146)` | combo `(303, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 4 | `kkC_15_004` | Timbre3 · Status | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| External2 | combi | combi |
| 5 | `kkC_15_005` | Timbre3 · Bank MSB | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_15_006` | Timbre3 · Bank LSB | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_15_007` | Timbre3 · Volume | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_15_008` | Timbre3 · Transpose | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -60..60 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_15_009` | Timbre3 · Detune | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_15_010` | Timbre3 · Delay Time | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..6001 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_15_011` | Timbre3 · Delay Tempo Base Note | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 12 | `kkC_15_012` | Timbre3 · Delay Mode | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | combi | combi |
| 13 | `kkC_15_013` | Timbre3 · Delay Tempo Times | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_15_014` | Timbre3 · Pan | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_15_015` | Timbre3 · Send1 | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_15_016` | Timbre3 · Send2 | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_15_017` | Timbre3 · Drum Kit Patch IFX1 | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_15_018` | Timbre3 · Drum Kit Patch IFX2 | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 19 | `kkC_15_019` | Timbre3 · Drum Kit Patch IFX3 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 20 | `kkC_15_020` | Timbre3 · Drum Kit Patch IFX4 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_15_021` | Timbre3 · Drum Kit Patch IFX5 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_15_022` | Timbre3 · Drum Kit Patch IFX6 | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 23 | `kkC_15_023` | Timbre3 · Drum Kit Patch IFX7 | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 24 | `kkC_15_024` | Timbre3 · Drum Kit Patch IFX8 | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 25 | `kkC_15_025` | Timbre3 · Drum Kit Patch IFX9 | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 26 | `kkC_15_026` | Timbre3 · Drum Kit Patch IFX10 | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 27 | `kkC_15_027` | Timbre3 · Drum Kit Patch IFX11 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_15_028` | Timbre3 · Drum Kit Patch IFX12 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_15_029` | Timbre3 · Bus Select | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 30 | `kkC_15_030` | Timbre3 · Fx Bus Select | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_15_031` | Timbre3 · Use Drum Kit Bus Setting | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_15_032` | Timbre3 · Rec Bus | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 33 | `kkC_15_033` | Timbre3 · Chord Source | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| Pad 8 | combi | combi |
| 34 | `kkC_15_034` | Timbre3 · Max # of Notes | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 16 | combi | combi |
| 35 | `kkC_15_035` | Timbre3 · Chord Mode | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Program \| 1 \| 2 \| Advanced | combi | combi |
| 36 | `kkC_15_036` | Timbre3 · (Filter) Program Change | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Disable \| Enable | combi | combi |
| 37 | `kkC_15_037` | Timbre3 · (Filter) After Touch | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Disable \| Enable | combi | combi |
| 38 | `kkC_15_038` | Timbre3 · (Filter) Damper | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Disable \| Enable | combi | combi |
| 39 | `kkC_15_039` | Timbre3 · (Filter) Portamento | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Disable \| Enable | combi | combi |
| 40 | `kkC_15_040` | Timbre3 · (Filter) JSX As Mod. | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Disable \| Enable | combi | combi |
| 41 | `kkC_15_041` | Timbre3 · (Filter) JS+Y | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Disable \| Enable | combi | combi |
| 42 | `kkC_15_042` | Timbre3 · (Filter) JS-Y | `(154, 312, 146)` | combo `(154, 325)` 146x20 | Disable \| Enable | combi | combi |
| 43 | `kkC_15_043` | Timbre3 · (Filter) Ribbon | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Disable \| Enable | combi | combi |
| 44 | `kkC_15_044` | Timbre3 · (Filter) Knob1 | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Disable \| Enable | combi | combi |
| 45 | `kkC_15_045` | Timbre3 · (Filter) Knob2 | `(601, 312, 146)` | combo `(601, 325)` 146x20 | Disable \| Enable | combi | combi |
| 46 | `kkC_15_046` | Timbre3 · (Filter) Knob3 | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Disable \| Enable | combi | combi |
| 47 | `kkC_15_047` | Timbre3 · (Filter) Knob4 | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Disable \| Enable | combi | combi |
| 48 | `kkC_15_048` | Timbre3 · (Filter) Knob5 | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Disable \| Enable | combi | combi |
| 49 | `kkC_15_049` | Timbre3 · (Filter) Knob6 | `(1197, 312, 146)` | combo `(1197, 325)` 146x20 | Disable \| Enable | combi | combi |
| 50 | `kkC_15_050` | Timbre3 · (Filter) Knob7 | `(1346, 312, 146)` | combo `(1346, 325)` 146x20 | Disable \| Enable | combi | combi |
| 51 | `kkC_15_051` | Timbre3 · (Filter) Knob8 | `(5, 361, 146)` | combo `(5, 374)` 146x20 | Disable \| Enable | combi | combi |
| 52 | `kkC_15_052` | Timbre3 · (Filter) Switch1 | `(154, 361, 146)` | combo `(154, 374)` 146x20 | Disable \| Enable | combi | combi |
| 53 | `kkC_15_053` | Timbre3 · (Filter) Switch2 | `(303, 361, 146)` | combo `(303, 374)` 146x20 | Disable \| Enable | combi | combi |
| 54 | `kkC_15_054` | Timbre3 · (Filter) Foot Switch | `(452, 361, 146)` | combo `(452, 374)` 146x20 | Disable \| Enable | combi | combi |
| 55 | `kkC_15_055` | Timbre3 · (Filter) Foot Pedal | `(601, 361, 146)` | combo `(601, 374)` 146x20 | Disable \| Enable | combi | combi |
| 56 | `kkC_15_056` | Timbre3 · (Filter) Other CC# | `(750, 361, 146)` | combo `(750, 374)` 146x20 | Disable \| Enable | combi | combi |
| 57 | `kkC_15_057` | Timbre3 · Use Program Scale | `(899, 361, 146)` | combo `(899, 374)` 146x20 | Off \| On | combi | combi |
| 58 | `kkC_15_058` | Timbre3 · Auto Load Program EQ | `(1048, 361, 146)` | combo `(1048, 374)` 146x20 | Off \| On | combi | combi |
| 59 | `kkC_15_059` | Timbre3 · Mute | `(1197, 361, 146)` | combo `(1197, 374)` 146x20 | Off \| On | combi | combi |
| 60 | `kkC_15_060` | Timbre3 · Osc Mode | `(1346, 361, 146)` | combo `(1346, 374)` 146x20 | Program \| 1 \| 2 \| Mono Legato | combi | combi |

#### Tab 16 - Timbre 3·2 (43 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_16_001` | Timbre3 · Osc Select | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Both \| 1 \| OSC2 | combi | combi |
| 2 | `kkC_16_002` | Timbre3 · Timbre Priority | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | combi | combi |
| 3 | `kkC_16_003` | Timbre3 · Osc On/Off By KARMA | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Normal \| 1 \| Osc Off by K | combi | combi |
| 4 | `kkC_16_004` | Timbre3 · (Filter) Waveform SysEx | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Disable \| Enable | combi | combi |
| 5 | `kkC_16_005` | Timbre3 · Key Window Top | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_16_006` | Timbre3 · Key Window Bottom | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_16_007` | Timbre3 · Vel.Window High | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_16_008` | Timbre3 · Vel.Window Low | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_16_009` | Timbre3 · Vel.Window High Slope | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 10 | `kkC_16_010` | Timbre3 · Vel.Window Low Slope | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 11 | `kkC_16_011` | Timbre3 · Quantize Trigger | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 12 | `kkC_16_012` | Timbre3 · Key Sync | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 13 | `kkC_16_013` | Timbre3 · (Track EQ) Trim | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_16_014` | Timbre3 · (Track EQ) Bypass | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_16_015` | Timbre3 · (Track EQ) Mid Frequency | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..165 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_16_016` | Timbre3 · (Track EQ) Low Gain | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 17 | `kkC_16_017` | Timbre3 · (Track EQ) Mid Gain | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 18 | `kkC_16_018` | Timbre3 · (Track EQ) High Gain | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 19 | `kkC_16_019` | Timbre3 · VJS Assign | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| -Y | combi | combi |
| 20 | `kkC_16_020` | Timbre3 · Volume Center | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..100 step 25.0 (0 dec) | combi | combi |
| 21 | `kkC_16_021` | Timbre3 · Program Vector Volume | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Off \| On | combi | combi |
| 22 | `kkC_16_022` | Timbre3 · Combi Vector CC | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| On | combi | combi |
| 23 | `kkC_16_023` | Timbre3 · Program Vector CC | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| On | combi | combi |
| 24 | `kkC_16_024` | Timbre3 · Switch1 Value | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | combi | combi |
| 25 | `kkC_16_025` | Timbre3 · Switch2 Value | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_16_026` | Timbre3 · Switch3 Value | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | combi | combi |
| 27 | `kkC_16_027` | Timbre3 · Switch4 Value | `(899, 214, 146)` | combo `(899, 227)` 146x20 | Off \| On | combi | combi |
| 28 | `kkC_16_028` | Timbre3 · Switch5 Value | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | Off \| On | combi | combi |
| 29 | `kkC_16_029` | Timbre3 · Switch6 Value | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| On | combi | combi |
| 30 | `kkC_16_030` | Timbre3 · Switch7 Value | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| On | combi | combi |
| 31 | `kkC_16_031` | Timbre3 · Switch8 Value | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_16_032` | Timbre3 · Switch9 Value | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | combi | combi |
| 33 | `kkC_16_033` | Timbre3 · Switch10 Value | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Off \| On | combi | combi |
| 34 | `kkC_16_034` | Timbre3 · Switch11 Value | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Off \| On | combi | combi |
| 35 | `kkC_16_035` | Timbre3 · Switch12 Value | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | combi | combi |
| 36 | `kkC_16_036` | Timbre3 · Switch13 Value | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Off \| On | combi | combi |
| 37 | `kkC_16_037` | Timbre3 · Switch14 Value | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Off \| On | combi | combi |
| 38 | `kkC_16_038` | Timbre3 · Switch15 Value | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| On | combi | combi |
| 39 | `kkC_16_039` | Timbre3 · Switch16 Value | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Off \| On | combi | combi |
| 40 | `kkC_16_040` | Timbre3 · EXi1 Input Source Bus | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 41 | `kkC_16_041` | Timbre3 · EXi1 Input Source Channel | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |
| 42 | `kkC_16_042` | Timbre3 · EXi2 Input Source Bus | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_16_043` | Timbre3 · EXi2 Input Source Channel | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |

#### Tab 17 - Timbre 4 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_17_001` | Timbre4 · Program Number | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 2 | `kkC_17_002` | Timbre4 · Bank Number | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..30 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_17_003` | Timbre4 · MIDI Channel | `(303, 116, 146)` | combo `(303, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 4 | `kkC_17_004` | Timbre4 · Status | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| External2 | combi | combi |
| 5 | `kkC_17_005` | Timbre4 · Bank MSB | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_17_006` | Timbre4 · Bank LSB | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_17_007` | Timbre4 · Volume | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_17_008` | Timbre4 · Transpose | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -60..60 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_17_009` | Timbre4 · Detune | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_17_010` | Timbre4 · Delay Time | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..6001 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_17_011` | Timbre4 · Delay Tempo Base Note | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 12 | `kkC_17_012` | Timbre4 · Delay Mode | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | combi | combi |
| 13 | `kkC_17_013` | Timbre4 · Delay Tempo Times | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_17_014` | Timbre4 · Pan | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_17_015` | Timbre4 · Send1 | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_17_016` | Timbre4 · Send2 | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_17_017` | Timbre4 · Drum Kit Patch IFX1 | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_17_018` | Timbre4 · Drum Kit Patch IFX2 | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 19 | `kkC_17_019` | Timbre4 · Drum Kit Patch IFX3 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 20 | `kkC_17_020` | Timbre4 · Drum Kit Patch IFX4 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_17_021` | Timbre4 · Drum Kit Patch IFX5 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_17_022` | Timbre4 · Drum Kit Patch IFX6 | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 23 | `kkC_17_023` | Timbre4 · Drum Kit Patch IFX7 | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 24 | `kkC_17_024` | Timbre4 · Drum Kit Patch IFX8 | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 25 | `kkC_17_025` | Timbre4 · Drum Kit Patch IFX9 | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 26 | `kkC_17_026` | Timbre4 · Drum Kit Patch IFX10 | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 27 | `kkC_17_027` | Timbre4 · Drum Kit Patch IFX11 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_17_028` | Timbre4 · Drum Kit Patch IFX12 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_17_029` | Timbre4 · Bus Select | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 30 | `kkC_17_030` | Timbre4 · Fx Bus Select | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_17_031` | Timbre4 · Use Drum Kit Bus Setting | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_17_032` | Timbre4 · Rec Bus | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 33 | `kkC_17_033` | Timbre4 · Chord Source | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| Pad 8 | combi | combi |
| 34 | `kkC_17_034` | Timbre4 · Max # of Notes | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 16 | combi | combi |
| 35 | `kkC_17_035` | Timbre4 · Chord Mode | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Program \| 1 \| 2 \| Advanced | combi | combi |
| 36 | `kkC_17_036` | Timbre4 · (Filter) Program Change | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Disable \| Enable | combi | combi |
| 37 | `kkC_17_037` | Timbre4 · (Filter) After Touch | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Disable \| Enable | combi | combi |
| 38 | `kkC_17_038` | Timbre4 · (Filter) Damper | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Disable \| Enable | combi | combi |
| 39 | `kkC_17_039` | Timbre4 · (Filter) Portamento | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Disable \| Enable | combi | combi |
| 40 | `kkC_17_040` | Timbre4 · (Filter) JSX As Mod. | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Disable \| Enable | combi | combi |
| 41 | `kkC_17_041` | Timbre4 · (Filter) JS+Y | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Disable \| Enable | combi | combi |
| 42 | `kkC_17_042` | Timbre4 · (Filter) JS-Y | `(154, 312, 146)` | combo `(154, 325)` 146x20 | Disable \| Enable | combi | combi |
| 43 | `kkC_17_043` | Timbre4 · (Filter) Ribbon | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Disable \| Enable | combi | combi |
| 44 | `kkC_17_044` | Timbre4 · (Filter) Knob1 | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Disable \| Enable | combi | combi |
| 45 | `kkC_17_045` | Timbre4 · (Filter) Knob2 | `(601, 312, 146)` | combo `(601, 325)` 146x20 | Disable \| Enable | combi | combi |
| 46 | `kkC_17_046` | Timbre4 · (Filter) Knob3 | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Disable \| Enable | combi | combi |
| 47 | `kkC_17_047` | Timbre4 · (Filter) Knob4 | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Disable \| Enable | combi | combi |
| 48 | `kkC_17_048` | Timbre4 · (Filter) Knob5 | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Disable \| Enable | combi | combi |
| 49 | `kkC_17_049` | Timbre4 · (Filter) Knob6 | `(1197, 312, 146)` | combo `(1197, 325)` 146x20 | Disable \| Enable | combi | combi |
| 50 | `kkC_17_050` | Timbre4 · (Filter) Knob7 | `(1346, 312, 146)` | combo `(1346, 325)` 146x20 | Disable \| Enable | combi | combi |
| 51 | `kkC_17_051` | Timbre4 · (Filter) Knob8 | `(5, 361, 146)` | combo `(5, 374)` 146x20 | Disable \| Enable | combi | combi |
| 52 | `kkC_17_052` | Timbre4 · (Filter) Switch1 | `(154, 361, 146)` | combo `(154, 374)` 146x20 | Disable \| Enable | combi | combi |
| 53 | `kkC_17_053` | Timbre4 · (Filter) Switch2 | `(303, 361, 146)` | combo `(303, 374)` 146x20 | Disable \| Enable | combi | combi |
| 54 | `kkC_17_054` | Timbre4 · (Filter) Foot Switch | `(452, 361, 146)` | combo `(452, 374)` 146x20 | Disable \| Enable | combi | combi |
| 55 | `kkC_17_055` | Timbre4 · (Filter) Foot Pedal | `(601, 361, 146)` | combo `(601, 374)` 146x20 | Disable \| Enable | combi | combi |
| 56 | `kkC_17_056` | Timbre4 · (Filter) Other CC# | `(750, 361, 146)` | combo `(750, 374)` 146x20 | Disable \| Enable | combi | combi |
| 57 | `kkC_17_057` | Timbre4 · Use Program Scale | `(899, 361, 146)` | combo `(899, 374)` 146x20 | Off \| On | combi | combi |
| 58 | `kkC_17_058` | Timbre4 · Auto Load Program EQ | `(1048, 361, 146)` | combo `(1048, 374)` 146x20 | Off \| On | combi | combi |
| 59 | `kkC_17_059` | Timbre4 · Mute | `(1197, 361, 146)` | combo `(1197, 374)` 146x20 | Off \| On | combi | combi |
| 60 | `kkC_17_060` | Timbre4 · Osc Mode | `(1346, 361, 146)` | combo `(1346, 374)` 146x20 | Program \| 1 \| 2 \| Mono Legato | combi | combi |

#### Tab 18 - Timbre 4·2 (43 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_18_001` | Timbre4 · Osc Select | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Both \| 1 \| OSC2 | combi | combi |
| 2 | `kkC_18_002` | Timbre4 · Timbre Priority | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | combi | combi |
| 3 | `kkC_18_003` | Timbre4 · Osc On/Off By KARMA | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Normal \| 1 \| Osc Off by K | combi | combi |
| 4 | `kkC_18_004` | Timbre4 · (Filter) Waveform SysEx | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Disable \| Enable | combi | combi |
| 5 | `kkC_18_005` | Timbre4 · Key Window Top | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_18_006` | Timbre4 · Key Window Bottom | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_18_007` | Timbre4 · Vel.Window High | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_18_008` | Timbre4 · Vel.Window Low | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_18_009` | Timbre4 · Vel.Window High Slope | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 10 | `kkC_18_010` | Timbre4 · Vel.Window Low Slope | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 11 | `kkC_18_011` | Timbre4 · Quantize Trigger | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 12 | `kkC_18_012` | Timbre4 · Key Sync | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 13 | `kkC_18_013` | Timbre4 · (Track EQ) Trim | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_18_014` | Timbre4 · (Track EQ) Bypass | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_18_015` | Timbre4 · (Track EQ) Mid Frequency | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..165 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_18_016` | Timbre4 · (Track EQ) Low Gain | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 17 | `kkC_18_017` | Timbre4 · (Track EQ) Mid Gain | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 18 | `kkC_18_018` | Timbre4 · (Track EQ) High Gain | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 19 | `kkC_18_019` | Timbre4 · VJS Assign | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| -Y | combi | combi |
| 20 | `kkC_18_020` | Timbre4 · Volume Center | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..100 step 25.0 (0 dec) | combi | combi |
| 21 | `kkC_18_021` | Timbre4 · Program Vector Volume | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Off \| On | combi | combi |
| 22 | `kkC_18_022` | Timbre4 · Combi Vector CC | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| On | combi | combi |
| 23 | `kkC_18_023` | Timbre4 · Program Vector CC | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| On | combi | combi |
| 24 | `kkC_18_024` | Timbre4 · Switch1 Value | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | combi | combi |
| 25 | `kkC_18_025` | Timbre4 · Switch2 Value | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_18_026` | Timbre4 · Switch3 Value | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | combi | combi |
| 27 | `kkC_18_027` | Timbre4 · Switch4 Value | `(899, 214, 146)` | combo `(899, 227)` 146x20 | Off \| On | combi | combi |
| 28 | `kkC_18_028` | Timbre4 · Switch5 Value | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | Off \| On | combi | combi |
| 29 | `kkC_18_029` | Timbre4 · Switch6 Value | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| On | combi | combi |
| 30 | `kkC_18_030` | Timbre4 · Switch7 Value | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| On | combi | combi |
| 31 | `kkC_18_031` | Timbre4 · Switch8 Value | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_18_032` | Timbre4 · Switch9 Value | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | combi | combi |
| 33 | `kkC_18_033` | Timbre4 · Switch10 Value | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Off \| On | combi | combi |
| 34 | `kkC_18_034` | Timbre4 · Switch11 Value | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Off \| On | combi | combi |
| 35 | `kkC_18_035` | Timbre4 · Switch12 Value | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | combi | combi |
| 36 | `kkC_18_036` | Timbre4 · Switch13 Value | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Off \| On | combi | combi |
| 37 | `kkC_18_037` | Timbre4 · Switch14 Value | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Off \| On | combi | combi |
| 38 | `kkC_18_038` | Timbre4 · Switch15 Value | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| On | combi | combi |
| 39 | `kkC_18_039` | Timbre4 · Switch16 Value | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Off \| On | combi | combi |
| 40 | `kkC_18_040` | Timbre4 · EXi1 Input Source Bus | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 41 | `kkC_18_041` | Timbre4 · EXi1 Input Source Channel | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |
| 42 | `kkC_18_042` | Timbre4 · EXi2 Input Source Bus | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_18_043` | Timbre4 · EXi2 Input Source Channel | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |

#### Tab 19 - Timbre 5 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_19_001` | Timbre5 · Program Number | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 2 | `kkC_19_002` | Timbre5 · Bank Number | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..30 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_19_003` | Timbre5 · MIDI Channel | `(303, 116, 146)` | combo `(303, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 4 | `kkC_19_004` | Timbre5 · Status | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| External2 | combi | combi |
| 5 | `kkC_19_005` | Timbre5 · Bank MSB | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_19_006` | Timbre5 · Bank LSB | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_19_007` | Timbre5 · Volume | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_19_008` | Timbre5 · Transpose | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -60..60 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_19_009` | Timbre5 · Detune | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_19_010` | Timbre5 · Delay Time | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..6001 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_19_011` | Timbre5 · Delay Tempo Base Note | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 12 | `kkC_19_012` | Timbre5 · Delay Mode | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | combi | combi |
| 13 | `kkC_19_013` | Timbre5 · Delay Tempo Times | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_19_014` | Timbre5 · Pan | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_19_015` | Timbre5 · Send1 | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_19_016` | Timbre5 · Send2 | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_19_017` | Timbre5 · Drum Kit Patch IFX1 | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_19_018` | Timbre5 · Drum Kit Patch IFX2 | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 19 | `kkC_19_019` | Timbre5 · Drum Kit Patch IFX3 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 20 | `kkC_19_020` | Timbre5 · Drum Kit Patch IFX4 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_19_021` | Timbre5 · Drum Kit Patch IFX5 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_19_022` | Timbre5 · Drum Kit Patch IFX6 | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 23 | `kkC_19_023` | Timbre5 · Drum Kit Patch IFX7 | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 24 | `kkC_19_024` | Timbre5 · Drum Kit Patch IFX8 | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 25 | `kkC_19_025` | Timbre5 · Drum Kit Patch IFX9 | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 26 | `kkC_19_026` | Timbre5 · Drum Kit Patch IFX10 | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 27 | `kkC_19_027` | Timbre5 · Drum Kit Patch IFX11 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_19_028` | Timbre5 · Drum Kit Patch IFX12 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_19_029` | Timbre5 · Bus Select | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 30 | `kkC_19_030` | Timbre5 · Fx Bus Select | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_19_031` | Timbre5 · Use Drum Kit Bus Setting | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_19_032` | Timbre5 · Rec Bus | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 33 | `kkC_19_033` | Timbre5 · Chord Source | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| Pad 8 | combi | combi |
| 34 | `kkC_19_034` | Timbre5 · Max # of Notes | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 16 | combi | combi |
| 35 | `kkC_19_035` | Timbre5 · Chord Mode | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Program \| 1 \| 2 \| Advanced | combi | combi |
| 36 | `kkC_19_036` | Timbre5 · (Filter) Program Change | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Disable \| Enable | combi | combi |
| 37 | `kkC_19_037` | Timbre5 · (Filter) After Touch | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Disable \| Enable | combi | combi |
| 38 | `kkC_19_038` | Timbre5 · (Filter) Damper | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Disable \| Enable | combi | combi |
| 39 | `kkC_19_039` | Timbre5 · (Filter) Portamento | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Disable \| Enable | combi | combi |
| 40 | `kkC_19_040` | Timbre5 · (Filter) JSX As Mod. | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Disable \| Enable | combi | combi |
| 41 | `kkC_19_041` | Timbre5 · (Filter) JS+Y | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Disable \| Enable | combi | combi |
| 42 | `kkC_19_042` | Timbre5 · (Filter) JS-Y | `(154, 312, 146)` | combo `(154, 325)` 146x20 | Disable \| Enable | combi | combi |
| 43 | `kkC_19_043` | Timbre5 · (Filter) Ribbon | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Disable \| Enable | combi | combi |
| 44 | `kkC_19_044` | Timbre5 · (Filter) Knob1 | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Disable \| Enable | combi | combi |
| 45 | `kkC_19_045` | Timbre5 · (Filter) Knob2 | `(601, 312, 146)` | combo `(601, 325)` 146x20 | Disable \| Enable | combi | combi |
| 46 | `kkC_19_046` | Timbre5 · (Filter) Knob3 | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Disable \| Enable | combi | combi |
| 47 | `kkC_19_047` | Timbre5 · (Filter) Knob4 | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Disable \| Enable | combi | combi |
| 48 | `kkC_19_048` | Timbre5 · (Filter) Knob5 | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Disable \| Enable | combi | combi |
| 49 | `kkC_19_049` | Timbre5 · (Filter) Knob6 | `(1197, 312, 146)` | combo `(1197, 325)` 146x20 | Disable \| Enable | combi | combi |
| 50 | `kkC_19_050` | Timbre5 · (Filter) Knob7 | `(1346, 312, 146)` | combo `(1346, 325)` 146x20 | Disable \| Enable | combi | combi |
| 51 | `kkC_19_051` | Timbre5 · (Filter) Knob8 | `(5, 361, 146)` | combo `(5, 374)` 146x20 | Disable \| Enable | combi | combi |
| 52 | `kkC_19_052` | Timbre5 · (Filter) Switch1 | `(154, 361, 146)` | combo `(154, 374)` 146x20 | Disable \| Enable | combi | combi |
| 53 | `kkC_19_053` | Timbre5 · (Filter) Switch2 | `(303, 361, 146)` | combo `(303, 374)` 146x20 | Disable \| Enable | combi | combi |
| 54 | `kkC_19_054` | Timbre5 · (Filter) Foot Switch | `(452, 361, 146)` | combo `(452, 374)` 146x20 | Disable \| Enable | combi | combi |
| 55 | `kkC_19_055` | Timbre5 · (Filter) Foot Pedal | `(601, 361, 146)` | combo `(601, 374)` 146x20 | Disable \| Enable | combi | combi |
| 56 | `kkC_19_056` | Timbre5 · (Filter) Other CC# | `(750, 361, 146)` | combo `(750, 374)` 146x20 | Disable \| Enable | combi | combi |
| 57 | `kkC_19_057` | Timbre5 · Use Program Scale | `(899, 361, 146)` | combo `(899, 374)` 146x20 | Off \| On | combi | combi |
| 58 | `kkC_19_058` | Timbre5 · Auto Load Program EQ | `(1048, 361, 146)` | combo `(1048, 374)` 146x20 | Off \| On | combi | combi |
| 59 | `kkC_19_059` | Timbre5 · Mute | `(1197, 361, 146)` | combo `(1197, 374)` 146x20 | Off \| On | combi | combi |
| 60 | `kkC_19_060` | Timbre5 · Osc Mode | `(1346, 361, 146)` | combo `(1346, 374)` 146x20 | Program \| 1 \| 2 \| Mono Legato | combi | combi |

#### Tab 20 - Timbre 5·2 (43 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_20_001` | Timbre5 · Osc Select | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Both \| 1 \| OSC2 | combi | combi |
| 2 | `kkC_20_002` | Timbre5 · Timbre Priority | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | combi | combi |
| 3 | `kkC_20_003` | Timbre5 · Osc On/Off By KARMA | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Normal \| 1 \| Osc Off by K | combi | combi |
| 4 | `kkC_20_004` | Timbre5 · (Filter) Waveform SysEx | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Disable \| Enable | combi | combi |
| 5 | `kkC_20_005` | Timbre5 · Key Window Top | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_20_006` | Timbre5 · Key Window Bottom | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_20_007` | Timbre5 · Vel.Window High | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_20_008` | Timbre5 · Vel.Window Low | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_20_009` | Timbre5 · Vel.Window High Slope | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 10 | `kkC_20_010` | Timbre5 · Vel.Window Low Slope | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 11 | `kkC_20_011` | Timbre5 · Quantize Trigger | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 12 | `kkC_20_012` | Timbre5 · Key Sync | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 13 | `kkC_20_013` | Timbre5 · (Track EQ) Trim | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_20_014` | Timbre5 · (Track EQ) Bypass | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_20_015` | Timbre5 · (Track EQ) Mid Frequency | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..165 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_20_016` | Timbre5 · (Track EQ) Low Gain | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 17 | `kkC_20_017` | Timbre5 · (Track EQ) Mid Gain | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 18 | `kkC_20_018` | Timbre5 · (Track EQ) High Gain | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 19 | `kkC_20_019` | Timbre5 · VJS Assign | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| -Y | combi | combi |
| 20 | `kkC_20_020` | Timbre5 · Volume Center | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..100 step 25.0 (0 dec) | combi | combi |
| 21 | `kkC_20_021` | Timbre5 · Program Vector Volume | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Off \| On | combi | combi |
| 22 | `kkC_20_022` | Timbre5 · Combi Vector CC | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| On | combi | combi |
| 23 | `kkC_20_023` | Timbre5 · Program Vector CC | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| On | combi | combi |
| 24 | `kkC_20_024` | Timbre5 · Switch1 Value | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | combi | combi |
| 25 | `kkC_20_025` | Timbre5 · Switch2 Value | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_20_026` | Timbre5 · Switch3 Value | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | combi | combi |
| 27 | `kkC_20_027` | Timbre5 · Switch4 Value | `(899, 214, 146)` | combo `(899, 227)` 146x20 | Off \| On | combi | combi |
| 28 | `kkC_20_028` | Timbre5 · Switch5 Value | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | Off \| On | combi | combi |
| 29 | `kkC_20_029` | Timbre5 · Switch6 Value | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| On | combi | combi |
| 30 | `kkC_20_030` | Timbre5 · Switch7 Value | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| On | combi | combi |
| 31 | `kkC_20_031` | Timbre5 · Switch8 Value | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_20_032` | Timbre5 · Switch9 Value | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | combi | combi |
| 33 | `kkC_20_033` | Timbre5 · Switch10 Value | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Off \| On | combi | combi |
| 34 | `kkC_20_034` | Timbre5 · Switch11 Value | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Off \| On | combi | combi |
| 35 | `kkC_20_035` | Timbre5 · Switch12 Value | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | combi | combi |
| 36 | `kkC_20_036` | Timbre5 · Switch13 Value | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Off \| On | combi | combi |
| 37 | `kkC_20_037` | Timbre5 · Switch14 Value | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Off \| On | combi | combi |
| 38 | `kkC_20_038` | Timbre5 · Switch15 Value | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| On | combi | combi |
| 39 | `kkC_20_039` | Timbre5 · Switch16 Value | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Off \| On | combi | combi |
| 40 | `kkC_20_040` | Timbre5 · EXi1 Input Source Bus | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 41 | `kkC_20_041` | Timbre5 · EXi1 Input Source Channel | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |
| 42 | `kkC_20_042` | Timbre5 · EXi2 Input Source Bus | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_20_043` | Timbre5 · EXi2 Input Source Channel | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |

#### Tab 21 - Timbre 6 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_21_001` | Timbre6 · Program Number | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 2 | `kkC_21_002` | Timbre6 · Bank Number | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..30 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_21_003` | Timbre6 · MIDI Channel | `(303, 116, 146)` | combo `(303, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 4 | `kkC_21_004` | Timbre6 · Status | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| External2 | combi | combi |
| 5 | `kkC_21_005` | Timbre6 · Bank MSB | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_21_006` | Timbre6 · Bank LSB | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_21_007` | Timbre6 · Volume | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_21_008` | Timbre6 · Transpose | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -60..60 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_21_009` | Timbre6 · Detune | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_21_010` | Timbre6 · Delay Time | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..6001 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_21_011` | Timbre6 · Delay Tempo Base Note | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 12 | `kkC_21_012` | Timbre6 · Delay Mode | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | combi | combi |
| 13 | `kkC_21_013` | Timbre6 · Delay Tempo Times | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_21_014` | Timbre6 · Pan | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_21_015` | Timbre6 · Send1 | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_21_016` | Timbre6 · Send2 | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_21_017` | Timbre6 · Drum Kit Patch IFX1 | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_21_018` | Timbre6 · Drum Kit Patch IFX2 | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 19 | `kkC_21_019` | Timbre6 · Drum Kit Patch IFX3 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 20 | `kkC_21_020` | Timbre6 · Drum Kit Patch IFX4 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_21_021` | Timbre6 · Drum Kit Patch IFX5 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_21_022` | Timbre6 · Drum Kit Patch IFX6 | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 23 | `kkC_21_023` | Timbre6 · Drum Kit Patch IFX7 | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 24 | `kkC_21_024` | Timbre6 · Drum Kit Patch IFX8 | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 25 | `kkC_21_025` | Timbre6 · Drum Kit Patch IFX9 | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 26 | `kkC_21_026` | Timbre6 · Drum Kit Patch IFX10 | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 27 | `kkC_21_027` | Timbre6 · Drum Kit Patch IFX11 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_21_028` | Timbre6 · Drum Kit Patch IFX12 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_21_029` | Timbre6 · Bus Select | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 30 | `kkC_21_030` | Timbre6 · Fx Bus Select | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_21_031` | Timbre6 · Use Drum Kit Bus Setting | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_21_032` | Timbre6 · Rec Bus | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 33 | `kkC_21_033` | Timbre6 · Chord Source | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| Pad 8 | combi | combi |
| 34 | `kkC_21_034` | Timbre6 · Max # of Notes | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 16 | combi | combi |
| 35 | `kkC_21_035` | Timbre6 · Chord Mode | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Program \| 1 \| 2 \| Advanced | combi | combi |
| 36 | `kkC_21_036` | Timbre6 · (Filter) Program Change | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Disable \| Enable | combi | combi |
| 37 | `kkC_21_037` | Timbre6 · (Filter) After Touch | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Disable \| Enable | combi | combi |
| 38 | `kkC_21_038` | Timbre6 · (Filter) Damper | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Disable \| Enable | combi | combi |
| 39 | `kkC_21_039` | Timbre6 · (Filter) Portamento | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Disable \| Enable | combi | combi |
| 40 | `kkC_21_040` | Timbre6 · (Filter) JSX As Mod. | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Disable \| Enable | combi | combi |
| 41 | `kkC_21_041` | Timbre6 · (Filter) JS+Y | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Disable \| Enable | combi | combi |
| 42 | `kkC_21_042` | Timbre6 · (Filter) JS-Y | `(154, 312, 146)` | combo `(154, 325)` 146x20 | Disable \| Enable | combi | combi |
| 43 | `kkC_21_043` | Timbre6 · (Filter) Ribbon | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Disable \| Enable | combi | combi |
| 44 | `kkC_21_044` | Timbre6 · (Filter) Knob1 | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Disable \| Enable | combi | combi |
| 45 | `kkC_21_045` | Timbre6 · (Filter) Knob2 | `(601, 312, 146)` | combo `(601, 325)` 146x20 | Disable \| Enable | combi | combi |
| 46 | `kkC_21_046` | Timbre6 · (Filter) Knob3 | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Disable \| Enable | combi | combi |
| 47 | `kkC_21_047` | Timbre6 · (Filter) Knob4 | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Disable \| Enable | combi | combi |
| 48 | `kkC_21_048` | Timbre6 · (Filter) Knob5 | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Disable \| Enable | combi | combi |
| 49 | `kkC_21_049` | Timbre6 · (Filter) Knob6 | `(1197, 312, 146)` | combo `(1197, 325)` 146x20 | Disable \| Enable | combi | combi |
| 50 | `kkC_21_050` | Timbre6 · (Filter) Knob7 | `(1346, 312, 146)` | combo `(1346, 325)` 146x20 | Disable \| Enable | combi | combi |
| 51 | `kkC_21_051` | Timbre6 · (Filter) Knob8 | `(5, 361, 146)` | combo `(5, 374)` 146x20 | Disable \| Enable | combi | combi |
| 52 | `kkC_21_052` | Timbre6 · (Filter) Switch1 | `(154, 361, 146)` | combo `(154, 374)` 146x20 | Disable \| Enable | combi | combi |
| 53 | `kkC_21_053` | Timbre6 · (Filter) Switch2 | `(303, 361, 146)` | combo `(303, 374)` 146x20 | Disable \| Enable | combi | combi |
| 54 | `kkC_21_054` | Timbre6 · (Filter) Foot Switch | `(452, 361, 146)` | combo `(452, 374)` 146x20 | Disable \| Enable | combi | combi |
| 55 | `kkC_21_055` | Timbre6 · (Filter) Foot Pedal | `(601, 361, 146)` | combo `(601, 374)` 146x20 | Disable \| Enable | combi | combi |
| 56 | `kkC_21_056` | Timbre6 · (Filter) Other CC# | `(750, 361, 146)` | combo `(750, 374)` 146x20 | Disable \| Enable | combi | combi |
| 57 | `kkC_21_057` | Timbre6 · Use Program Scale | `(899, 361, 146)` | combo `(899, 374)` 146x20 | Off \| On | combi | combi |
| 58 | `kkC_21_058` | Timbre6 · Auto Load Program EQ | `(1048, 361, 146)` | combo `(1048, 374)` 146x20 | Off \| On | combi | combi |
| 59 | `kkC_21_059` | Timbre6 · Mute | `(1197, 361, 146)` | combo `(1197, 374)` 146x20 | Off \| On | combi | combi |
| 60 | `kkC_21_060` | Timbre6 · Osc Mode | `(1346, 361, 146)` | combo `(1346, 374)` 146x20 | Program \| 1 \| 2 \| Mono Legato | combi | combi |

#### Tab 22 - Timbre 6·2 (43 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_22_001` | Timbre6 · Osc Select | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Both \| 1 \| OSC2 | combi | combi |
| 2 | `kkC_22_002` | Timbre6 · Timbre Priority | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | combi | combi |
| 3 | `kkC_22_003` | Timbre6 · Osc On/Off By KARMA | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Normal \| 1 \| Osc Off by K | combi | combi |
| 4 | `kkC_22_004` | Timbre6 · (Filter) Waveform SysEx | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Disable \| Enable | combi | combi |
| 5 | `kkC_22_005` | Timbre6 · Key Window Top | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_22_006` | Timbre6 · Key Window Bottom | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_22_007` | Timbre6 · Vel.Window High | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_22_008` | Timbre6 · Vel.Window Low | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_22_009` | Timbre6 · Vel.Window High Slope | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 10 | `kkC_22_010` | Timbre6 · Vel.Window Low Slope | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 11 | `kkC_22_011` | Timbre6 · Quantize Trigger | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 12 | `kkC_22_012` | Timbre6 · Key Sync | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 13 | `kkC_22_013` | Timbre6 · (Track EQ) Trim | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_22_014` | Timbre6 · (Track EQ) Bypass | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_22_015` | Timbre6 · (Track EQ) Mid Frequency | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..165 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_22_016` | Timbre6 · (Track EQ) Low Gain | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 17 | `kkC_22_017` | Timbre6 · (Track EQ) Mid Gain | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 18 | `kkC_22_018` | Timbre6 · (Track EQ) High Gain | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 19 | `kkC_22_019` | Timbre6 · VJS Assign | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| -Y | combi | combi |
| 20 | `kkC_22_020` | Timbre6 · Volume Center | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..100 step 25.0 (0 dec) | combi | combi |
| 21 | `kkC_22_021` | Timbre6 · Program Vector Volume | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Off \| On | combi | combi |
| 22 | `kkC_22_022` | Timbre6 · Combi Vector CC | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| On | combi | combi |
| 23 | `kkC_22_023` | Timbre6 · Program Vector CC | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| On | combi | combi |
| 24 | `kkC_22_024` | Timbre6 · Switch1 Value | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | combi | combi |
| 25 | `kkC_22_025` | Timbre6 · Switch2 Value | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_22_026` | Timbre6 · Switch3 Value | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | combi | combi |
| 27 | `kkC_22_027` | Timbre6 · Switch4 Value | `(899, 214, 146)` | combo `(899, 227)` 146x20 | Off \| On | combi | combi |
| 28 | `kkC_22_028` | Timbre6 · Switch5 Value | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | Off \| On | combi | combi |
| 29 | `kkC_22_029` | Timbre6 · Switch6 Value | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| On | combi | combi |
| 30 | `kkC_22_030` | Timbre6 · Switch7 Value | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| On | combi | combi |
| 31 | `kkC_22_031` | Timbre6 · Switch8 Value | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_22_032` | Timbre6 · Switch9 Value | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | combi | combi |
| 33 | `kkC_22_033` | Timbre6 · Switch10 Value | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Off \| On | combi | combi |
| 34 | `kkC_22_034` | Timbre6 · Switch11 Value | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Off \| On | combi | combi |
| 35 | `kkC_22_035` | Timbre6 · Switch12 Value | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | combi | combi |
| 36 | `kkC_22_036` | Timbre6 · Switch13 Value | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Off \| On | combi | combi |
| 37 | `kkC_22_037` | Timbre6 · Switch14 Value | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Off \| On | combi | combi |
| 38 | `kkC_22_038` | Timbre6 · Switch15 Value | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| On | combi | combi |
| 39 | `kkC_22_039` | Timbre6 · Switch16 Value | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Off \| On | combi | combi |
| 40 | `kkC_22_040` | Timbre6 · EXi1 Input Source Bus | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 41 | `kkC_22_041` | Timbre6 · EXi1 Input Source Channel | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |
| 42 | `kkC_22_042` | Timbre6 · EXi2 Input Source Bus | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_22_043` | Timbre6 · EXi2 Input Source Channel | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |

#### Tab 23 - Timbre 7 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_23_001` | Timbre7 · Program Number | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 2 | `kkC_23_002` | Timbre7 · Bank Number | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..30 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_23_003` | Timbre7 · MIDI Channel | `(303, 116, 146)` | combo `(303, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 4 | `kkC_23_004` | Timbre7 · Status | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| External2 | combi | combi |
| 5 | `kkC_23_005` | Timbre7 · Bank MSB | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_23_006` | Timbre7 · Bank LSB | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_23_007` | Timbre7 · Volume | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_23_008` | Timbre7 · Transpose | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -60..60 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_23_009` | Timbre7 · Detune | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_23_010` | Timbre7 · Delay Time | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..6001 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_23_011` | Timbre7 · Delay Tempo Base Note | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 12 | `kkC_23_012` | Timbre7 · Delay Mode | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | combi | combi |
| 13 | `kkC_23_013` | Timbre7 · Delay Tempo Times | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_23_014` | Timbre7 · Pan | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_23_015` | Timbre7 · Send1 | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_23_016` | Timbre7 · Send2 | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_23_017` | Timbre7 · Drum Kit Patch IFX1 | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_23_018` | Timbre7 · Drum Kit Patch IFX2 | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 19 | `kkC_23_019` | Timbre7 · Drum Kit Patch IFX3 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 20 | `kkC_23_020` | Timbre7 · Drum Kit Patch IFX4 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_23_021` | Timbre7 · Drum Kit Patch IFX5 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_23_022` | Timbre7 · Drum Kit Patch IFX6 | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 23 | `kkC_23_023` | Timbre7 · Drum Kit Patch IFX7 | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 24 | `kkC_23_024` | Timbre7 · Drum Kit Patch IFX8 | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 25 | `kkC_23_025` | Timbre7 · Drum Kit Patch IFX9 | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 26 | `kkC_23_026` | Timbre7 · Drum Kit Patch IFX10 | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 27 | `kkC_23_027` | Timbre7 · Drum Kit Patch IFX11 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_23_028` | Timbre7 · Drum Kit Patch IFX12 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_23_029` | Timbre7 · Bus Select | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 30 | `kkC_23_030` | Timbre7 · Fx Bus Select | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_23_031` | Timbre7 · Use Drum Kit Bus Setting | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_23_032` | Timbre7 · Rec Bus | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 33 | `kkC_23_033` | Timbre7 · Chord Source | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| Pad 8 | combi | combi |
| 34 | `kkC_23_034` | Timbre7 · Max # of Notes | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 16 | combi | combi |
| 35 | `kkC_23_035` | Timbre7 · Chord Mode | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Program \| 1 \| 2 \| Advanced | combi | combi |
| 36 | `kkC_23_036` | Timbre7 · (Filter) Program Change | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Disable \| Enable | combi | combi |
| 37 | `kkC_23_037` | Timbre7 · (Filter) After Touch | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Disable \| Enable | combi | combi |
| 38 | `kkC_23_038` | Timbre7 · (Filter) Damper | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Disable \| Enable | combi | combi |
| 39 | `kkC_23_039` | Timbre7 · (Filter) Portamento | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Disable \| Enable | combi | combi |
| 40 | `kkC_23_040` | Timbre7 · (Filter) JSX As Mod. | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Disable \| Enable | combi | combi |
| 41 | `kkC_23_041` | Timbre7 · (Filter) JS+Y | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Disable \| Enable | combi | combi |
| 42 | `kkC_23_042` | Timbre7 · (Filter) JS-Y | `(154, 312, 146)` | combo `(154, 325)` 146x20 | Disable \| Enable | combi | combi |
| 43 | `kkC_23_043` | Timbre7 · (Filter) Ribbon | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Disable \| Enable | combi | combi |
| 44 | `kkC_23_044` | Timbre7 · (Filter) Knob1 | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Disable \| Enable | combi | combi |
| 45 | `kkC_23_045` | Timbre7 · (Filter) Knob2 | `(601, 312, 146)` | combo `(601, 325)` 146x20 | Disable \| Enable | combi | combi |
| 46 | `kkC_23_046` | Timbre7 · (Filter) Knob3 | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Disable \| Enable | combi | combi |
| 47 | `kkC_23_047` | Timbre7 · (Filter) Knob4 | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Disable \| Enable | combi | combi |
| 48 | `kkC_23_048` | Timbre7 · (Filter) Knob5 | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Disable \| Enable | combi | combi |
| 49 | `kkC_23_049` | Timbre7 · (Filter) Knob6 | `(1197, 312, 146)` | combo `(1197, 325)` 146x20 | Disable \| Enable | combi | combi |
| 50 | `kkC_23_050` | Timbre7 · (Filter) Knob7 | `(1346, 312, 146)` | combo `(1346, 325)` 146x20 | Disable \| Enable | combi | combi |
| 51 | `kkC_23_051` | Timbre7 · (Filter) Knob8 | `(5, 361, 146)` | combo `(5, 374)` 146x20 | Disable \| Enable | combi | combi |
| 52 | `kkC_23_052` | Timbre7 · (Filter) Switch1 | `(154, 361, 146)` | combo `(154, 374)` 146x20 | Disable \| Enable | combi | combi |
| 53 | `kkC_23_053` | Timbre7 · (Filter) Switch2 | `(303, 361, 146)` | combo `(303, 374)` 146x20 | Disable \| Enable | combi | combi |
| 54 | `kkC_23_054` | Timbre7 · (Filter) Foot Switch | `(452, 361, 146)` | combo `(452, 374)` 146x20 | Disable \| Enable | combi | combi |
| 55 | `kkC_23_055` | Timbre7 · (Filter) Foot Pedal | `(601, 361, 146)` | combo `(601, 374)` 146x20 | Disable \| Enable | combi | combi |
| 56 | `kkC_23_056` | Timbre7 · (Filter) Other CC# | `(750, 361, 146)` | combo `(750, 374)` 146x20 | Disable \| Enable | combi | combi |
| 57 | `kkC_23_057` | Timbre7 · Use Program Scale | `(899, 361, 146)` | combo `(899, 374)` 146x20 | Off \| On | combi | combi |
| 58 | `kkC_23_058` | Timbre7 · Auto Load Program EQ | `(1048, 361, 146)` | combo `(1048, 374)` 146x20 | Off \| On | combi | combi |
| 59 | `kkC_23_059` | Timbre7 · Mute | `(1197, 361, 146)` | combo `(1197, 374)` 146x20 | Off \| On | combi | combi |
| 60 | `kkC_23_060` | Timbre7 · Osc Mode | `(1346, 361, 146)` | combo `(1346, 374)` 146x20 | Program \| 1 \| 2 \| Mono Legato | combi | combi |

#### Tab 24 - Timbre 7·2 (43 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_24_001` | Timbre7 · Osc Select | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Both \| 1 \| OSC2 | combi | combi |
| 2 | `kkC_24_002` | Timbre7 · Timbre Priority | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | combi | combi |
| 3 | `kkC_24_003` | Timbre7 · Osc On/Off By KARMA | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Normal \| 1 \| Osc Off by K | combi | combi |
| 4 | `kkC_24_004` | Timbre7 · (Filter) Waveform SysEx | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Disable \| Enable | combi | combi |
| 5 | `kkC_24_005` | Timbre7 · Key Window Top | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_24_006` | Timbre7 · Key Window Bottom | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_24_007` | Timbre7 · Vel.Window High | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_24_008` | Timbre7 · Vel.Window Low | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_24_009` | Timbre7 · Vel.Window High Slope | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 10 | `kkC_24_010` | Timbre7 · Vel.Window Low Slope | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 11 | `kkC_24_011` | Timbre7 · Quantize Trigger | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 12 | `kkC_24_012` | Timbre7 · Key Sync | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 13 | `kkC_24_013` | Timbre7 · (Track EQ) Trim | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_24_014` | Timbre7 · (Track EQ) Bypass | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_24_015` | Timbre7 · (Track EQ) Mid Frequency | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..165 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_24_016` | Timbre7 · (Track EQ) Low Gain | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 17 | `kkC_24_017` | Timbre7 · (Track EQ) Mid Gain | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 18 | `kkC_24_018` | Timbre7 · (Track EQ) High Gain | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 19 | `kkC_24_019` | Timbre7 · VJS Assign | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| -Y | combi | combi |
| 20 | `kkC_24_020` | Timbre7 · Volume Center | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..100 step 25.0 (0 dec) | combi | combi |
| 21 | `kkC_24_021` | Timbre7 · Program Vector Volume | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Off \| On | combi | combi |
| 22 | `kkC_24_022` | Timbre7 · Combi Vector CC | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| On | combi | combi |
| 23 | `kkC_24_023` | Timbre7 · Program Vector CC | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| On | combi | combi |
| 24 | `kkC_24_024` | Timbre7 · Switch1 Value | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | combi | combi |
| 25 | `kkC_24_025` | Timbre7 · Switch2 Value | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_24_026` | Timbre7 · Switch3 Value | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | combi | combi |
| 27 | `kkC_24_027` | Timbre7 · Switch4 Value | `(899, 214, 146)` | combo `(899, 227)` 146x20 | Off \| On | combi | combi |
| 28 | `kkC_24_028` | Timbre7 · Switch5 Value | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | Off \| On | combi | combi |
| 29 | `kkC_24_029` | Timbre7 · Switch6 Value | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| On | combi | combi |
| 30 | `kkC_24_030` | Timbre7 · Switch7 Value | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| On | combi | combi |
| 31 | `kkC_24_031` | Timbre7 · Switch8 Value | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_24_032` | Timbre7 · Switch9 Value | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | combi | combi |
| 33 | `kkC_24_033` | Timbre7 · Switch10 Value | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Off \| On | combi | combi |
| 34 | `kkC_24_034` | Timbre7 · Switch11 Value | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Off \| On | combi | combi |
| 35 | `kkC_24_035` | Timbre7 · Switch12 Value | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | combi | combi |
| 36 | `kkC_24_036` | Timbre7 · Switch13 Value | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Off \| On | combi | combi |
| 37 | `kkC_24_037` | Timbre7 · Switch14 Value | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Off \| On | combi | combi |
| 38 | `kkC_24_038` | Timbre7 · Switch15 Value | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| On | combi | combi |
| 39 | `kkC_24_039` | Timbre7 · Switch16 Value | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Off \| On | combi | combi |
| 40 | `kkC_24_040` | Timbre7 · EXi1 Input Source Bus | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 41 | `kkC_24_041` | Timbre7 · EXi1 Input Source Channel | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |
| 42 | `kkC_24_042` | Timbre7 · EXi2 Input Source Bus | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_24_043` | Timbre7 · EXi2 Input Source Channel | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |

#### Tab 25 - Timbre 8 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_25_001` | Timbre8 · Program Number | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 2 | `kkC_25_002` | Timbre8 · Bank Number | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..30 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_25_003` | Timbre8 · MIDI Channel | `(303, 116, 146)` | combo `(303, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 4 | `kkC_25_004` | Timbre8 · Status | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| External2 | combi | combi |
| 5 | `kkC_25_005` | Timbre8 · Bank MSB | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_25_006` | Timbre8 · Bank LSB | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_25_007` | Timbre8 · Volume | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_25_008` | Timbre8 · Transpose | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -60..60 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_25_009` | Timbre8 · Detune | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_25_010` | Timbre8 · Delay Time | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..6001 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_25_011` | Timbre8 · Delay Tempo Base Note | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 12 | `kkC_25_012` | Timbre8 · Delay Mode | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | combi | combi |
| 13 | `kkC_25_013` | Timbre8 · Delay Tempo Times | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_25_014` | Timbre8 · Pan | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_25_015` | Timbre8 · Send1 | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_25_016` | Timbre8 · Send2 | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_25_017` | Timbre8 · Drum Kit Patch IFX1 | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_25_018` | Timbre8 · Drum Kit Patch IFX2 | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 19 | `kkC_25_019` | Timbre8 · Drum Kit Patch IFX3 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 20 | `kkC_25_020` | Timbre8 · Drum Kit Patch IFX4 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_25_021` | Timbre8 · Drum Kit Patch IFX5 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_25_022` | Timbre8 · Drum Kit Patch IFX6 | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 23 | `kkC_25_023` | Timbre8 · Drum Kit Patch IFX7 | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 24 | `kkC_25_024` | Timbre8 · Drum Kit Patch IFX8 | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 25 | `kkC_25_025` | Timbre8 · Drum Kit Patch IFX9 | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 26 | `kkC_25_026` | Timbre8 · Drum Kit Patch IFX10 | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 27 | `kkC_25_027` | Timbre8 · Drum Kit Patch IFX11 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_25_028` | Timbre8 · Drum Kit Patch IFX12 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_25_029` | Timbre8 · Bus Select | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 30 | `kkC_25_030` | Timbre8 · Fx Bus Select | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_25_031` | Timbre8 · Use Drum Kit Bus Setting | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_25_032` | Timbre8 · Rec Bus | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 33 | `kkC_25_033` | Timbre8 · Chord Source | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| Pad 8 | combi | combi |
| 34 | `kkC_25_034` | Timbre8 · Max # of Notes | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 16 | combi | combi |
| 35 | `kkC_25_035` | Timbre8 · Chord Mode | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Program \| 1 \| 2 \| Advanced | combi | combi |
| 36 | `kkC_25_036` | Timbre8 · (Filter) Program Change | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Disable \| Enable | combi | combi |
| 37 | `kkC_25_037` | Timbre8 · (Filter) After Touch | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Disable \| Enable | combi | combi |
| 38 | `kkC_25_038` | Timbre8 · (Filter) Damper | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Disable \| Enable | combi | combi |
| 39 | `kkC_25_039` | Timbre8 · (Filter) Portamento | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Disable \| Enable | combi | combi |
| 40 | `kkC_25_040` | Timbre8 · (Filter) JSX As Mod. | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Disable \| Enable | combi | combi |
| 41 | `kkC_25_041` | Timbre8 · (Filter) JS+Y | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Disable \| Enable | combi | combi |
| 42 | `kkC_25_042` | Timbre8 · (Filter) JS-Y | `(154, 312, 146)` | combo `(154, 325)` 146x20 | Disable \| Enable | combi | combi |
| 43 | `kkC_25_043` | Timbre8 · (Filter) Ribbon | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Disable \| Enable | combi | combi |
| 44 | `kkC_25_044` | Timbre8 · (Filter) Knob1 | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Disable \| Enable | combi | combi |
| 45 | `kkC_25_045` | Timbre8 · (Filter) Knob2 | `(601, 312, 146)` | combo `(601, 325)` 146x20 | Disable \| Enable | combi | combi |
| 46 | `kkC_25_046` | Timbre8 · (Filter) Knob3 | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Disable \| Enable | combi | combi |
| 47 | `kkC_25_047` | Timbre8 · (Filter) Knob4 | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Disable \| Enable | combi | combi |
| 48 | `kkC_25_048` | Timbre8 · (Filter) Knob5 | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Disable \| Enable | combi | combi |
| 49 | `kkC_25_049` | Timbre8 · (Filter) Knob6 | `(1197, 312, 146)` | combo `(1197, 325)` 146x20 | Disable \| Enable | combi | combi |
| 50 | `kkC_25_050` | Timbre8 · (Filter) Knob7 | `(1346, 312, 146)` | combo `(1346, 325)` 146x20 | Disable \| Enable | combi | combi |
| 51 | `kkC_25_051` | Timbre8 · (Filter) Knob8 | `(5, 361, 146)` | combo `(5, 374)` 146x20 | Disable \| Enable | combi | combi |
| 52 | `kkC_25_052` | Timbre8 · (Filter) Switch1 | `(154, 361, 146)` | combo `(154, 374)` 146x20 | Disable \| Enable | combi | combi |
| 53 | `kkC_25_053` | Timbre8 · (Filter) Switch2 | `(303, 361, 146)` | combo `(303, 374)` 146x20 | Disable \| Enable | combi | combi |
| 54 | `kkC_25_054` | Timbre8 · (Filter) Foot Switch | `(452, 361, 146)` | combo `(452, 374)` 146x20 | Disable \| Enable | combi | combi |
| 55 | `kkC_25_055` | Timbre8 · (Filter) Foot Pedal | `(601, 361, 146)` | combo `(601, 374)` 146x20 | Disable \| Enable | combi | combi |
| 56 | `kkC_25_056` | Timbre8 · (Filter) Other CC# | `(750, 361, 146)` | combo `(750, 374)` 146x20 | Disable \| Enable | combi | combi |
| 57 | `kkC_25_057` | Timbre8 · Use Program Scale | `(899, 361, 146)` | combo `(899, 374)` 146x20 | Off \| On | combi | combi |
| 58 | `kkC_25_058` | Timbre8 · Auto Load Program EQ | `(1048, 361, 146)` | combo `(1048, 374)` 146x20 | Off \| On | combi | combi |
| 59 | `kkC_25_059` | Timbre8 · Mute | `(1197, 361, 146)` | combo `(1197, 374)` 146x20 | Off \| On | combi | combi |
| 60 | `kkC_25_060` | Timbre8 · Osc Mode | `(1346, 361, 146)` | combo `(1346, 374)` 146x20 | Program \| 1 \| 2 \| Mono Legato | combi | combi |

#### Tab 26 - Timbre 8·2 (43 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_26_001` | Timbre8 · Osc Select | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Both \| 1 \| OSC2 | combi | combi |
| 2 | `kkC_26_002` | Timbre8 · Timbre Priority | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | combi | combi |
| 3 | `kkC_26_003` | Timbre8 · Osc On/Off By KARMA | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Normal \| 1 \| Osc Off by K | combi | combi |
| 4 | `kkC_26_004` | Timbre8 · (Filter) Waveform SysEx | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Disable \| Enable | combi | combi |
| 5 | `kkC_26_005` | Timbre8 · Key Window Top | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_26_006` | Timbre8 · Key Window Bottom | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_26_007` | Timbre8 · Vel.Window High | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_26_008` | Timbre8 · Vel.Window Low | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_26_009` | Timbre8 · Vel.Window High Slope | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 10 | `kkC_26_010` | Timbre8 · Vel.Window Low Slope | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 11 | `kkC_26_011` | Timbre8 · Quantize Trigger | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 12 | `kkC_26_012` | Timbre8 · Key Sync | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 13 | `kkC_26_013` | Timbre8 · (Track EQ) Trim | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_26_014` | Timbre8 · (Track EQ) Bypass | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_26_015` | Timbre8 · (Track EQ) Mid Frequency | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..165 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_26_016` | Timbre8 · (Track EQ) Low Gain | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 17 | `kkC_26_017` | Timbre8 · (Track EQ) Mid Gain | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 18 | `kkC_26_018` | Timbre8 · (Track EQ) High Gain | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 19 | `kkC_26_019` | Timbre8 · VJS Assign | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| -Y | combi | combi |
| 20 | `kkC_26_020` | Timbre8 · Volume Center | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..100 step 25.0 (0 dec) | combi | combi |
| 21 | `kkC_26_021` | Timbre8 · Program Vector Volume | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Off \| On | combi | combi |
| 22 | `kkC_26_022` | Timbre8 · Combi Vector CC | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| On | combi | combi |
| 23 | `kkC_26_023` | Timbre8 · Program Vector CC | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| On | combi | combi |
| 24 | `kkC_26_024` | Timbre8 · Switch1 Value | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | combi | combi |
| 25 | `kkC_26_025` | Timbre8 · Switch2 Value | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_26_026` | Timbre8 · Switch3 Value | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | combi | combi |
| 27 | `kkC_26_027` | Timbre8 · Switch4 Value | `(899, 214, 146)` | combo `(899, 227)` 146x20 | Off \| On | combi | combi |
| 28 | `kkC_26_028` | Timbre8 · Switch5 Value | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | Off \| On | combi | combi |
| 29 | `kkC_26_029` | Timbre8 · Switch6 Value | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| On | combi | combi |
| 30 | `kkC_26_030` | Timbre8 · Switch7 Value | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| On | combi | combi |
| 31 | `kkC_26_031` | Timbre8 · Switch8 Value | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_26_032` | Timbre8 · Switch9 Value | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | combi | combi |
| 33 | `kkC_26_033` | Timbre8 · Switch10 Value | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Off \| On | combi | combi |
| 34 | `kkC_26_034` | Timbre8 · Switch11 Value | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Off \| On | combi | combi |
| 35 | `kkC_26_035` | Timbre8 · Switch12 Value | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | combi | combi |
| 36 | `kkC_26_036` | Timbre8 · Switch13 Value | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Off \| On | combi | combi |
| 37 | `kkC_26_037` | Timbre8 · Switch14 Value | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Off \| On | combi | combi |
| 38 | `kkC_26_038` | Timbre8 · Switch15 Value | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| On | combi | combi |
| 39 | `kkC_26_039` | Timbre8 · Switch16 Value | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Off \| On | combi | combi |
| 40 | `kkC_26_040` | Timbre8 · EXi1 Input Source Bus | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 41 | `kkC_26_041` | Timbre8 · EXi1 Input Source Channel | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |
| 42 | `kkC_26_042` | Timbre8 · EXi2 Input Source Bus | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_26_043` | Timbre8 · EXi2 Input Source Channel | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |

#### Tab 27 - Timbre 9 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_27_001` | Timbre9 · Program Number | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 2 | `kkC_27_002` | Timbre9 · Bank Number | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..30 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_27_003` | Timbre9 · MIDI Channel | `(303, 116, 146)` | combo `(303, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 4 | `kkC_27_004` | Timbre9 · Status | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| External2 | combi | combi |
| 5 | `kkC_27_005` | Timbre9 · Bank MSB | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_27_006` | Timbre9 · Bank LSB | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_27_007` | Timbre9 · Volume | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_27_008` | Timbre9 · Transpose | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -60..60 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_27_009` | Timbre9 · Detune | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_27_010` | Timbre9 · Delay Time | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..6001 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_27_011` | Timbre9 · Delay Tempo Base Note | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 12 | `kkC_27_012` | Timbre9 · Delay Mode | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | combi | combi |
| 13 | `kkC_27_013` | Timbre9 · Delay Tempo Times | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_27_014` | Timbre9 · Pan | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_27_015` | Timbre9 · Send1 | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_27_016` | Timbre9 · Send2 | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_27_017` | Timbre9 · Drum Kit Patch IFX1 | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_27_018` | Timbre9 · Drum Kit Patch IFX2 | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 19 | `kkC_27_019` | Timbre9 · Drum Kit Patch IFX3 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 20 | `kkC_27_020` | Timbre9 · Drum Kit Patch IFX4 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_27_021` | Timbre9 · Drum Kit Patch IFX5 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_27_022` | Timbre9 · Drum Kit Patch IFX6 | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 23 | `kkC_27_023` | Timbre9 · Drum Kit Patch IFX7 | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 24 | `kkC_27_024` | Timbre9 · Drum Kit Patch IFX8 | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 25 | `kkC_27_025` | Timbre9 · Drum Kit Patch IFX9 | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 26 | `kkC_27_026` | Timbre9 · Drum Kit Patch IFX10 | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 27 | `kkC_27_027` | Timbre9 · Drum Kit Patch IFX11 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_27_028` | Timbre9 · Drum Kit Patch IFX12 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_27_029` | Timbre9 · Bus Select | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 30 | `kkC_27_030` | Timbre9 · Fx Bus Select | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_27_031` | Timbre9 · Use Drum Kit Bus Setting | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_27_032` | Timbre9 · Rec Bus | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 33 | `kkC_27_033` | Timbre9 · Chord Source | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| Pad 8 | combi | combi |
| 34 | `kkC_27_034` | Timbre9 · Max # of Notes | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 16 | combi | combi |
| 35 | `kkC_27_035` | Timbre9 · Chord Mode | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Program \| 1 \| 2 \| Advanced | combi | combi |
| 36 | `kkC_27_036` | Timbre9 · (Filter) Program Change | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Disable \| Enable | combi | combi |
| 37 | `kkC_27_037` | Timbre9 · (Filter) After Touch | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Disable \| Enable | combi | combi |
| 38 | `kkC_27_038` | Timbre9 · (Filter) Damper | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Disable \| Enable | combi | combi |
| 39 | `kkC_27_039` | Timbre9 · (Filter) Portamento | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Disable \| Enable | combi | combi |
| 40 | `kkC_27_040` | Timbre9 · (Filter) JSX As Mod. | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Disable \| Enable | combi | combi |
| 41 | `kkC_27_041` | Timbre9 · (Filter) JS+Y | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Disable \| Enable | combi | combi |
| 42 | `kkC_27_042` | Timbre9 · (Filter) JS-Y | `(154, 312, 146)` | combo `(154, 325)` 146x20 | Disable \| Enable | combi | combi |
| 43 | `kkC_27_043` | Timbre9 · (Filter) Ribbon | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Disable \| Enable | combi | combi |
| 44 | `kkC_27_044` | Timbre9 · (Filter) Knob1 | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Disable \| Enable | combi | combi |
| 45 | `kkC_27_045` | Timbre9 · (Filter) Knob2 | `(601, 312, 146)` | combo `(601, 325)` 146x20 | Disable \| Enable | combi | combi |
| 46 | `kkC_27_046` | Timbre9 · (Filter) Knob3 | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Disable \| Enable | combi | combi |
| 47 | `kkC_27_047` | Timbre9 · (Filter) Knob4 | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Disable \| Enable | combi | combi |
| 48 | `kkC_27_048` | Timbre9 · (Filter) Knob5 | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Disable \| Enable | combi | combi |
| 49 | `kkC_27_049` | Timbre9 · (Filter) Knob6 | `(1197, 312, 146)` | combo `(1197, 325)` 146x20 | Disable \| Enable | combi | combi |
| 50 | `kkC_27_050` | Timbre9 · (Filter) Knob7 | `(1346, 312, 146)` | combo `(1346, 325)` 146x20 | Disable \| Enable | combi | combi |
| 51 | `kkC_27_051` | Timbre9 · (Filter) Knob8 | `(5, 361, 146)` | combo `(5, 374)` 146x20 | Disable \| Enable | combi | combi |
| 52 | `kkC_27_052` | Timbre9 · (Filter) Switch1 | `(154, 361, 146)` | combo `(154, 374)` 146x20 | Disable \| Enable | combi | combi |
| 53 | `kkC_27_053` | Timbre9 · (Filter) Switch2 | `(303, 361, 146)` | combo `(303, 374)` 146x20 | Disable \| Enable | combi | combi |
| 54 | `kkC_27_054` | Timbre9 · (Filter) Foot Switch | `(452, 361, 146)` | combo `(452, 374)` 146x20 | Disable \| Enable | combi | combi |
| 55 | `kkC_27_055` | Timbre9 · (Filter) Foot Pedal | `(601, 361, 146)` | combo `(601, 374)` 146x20 | Disable \| Enable | combi | combi |
| 56 | `kkC_27_056` | Timbre9 · (Filter) Other CC# | `(750, 361, 146)` | combo `(750, 374)` 146x20 | Disable \| Enable | combi | combi |
| 57 | `kkC_27_057` | Timbre9 · Use Program Scale | `(899, 361, 146)` | combo `(899, 374)` 146x20 | Off \| On | combi | combi |
| 58 | `kkC_27_058` | Timbre9 · Auto Load Program EQ | `(1048, 361, 146)` | combo `(1048, 374)` 146x20 | Off \| On | combi | combi |
| 59 | `kkC_27_059` | Timbre9 · Mute | `(1197, 361, 146)` | combo `(1197, 374)` 146x20 | Off \| On | combi | combi |
| 60 | `kkC_27_060` | Timbre9 · Osc Mode | `(1346, 361, 146)` | combo `(1346, 374)` 146x20 | Program \| 1 \| 2 \| Mono Legato | combi | combi |

#### Tab 28 - Timbre 9·2 (43 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_28_001` | Timbre9 · Osc Select | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Both \| 1 \| OSC2 | combi | combi |
| 2 | `kkC_28_002` | Timbre9 · Timbre Priority | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | combi | combi |
| 3 | `kkC_28_003` | Timbre9 · Osc On/Off By KARMA | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Normal \| 1 \| Osc Off by K | combi | combi |
| 4 | `kkC_28_004` | Timbre9 · (Filter) Waveform SysEx | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Disable \| Enable | combi | combi |
| 5 | `kkC_28_005` | Timbre9 · Key Window Top | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_28_006` | Timbre9 · Key Window Bottom | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_28_007` | Timbre9 · Vel.Window High | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_28_008` | Timbre9 · Vel.Window Low | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_28_009` | Timbre9 · Vel.Window High Slope | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 10 | `kkC_28_010` | Timbre9 · Vel.Window Low Slope | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 11 | `kkC_28_011` | Timbre9 · Quantize Trigger | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 12 | `kkC_28_012` | Timbre9 · Key Sync | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 13 | `kkC_28_013` | Timbre9 · (Track EQ) Trim | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_28_014` | Timbre9 · (Track EQ) Bypass | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_28_015` | Timbre9 · (Track EQ) Mid Frequency | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..165 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_28_016` | Timbre9 · (Track EQ) Low Gain | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 17 | `kkC_28_017` | Timbre9 · (Track EQ) Mid Gain | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 18 | `kkC_28_018` | Timbre9 · (Track EQ) High Gain | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 19 | `kkC_28_019` | Timbre9 · VJS Assign | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| -Y | combi | combi |
| 20 | `kkC_28_020` | Timbre9 · Volume Center | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..100 step 25.0 (0 dec) | combi | combi |
| 21 | `kkC_28_021` | Timbre9 · Program Vector Volume | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Off \| On | combi | combi |
| 22 | `kkC_28_022` | Timbre9 · Combi Vector CC | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| On | combi | combi |
| 23 | `kkC_28_023` | Timbre9 · Program Vector CC | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| On | combi | combi |
| 24 | `kkC_28_024` | Timbre9 · Switch1 Value | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | combi | combi |
| 25 | `kkC_28_025` | Timbre9 · Switch2 Value | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_28_026` | Timbre9 · Switch3 Value | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | combi | combi |
| 27 | `kkC_28_027` | Timbre9 · Switch4 Value | `(899, 214, 146)` | combo `(899, 227)` 146x20 | Off \| On | combi | combi |
| 28 | `kkC_28_028` | Timbre9 · Switch5 Value | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | Off \| On | combi | combi |
| 29 | `kkC_28_029` | Timbre9 · Switch6 Value | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| On | combi | combi |
| 30 | `kkC_28_030` | Timbre9 · Switch7 Value | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| On | combi | combi |
| 31 | `kkC_28_031` | Timbre9 · Switch8 Value | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_28_032` | Timbre9 · Switch9 Value | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | combi | combi |
| 33 | `kkC_28_033` | Timbre9 · Switch10 Value | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Off \| On | combi | combi |
| 34 | `kkC_28_034` | Timbre9 · Switch11 Value | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Off \| On | combi | combi |
| 35 | `kkC_28_035` | Timbre9 · Switch12 Value | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | combi | combi |
| 36 | `kkC_28_036` | Timbre9 · Switch13 Value | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Off \| On | combi | combi |
| 37 | `kkC_28_037` | Timbre9 · Switch14 Value | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Off \| On | combi | combi |
| 38 | `kkC_28_038` | Timbre9 · Switch15 Value | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| On | combi | combi |
| 39 | `kkC_28_039` | Timbre9 · Switch16 Value | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Off \| On | combi | combi |
| 40 | `kkC_28_040` | Timbre9 · EXi1 Input Source Bus | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 41 | `kkC_28_041` | Timbre9 · EXi1 Input Source Channel | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |
| 42 | `kkC_28_042` | Timbre9 · EXi2 Input Source Bus | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_28_043` | Timbre9 · EXi2 Input Source Channel | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |

#### Tab 29 - Timbre 10 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_29_001` | Timbre10 · Program Number | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 2 | `kkC_29_002` | Timbre10 · Bank Number | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..30 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_29_003` | Timbre10 · MIDI Channel | `(303, 116, 146)` | combo `(303, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 4 | `kkC_29_004` | Timbre10 · Status | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| External2 | combi | combi |
| 5 | `kkC_29_005` | Timbre10 · Bank MSB | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_29_006` | Timbre10 · Bank LSB | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_29_007` | Timbre10 · Volume | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_29_008` | Timbre10 · Transpose | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -60..60 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_29_009` | Timbre10 · Detune | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_29_010` | Timbre10 · Delay Time | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..6001 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_29_011` | Timbre10 · Delay Tempo Base Note | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 12 | `kkC_29_012` | Timbre10 · Delay Mode | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | combi | combi |
| 13 | `kkC_29_013` | Timbre10 · Delay Tempo Times | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_29_014` | Timbre10 · Pan | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_29_015` | Timbre10 · Send1 | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_29_016` | Timbre10 · Send2 | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_29_017` | Timbre10 · Drum Kit Patch IFX1 | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_29_018` | Timbre10 · Drum Kit Patch IFX2 | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 19 | `kkC_29_019` | Timbre10 · Drum Kit Patch IFX3 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 20 | `kkC_29_020` | Timbre10 · Drum Kit Patch IFX4 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_29_021` | Timbre10 · Drum Kit Patch IFX5 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_29_022` | Timbre10 · Drum Kit Patch IFX6 | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 23 | `kkC_29_023` | Timbre10 · Drum Kit Patch IFX7 | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 24 | `kkC_29_024` | Timbre10 · Drum Kit Patch IFX8 | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 25 | `kkC_29_025` | Timbre10 · Drum Kit Patch IFX9 | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 26 | `kkC_29_026` | Timbre10 · Drum Kit Patch IFX10 | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 27 | `kkC_29_027` | Timbre10 · Drum Kit Patch IFX11 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_29_028` | Timbre10 · Drum Kit Patch IFX12 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_29_029` | Timbre10 · Bus Select | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 30 | `kkC_29_030` | Timbre10 · Fx Bus Select | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_29_031` | Timbre10 · Use Drum Kit Bus Setting | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_29_032` | Timbre10 · Rec Bus | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 33 | `kkC_29_033` | Timbre10 · Chord Source | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| Pad 8 | combi | combi |
| 34 | `kkC_29_034` | Timbre10 · Max # of Notes | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 16 | combi | combi |
| 35 | `kkC_29_035` | Timbre10 · Chord Mode | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Program \| 1 \| 2 \| Advanced | combi | combi |
| 36 | `kkC_29_036` | Timbre10 · (Filter) Program Change | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Disable \| Enable | combi | combi |
| 37 | `kkC_29_037` | Timbre10 · (Filter) After Touch | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Disable \| Enable | combi | combi |
| 38 | `kkC_29_038` | Timbre10 · (Filter) Damper | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Disable \| Enable | combi | combi |
| 39 | `kkC_29_039` | Timbre10 · (Filter) Portamento | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Disable \| Enable | combi | combi |
| 40 | `kkC_29_040` | Timbre10 · (Filter) JSX As Mod. | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Disable \| Enable | combi | combi |
| 41 | `kkC_29_041` | Timbre10 · (Filter) JS+Y | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Disable \| Enable | combi | combi |
| 42 | `kkC_29_042` | Timbre10 · (Filter) JS-Y | `(154, 312, 146)` | combo `(154, 325)` 146x20 | Disable \| Enable | combi | combi |
| 43 | `kkC_29_043` | Timbre10 · (Filter) Ribbon | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Disable \| Enable | combi | combi |
| 44 | `kkC_29_044` | Timbre10 · (Filter) Knob1 | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Disable \| Enable | combi | combi |
| 45 | `kkC_29_045` | Timbre10 · (Filter) Knob2 | `(601, 312, 146)` | combo `(601, 325)` 146x20 | Disable \| Enable | combi | combi |
| 46 | `kkC_29_046` | Timbre10 · (Filter) Knob3 | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Disable \| Enable | combi | combi |
| 47 | `kkC_29_047` | Timbre10 · (Filter) Knob4 | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Disable \| Enable | combi | combi |
| 48 | `kkC_29_048` | Timbre10 · (Filter) Knob5 | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Disable \| Enable | combi | combi |
| 49 | `kkC_29_049` | Timbre10 · (Filter) Knob6 | `(1197, 312, 146)` | combo `(1197, 325)` 146x20 | Disable \| Enable | combi | combi |
| 50 | `kkC_29_050` | Timbre10 · (Filter) Knob7 | `(1346, 312, 146)` | combo `(1346, 325)` 146x20 | Disable \| Enable | combi | combi |
| 51 | `kkC_29_051` | Timbre10 · (Filter) Knob8 | `(5, 361, 146)` | combo `(5, 374)` 146x20 | Disable \| Enable | combi | combi |
| 52 | `kkC_29_052` | Timbre10 · (Filter) Switch1 | `(154, 361, 146)` | combo `(154, 374)` 146x20 | Disable \| Enable | combi | combi |
| 53 | `kkC_29_053` | Timbre10 · (Filter) Switch2 | `(303, 361, 146)` | combo `(303, 374)` 146x20 | Disable \| Enable | combi | combi |
| 54 | `kkC_29_054` | Timbre10 · (Filter) Foot Switch | `(452, 361, 146)` | combo `(452, 374)` 146x20 | Disable \| Enable | combi | combi |
| 55 | `kkC_29_055` | Timbre10 · (Filter) Foot Pedal | `(601, 361, 146)` | combo `(601, 374)` 146x20 | Disable \| Enable | combi | combi |
| 56 | `kkC_29_056` | Timbre10 · (Filter) Other CC# | `(750, 361, 146)` | combo `(750, 374)` 146x20 | Disable \| Enable | combi | combi |
| 57 | `kkC_29_057` | Timbre10 · Use Program Scale | `(899, 361, 146)` | combo `(899, 374)` 146x20 | Off \| On | combi | combi |
| 58 | `kkC_29_058` | Timbre10 · Auto Load Program EQ | `(1048, 361, 146)` | combo `(1048, 374)` 146x20 | Off \| On | combi | combi |
| 59 | `kkC_29_059` | Timbre10 · Mute | `(1197, 361, 146)` | combo `(1197, 374)` 146x20 | Off \| On | combi | combi |
| 60 | `kkC_29_060` | Timbre10 · Osc Mode | `(1346, 361, 146)` | combo `(1346, 374)` 146x20 | Program \| 1 \| 2 \| Mono Legato | combi | combi |

#### Tab 30 - Timbre 10·2 (43 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_30_001` | Timbre10 · Osc Select | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Both \| 1 \| OSC2 | combi | combi |
| 2 | `kkC_30_002` | Timbre10 · Timbre Priority | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | combi | combi |
| 3 | `kkC_30_003` | Timbre10 · Osc On/Off By KARMA | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Normal \| 1 \| Osc Off by K | combi | combi |
| 4 | `kkC_30_004` | Timbre10 · (Filter) Waveform SysEx | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Disable \| Enable | combi | combi |
| 5 | `kkC_30_005` | Timbre10 · Key Window Top | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_30_006` | Timbre10 · Key Window Bottom | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_30_007` | Timbre10 · Vel.Window High | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_30_008` | Timbre10 · Vel.Window Low | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_30_009` | Timbre10 · Vel.Window High Slope | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 10 | `kkC_30_010` | Timbre10 · Vel.Window Low Slope | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 11 | `kkC_30_011` | Timbre10 · Quantize Trigger | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 12 | `kkC_30_012` | Timbre10 · Key Sync | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 13 | `kkC_30_013` | Timbre10 · (Track EQ) Trim | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_30_014` | Timbre10 · (Track EQ) Bypass | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_30_015` | Timbre10 · (Track EQ) Mid Frequency | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..165 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_30_016` | Timbre10 · (Track EQ) Low Gain | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 17 | `kkC_30_017` | Timbre10 · (Track EQ) Mid Gain | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 18 | `kkC_30_018` | Timbre10 · (Track EQ) High Gain | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 19 | `kkC_30_019` | Timbre10 · VJS Assign | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| -Y | combi | combi |
| 20 | `kkC_30_020` | Timbre10 · Volume Center | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..100 step 25.0 (0 dec) | combi | combi |
| 21 | `kkC_30_021` | Timbre10 · Program Vector Volume | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Off \| On | combi | combi |
| 22 | `kkC_30_022` | Timbre10 · Combi Vector CC | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| On | combi | combi |
| 23 | `kkC_30_023` | Timbre10 · Program Vector CC | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| On | combi | combi |
| 24 | `kkC_30_024` | Timbre10 · Switch1 Value | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | combi | combi |
| 25 | `kkC_30_025` | Timbre10 · Switch2 Value | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_30_026` | Timbre10 · Switch3 Value | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | combi | combi |
| 27 | `kkC_30_027` | Timbre10 · Switch4 Value | `(899, 214, 146)` | combo `(899, 227)` 146x20 | Off \| On | combi | combi |
| 28 | `kkC_30_028` | Timbre10 · Switch5 Value | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | Off \| On | combi | combi |
| 29 | `kkC_30_029` | Timbre10 · Switch6 Value | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| On | combi | combi |
| 30 | `kkC_30_030` | Timbre10 · Switch7 Value | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| On | combi | combi |
| 31 | `kkC_30_031` | Timbre10 · Switch8 Value | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_30_032` | Timbre10 · Switch9 Value | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | combi | combi |
| 33 | `kkC_30_033` | Timbre10 · Switch10 Value | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Off \| On | combi | combi |
| 34 | `kkC_30_034` | Timbre10 · Switch11 Value | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Off \| On | combi | combi |
| 35 | `kkC_30_035` | Timbre10 · Switch12 Value | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | combi | combi |
| 36 | `kkC_30_036` | Timbre10 · Switch13 Value | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Off \| On | combi | combi |
| 37 | `kkC_30_037` | Timbre10 · Switch14 Value | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Off \| On | combi | combi |
| 38 | `kkC_30_038` | Timbre10 · Switch15 Value | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| On | combi | combi |
| 39 | `kkC_30_039` | Timbre10 · Switch16 Value | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Off \| On | combi | combi |
| 40 | `kkC_30_040` | Timbre10 · EXi1 Input Source Bus | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 41 | `kkC_30_041` | Timbre10 · EXi1 Input Source Channel | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |
| 42 | `kkC_30_042` | Timbre10 · EXi2 Input Source Bus | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_30_043` | Timbre10 · EXi2 Input Source Channel | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |

#### Tab 31 - Timbre 11 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_31_001` | Timbre11 · Program Number | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 2 | `kkC_31_002` | Timbre11 · Bank Number | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..30 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_31_003` | Timbre11 · MIDI Channel | `(303, 116, 146)` | combo `(303, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 4 | `kkC_31_004` | Timbre11 · Status | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| External2 | combi | combi |
| 5 | `kkC_31_005` | Timbre11 · Bank MSB | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_31_006` | Timbre11 · Bank LSB | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_31_007` | Timbre11 · Volume | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_31_008` | Timbre11 · Transpose | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -60..60 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_31_009` | Timbre11 · Detune | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_31_010` | Timbre11 · Delay Time | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..6001 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_31_011` | Timbre11 · Delay Tempo Base Note | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 12 | `kkC_31_012` | Timbre11 · Delay Mode | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | combi | combi |
| 13 | `kkC_31_013` | Timbre11 · Delay Tempo Times | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_31_014` | Timbre11 · Pan | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_31_015` | Timbre11 · Send1 | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_31_016` | Timbre11 · Send2 | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_31_017` | Timbre11 · Drum Kit Patch IFX1 | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_31_018` | Timbre11 · Drum Kit Patch IFX2 | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 19 | `kkC_31_019` | Timbre11 · Drum Kit Patch IFX3 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 20 | `kkC_31_020` | Timbre11 · Drum Kit Patch IFX4 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_31_021` | Timbre11 · Drum Kit Patch IFX5 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_31_022` | Timbre11 · Drum Kit Patch IFX6 | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 23 | `kkC_31_023` | Timbre11 · Drum Kit Patch IFX7 | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 24 | `kkC_31_024` | Timbre11 · Drum Kit Patch IFX8 | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 25 | `kkC_31_025` | Timbre11 · Drum Kit Patch IFX9 | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 26 | `kkC_31_026` | Timbre11 · Drum Kit Patch IFX10 | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 27 | `kkC_31_027` | Timbre11 · Drum Kit Patch IFX11 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_31_028` | Timbre11 · Drum Kit Patch IFX12 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_31_029` | Timbre11 · Bus Select | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 30 | `kkC_31_030` | Timbre11 · Fx Bus Select | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_31_031` | Timbre11 · Use Drum Kit Bus Setting | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_31_032` | Timbre11 · Rec Bus | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 33 | `kkC_31_033` | Timbre11 · Chord Source | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| Pad 8 | combi | combi |
| 34 | `kkC_31_034` | Timbre11 · Max # of Notes | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 16 | combi | combi |
| 35 | `kkC_31_035` | Timbre11 · Chord Mode | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Program \| 1 \| 2 \| Advanced | combi | combi |
| 36 | `kkC_31_036` | Timbre11 · (Filter) Program Change | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Disable \| Enable | combi | combi |
| 37 | `kkC_31_037` | Timbre11 · (Filter) After Touch | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Disable \| Enable | combi | combi |
| 38 | `kkC_31_038` | Timbre11 · (Filter) Damper | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Disable \| Enable | combi | combi |
| 39 | `kkC_31_039` | Timbre11 · (Filter) Portamento | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Disable \| Enable | combi | combi |
| 40 | `kkC_31_040` | Timbre11 · (Filter) JSX As Mod. | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Disable \| Enable | combi | combi |
| 41 | `kkC_31_041` | Timbre11 · (Filter) JS+Y | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Disable \| Enable | combi | combi |
| 42 | `kkC_31_042` | Timbre11 · (Filter) JS-Y | `(154, 312, 146)` | combo `(154, 325)` 146x20 | Disable \| Enable | combi | combi |
| 43 | `kkC_31_043` | Timbre11 · (Filter) Ribbon | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Disable \| Enable | combi | combi |
| 44 | `kkC_31_044` | Timbre11 · (Filter) Knob1 | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Disable \| Enable | combi | combi |
| 45 | `kkC_31_045` | Timbre11 · (Filter) Knob2 | `(601, 312, 146)` | combo `(601, 325)` 146x20 | Disable \| Enable | combi | combi |
| 46 | `kkC_31_046` | Timbre11 · (Filter) Knob3 | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Disable \| Enable | combi | combi |
| 47 | `kkC_31_047` | Timbre11 · (Filter) Knob4 | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Disable \| Enable | combi | combi |
| 48 | `kkC_31_048` | Timbre11 · (Filter) Knob5 | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Disable \| Enable | combi | combi |
| 49 | `kkC_31_049` | Timbre11 · (Filter) Knob6 | `(1197, 312, 146)` | combo `(1197, 325)` 146x20 | Disable \| Enable | combi | combi |
| 50 | `kkC_31_050` | Timbre11 · (Filter) Knob7 | `(1346, 312, 146)` | combo `(1346, 325)` 146x20 | Disable \| Enable | combi | combi |
| 51 | `kkC_31_051` | Timbre11 · (Filter) Knob8 | `(5, 361, 146)` | combo `(5, 374)` 146x20 | Disable \| Enable | combi | combi |
| 52 | `kkC_31_052` | Timbre11 · (Filter) Switch1 | `(154, 361, 146)` | combo `(154, 374)` 146x20 | Disable \| Enable | combi | combi |
| 53 | `kkC_31_053` | Timbre11 · (Filter) Switch2 | `(303, 361, 146)` | combo `(303, 374)` 146x20 | Disable \| Enable | combi | combi |
| 54 | `kkC_31_054` | Timbre11 · (Filter) Foot Switch | `(452, 361, 146)` | combo `(452, 374)` 146x20 | Disable \| Enable | combi | combi |
| 55 | `kkC_31_055` | Timbre11 · (Filter) Foot Pedal | `(601, 361, 146)` | combo `(601, 374)` 146x20 | Disable \| Enable | combi | combi |
| 56 | `kkC_31_056` | Timbre11 · (Filter) Other CC# | `(750, 361, 146)` | combo `(750, 374)` 146x20 | Disable \| Enable | combi | combi |
| 57 | `kkC_31_057` | Timbre11 · Use Program Scale | `(899, 361, 146)` | combo `(899, 374)` 146x20 | Off \| On | combi | combi |
| 58 | `kkC_31_058` | Timbre11 · Auto Load Program EQ | `(1048, 361, 146)` | combo `(1048, 374)` 146x20 | Off \| On | combi | combi |
| 59 | `kkC_31_059` | Timbre11 · Mute | `(1197, 361, 146)` | combo `(1197, 374)` 146x20 | Off \| On | combi | combi |
| 60 | `kkC_31_060` | Timbre11 · Osc Mode | `(1346, 361, 146)` | combo `(1346, 374)` 146x20 | Program \| 1 \| 2 \| Mono Legato | combi | combi |

#### Tab 32 - Timbre 11·2 (43 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_32_001` | Timbre11 · Osc Select | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Both \| 1 \| OSC2 | combi | combi |
| 2 | `kkC_32_002` | Timbre11 · Timbre Priority | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | combi | combi |
| 3 | `kkC_32_003` | Timbre11 · Osc On/Off By KARMA | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Normal \| 1 \| Osc Off by K | combi | combi |
| 4 | `kkC_32_004` | Timbre11 · (Filter) Waveform SysEx | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Disable \| Enable | combi | combi |
| 5 | `kkC_32_005` | Timbre11 · Key Window Top | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_32_006` | Timbre11 · Key Window Bottom | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_32_007` | Timbre11 · Vel.Window High | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_32_008` | Timbre11 · Vel.Window Low | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_32_009` | Timbre11 · Vel.Window High Slope | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 10 | `kkC_32_010` | Timbre11 · Vel.Window Low Slope | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 11 | `kkC_32_011` | Timbre11 · Quantize Trigger | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 12 | `kkC_32_012` | Timbre11 · Key Sync | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 13 | `kkC_32_013` | Timbre11 · (Track EQ) Trim | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_32_014` | Timbre11 · (Track EQ) Bypass | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_32_015` | Timbre11 · (Track EQ) Mid Frequency | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..165 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_32_016` | Timbre11 · (Track EQ) Low Gain | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 17 | `kkC_32_017` | Timbre11 · (Track EQ) Mid Gain | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 18 | `kkC_32_018` | Timbre11 · (Track EQ) High Gain | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 19 | `kkC_32_019` | Timbre11 · VJS Assign | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| -Y | combi | combi |
| 20 | `kkC_32_020` | Timbre11 · Volume Center | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..100 step 25.0 (0 dec) | combi | combi |
| 21 | `kkC_32_021` | Timbre11 · Program Vector Volume | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Off \| On | combi | combi |
| 22 | `kkC_32_022` | Timbre11 · Combi Vector CC | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| On | combi | combi |
| 23 | `kkC_32_023` | Timbre11 · Program Vector CC | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| On | combi | combi |
| 24 | `kkC_32_024` | Timbre11 · Switch1 Value | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | combi | combi |
| 25 | `kkC_32_025` | Timbre11 · Switch2 Value | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_32_026` | Timbre11 · Switch3 Value | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | combi | combi |
| 27 | `kkC_32_027` | Timbre11 · Switch4 Value | `(899, 214, 146)` | combo `(899, 227)` 146x20 | Off \| On | combi | combi |
| 28 | `kkC_32_028` | Timbre11 · Switch5 Value | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | Off \| On | combi | combi |
| 29 | `kkC_32_029` | Timbre11 · Switch6 Value | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| On | combi | combi |
| 30 | `kkC_32_030` | Timbre11 · Switch7 Value | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| On | combi | combi |
| 31 | `kkC_32_031` | Timbre11 · Switch8 Value | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_32_032` | Timbre11 · Switch9 Value | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | combi | combi |
| 33 | `kkC_32_033` | Timbre11 · Switch10 Value | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Off \| On | combi | combi |
| 34 | `kkC_32_034` | Timbre11 · Switch11 Value | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Off \| On | combi | combi |
| 35 | `kkC_32_035` | Timbre11 · Switch12 Value | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | combi | combi |
| 36 | `kkC_32_036` | Timbre11 · Switch13 Value | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Off \| On | combi | combi |
| 37 | `kkC_32_037` | Timbre11 · Switch14 Value | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Off \| On | combi | combi |
| 38 | `kkC_32_038` | Timbre11 · Switch15 Value | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| On | combi | combi |
| 39 | `kkC_32_039` | Timbre11 · Switch16 Value | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Off \| On | combi | combi |
| 40 | `kkC_32_040` | Timbre11 · EXi1 Input Source Bus | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 41 | `kkC_32_041` | Timbre11 · EXi1 Input Source Channel | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |
| 42 | `kkC_32_042` | Timbre11 · EXi2 Input Source Bus | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_32_043` | Timbre11 · EXi2 Input Source Channel | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |

#### Tab 33 - Timbre 12 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_33_001` | Timbre12 · Program Number | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 2 | `kkC_33_002` | Timbre12 · Bank Number | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..30 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_33_003` | Timbre12 · MIDI Channel | `(303, 116, 146)` | combo `(303, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 4 | `kkC_33_004` | Timbre12 · Status | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| External2 | combi | combi |
| 5 | `kkC_33_005` | Timbre12 · Bank MSB | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_33_006` | Timbre12 · Bank LSB | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_33_007` | Timbre12 · Volume | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_33_008` | Timbre12 · Transpose | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -60..60 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_33_009` | Timbre12 · Detune | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_33_010` | Timbre12 · Delay Time | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..6001 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_33_011` | Timbre12 · Delay Tempo Base Note | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 12 | `kkC_33_012` | Timbre12 · Delay Mode | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | combi | combi |
| 13 | `kkC_33_013` | Timbre12 · Delay Tempo Times | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_33_014` | Timbre12 · Pan | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_33_015` | Timbre12 · Send1 | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_33_016` | Timbre12 · Send2 | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_33_017` | Timbre12 · Drum Kit Patch IFX1 | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_33_018` | Timbre12 · Drum Kit Patch IFX2 | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 19 | `kkC_33_019` | Timbre12 · Drum Kit Patch IFX3 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 20 | `kkC_33_020` | Timbre12 · Drum Kit Patch IFX4 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_33_021` | Timbre12 · Drum Kit Patch IFX5 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_33_022` | Timbre12 · Drum Kit Patch IFX6 | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 23 | `kkC_33_023` | Timbre12 · Drum Kit Patch IFX7 | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 24 | `kkC_33_024` | Timbre12 · Drum Kit Patch IFX8 | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 25 | `kkC_33_025` | Timbre12 · Drum Kit Patch IFX9 | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 26 | `kkC_33_026` | Timbre12 · Drum Kit Patch IFX10 | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 27 | `kkC_33_027` | Timbre12 · Drum Kit Patch IFX11 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_33_028` | Timbre12 · Drum Kit Patch IFX12 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_33_029` | Timbre12 · Bus Select | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 30 | `kkC_33_030` | Timbre12 · Fx Bus Select | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_33_031` | Timbre12 · Use Drum Kit Bus Setting | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_33_032` | Timbre12 · Rec Bus | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 33 | `kkC_33_033` | Timbre12 · Chord Source | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| Pad 8 | combi | combi |
| 34 | `kkC_33_034` | Timbre12 · Max # of Notes | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 16 | combi | combi |
| 35 | `kkC_33_035` | Timbre12 · Chord Mode | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Program \| 1 \| 2 \| Advanced | combi | combi |
| 36 | `kkC_33_036` | Timbre12 · (Filter) Program Change | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Disable \| Enable | combi | combi |
| 37 | `kkC_33_037` | Timbre12 · (Filter) After Touch | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Disable \| Enable | combi | combi |
| 38 | `kkC_33_038` | Timbre12 · (Filter) Damper | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Disable \| Enable | combi | combi |
| 39 | `kkC_33_039` | Timbre12 · (Filter) Portamento | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Disable \| Enable | combi | combi |
| 40 | `kkC_33_040` | Timbre12 · (Filter) JSX As Mod. | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Disable \| Enable | combi | combi |
| 41 | `kkC_33_041` | Timbre12 · (Filter) JS+Y | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Disable \| Enable | combi | combi |
| 42 | `kkC_33_042` | Timbre12 · (Filter) JS-Y | `(154, 312, 146)` | combo `(154, 325)` 146x20 | Disable \| Enable | combi | combi |
| 43 | `kkC_33_043` | Timbre12 · (Filter) Ribbon | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Disable \| Enable | combi | combi |
| 44 | `kkC_33_044` | Timbre12 · (Filter) Knob1 | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Disable \| Enable | combi | combi |
| 45 | `kkC_33_045` | Timbre12 · (Filter) Knob2 | `(601, 312, 146)` | combo `(601, 325)` 146x20 | Disable \| Enable | combi | combi |
| 46 | `kkC_33_046` | Timbre12 · (Filter) Knob3 | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Disable \| Enable | combi | combi |
| 47 | `kkC_33_047` | Timbre12 · (Filter) Knob4 | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Disable \| Enable | combi | combi |
| 48 | `kkC_33_048` | Timbre12 · (Filter) Knob5 | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Disable \| Enable | combi | combi |
| 49 | `kkC_33_049` | Timbre12 · (Filter) Knob6 | `(1197, 312, 146)` | combo `(1197, 325)` 146x20 | Disable \| Enable | combi | combi |
| 50 | `kkC_33_050` | Timbre12 · (Filter) Knob7 | `(1346, 312, 146)` | combo `(1346, 325)` 146x20 | Disable \| Enable | combi | combi |
| 51 | `kkC_33_051` | Timbre12 · (Filter) Knob8 | `(5, 361, 146)` | combo `(5, 374)` 146x20 | Disable \| Enable | combi | combi |
| 52 | `kkC_33_052` | Timbre12 · (Filter) Switch1 | `(154, 361, 146)` | combo `(154, 374)` 146x20 | Disable \| Enable | combi | combi |
| 53 | `kkC_33_053` | Timbre12 · (Filter) Switch2 | `(303, 361, 146)` | combo `(303, 374)` 146x20 | Disable \| Enable | combi | combi |
| 54 | `kkC_33_054` | Timbre12 · (Filter) Foot Switch | `(452, 361, 146)` | combo `(452, 374)` 146x20 | Disable \| Enable | combi | combi |
| 55 | `kkC_33_055` | Timbre12 · (Filter) Foot Pedal | `(601, 361, 146)` | combo `(601, 374)` 146x20 | Disable \| Enable | combi | combi |
| 56 | `kkC_33_056` | Timbre12 · (Filter) Other CC# | `(750, 361, 146)` | combo `(750, 374)` 146x20 | Disable \| Enable | combi | combi |
| 57 | `kkC_33_057` | Timbre12 · Use Program Scale | `(899, 361, 146)` | combo `(899, 374)` 146x20 | Off \| On | combi | combi |
| 58 | `kkC_33_058` | Timbre12 · Auto Load Program EQ | `(1048, 361, 146)` | combo `(1048, 374)` 146x20 | Off \| On | combi | combi |
| 59 | `kkC_33_059` | Timbre12 · Mute | `(1197, 361, 146)` | combo `(1197, 374)` 146x20 | Off \| On | combi | combi |
| 60 | `kkC_33_060` | Timbre12 · Osc Mode | `(1346, 361, 146)` | combo `(1346, 374)` 146x20 | Program \| 1 \| 2 \| Mono Legato | combi | combi |

#### Tab 34 - Timbre 12·2 (43 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_34_001` | Timbre12 · Osc Select | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Both \| 1 \| OSC2 | combi | combi |
| 2 | `kkC_34_002` | Timbre12 · Timbre Priority | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | combi | combi |
| 3 | `kkC_34_003` | Timbre12 · Osc On/Off By KARMA | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Normal \| 1 \| Osc Off by K | combi | combi |
| 4 | `kkC_34_004` | Timbre12 · (Filter) Waveform SysEx | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Disable \| Enable | combi | combi |
| 5 | `kkC_34_005` | Timbre12 · Key Window Top | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_34_006` | Timbre12 · Key Window Bottom | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_34_007` | Timbre12 · Vel.Window High | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_34_008` | Timbre12 · Vel.Window Low | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_34_009` | Timbre12 · Vel.Window High Slope | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 10 | `kkC_34_010` | Timbre12 · Vel.Window Low Slope | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 11 | `kkC_34_011` | Timbre12 · Quantize Trigger | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 12 | `kkC_34_012` | Timbre12 · Key Sync | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 13 | `kkC_34_013` | Timbre12 · (Track EQ) Trim | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_34_014` | Timbre12 · (Track EQ) Bypass | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_34_015` | Timbre12 · (Track EQ) Mid Frequency | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..165 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_34_016` | Timbre12 · (Track EQ) Low Gain | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 17 | `kkC_34_017` | Timbre12 · (Track EQ) Mid Gain | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 18 | `kkC_34_018` | Timbre12 · (Track EQ) High Gain | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 19 | `kkC_34_019` | Timbre12 · VJS Assign | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| -Y | combi | combi |
| 20 | `kkC_34_020` | Timbre12 · Volume Center | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..100 step 25.0 (0 dec) | combi | combi |
| 21 | `kkC_34_021` | Timbre12 · Program Vector Volume | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Off \| On | combi | combi |
| 22 | `kkC_34_022` | Timbre12 · Combi Vector CC | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| On | combi | combi |
| 23 | `kkC_34_023` | Timbre12 · Program Vector CC | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| On | combi | combi |
| 24 | `kkC_34_024` | Timbre12 · Switch1 Value | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | combi | combi |
| 25 | `kkC_34_025` | Timbre12 · Switch2 Value | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_34_026` | Timbre12 · Switch3 Value | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | combi | combi |
| 27 | `kkC_34_027` | Timbre12 · Switch4 Value | `(899, 214, 146)` | combo `(899, 227)` 146x20 | Off \| On | combi | combi |
| 28 | `kkC_34_028` | Timbre12 · Switch5 Value | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | Off \| On | combi | combi |
| 29 | `kkC_34_029` | Timbre12 · Switch6 Value | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| On | combi | combi |
| 30 | `kkC_34_030` | Timbre12 · Switch7 Value | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| On | combi | combi |
| 31 | `kkC_34_031` | Timbre12 · Switch8 Value | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_34_032` | Timbre12 · Switch9 Value | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | combi | combi |
| 33 | `kkC_34_033` | Timbre12 · Switch10 Value | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Off \| On | combi | combi |
| 34 | `kkC_34_034` | Timbre12 · Switch11 Value | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Off \| On | combi | combi |
| 35 | `kkC_34_035` | Timbre12 · Switch12 Value | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | combi | combi |
| 36 | `kkC_34_036` | Timbre12 · Switch13 Value | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Off \| On | combi | combi |
| 37 | `kkC_34_037` | Timbre12 · Switch14 Value | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Off \| On | combi | combi |
| 38 | `kkC_34_038` | Timbre12 · Switch15 Value | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| On | combi | combi |
| 39 | `kkC_34_039` | Timbre12 · Switch16 Value | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Off \| On | combi | combi |
| 40 | `kkC_34_040` | Timbre12 · EXi1 Input Source Bus | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 41 | `kkC_34_041` | Timbre12 · EXi1 Input Source Channel | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |
| 42 | `kkC_34_042` | Timbre12 · EXi2 Input Source Bus | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_34_043` | Timbre12 · EXi2 Input Source Channel | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |

#### Tab 35 - Timbre 13 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_35_001` | Timbre13 · Program Number | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 2 | `kkC_35_002` | Timbre13 · Bank Number | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..30 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_35_003` | Timbre13 · MIDI Channel | `(303, 116, 146)` | combo `(303, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 4 | `kkC_35_004` | Timbre13 · Status | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| External2 | combi | combi |
| 5 | `kkC_35_005` | Timbre13 · Bank MSB | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_35_006` | Timbre13 · Bank LSB | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_35_007` | Timbre13 · Volume | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_35_008` | Timbre13 · Transpose | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -60..60 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_35_009` | Timbre13 · Detune | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_35_010` | Timbre13 · Delay Time | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..6001 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_35_011` | Timbre13 · Delay Tempo Base Note | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 12 | `kkC_35_012` | Timbre13 · Delay Mode | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | combi | combi |
| 13 | `kkC_35_013` | Timbre13 · Delay Tempo Times | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_35_014` | Timbre13 · Pan | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_35_015` | Timbre13 · Send1 | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_35_016` | Timbre13 · Send2 | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_35_017` | Timbre13 · Drum Kit Patch IFX1 | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_35_018` | Timbre13 · Drum Kit Patch IFX2 | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 19 | `kkC_35_019` | Timbre13 · Drum Kit Patch IFX3 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 20 | `kkC_35_020` | Timbre13 · Drum Kit Patch IFX4 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_35_021` | Timbre13 · Drum Kit Patch IFX5 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_35_022` | Timbre13 · Drum Kit Patch IFX6 | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 23 | `kkC_35_023` | Timbre13 · Drum Kit Patch IFX7 | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 24 | `kkC_35_024` | Timbre13 · Drum Kit Patch IFX8 | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 25 | `kkC_35_025` | Timbre13 · Drum Kit Patch IFX9 | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 26 | `kkC_35_026` | Timbre13 · Drum Kit Patch IFX10 | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 27 | `kkC_35_027` | Timbre13 · Drum Kit Patch IFX11 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_35_028` | Timbre13 · Drum Kit Patch IFX12 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_35_029` | Timbre13 · Bus Select | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 30 | `kkC_35_030` | Timbre13 · Fx Bus Select | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_35_031` | Timbre13 · Use Drum Kit Bus Setting | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_35_032` | Timbre13 · Rec Bus | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 33 | `kkC_35_033` | Timbre13 · Chord Source | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| Pad 8 | combi | combi |
| 34 | `kkC_35_034` | Timbre13 · Max # of Notes | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 16 | combi | combi |
| 35 | `kkC_35_035` | Timbre13 · Chord Mode | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Program \| 1 \| 2 \| Advanced | combi | combi |
| 36 | `kkC_35_036` | Timbre13 · (Filter) Program Change | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Disable \| Enable | combi | combi |
| 37 | `kkC_35_037` | Timbre13 · (Filter) After Touch | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Disable \| Enable | combi | combi |
| 38 | `kkC_35_038` | Timbre13 · (Filter) Damper | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Disable \| Enable | combi | combi |
| 39 | `kkC_35_039` | Timbre13 · (Filter) Portamento | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Disable \| Enable | combi | combi |
| 40 | `kkC_35_040` | Timbre13 · (Filter) JSX As Mod. | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Disable \| Enable | combi | combi |
| 41 | `kkC_35_041` | Timbre13 · (Filter) JS+Y | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Disable \| Enable | combi | combi |
| 42 | `kkC_35_042` | Timbre13 · (Filter) JS-Y | `(154, 312, 146)` | combo `(154, 325)` 146x20 | Disable \| Enable | combi | combi |
| 43 | `kkC_35_043` | Timbre13 · (Filter) Ribbon | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Disable \| Enable | combi | combi |
| 44 | `kkC_35_044` | Timbre13 · (Filter) Knob1 | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Disable \| Enable | combi | combi |
| 45 | `kkC_35_045` | Timbre13 · (Filter) Knob2 | `(601, 312, 146)` | combo `(601, 325)` 146x20 | Disable \| Enable | combi | combi |
| 46 | `kkC_35_046` | Timbre13 · (Filter) Knob3 | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Disable \| Enable | combi | combi |
| 47 | `kkC_35_047` | Timbre13 · (Filter) Knob4 | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Disable \| Enable | combi | combi |
| 48 | `kkC_35_048` | Timbre13 · (Filter) Knob5 | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Disable \| Enable | combi | combi |
| 49 | `kkC_35_049` | Timbre13 · (Filter) Knob6 | `(1197, 312, 146)` | combo `(1197, 325)` 146x20 | Disable \| Enable | combi | combi |
| 50 | `kkC_35_050` | Timbre13 · (Filter) Knob7 | `(1346, 312, 146)` | combo `(1346, 325)` 146x20 | Disable \| Enable | combi | combi |
| 51 | `kkC_35_051` | Timbre13 · (Filter) Knob8 | `(5, 361, 146)` | combo `(5, 374)` 146x20 | Disable \| Enable | combi | combi |
| 52 | `kkC_35_052` | Timbre13 · (Filter) Switch1 | `(154, 361, 146)` | combo `(154, 374)` 146x20 | Disable \| Enable | combi | combi |
| 53 | `kkC_35_053` | Timbre13 · (Filter) Switch2 | `(303, 361, 146)` | combo `(303, 374)` 146x20 | Disable \| Enable | combi | combi |
| 54 | `kkC_35_054` | Timbre13 · (Filter) Foot Switch | `(452, 361, 146)` | combo `(452, 374)` 146x20 | Disable \| Enable | combi | combi |
| 55 | `kkC_35_055` | Timbre13 · (Filter) Foot Pedal | `(601, 361, 146)` | combo `(601, 374)` 146x20 | Disable \| Enable | combi | combi |
| 56 | `kkC_35_056` | Timbre13 · (Filter) Other CC# | `(750, 361, 146)` | combo `(750, 374)` 146x20 | Disable \| Enable | combi | combi |
| 57 | `kkC_35_057` | Timbre13 · Use Program Scale | `(899, 361, 146)` | combo `(899, 374)` 146x20 | Off \| On | combi | combi |
| 58 | `kkC_35_058` | Timbre13 · Auto Load Program EQ | `(1048, 361, 146)` | combo `(1048, 374)` 146x20 | Off \| On | combi | combi |
| 59 | `kkC_35_059` | Timbre13 · Mute | `(1197, 361, 146)` | combo `(1197, 374)` 146x20 | Off \| On | combi | combi |
| 60 | `kkC_35_060` | Timbre13 · Osc Mode | `(1346, 361, 146)` | combo `(1346, 374)` 146x20 | Program \| 1 \| 2 \| Mono Legato | combi | combi |

#### Tab 36 - Timbre 13·2 (43 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_36_001` | Timbre13 · Osc Select | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Both \| 1 \| OSC2 | combi | combi |
| 2 | `kkC_36_002` | Timbre13 · Timbre Priority | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | combi | combi |
| 3 | `kkC_36_003` | Timbre13 · Osc On/Off By KARMA | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Normal \| 1 \| Osc Off by K | combi | combi |
| 4 | `kkC_36_004` | Timbre13 · (Filter) Waveform SysEx | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Disable \| Enable | combi | combi |
| 5 | `kkC_36_005` | Timbre13 · Key Window Top | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_36_006` | Timbre13 · Key Window Bottom | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_36_007` | Timbre13 · Vel.Window High | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_36_008` | Timbre13 · Vel.Window Low | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_36_009` | Timbre13 · Vel.Window High Slope | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 10 | `kkC_36_010` | Timbre13 · Vel.Window Low Slope | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 11 | `kkC_36_011` | Timbre13 · Quantize Trigger | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 12 | `kkC_36_012` | Timbre13 · Key Sync | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 13 | `kkC_36_013` | Timbre13 · (Track EQ) Trim | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_36_014` | Timbre13 · (Track EQ) Bypass | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_36_015` | Timbre13 · (Track EQ) Mid Frequency | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..165 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_36_016` | Timbre13 · (Track EQ) Low Gain | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 17 | `kkC_36_017` | Timbre13 · (Track EQ) Mid Gain | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 18 | `kkC_36_018` | Timbre13 · (Track EQ) High Gain | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 19 | `kkC_36_019` | Timbre13 · VJS Assign | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| -Y | combi | combi |
| 20 | `kkC_36_020` | Timbre13 · Volume Center | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..100 step 25.0 (0 dec) | combi | combi |
| 21 | `kkC_36_021` | Timbre13 · Program Vector Volume | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Off \| On | combi | combi |
| 22 | `kkC_36_022` | Timbre13 · Combi Vector CC | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| On | combi | combi |
| 23 | `kkC_36_023` | Timbre13 · Program Vector CC | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| On | combi | combi |
| 24 | `kkC_36_024` | Timbre13 · Switch1 Value | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | combi | combi |
| 25 | `kkC_36_025` | Timbre13 · Switch2 Value | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_36_026` | Timbre13 · Switch3 Value | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | combi | combi |
| 27 | `kkC_36_027` | Timbre13 · Switch4 Value | `(899, 214, 146)` | combo `(899, 227)` 146x20 | Off \| On | combi | combi |
| 28 | `kkC_36_028` | Timbre13 · Switch5 Value | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | Off \| On | combi | combi |
| 29 | `kkC_36_029` | Timbre13 · Switch6 Value | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| On | combi | combi |
| 30 | `kkC_36_030` | Timbre13 · Switch7 Value | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| On | combi | combi |
| 31 | `kkC_36_031` | Timbre13 · Switch8 Value | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_36_032` | Timbre13 · Switch9 Value | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | combi | combi |
| 33 | `kkC_36_033` | Timbre13 · Switch10 Value | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Off \| On | combi | combi |
| 34 | `kkC_36_034` | Timbre13 · Switch11 Value | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Off \| On | combi | combi |
| 35 | `kkC_36_035` | Timbre13 · Switch12 Value | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | combi | combi |
| 36 | `kkC_36_036` | Timbre13 · Switch13 Value | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Off \| On | combi | combi |
| 37 | `kkC_36_037` | Timbre13 · Switch14 Value | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Off \| On | combi | combi |
| 38 | `kkC_36_038` | Timbre13 · Switch15 Value | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| On | combi | combi |
| 39 | `kkC_36_039` | Timbre13 · Switch16 Value | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Off \| On | combi | combi |
| 40 | `kkC_36_040` | Timbre13 · EXi1 Input Source Bus | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 41 | `kkC_36_041` | Timbre13 · EXi1 Input Source Channel | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |
| 42 | `kkC_36_042` | Timbre13 · EXi2 Input Source Bus | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_36_043` | Timbre13 · EXi2 Input Source Channel | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |

#### Tab 37 - Timbre 14 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_37_001` | Timbre14 · Program Number | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 2 | `kkC_37_002` | Timbre14 · Bank Number | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..30 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_37_003` | Timbre14 · MIDI Channel | `(303, 116, 146)` | combo `(303, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 4 | `kkC_37_004` | Timbre14 · Status | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| External2 | combi | combi |
| 5 | `kkC_37_005` | Timbre14 · Bank MSB | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_37_006` | Timbre14 · Bank LSB | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_37_007` | Timbre14 · Volume | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_37_008` | Timbre14 · Transpose | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -60..60 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_37_009` | Timbre14 · Detune | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_37_010` | Timbre14 · Delay Time | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..6001 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_37_011` | Timbre14 · Delay Tempo Base Note | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 12 | `kkC_37_012` | Timbre14 · Delay Mode | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | combi | combi |
| 13 | `kkC_37_013` | Timbre14 · Delay Tempo Times | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_37_014` | Timbre14 · Pan | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_37_015` | Timbre14 · Send1 | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_37_016` | Timbre14 · Send2 | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_37_017` | Timbre14 · Drum Kit Patch IFX1 | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_37_018` | Timbre14 · Drum Kit Patch IFX2 | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 19 | `kkC_37_019` | Timbre14 · Drum Kit Patch IFX3 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 20 | `kkC_37_020` | Timbre14 · Drum Kit Patch IFX4 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_37_021` | Timbre14 · Drum Kit Patch IFX5 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_37_022` | Timbre14 · Drum Kit Patch IFX6 | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 23 | `kkC_37_023` | Timbre14 · Drum Kit Patch IFX7 | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 24 | `kkC_37_024` | Timbre14 · Drum Kit Patch IFX8 | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 25 | `kkC_37_025` | Timbre14 · Drum Kit Patch IFX9 | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 26 | `kkC_37_026` | Timbre14 · Drum Kit Patch IFX10 | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 27 | `kkC_37_027` | Timbre14 · Drum Kit Patch IFX11 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_37_028` | Timbre14 · Drum Kit Patch IFX12 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_37_029` | Timbre14 · Bus Select | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 30 | `kkC_37_030` | Timbre14 · Fx Bus Select | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_37_031` | Timbre14 · Use Drum Kit Bus Setting | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_37_032` | Timbre14 · Rec Bus | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 33 | `kkC_37_033` | Timbre14 · Chord Source | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| Pad 8 | combi | combi |
| 34 | `kkC_37_034` | Timbre14 · Max # of Notes | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 16 | combi | combi |
| 35 | `kkC_37_035` | Timbre14 · Chord Mode | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Program \| 1 \| 2 \| Advanced | combi | combi |
| 36 | `kkC_37_036` | Timbre14 · (Filter) Program Change | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Disable \| Enable | combi | combi |
| 37 | `kkC_37_037` | Timbre14 · (Filter) After Touch | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Disable \| Enable | combi | combi |
| 38 | `kkC_37_038` | Timbre14 · (Filter) Damper | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Disable \| Enable | combi | combi |
| 39 | `kkC_37_039` | Timbre14 · (Filter) Portamento | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Disable \| Enable | combi | combi |
| 40 | `kkC_37_040` | Timbre14 · (Filter) JSX As Mod. | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Disable \| Enable | combi | combi |
| 41 | `kkC_37_041` | Timbre14 · (Filter) JS+Y | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Disable \| Enable | combi | combi |
| 42 | `kkC_37_042` | Timbre14 · (Filter) JS-Y | `(154, 312, 146)` | combo `(154, 325)` 146x20 | Disable \| Enable | combi | combi |
| 43 | `kkC_37_043` | Timbre14 · (Filter) Ribbon | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Disable \| Enable | combi | combi |
| 44 | `kkC_37_044` | Timbre14 · (Filter) Knob1 | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Disable \| Enable | combi | combi |
| 45 | `kkC_37_045` | Timbre14 · (Filter) Knob2 | `(601, 312, 146)` | combo `(601, 325)` 146x20 | Disable \| Enable | combi | combi |
| 46 | `kkC_37_046` | Timbre14 · (Filter) Knob3 | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Disable \| Enable | combi | combi |
| 47 | `kkC_37_047` | Timbre14 · (Filter) Knob4 | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Disable \| Enable | combi | combi |
| 48 | `kkC_37_048` | Timbre14 · (Filter) Knob5 | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Disable \| Enable | combi | combi |
| 49 | `kkC_37_049` | Timbre14 · (Filter) Knob6 | `(1197, 312, 146)` | combo `(1197, 325)` 146x20 | Disable \| Enable | combi | combi |
| 50 | `kkC_37_050` | Timbre14 · (Filter) Knob7 | `(1346, 312, 146)` | combo `(1346, 325)` 146x20 | Disable \| Enable | combi | combi |
| 51 | `kkC_37_051` | Timbre14 · (Filter) Knob8 | `(5, 361, 146)` | combo `(5, 374)` 146x20 | Disable \| Enable | combi | combi |
| 52 | `kkC_37_052` | Timbre14 · (Filter) Switch1 | `(154, 361, 146)` | combo `(154, 374)` 146x20 | Disable \| Enable | combi | combi |
| 53 | `kkC_37_053` | Timbre14 · (Filter) Switch2 | `(303, 361, 146)` | combo `(303, 374)` 146x20 | Disable \| Enable | combi | combi |
| 54 | `kkC_37_054` | Timbre14 · (Filter) Foot Switch | `(452, 361, 146)` | combo `(452, 374)` 146x20 | Disable \| Enable | combi | combi |
| 55 | `kkC_37_055` | Timbre14 · (Filter) Foot Pedal | `(601, 361, 146)` | combo `(601, 374)` 146x20 | Disable \| Enable | combi | combi |
| 56 | `kkC_37_056` | Timbre14 · (Filter) Other CC# | `(750, 361, 146)` | combo `(750, 374)` 146x20 | Disable \| Enable | combi | combi |
| 57 | `kkC_37_057` | Timbre14 · Use Program Scale | `(899, 361, 146)` | combo `(899, 374)` 146x20 | Off \| On | combi | combi |
| 58 | `kkC_37_058` | Timbre14 · Auto Load Program EQ | `(1048, 361, 146)` | combo `(1048, 374)` 146x20 | Off \| On | combi | combi |
| 59 | `kkC_37_059` | Timbre14 · Mute | `(1197, 361, 146)` | combo `(1197, 374)` 146x20 | Off \| On | combi | combi |
| 60 | `kkC_37_060` | Timbre14 · Osc Mode | `(1346, 361, 146)` | combo `(1346, 374)` 146x20 | Program \| 1 \| 2 \| Mono Legato | combi | combi |

#### Tab 38 - Timbre 14·2 (43 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_38_001` | Timbre14 · Osc Select | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Both \| 1 \| OSC2 | combi | combi |
| 2 | `kkC_38_002` | Timbre14 · Timbre Priority | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | combi | combi |
| 3 | `kkC_38_003` | Timbre14 · Osc On/Off By KARMA | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Normal \| 1 \| Osc Off by K | combi | combi |
| 4 | `kkC_38_004` | Timbre14 · (Filter) Waveform SysEx | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Disable \| Enable | combi | combi |
| 5 | `kkC_38_005` | Timbre14 · Key Window Top | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_38_006` | Timbre14 · Key Window Bottom | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_38_007` | Timbre14 · Vel.Window High | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_38_008` | Timbre14 · Vel.Window Low | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_38_009` | Timbre14 · Vel.Window High Slope | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 10 | `kkC_38_010` | Timbre14 · Vel.Window Low Slope | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 11 | `kkC_38_011` | Timbre14 · Quantize Trigger | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 12 | `kkC_38_012` | Timbre14 · Key Sync | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 13 | `kkC_38_013` | Timbre14 · (Track EQ) Trim | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_38_014` | Timbre14 · (Track EQ) Bypass | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_38_015` | Timbre14 · (Track EQ) Mid Frequency | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..165 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_38_016` | Timbre14 · (Track EQ) Low Gain | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 17 | `kkC_38_017` | Timbre14 · (Track EQ) Mid Gain | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 18 | `kkC_38_018` | Timbre14 · (Track EQ) High Gain | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 19 | `kkC_38_019` | Timbre14 · VJS Assign | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| -Y | combi | combi |
| 20 | `kkC_38_020` | Timbre14 · Volume Center | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..100 step 25.0 (0 dec) | combi | combi |
| 21 | `kkC_38_021` | Timbre14 · Program Vector Volume | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Off \| On | combi | combi |
| 22 | `kkC_38_022` | Timbre14 · Combi Vector CC | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| On | combi | combi |
| 23 | `kkC_38_023` | Timbre14 · Program Vector CC | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| On | combi | combi |
| 24 | `kkC_38_024` | Timbre14 · Switch1 Value | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | combi | combi |
| 25 | `kkC_38_025` | Timbre14 · Switch2 Value | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_38_026` | Timbre14 · Switch3 Value | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | combi | combi |
| 27 | `kkC_38_027` | Timbre14 · Switch4 Value | `(899, 214, 146)` | combo `(899, 227)` 146x20 | Off \| On | combi | combi |
| 28 | `kkC_38_028` | Timbre14 · Switch5 Value | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | Off \| On | combi | combi |
| 29 | `kkC_38_029` | Timbre14 · Switch6 Value | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| On | combi | combi |
| 30 | `kkC_38_030` | Timbre14 · Switch7 Value | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| On | combi | combi |
| 31 | `kkC_38_031` | Timbre14 · Switch8 Value | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_38_032` | Timbre14 · Switch9 Value | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | combi | combi |
| 33 | `kkC_38_033` | Timbre14 · Switch10 Value | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Off \| On | combi | combi |
| 34 | `kkC_38_034` | Timbre14 · Switch11 Value | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Off \| On | combi | combi |
| 35 | `kkC_38_035` | Timbre14 · Switch12 Value | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | combi | combi |
| 36 | `kkC_38_036` | Timbre14 · Switch13 Value | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Off \| On | combi | combi |
| 37 | `kkC_38_037` | Timbre14 · Switch14 Value | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Off \| On | combi | combi |
| 38 | `kkC_38_038` | Timbre14 · Switch15 Value | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| On | combi | combi |
| 39 | `kkC_38_039` | Timbre14 · Switch16 Value | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Off \| On | combi | combi |
| 40 | `kkC_38_040` | Timbre14 · EXi1 Input Source Bus | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 41 | `kkC_38_041` | Timbre14 · EXi1 Input Source Channel | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |
| 42 | `kkC_38_042` | Timbre14 · EXi2 Input Source Bus | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_38_043` | Timbre14 · EXi2 Input Source Channel | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |

#### Tab 39 - Timbre 15 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_39_001` | Timbre15 · Program Number | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 2 | `kkC_39_002` | Timbre15 · Bank Number | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..30 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_39_003` | Timbre15 · MIDI Channel | `(303, 116, 146)` | combo `(303, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 4 | `kkC_39_004` | Timbre15 · Status | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| External2 | combi | combi |
| 5 | `kkC_39_005` | Timbre15 · Bank MSB | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_39_006` | Timbre15 · Bank LSB | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_39_007` | Timbre15 · Volume | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_39_008` | Timbre15 · Transpose | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -60..60 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_39_009` | Timbre15 · Detune | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_39_010` | Timbre15 · Delay Time | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..6001 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_39_011` | Timbre15 · Delay Tempo Base Note | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 12 | `kkC_39_012` | Timbre15 · Delay Mode | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | combi | combi |
| 13 | `kkC_39_013` | Timbre15 · Delay Tempo Times | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_39_014` | Timbre15 · Pan | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_39_015` | Timbre15 · Send1 | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_39_016` | Timbre15 · Send2 | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_39_017` | Timbre15 · Drum Kit Patch IFX1 | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_39_018` | Timbre15 · Drum Kit Patch IFX2 | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 19 | `kkC_39_019` | Timbre15 · Drum Kit Patch IFX3 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 20 | `kkC_39_020` | Timbre15 · Drum Kit Patch IFX4 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_39_021` | Timbre15 · Drum Kit Patch IFX5 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_39_022` | Timbre15 · Drum Kit Patch IFX6 | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 23 | `kkC_39_023` | Timbre15 · Drum Kit Patch IFX7 | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 24 | `kkC_39_024` | Timbre15 · Drum Kit Patch IFX8 | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 25 | `kkC_39_025` | Timbre15 · Drum Kit Patch IFX9 | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 26 | `kkC_39_026` | Timbre15 · Drum Kit Patch IFX10 | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 27 | `kkC_39_027` | Timbre15 · Drum Kit Patch IFX11 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_39_028` | Timbre15 · Drum Kit Patch IFX12 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_39_029` | Timbre15 · Bus Select | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 30 | `kkC_39_030` | Timbre15 · Fx Bus Select | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_39_031` | Timbre15 · Use Drum Kit Bus Setting | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_39_032` | Timbre15 · Rec Bus | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 33 | `kkC_39_033` | Timbre15 · Chord Source | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| Pad 8 | combi | combi |
| 34 | `kkC_39_034` | Timbre15 · Max # of Notes | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 16 | combi | combi |
| 35 | `kkC_39_035` | Timbre15 · Chord Mode | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Program \| 1 \| 2 \| Advanced | combi | combi |
| 36 | `kkC_39_036` | Timbre15 · (Filter) Program Change | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Disable \| Enable | combi | combi |
| 37 | `kkC_39_037` | Timbre15 · (Filter) After Touch | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Disable \| Enable | combi | combi |
| 38 | `kkC_39_038` | Timbre15 · (Filter) Damper | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Disable \| Enable | combi | combi |
| 39 | `kkC_39_039` | Timbre15 · (Filter) Portamento | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Disable \| Enable | combi | combi |
| 40 | `kkC_39_040` | Timbre15 · (Filter) JSX As Mod. | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Disable \| Enable | combi | combi |
| 41 | `kkC_39_041` | Timbre15 · (Filter) JS+Y | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Disable \| Enable | combi | combi |
| 42 | `kkC_39_042` | Timbre15 · (Filter) JS-Y | `(154, 312, 146)` | combo `(154, 325)` 146x20 | Disable \| Enable | combi | combi |
| 43 | `kkC_39_043` | Timbre15 · (Filter) Ribbon | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Disable \| Enable | combi | combi |
| 44 | `kkC_39_044` | Timbre15 · (Filter) Knob1 | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Disable \| Enable | combi | combi |
| 45 | `kkC_39_045` | Timbre15 · (Filter) Knob2 | `(601, 312, 146)` | combo `(601, 325)` 146x20 | Disable \| Enable | combi | combi |
| 46 | `kkC_39_046` | Timbre15 · (Filter) Knob3 | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Disable \| Enable | combi | combi |
| 47 | `kkC_39_047` | Timbre15 · (Filter) Knob4 | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Disable \| Enable | combi | combi |
| 48 | `kkC_39_048` | Timbre15 · (Filter) Knob5 | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Disable \| Enable | combi | combi |
| 49 | `kkC_39_049` | Timbre15 · (Filter) Knob6 | `(1197, 312, 146)` | combo `(1197, 325)` 146x20 | Disable \| Enable | combi | combi |
| 50 | `kkC_39_050` | Timbre15 · (Filter) Knob7 | `(1346, 312, 146)` | combo `(1346, 325)` 146x20 | Disable \| Enable | combi | combi |
| 51 | `kkC_39_051` | Timbre15 · (Filter) Knob8 | `(5, 361, 146)` | combo `(5, 374)` 146x20 | Disable \| Enable | combi | combi |
| 52 | `kkC_39_052` | Timbre15 · (Filter) Switch1 | `(154, 361, 146)` | combo `(154, 374)` 146x20 | Disable \| Enable | combi | combi |
| 53 | `kkC_39_053` | Timbre15 · (Filter) Switch2 | `(303, 361, 146)` | combo `(303, 374)` 146x20 | Disable \| Enable | combi | combi |
| 54 | `kkC_39_054` | Timbre15 · (Filter) Foot Switch | `(452, 361, 146)` | combo `(452, 374)` 146x20 | Disable \| Enable | combi | combi |
| 55 | `kkC_39_055` | Timbre15 · (Filter) Foot Pedal | `(601, 361, 146)` | combo `(601, 374)` 146x20 | Disable \| Enable | combi | combi |
| 56 | `kkC_39_056` | Timbre15 · (Filter) Other CC# | `(750, 361, 146)` | combo `(750, 374)` 146x20 | Disable \| Enable | combi | combi |
| 57 | `kkC_39_057` | Timbre15 · Use Program Scale | `(899, 361, 146)` | combo `(899, 374)` 146x20 | Off \| On | combi | combi |
| 58 | `kkC_39_058` | Timbre15 · Auto Load Program EQ | `(1048, 361, 146)` | combo `(1048, 374)` 146x20 | Off \| On | combi | combi |
| 59 | `kkC_39_059` | Timbre15 · Mute | `(1197, 361, 146)` | combo `(1197, 374)` 146x20 | Off \| On | combi | combi |
| 60 | `kkC_39_060` | Timbre15 · Osc Mode | `(1346, 361, 146)` | combo `(1346, 374)` 146x20 | Program \| 1 \| 2 \| Mono Legato | combi | combi |

#### Tab 40 - Timbre 15·2 (43 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_40_001` | Timbre15 · Osc Select | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Both \| 1 \| OSC2 | combi | combi |
| 2 | `kkC_40_002` | Timbre15 · Timbre Priority | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | combi | combi |
| 3 | `kkC_40_003` | Timbre15 · Osc On/Off By KARMA | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Normal \| 1 \| Osc Off by K | combi | combi |
| 4 | `kkC_40_004` | Timbre15 · (Filter) Waveform SysEx | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Disable \| Enable | combi | combi |
| 5 | `kkC_40_005` | Timbre15 · Key Window Top | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_40_006` | Timbre15 · Key Window Bottom | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_40_007` | Timbre15 · Vel.Window High | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_40_008` | Timbre15 · Vel.Window Low | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_40_009` | Timbre15 · Vel.Window High Slope | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 10 | `kkC_40_010` | Timbre15 · Vel.Window Low Slope | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 11 | `kkC_40_011` | Timbre15 · Quantize Trigger | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 12 | `kkC_40_012` | Timbre15 · Key Sync | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 13 | `kkC_40_013` | Timbre15 · (Track EQ) Trim | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_40_014` | Timbre15 · (Track EQ) Bypass | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_40_015` | Timbre15 · (Track EQ) Mid Frequency | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..165 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_40_016` | Timbre15 · (Track EQ) Low Gain | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 17 | `kkC_40_017` | Timbre15 · (Track EQ) Mid Gain | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 18 | `kkC_40_018` | Timbre15 · (Track EQ) High Gain | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 19 | `kkC_40_019` | Timbre15 · VJS Assign | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| -Y | combi | combi |
| 20 | `kkC_40_020` | Timbre15 · Volume Center | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..100 step 25.0 (0 dec) | combi | combi |
| 21 | `kkC_40_021` | Timbre15 · Program Vector Volume | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Off \| On | combi | combi |
| 22 | `kkC_40_022` | Timbre15 · Combi Vector CC | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| On | combi | combi |
| 23 | `kkC_40_023` | Timbre15 · Program Vector CC | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| On | combi | combi |
| 24 | `kkC_40_024` | Timbre15 · Switch1 Value | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | combi | combi |
| 25 | `kkC_40_025` | Timbre15 · Switch2 Value | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_40_026` | Timbre15 · Switch3 Value | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | combi | combi |
| 27 | `kkC_40_027` | Timbre15 · Switch4 Value | `(899, 214, 146)` | combo `(899, 227)` 146x20 | Off \| On | combi | combi |
| 28 | `kkC_40_028` | Timbre15 · Switch5 Value | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | Off \| On | combi | combi |
| 29 | `kkC_40_029` | Timbre15 · Switch6 Value | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| On | combi | combi |
| 30 | `kkC_40_030` | Timbre15 · Switch7 Value | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| On | combi | combi |
| 31 | `kkC_40_031` | Timbre15 · Switch8 Value | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_40_032` | Timbre15 · Switch9 Value | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | combi | combi |
| 33 | `kkC_40_033` | Timbre15 · Switch10 Value | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Off \| On | combi | combi |
| 34 | `kkC_40_034` | Timbre15 · Switch11 Value | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Off \| On | combi | combi |
| 35 | `kkC_40_035` | Timbre15 · Switch12 Value | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | combi | combi |
| 36 | `kkC_40_036` | Timbre15 · Switch13 Value | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Off \| On | combi | combi |
| 37 | `kkC_40_037` | Timbre15 · Switch14 Value | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Off \| On | combi | combi |
| 38 | `kkC_40_038` | Timbre15 · Switch15 Value | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| On | combi | combi |
| 39 | `kkC_40_039` | Timbre15 · Switch16 Value | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Off \| On | combi | combi |
| 40 | `kkC_40_040` | Timbre15 · EXi1 Input Source Bus | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 41 | `kkC_40_041` | Timbre15 · EXi1 Input Source Channel | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |
| 42 | `kkC_40_042` | Timbre15 · EXi2 Input Source Bus | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_40_043` | Timbre15 · EXi2 Input Source Channel | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |

#### Tab 41 - Timbre 16 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_41_001` | Timbre16 · Program Number | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 2 | `kkC_41_002` | Timbre16 · Bank Number | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..30 step 1.0 (0 dec) | combi | combi |
| 3 | `kkC_41_003` | Timbre16 · MIDI Channel | `(303, 116, 146)` | combo `(303, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Global | combi | combi |
| 4 | `kkC_41_004` | Timbre16 · Status | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| External2 | combi | combi |
| 5 | `kkC_41_005` | Timbre16 · Bank MSB | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_41_006` | Timbre16 · Bank LSB | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_41_007` | Timbre16 · Volume | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_41_008` | Timbre16 · Transpose | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -60..60 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_41_009` | Timbre16 · Detune | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | combi | combi |
| 10 | `kkC_41_010` | Timbre16 · Delay Time | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..6001 step 1.0 (0 dec) | combi | combi |
| 11 | `kkC_41_011` | Timbre16 · Delay Tempo Base Note | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1/32 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 1/1 | combi | combi |
| 12 | `kkC_41_012` | Timbre16 · Delay Mode | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | combi | combi |
| 13 | `kkC_41_013` | Timbre16 · Delay Tempo Times | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 1..32 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_41_014` | Timbre16 · Pan | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 15 | `kkC_41_015` | Timbre16 · Send1 | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_41_016` | Timbre16 · Send2 | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 17 | `kkC_41_017` | Timbre16 · Drum Kit Patch IFX1 | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 18 | `kkC_41_018` | Timbre16 · Drum Kit Patch IFX2 | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 19 | `kkC_41_019` | Timbre16 · Drum Kit Patch IFX3 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 20 | `kkC_41_020` | Timbre16 · Drum Kit Patch IFX4 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 21 | `kkC_41_021` | Timbre16 · Drum Kit Patch IFX5 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 22 | `kkC_41_022` | Timbre16 · Drum Kit Patch IFX6 | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 23 | `kkC_41_023` | Timbre16 · Drum Kit Patch IFX7 | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 24 | `kkC_41_024` | Timbre16 · Drum Kit Patch IFX8 | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 25 | `kkC_41_025` | Timbre16 · Drum Kit Patch IFX9 | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 26 | `kkC_41_026` | Timbre16 · Drum Kit Patch IFX10 | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 27 | `kkC_41_027` | Timbre16 · Drum Kit Patch IFX11 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 28 | `kkC_41_028` | Timbre16 · Drum Kit Patch IFX12 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 29 | `kkC_41_029` | Timbre16 · Bus Select | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | combi | combi |
| 30 | `kkC_41_030` | Timbre16 · Fx Bus Select | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| FX Control2 | combi | combi |
| 31 | `kkC_41_031` | Timbre16 · Use Drum Kit Bus Setting | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_41_032` | Timbre16 · Rec Bus | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | combi | combi |
| 33 | `kkC_41_033` | Timbre16 · Chord Source | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| Pad 8 | combi | combi |
| 34 | `kkC_41_034` | Timbre16 · Max # of Notes | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Program \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 16 | combi | combi |
| 35 | `kkC_41_035` | Timbre16 · Chord Mode | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Program \| 1 \| 2 \| Advanced | combi | combi |
| 36 | `kkC_41_036` | Timbre16 · (Filter) Program Change | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Disable \| Enable | combi | combi |
| 37 | `kkC_41_037` | Timbre16 · (Filter) After Touch | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Disable \| Enable | combi | combi |
| 38 | `kkC_41_038` | Timbre16 · (Filter) Damper | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Disable \| Enable | combi | combi |
| 39 | `kkC_41_039` | Timbre16 · (Filter) Portamento | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Disable \| Enable | combi | combi |
| 40 | `kkC_41_040` | Timbre16 · (Filter) JSX As Mod. | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Disable \| Enable | combi | combi |
| 41 | `kkC_41_041` | Timbre16 · (Filter) JS+Y | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Disable \| Enable | combi | combi |
| 42 | `kkC_41_042` | Timbre16 · (Filter) JS-Y | `(154, 312, 146)` | combo `(154, 325)` 146x20 | Disable \| Enable | combi | combi |
| 43 | `kkC_41_043` | Timbre16 · (Filter) Ribbon | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Disable \| Enable | combi | combi |
| 44 | `kkC_41_044` | Timbre16 · (Filter) Knob1 | `(452, 312, 146)` | combo `(452, 325)` 146x20 | Disable \| Enable | combi | combi |
| 45 | `kkC_41_045` | Timbre16 · (Filter) Knob2 | `(601, 312, 146)` | combo `(601, 325)` 146x20 | Disable \| Enable | combi | combi |
| 46 | `kkC_41_046` | Timbre16 · (Filter) Knob3 | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Disable \| Enable | combi | combi |
| 47 | `kkC_41_047` | Timbre16 · (Filter) Knob4 | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Disable \| Enable | combi | combi |
| 48 | `kkC_41_048` | Timbre16 · (Filter) Knob5 | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Disable \| Enable | combi | combi |
| 49 | `kkC_41_049` | Timbre16 · (Filter) Knob6 | `(1197, 312, 146)` | combo `(1197, 325)` 146x20 | Disable \| Enable | combi | combi |
| 50 | `kkC_41_050` | Timbre16 · (Filter) Knob7 | `(1346, 312, 146)` | combo `(1346, 325)` 146x20 | Disable \| Enable | combi | combi |
| 51 | `kkC_41_051` | Timbre16 · (Filter) Knob8 | `(5, 361, 146)` | combo `(5, 374)` 146x20 | Disable \| Enable | combi | combi |
| 52 | `kkC_41_052` | Timbre16 · (Filter) Switch1 | `(154, 361, 146)` | combo `(154, 374)` 146x20 | Disable \| Enable | combi | combi |
| 53 | `kkC_41_053` | Timbre16 · (Filter) Switch2 | `(303, 361, 146)` | combo `(303, 374)` 146x20 | Disable \| Enable | combi | combi |
| 54 | `kkC_41_054` | Timbre16 · (Filter) Foot Switch | `(452, 361, 146)` | combo `(452, 374)` 146x20 | Disable \| Enable | combi | combi |
| 55 | `kkC_41_055` | Timbre16 · (Filter) Foot Pedal | `(601, 361, 146)` | combo `(601, 374)` 146x20 | Disable \| Enable | combi | combi |
| 56 | `kkC_41_056` | Timbre16 · (Filter) Other CC# | `(750, 361, 146)` | combo `(750, 374)` 146x20 | Disable \| Enable | combi | combi |
| 57 | `kkC_41_057` | Timbre16 · Use Program Scale | `(899, 361, 146)` | combo `(899, 374)` 146x20 | Off \| On | combi | combi |
| 58 | `kkC_41_058` | Timbre16 · Auto Load Program EQ | `(1048, 361, 146)` | combo `(1048, 374)` 146x20 | Off \| On | combi | combi |
| 59 | `kkC_41_059` | Timbre16 · Mute | `(1197, 361, 146)` | combo `(1197, 374)` 146x20 | Off \| On | combi | combi |
| 60 | `kkC_41_060` | Timbre16 · Osc Mode | `(1346, 361, 146)` | combo `(1346, 374)` 146x20 | Program \| 1 \| 2 \| Mono Legato | combi | combi |

#### Tab 42 - Timbre 16·2 (43 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkC_42_001` | Timbre16 · Osc Select | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Both \| 1 \| OSC2 | combi | combi |
| 2 | `kkC_42_002` | Timbre16 · Timbre Priority | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | combi | combi |
| 3 | `kkC_42_003` | Timbre16 · Osc On/Off By KARMA | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Normal \| 1 \| Osc Off by K | combi | combi |
| 4 | `kkC_42_004` | Timbre16 · (Filter) Waveform SysEx | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Disable \| Enable | combi | combi |
| 5 | `kkC_42_005` | Timbre16 · Key Window Top | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 6 | `kkC_42_006` | Timbre16 · Key Window Bottom | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | combi | combi |
| 7 | `kkC_42_007` | Timbre16 · Vel.Window High | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 8 | `kkC_42_008` | Timbre16 · Vel.Window Low | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 1..127 step 1.0 (0 dec) | combi | combi |
| 9 | `kkC_42_009` | Timbre16 · Vel.Window High Slope | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 10 | `kkC_42_010` | Timbre16 · Vel.Window Low Slope | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..120 step 8.0 (0 dec) | combi | combi |
| 11 | `kkC_42_011` | Timbre16 · Quantize Trigger | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 12 | `kkC_42_012` | Timbre16 · Key Sync | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Program \| 1 \| On | combi | combi |
| 13 | `kkC_42_013` | Timbre16 · (Track EQ) Trim | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..99 step 1.0 (0 dec) | combi | combi |
| 14 | `kkC_42_014` | Timbre16 · (Track EQ) Bypass | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | combi | combi |
| 15 | `kkC_42_015` | Timbre16 · (Track EQ) Mid Frequency | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..165 step 1.0 (0 dec) | combi | combi |
| 16 | `kkC_42_016` | Timbre16 · (Track EQ) Low Gain | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 17 | `kkC_42_017` | Timbre16 · (Track EQ) Mid Gain | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 18 | `kkC_42_018` | Timbre16 · (Track EQ) High Gain | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -18..18 step 0.5 (4 dec) | combi | combi |
| 19 | `kkC_42_019` | Timbre16 · VJS Assign | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| -Y | combi | combi |
| 20 | `kkC_42_020` | Timbre16 · Volume Center | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..100 step 25.0 (0 dec) | combi | combi |
| 21 | `kkC_42_021` | Timbre16 · Program Vector Volume | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Off \| On | combi | combi |
| 22 | `kkC_42_022` | Timbre16 · Combi Vector CC | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| On | combi | combi |
| 23 | `kkC_42_023` | Timbre16 · Program Vector CC | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| On | combi | combi |
| 24 | `kkC_42_024` | Timbre16 · Switch1 Value | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | combi | combi |
| 25 | `kkC_42_025` | Timbre16 · Switch2 Value | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | combi | combi |
| 26 | `kkC_42_026` | Timbre16 · Switch3 Value | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | combi | combi |
| 27 | `kkC_42_027` | Timbre16 · Switch4 Value | `(899, 214, 146)` | combo `(899, 227)` 146x20 | Off \| On | combi | combi |
| 28 | `kkC_42_028` | Timbre16 · Switch5 Value | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | Off \| On | combi | combi |
| 29 | `kkC_42_029` | Timbre16 · Switch6 Value | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| On | combi | combi |
| 30 | `kkC_42_030` | Timbre16 · Switch7 Value | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| On | combi | combi |
| 31 | `kkC_42_031` | Timbre16 · Switch8 Value | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| On | combi | combi |
| 32 | `kkC_42_032` | Timbre16 · Switch9 Value | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | combi | combi |
| 33 | `kkC_42_033` | Timbre16 · Switch10 Value | `(303, 263, 146)` | combo `(303, 276)` 146x20 | Off \| On | combi | combi |
| 34 | `kkC_42_034` | Timbre16 · Switch11 Value | `(452, 263, 146)` | combo `(452, 276)` 146x20 | Off \| On | combi | combi |
| 35 | `kkC_42_035` | Timbre16 · Switch12 Value | `(601, 263, 146)` | combo `(601, 276)` 146x20 | Off \| On | combi | combi |
| 36 | `kkC_42_036` | Timbre16 · Switch13 Value | `(750, 263, 146)` | combo `(750, 276)` 146x20 | Off \| On | combi | combi |
| 37 | `kkC_42_037` | Timbre16 · Switch14 Value | `(899, 263, 146)` | combo `(899, 276)` 146x20 | Off \| On | combi | combi |
| 38 | `kkC_42_038` | Timbre16 · Switch15 Value | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| On | combi | combi |
| 39 | `kkC_42_039` | Timbre16 · Switch16 Value | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Off \| On | combi | combi |
| 40 | `kkC_42_040` | Timbre16 · EXi1 Input Source Bus | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 41 | `kkC_42_041` | Timbre16 · EXi1 Input Source Channel | `(5, 312, 146)` | combo `(5, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |
| 42 | `kkC_42_042` | Timbre16 · EXi2 Input Source Bus | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..29 step 1.0 (0 dec) | combi | combi |
| 43 | `kkC_42_043` | Timbre16 · EXi2 Input Source Channel | `(303, 312, 146)` | combo `(303, 325)` 146x20 | Stereo/L+R \| 1 \| Right | combi | combi |


### 6.3 Drum Kit - `kkEdTabsK` - 0x4B dump obj 04 (Drum Kit)

#### Tab 1 - Note 1 · Commun (24 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkK_01_001` | Note1 Common · Pan | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | kit | kit |
| 2 | `kkK_01_002` | Note1 Common · Bus Select | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..25 step 1.0 (0 dec) | kit | kit |
| 3 | `kkK_01_003` | Note1 Common · FX Control Bus | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Off \| 1 \| FX Control2 | kit | kit |
| 4 | `kkK_01_004` | Note1 Common · Send 1 Level | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | kit | kit |
| 5 | `kkK_01_005` | Note1 Common · Send 2 Level | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | kit | kit |
| 6 | `kkK_01_006` | Note1 Common · Exclusive Group | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | kit | kit |
| 7 | `kkK_01_007` | Note1 Common · Assign | `(899, 116, 146)` | combo `(899, 129)` 146x20 | Off \| On | kit | kit |
| 8 | `kkK_01_008` | Note1 Common · Single Trigger | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | Off \| On | kit | kit |
| 9 | `kkK_01_009` | Note1 Common · Receive Note On | `(1197, 116, 146)` | combo `(1197, 129)` 146x20 | Off \| On | kit | kit |
| 10 | `kkK_01_010` | Note1 Common · Receive Note Off | `(1346, 116, 146)` | combo `(1346, 129)` 146x20 | Off \| On | kit | kit |
| 11 | `kkK_01_011` | Velocity Control · Velocity XFade Range | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | kit | kit |
| 12 | `kkK_01_012` | Velocity Control · Velocity XFade Shape | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Linear \| 1 \| Layer | kit | kit |
| 13 | `kkK_01_013` | Velocity Control · Velocity XFade Range | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | kit | kit |
| 14 | `kkK_01_014` | Velocity Control · Velocity XFade Shape | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Linear \| 1 \| Layer | kit | kit |
| 15 | `kkK_01_015` | Velocity Control · Velocity XFade Range | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | kit | kit |
| 16 | `kkK_01_016` | Velocity Control · Velocity XFade Shape | `(750, 165, 146)` | combo `(750, 178)` 146x20 | Linear \| 1 \| Layer | kit | kit |
| 17 | `kkK_01_017` | Velocity Control · Velocity XFade Range | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | kit | kit |
| 18 | `kkK_01_018` | Velocity Control · Velocity XFade Shape | `(1048, 165, 146)` | combo `(1048, 178)` 146x20 | Linear \| 1 \| Layer | kit | kit |
| 19 | `kkK_01_019` | Velocity Control · Velocity XFade Range | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | kit | kit |
| 20 | `kkK_01_020` | Velocity Control · Velocity XFade Shape | `(1346, 165, 146)` | combo `(1346, 178)` 146x20 | Linear \| 1 \| Layer | kit | kit |
| 21 | `kkK_01_021` | Velocity Control · Velocity XFade Range | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | kit | kit |
| 22 | `kkK_01_022` | Velocity Control · Velocity XFade Shape | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Linear \| 1 \| Layer | kit | kit |
| 23 | `kkK_01_023` | Velocity Control · Velocity XFade Range | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | kit | kit |
| 24 | `kkK_01_024` | Velocity Control · Velocity XFade Shape | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Linear \| 1 \| Layer | kit | kit |

#### Tab 2 - Note 1 · Zone 1 (16 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkK_02_001` | Note1 Zone1 DS · Sample On/Off | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Off \| On | kit | kit |
| 2 | `kkK_02_002` | Note1 Zone1 DS · Sample Id | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..65534 step 1.0 (0 dec) | kit | kit |
| 3 | `kkK_02_003` | Note1 Zone1 DS · Level | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | kit | kit |
| 4 | `kkK_02_004` | Note1 Zone1 DS · Start Offset | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8th | kit | kit |
| 5 | `kkK_02_005` | Note1 Zone1 DS · Sample Reverse | `(601, 116, 146)` | combo `(601, 129)` 146x20 | Off \| On | kit | kit |
| 6 | `kkK_02_006` | Note1 Zone1 DS · Transpose | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | -64..63 step 1.0 (0 dec) | kit | kit |
| 7 | `kkK_02_007` | Note1 Zone1 DS · Tune | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | kit | kit |
| 8 | `kkK_02_008` | Note1 Zone1 DS · Attack | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -64..63 step 1.0 (0 dec) | kit | kit |
| 9 | `kkK_02_009` | Note1 Zone1 DS · Decay | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -64..63 step 1.0 (0 dec) | kit | kit |
| 10 | `kkK_02_010` | Note1 Zone1 DS · Cutoff | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | -64..63 step 1.0 (0 dec) | kit | kit |
| 11 | `kkK_02_011` | Note1 Zone1 DS · Resonance | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | -64..63 step 1.0 (0 dec) | kit | kit |
| 12 | `kkK_02_012` | Note1 Zone1 DS · EQ High Gain | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | -72..72 step 1.0 (0 dec) | kit | kit |
| 13 | `kkK_02_013` | Note1 Zone1 DS · EQ Mid Gain | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | -72..72 step 1.0 (0 dec) | kit | kit |
| 14 | `kkK_02_014` | Note1 Zone1 DS · EQ Low Gain | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | -72..72 step 1.0 (0 dec) | kit | kit |
| 15 | `kkK_02_015` | Note1 Zone1 DS · Drive | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | kit | kit |
| 16 | `kkK_02_016` | Note1 Zone1 DS · Low Boost | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | kit | kit |

#### Tab 3 - Note 1 · Zones 2-8 (21 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkK_03_001` | Note1 Zone2 DS · Sample On/Off | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Off \| On | kit | kit |
| 2 | `kkK_03_002` | Note1 Zone2 DS · Low Boost | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | kit | kit |
| 3 | `kkK_03_003` | Note1 Zone3 DS · Sample On/Off | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Off \| On | kit | kit |
| 4 | `kkK_03_004` | Note1 Zone3 DS · Low Boost | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | kit | kit |
| 5 | `kkK_03_005` | Note1 Zone4 DS · Sample On/Off | `(601, 116, 146)` | combo `(601, 129)` 146x20 | Off \| On | kit | kit |
| 6 | `kkK_03_006` | Note1 Zone4 DS · Low Boost | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | kit | kit |
| 7 | `kkK_03_007` | Note1 Zone5 DS · Sample On/Off | `(899, 116, 146)` | combo `(899, 129)` 146x20 | Off \| On | kit | kit |
| 8 | `kkK_03_008` | Note1 Zone5 DS · Low Boost | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | kit | kit |
| 9 | `kkK_03_009` | Note1 Zone6 DS · Sample On/Off | `(1197, 116, 146)` | combo `(1197, 129)` 146x20 | Off \| On | kit | kit |
| 10 | `kkK_03_010` | Note1 Zone6 DS · Low Boost | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | kit | kit |
| 11 | `kkK_03_011` | Note1 Zone7 DS · Sample On/Off | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Off \| On | kit | kit |
| 12 | `kkK_03_012` | Note1 Zone7 DS · Low Boost | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | kit | kit |
| 13 | `kkK_03_013` | Note1 Zone8 DS · Sample On/Off | `(303, 165, 146)` | combo `(303, 178)` 146x20 | Off \| On | kit | kit |
| 14 | `kkK_03_014` | Note1 Zone8 DS · Low Boost | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | kit | kit |
| 15 | `kkK_03_015` | Note1 Zone1 - 2 · Bottom Velocity | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 1..127 step 1.0 (0 dec) | kit | kit |
| 16 | `kkK_03_016` | Note1 Zone2 - 3 · Bottom Velocity | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 1..127 step 1.0 (0 dec) | kit | kit |
| 17 | `kkK_03_017` | Note1 Zone3 - 4 · Bottom Velocity | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 1..127 step 1.0 (0 dec) | kit | kit |
| 18 | `kkK_03_018` | Note1 Zone4 - 5 · Bottom Velocity | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 1..127 step 1.0 (0 dec) | kit | kit |
| 19 | `kkK_03_019` | Note1 Zone5 - 6 · Bottom Velocity | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 1..127 step 1.0 (0 dec) | kit | kit |
| 20 | `kkK_03_020` | Note1 Zone6 - 7 · Bottom Velocity | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 1..127 step 1.0 (0 dec) | kit | kit |
| 21 | `kkK_03_021` | Note1 Zone7 - 8 · Bottom Velocity | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 1..127 step 1.0 (0 dec) | kit | kit |

#### Tab 4 - Note 2 (5 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkK_04_001` | Note2 Common · Assign | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Off \| On | kit | kit |
| 2 | `kkK_04_002` | Note2 Common · Single Trigger | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | kit | kit |
| 3 | `kkK_04_003` | Note2 Common · Receive Note On | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Off \| On | kit | kit |
| 4 | `kkK_04_004` | Note2 Common · Receive Note Off | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| On | kit | kit |
| 5 | `kkK_04_005` | Note2 Zone1 DS · Sample On/Off | `(601, 116, 146)` | combo `(601, 129)` 146x20 | Off \| On | kit | kit |

#### Tab 5 - Note 128 (5 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkK_05_001` | Note128 Common · Assign | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Off \| On | kit | kit |
| 2 | `kkK_05_002` | Note128 Common · Single Trigger | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Off \| On | kit | kit |
| 3 | `kkK_05_003` | Note128 Common · Receive Note On | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Off \| On | kit | kit |
| 4 | `kkK_05_004` | Note128 Common · Receive Note Off | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| On | kit | kit |
| 5 | `kkK_05_005` | Note128 High DS · Sample On/Off | `(601, 116, 146)` | combo `(601, 129)` 146x20 | Off \| On | kit | kit |


### 6.4 Wave Seq - `kkEdTabsW` - 0x4B dump obj 05 (Wave Sequence)

#### Tab 1 - Commun (12 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkW_01_001` | Common · Note-On Advance | `(5, 116, 146)` | combo `(5, 129)` 146x20 | Off \| On | wsq | wsq |
| 2 | `kkW_01_002` | Common · End Step | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..63 step 1.0 (0 dec) | wsq | wsq |
| 3 | `kkW_01_003` | Common · Start Step | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..63 step 1.0 (0 dec) | wsq | wsq |
| 4 | `kkW_01_004` | Common · Start Step AMS Source | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..76 step 1.0 (0 dec) | wsq | wsq |
| 5 | `kkW_01_005` | Common · Start Step AMS Intensity | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | -63..63 step 1.0 (0 dec) | wsq | wsq |
| 6 | `kkW_01_006` | Common · Position AMS Source | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..76 step 1.0 (0 dec) | wsq | wsq |
| 7 | `kkW_01_007` | Common · Position AMS Intensity | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | -63..63 step 1.0 (0 dec) | wsq | wsq |
| 8 | `kkW_01_008` | Common · Duration AMS Source | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..76 step 1.0 (0 dec) | wsq | wsq |
| 9 | `kkW_01_009` | Common · Duration AMS Intensity | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..399 step 1.0 (0 dec) | wsq | wsq |
| 10 | `kkW_01_010` | Common · Loop Start | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..63 step 1.0 (0 dec) | wsq | wsq |
| 11 | `kkW_01_011` | Common · Loop End | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | 0..63 step 1.0 (0 dec) | wsq | wsq |
| 12 | `kkW_01_012` | Common · Loop Repeat | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | 0..128 step 1.0 (0 dec) | wsq | wsq |

#### Tab 2 - Steps (16 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkW_02_001` | Step1 · Multisample Select | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..16382 step 1.0 (0 dec) | wsq | wsq |
| 2 | `kkW_02_002` | Step1 · Level | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | wsq | wsq |
| 3 | `kkW_02_003` | Step1 · Start Offset | `(303, 116, 146)` | combo `(303, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8th | wsq | wsq |
| 4 | `kkW_02_004` | Step1 · Reverse | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| On | wsq | wsq |
| 5 | `kkW_02_005` | Step1 · Tune | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | -1200..1200 step 1.0 (0 dec) | wsq | wsq |
| 6 | `kkW_02_006` | Step1 · Transpose | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | -24..24 step 1.0 (0 dec) | wsq | wsq |
| 7 | `kkW_02_007` | Step1 · AMS1 Output | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | wsq | wsq |
| 8 | `kkW_02_008` | Step1 · AMS2 Output | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | wsq | wsq |
| 9 | `kkW_02_009` | Step1 · Duration | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..146 step 1.0 (0 dec) | wsq | wsq |
| 10 | `kkW_02_010` | Step1 · Tempo Base Note | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..10 step 1.0 (0 dec) | wsq | wsq |
| 11 | `kkW_02_011` | Step1 · Tempo Multiplier | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | 0..31 step 1.0 (0 dec) | wsq | wsq |
| 12 | `kkW_02_012` | Step1 · Crossfade | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | 0..145 step 1.0 (0 dec) | wsq | wsq |
| 13 | `kkW_02_013` | Step1 · Fade-In Shape | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | -128..127 step 1.0 (0 dec) | wsq | wsq |
| 14 | `kkW_02_014` | Step1 · Fade-Out Shape | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | -128..127 step 1.0 (0 dec) | wsq | wsq |
| 15 | `kkW_02_015` | Step2 · Fade-Out Shape | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | -128..127 step 1.0 (0 dec) | wsq | wsq |
| 16 | `kkW_02_016` | Step64 · Fade-Out Shape | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -128..127 step 1.0 (0 dec) | wsq | wsq |


### 6.5 Global - `kkEdTabsG` - 0x4B dump obj 03 (Global)

#### Tab 1 - Basic (30 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkG_01_001` | Basic · Master Tune | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | -50..50 step 1.0 (0 dec) | global | global |
| 2 | `kkG_01_002` | Basic · Key Transpose | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | -12..12 step 1.0 (0 dec) | global | global |
| 3 | `kkG_01_003` | Basic · Velocity Curve | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 1..9 step 1.0 (0 dec) | global | global |
| 4 | `kkG_01_004` | Basic · Aftertouch Curve | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 1..8 step 1.0 (0 dec) | global | global |
| 5 | `kkG_01_005` | Basic · Prog Auto KARMA | `(601, 116, 146)` | combo `(601, 129)` 146x20 | Off \| On | global | global |
| 6 | `kkG_01_006` | Basic · Combi Auto KARMA | `(750, 116, 146)` | combo `(750, 129)` 146x20 | Off \| On | global | global |
| 7 | `kkG_01_007` | Basic · All KARMA Off | `(899, 116, 146)` | combo `(899, 129)` 146x20 | Off \| On | global | global |
| 8 | `kkG_01_008` | Basic · Knob Slider Mode | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | Jump \| Catch | global | global |
| 9 | `kkG_01_009` | Basic · Auto Optimize Ram | `(1197, 116, 146)` | combo `(1197, 129)` 146x20 | Off \| On | global | global |
| 10 | `kkG_01_010` | Basic · System Clock | `(1346, 116, 146)` | combo `(1346, 129)` 146x20 | Internal \| 1 \| S/P DIF | global | global |
| 11 | `kkG_01_011` | Basic · SPDIF SampleRate | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 48kHz \| 1 \| 96kHz Hi | global | global |
| 12 | `kkG_01_012` | Basic · HDR Bit Depth | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | 16..24 step 8.0 (0 dec) | global | global |
| 13 | `kkG_01_013` | Basic · Sampling to Disk Bit Depth | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 16..24 step 8.0 (0 dec) | global | global |
| 14 | `kkG_01_014` | Basic · Sampling to Ram Bit Depth | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 16..24 step 8.0 (0 dec) | global | global |
| 15 | `kkG_01_015` | Basic · Show MS/WS/DKit Graphics | `(601, 165, 146)` | combo `(601, 178)` 146x20 | Off \| On | global | global |
| 16 | `kkG_01_016` | Basic · Headroom | `(750, 165, 146)` | combo `(750, 178)` 146x20 | Standard \| 1 \| 2 \| 3 \| +48dB | global | global |
| 17 | `kkG_01_017` | Basic · Drum Track Off | `(899, 165, 146)` | combo `(899, 178)` 146x20 | Off \| On | global | global |
| 18 | `kkG_01_018` | Basic · Bank Map | `(1048, 165, 146)` | combo `(1048, 178)` 146x20 | KORG \| GM(2) | global | global |
| 19 | `kkG_01_019` | Basic · Power On Mode | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Reset \| Mem | global | global |
| 20 | `kkG_01_020` | Basic · Beep Enable | `(1346, 165, 146)` | combo `(1346, 178)` 146x20 | Off \| On | global | global |
| 21 | `kkG_01_021` | Basic · Mute Mode | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Studio \| Live | global | global |
| 22 | `kkG_01_022` | Basic · Protect Program | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| On | global | global |
| 23 | `kkG_01_023` | Basic · Protect Combi | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| On | global | global |
| 24 | `kkG_01_024` | Basic · Protect Song | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | global | global |
| 25 | `kkG_01_025` | Basic · Protect DrumKit | `(601, 214, 146)` | combo `(601, 227)` 146x20 | Off \| On | global | global |
| 26 | `kkG_01_026` | Basic · Protect WaveSeq | `(750, 214, 146)` | combo `(750, 227)` 146x20 | Off \| On | global | global |
| 27 | `kkG_01_027` | Basic · Protect KARMA GE | `(899, 214, 146)` | combo `(899, 227)` 146x20 | Off \| On | global | global |
| 28 | `kkG_01_028` | Basic · Internal HDD Save | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | Off \| On | global | global |
| 29 | `kkG_01_029` | Basic · LRBus Individual Out Assign | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | Off \| 1 \| 2 \| 3 \| 7/8 | global | global |
| 30 | `kkG_01_030` | Basic · Hold Time | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | 00Sec \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| 16 \| 17 \| 18 \| 19 \| 20 \| 21 \| 60Sec | global | global |

#### Tab 2 - Controller (34 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkG_02_001` | Controller · Foot SW Polarity | `(5, 116, 146)` | combo `(5, 129)` 146x20 | - \| + | global | global |
| 2 | `kkG_02_002` | Controller · Damper Polarity | `(154, 116, 146)` | combo `(154, 129)` 146x20 | - \| + | global | global |
| 3 | `kkG_02_003` | Controller · Foot SW Assign | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..53 step 1.0 (0 dec) | global | global |
| 4 | `kkG_02_004` | Controller · Foot Pedal Assign | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..31 step 1.0 (0 dec) | global | global |
| 5 | `kkG_02_005` | Controller · Foot Pedal Behavior | `(601, 116, 146)` | combo `(601, 129)` 146x20 | Keep Current \| Reset | global | global |
| 6 | `kkG_02_006` | Controller · KARMA CC# Assign (ON/OFF) | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 7 | `kkG_02_007` | Controller · KARMA CC# Assign (SCENE) | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 8 | `kkG_02_008` | Controller · KARMA CC# Assign (LATCH) | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 9 | `kkG_02_009` | Controller · KARMA CC# Assign (SLIDER1) | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 10 | `kkG_02_010` | Controller · KARMA CC# Assign (SLIDER2) | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 11 | `kkG_02_011` | Controller · KARMA CC# Assign (SLIDER3) | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 12 | `kkG_02_012` | Controller · KARMA CC# Assign (SLIDER4) | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 13 | `kkG_02_013` | Controller · KARMA CC# Assign (SLIDER5) | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 14 | `kkG_02_014` | Controller · KARMA CC# Assign (SLIDER6) | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 15 | `kkG_02_015` | Controller · KARMA CC# Assign (SLIDER7) | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 16 | `kkG_02_016` | Controller · KARMA CC# Assign (SLIDER8) | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 17 | `kkG_02_017` | Controller · KARMA CC# Assign (SW1) | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 18 | `kkG_02_018` | Controller · KARMA CC# Assign (SW2) | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 19 | `kkG_02_019` | Controller · KARMA CC# Assign (SW3) | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 20 | `kkG_02_020` | Controller · KARMA CC# Assign (SW4) | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 21 | `kkG_02_021` | Controller · KARMA CC# Assign (SW5) | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 22 | `kkG_02_022` | Controller · KARMA CC# Assign (SW6) | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 23 | `kkG_02_023` | Controller · KARMA CC# Assign (SW7) | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 24 | `kkG_02_024` | Controller · KARMA CC# Assign (SW8) | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 25 | `kkG_02_025` | Controller · Pad CC# Assign (PAD1) | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..65528 step 1.0 (0 dec) | global | global |
| 26 | `kkG_02_026` | Controller · Pad CC# Assign (PAD2) | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..65528 step 1.0 (0 dec) | global | global |
| 27 | `kkG_02_027` | Controller · Pad CC# Assign (PAD3) | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..65528 step 1.0 (0 dec) | global | global |
| 28 | `kkG_02_028` | Controller · Pad CC# Assign (PAD4) | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..65528 step 1.0 (0 dec) | global | global |
| 29 | `kkG_02_029` | Controller · Pad CC# Assign (PAD5) | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..65528 step 1.0 (0 dec) | global | global |
| 30 | `kkG_02_030` | Controller · Pad CC# Assign (PAD6) | `(1346, 214, 146)` | knob `(1401, 226)` 36x36 rotary | 0..65528 step 1.0 (0 dec) | global | global |
| 31 | `kkG_02_031` | Controller · Pad CC# Assign (PAD7) | `(5, 263, 146)` | knob `(60, 275)` 36x36 rotary | 0..65528 step 1.0 (0 dec) | global | global |
| 32 | `kkG_02_032` | Controller · Pad CC# Assign (PAD8) | `(154, 263, 146)` | knob `(209, 275)` 36x36 rotary | 0..65528 step 1.0 (0 dec) | global | global |
| 33 | `kkG_02_033` | Controller · Vector CC# Assign (X) | `(303, 263, 146)` | knob `(358, 275)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 34 | `kkG_02_034` | Controller · Vector CC# Assign (Y) | `(452, 263, 146)` | knob `(507, 275)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |

#### Tab 3 - MIDI (21 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkG_03_001` | MIDI · MIDI Convert Position | `(5, 116, 146)` | combo `(5, 129)` 146x20 | PreMIDI \| PostMIDI | global | global |
| 2 | `kkG_03_002` | MIDI · Vector MIDI Out | `(154, 116, 146)` | combo `(154, 129)` 146x20 | Joystick \| CC Control | global | global |
| 3 | `kkG_03_003` | MIDI · Pads MIDI Out | `(303, 116, 146)` | combo `(303, 129)` 146x20 | CC/Note \| Chord Notes | global | global |
| 4 | `kkG_03_004` | MIDI · KARMA Module to MIDI Out | `(452, 116, 146)` | combo `(452, 129)` 146x20 | Off \| On | global | global |
| 5 | `kkG_03_005` | MIDI · MIDI In to KARMA Module | `(601, 116, 146)` | combo `(601, 129)` 146x20 | Off \| On | global | global |
| 6 | `kkG_03_006` | MIDI · SEQ Track MIDI Out | `(750, 116, 146)` | combo `(750, 129)` 146x20 | for Master \| Ext Seq | global | global |
| 7 | `kkG_03_007` | MIDI · SEQ Param MIDI Out | `(899, 116, 146)` | combo `(899, 129)` 146x20 | Ctrl Chg \| Param Chg | global | global |
| 8 | `kkG_03_008` | MIDI · Ext Mode Set Select | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 9 | `kkG_03_009` | MIDI · Global MIDI Channel | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 1..16 step 1.0 (0 dec) | global | global |
| 10 | `kkG_03_010` | MIDI · Local On | `(1346, 116, 146)` | combo `(1346, 129)` 146x20 | Off \| On | global | global |
| 11 | `kkG_03_011` | MIDI · Midi Clock | `(5, 165, 146)` | combo `(5, 178)` 146x20 | Internal \| 1 \| Auto | global | global |
| 12 | `kkG_03_012` | MIDI · Receive EXT.RTCommand | `(154, 165, 146)` | combo `(154, 178)` 146x20 | Off \| On | global | global |
| 13 | `kkG_03_013` | MIDI · Program Change Enable | `(303, 165, 146)` | combo `(303, 178)` 146x20 | Off \| On | global | global |
| 14 | `kkG_03_014` | MIDI · Bank Change Enable | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| On | global | global |
| 15 | `kkG_03_015` | MIDI · Combi Change Enable | `(601, 165, 146)` | combo `(601, 178)` 146x20 | Off \| On | global | global |
| 16 | `kkG_03_016` | MIDI · Aftertouch Enable | `(750, 165, 146)` | combo `(750, 178)` 146x20 | Off \| On | global | global |
| 17 | `kkG_03_017` | MIDI · Control Change Enable | `(899, 165, 146)` | combo `(899, 178)` 146x20 | Off \| On | global | global |
| 18 | `kkG_03_018` | MIDI · SysEx Enable | `(1048, 165, 146)` | combo `(1048, 178)` 146x20 | Off \| On | global | global |
| 19 | `kkG_03_019` | MIDI · Start/Stop Out Enable | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | Off \| On | global | global |
| 20 | `kkG_03_020` | MIDI · Prog Drum Track MIDI Ch | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 1..16 step 1.0 (0 dec) | global | global |
| 21 | `kkG_03_021` | MIDI · Prog Drum Track MIDI MIDI Out | `(5, 214, 146)` | combo `(5, 227)` 146x20 | Off \| On | global | global |

#### Tab 4 - MIDI Ext Set 1 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkG_04_001` | MIDI · (External Set1 - Knob1) Channel | `(5, 116, 146)` | combo `(5, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 2 | `kkG_04_002` | MIDI · (External Set1 - Knob1) CC# Assign | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 3 | `kkG_04_003` | MIDI · (External Set1 - Knob2) Channel | `(303, 116, 146)` | combo `(303, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 4 | `kkG_04_004` | MIDI · (External Set1 - Knob2) CC# Assign | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 5 | `kkG_04_005` | MIDI · (External Set1 - Knob3) Channel | `(601, 116, 146)` | combo `(601, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 6 | `kkG_04_006` | MIDI · (External Set1 - Knob3) CC# Assign | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 7 | `kkG_04_007` | MIDI · (External Set1 - Knob4) Channel | `(899, 116, 146)` | combo `(899, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 8 | `kkG_04_008` | MIDI · (External Set1 - Knob4) CC# Assign | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 9 | `kkG_04_009` | MIDI · (External Set1 - Knob5) Channel | `(1197, 116, 146)` | combo `(1197, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 10 | `kkG_04_010` | MIDI · (External Set1 - Knob5) CC# Assign | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 11 | `kkG_04_011` | MIDI · (External Set1 - Knob6) Channel | `(5, 165, 146)` | combo `(5, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 12 | `kkG_04_012` | MIDI · (External Set1 - Knob6) CC# Assign | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 13 | `kkG_04_013` | MIDI · (External Set1 - Knob7) Channel | `(303, 165, 146)` | combo `(303, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 14 | `kkG_04_014` | MIDI · (External Set1 - Knob7) CC# Assign | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 15 | `kkG_04_015` | MIDI · (External Set1 - Knob8) Channel | `(601, 165, 146)` | combo `(601, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 16 | `kkG_04_016` | MIDI · (External Set1 - Knob8) CC# Assign | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 17 | `kkG_04_017` | MIDI · (External Set1 - Switch1) Channel | `(899, 165, 146)` | combo `(899, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 18 | `kkG_04_018` | MIDI · (External Set1 - Switch1) CC# Assign | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 19 | `kkG_04_019` | MIDI · (External Set1 - Switch2) Channel | `(1197, 165, 146)` | combo `(1197, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 20 | `kkG_04_020` | MIDI · (External Set1 - Switch2) CC# Assign | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 21 | `kkG_04_021` | MIDI · (External Set1 - Switch3) Channel | `(5, 214, 146)` | combo `(5, 227)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 22 | `kkG_04_022` | MIDI · (External Set1 - Switch3) CC# Assign | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 23 | `kkG_04_023` | MIDI · (External Set1 - Switch4) Channel | `(303, 214, 146)` | combo `(303, 227)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 24 | `kkG_04_024` | MIDI · (External Set1 - Switch4) CC# Assign | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 25 | `kkG_04_025` | MIDI · (External Set1 - Switch5) Channel | `(601, 214, 146)` | combo `(601, 227)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 26 | `kkG_04_026` | MIDI · (External Set1 - Switch5) CC# Assign | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 27 | `kkG_04_027` | MIDI · (External Set1 - Switch6) Channel | `(899, 214, 146)` | combo `(899, 227)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 28 | `kkG_04_028` | MIDI · (External Set1 - Switch6) CC# Assign | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 29 | `kkG_04_029` | MIDI · (External Set1 - Switch7) Channel | `(1197, 214, 146)` | combo `(1197, 227)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 30 | `kkG_04_030` | MIDI · (External Set1 - Switch7) CC# Assign | `(1346, 214, 146)` | knob `(1401, 226)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 31 | `kkG_04_031` | MIDI · (External Set1 - Switch8) Channel | `(5, 263, 146)` | combo `(5, 276)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 32 | `kkG_04_032` | MIDI · (External Set1 - Switch8) CC# Assign | `(154, 263, 146)` | knob `(209, 275)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 33 | `kkG_04_033` | MIDI · (External Set1 - Switch9) Channel | `(303, 263, 146)` | combo `(303, 276)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 34 | `kkG_04_034` | MIDI · (External Set1 - Switch9) CC# Assign | `(452, 263, 146)` | knob `(507, 275)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 35 | `kkG_04_035` | MIDI · (External Set1 - Switch10) Channel | `(601, 263, 146)` | combo `(601, 276)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 36 | `kkG_04_036` | MIDI · (External Set1 - Switch10) CC# Assign | `(750, 263, 146)` | knob `(805, 275)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 37 | `kkG_04_037` | MIDI · (External Set1 - Switch11) Channel | `(899, 263, 146)` | combo `(899, 276)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 38 | `kkG_04_038` | MIDI · (External Set1 - Switch11) CC# Assign | `(1048, 263, 146)` | knob `(1103, 275)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 39 | `kkG_04_039` | MIDI · (External Set1 - Switch12) Channel | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 40 | `kkG_04_040` | MIDI · (External Set1 - Switch12) CC# Assign | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 41 | `kkG_04_041` | MIDI · (External Set1 - Switch13) Channel | `(5, 312, 146)` | combo `(5, 325)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 42 | `kkG_04_042` | MIDI · (External Set1 - Switch13) CC# Assign | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 43 | `kkG_04_043` | MIDI · (External Set1 - Switch14) Channel | `(303, 312, 146)` | combo `(303, 325)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 44 | `kkG_04_044` | MIDI · (External Set1 - Switch14) CC# Assign | `(452, 312, 146)` | knob `(507, 324)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 45 | `kkG_04_045` | MIDI · (External Set1 - Switch15) Channel | `(601, 312, 146)` | combo `(601, 325)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 46 | `kkG_04_046` | MIDI · (External Set1 - Switch15) CC# Assign | `(750, 312, 146)` | knob `(805, 324)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 47 | `kkG_04_047` | MIDI · (External Set1 - Switch16) Channel | `(899, 312, 146)` | combo `(899, 325)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 48 | `kkG_04_048` | MIDI · (External Set1 - Switch16) CC# Assign | `(1048, 312, 146)` | knob `(1103, 324)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 49 | `kkG_04_049` | MIDI · (External Set1 - Slider1) Channel | `(1197, 312, 146)` | combo `(1197, 325)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 50 | `kkG_04_050` | MIDI · (External Set1 - Slider1) CC# Assign | `(1346, 312, 146)` | knob `(1401, 324)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 51 | `kkG_04_051` | MIDI · (External Set1 - Slider2) Channel | `(5, 361, 146)` | combo `(5, 374)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 52 | `kkG_04_052` | MIDI · (External Set1 - Slider2) CC# Assign | `(154, 361, 146)` | knob `(209, 373)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 53 | `kkG_04_053` | MIDI · (External Set1 - Slider3) Channel | `(303, 361, 146)` | combo `(303, 374)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 54 | `kkG_04_054` | MIDI · (External Set1 - Slider3) CC# Assign | `(452, 361, 146)` | knob `(507, 373)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 55 | `kkG_04_055` | MIDI · (External Set1 - Slider4) Channel | `(601, 361, 146)` | combo `(601, 374)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 56 | `kkG_04_056` | MIDI · (External Set1 - Slider4) CC# Assign | `(750, 361, 146)` | knob `(805, 373)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 57 | `kkG_04_057` | MIDI · (External Set1 - Slider5) Channel | `(899, 361, 146)` | combo `(899, 374)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 58 | `kkG_04_058` | MIDI · (External Set1 - Slider5) CC# Assign | `(1048, 361, 146)` | knob `(1103, 373)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 59 | `kkG_04_059` | MIDI · (External Set1 - Slider6) Channel | `(1197, 361, 146)` | combo `(1197, 374)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 60 | `kkG_04_060` | MIDI · (External Set1 - Slider6) CC# Assign | `(1346, 361, 146)` | knob `(1401, 373)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |

#### Tab 5 - Octave Scale (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkG_05_001` | User Octave Scale 00 · C | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 2 | `kkG_05_002` | User Octave Scale 00 · C# | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 3 | `kkG_05_003` | User Octave Scale 00 · D | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 4 | `kkG_05_004` | User Octave Scale 00 · D# | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 5 | `kkG_05_005` | User Octave Scale 00 · E | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 6 | `kkG_05_006` | User Octave Scale 00 · F | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 7 | `kkG_05_007` | User Octave Scale 00 · F# | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 8 | `kkG_05_008` | User Octave Scale 00 · G | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 9 | `kkG_05_009` | User Octave Scale 00 · G# | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 10 | `kkG_05_010` | User Octave Scale 00 · A | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 11 | `kkG_05_011` | User Octave Scale 00 · A# | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 12 | `kkG_05_012` | User Octave Scale 00 · B | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 13 | `kkG_05_013` | User Octave Scale 01 · C | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 14 | `kkG_05_014` | User Octave Scale 01 · C# | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 15 | `kkG_05_015` | User Octave Scale 01 · D | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 16 | `kkG_05_016` | User Octave Scale 01 · D# | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 17 | `kkG_05_017` | User Octave Scale 01 · E | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 18 | `kkG_05_018` | User Octave Scale 01 · F | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 19 | `kkG_05_019` | User Octave Scale 01 · F# | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 20 | `kkG_05_020` | User Octave Scale 01 · G | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 21 | `kkG_05_021` | User Octave Scale 01 · G# | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 22 | `kkG_05_022` | User Octave Scale 01 · A | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 23 | `kkG_05_023` | User Octave Scale 01 · A# | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 24 | `kkG_05_024` | User Octave Scale 01 · B | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 25 | `kkG_05_025` | User Octave Scale 02 · C | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 26 | `kkG_05_026` | User Octave Scale 02 · C# | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 27 | `kkG_05_027` | User Octave Scale 02 · D | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 28 | `kkG_05_028` | User Octave Scale 02 · D# | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 29 | `kkG_05_029` | User Octave Scale 02 · E | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 30 | `kkG_05_030` | User Octave Scale 02 · F | `(1346, 214, 146)` | knob `(1401, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 31 | `kkG_05_031` | User Octave Scale 02 · F# | `(5, 263, 146)` | knob `(60, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 32 | `kkG_05_032` | User Octave Scale 02 · G | `(154, 263, 146)` | knob `(209, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 33 | `kkG_05_033` | User Octave Scale 02 · G# | `(303, 263, 146)` | knob `(358, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 34 | `kkG_05_034` | User Octave Scale 02 · A | `(452, 263, 146)` | knob `(507, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 35 | `kkG_05_035` | User Octave Scale 02 · A# | `(601, 263, 146)` | knob `(656, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 36 | `kkG_05_036` | User Octave Scale 02 · B | `(750, 263, 146)` | knob `(805, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 37 | `kkG_05_037` | User Octave Scale 03 · C | `(899, 263, 146)` | knob `(954, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 38 | `kkG_05_038` | User Octave Scale 03 · C# | `(1048, 263, 146)` | knob `(1103, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 39 | `kkG_05_039` | User Octave Scale 03 · D | `(1197, 263, 146)` | knob `(1252, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 40 | `kkG_05_040` | User Octave Scale 03 · D# | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 41 | `kkG_05_041` | User Octave Scale 03 · E | `(5, 312, 146)` | knob `(60, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 42 | `kkG_05_042` | User Octave Scale 03 · F | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 43 | `kkG_05_043` | User Octave Scale 03 · F# | `(303, 312, 146)` | knob `(358, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 44 | `kkG_05_044` | User Octave Scale 03 · G | `(452, 312, 146)` | knob `(507, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 45 | `kkG_05_045` | User Octave Scale 03 · G# | `(601, 312, 146)` | knob `(656, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 46 | `kkG_05_046` | User Octave Scale 03 · A | `(750, 312, 146)` | knob `(805, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 47 | `kkG_05_047` | User Octave Scale 03 · A# | `(899, 312, 146)` | knob `(954, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 48 | `kkG_05_048` | User Octave Scale 03 · B | `(1048, 312, 146)` | knob `(1103, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 49 | `kkG_05_049` | User Octave Scale 04 · C | `(1197, 312, 146)` | knob `(1252, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 50 | `kkG_05_050` | User Octave Scale 04 · C# | `(1346, 312, 146)` | knob `(1401, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 51 | `kkG_05_051` | User Octave Scale 04 · D | `(5, 361, 146)` | knob `(60, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 52 | `kkG_05_052` | User Octave Scale 04 · D# | `(154, 361, 146)` | knob `(209, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 53 | `kkG_05_053` | User Octave Scale 04 · E | `(303, 361, 146)` | knob `(358, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 54 | `kkG_05_054` | User Octave Scale 04 · F | `(452, 361, 146)` | knob `(507, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 55 | `kkG_05_055` | User Octave Scale 04 · F# | `(601, 361, 146)` | knob `(656, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 56 | `kkG_05_056` | User Octave Scale 04 · G | `(750, 361, 146)` | knob `(805, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 57 | `kkG_05_057` | User Octave Scale 04 · G# | `(899, 361, 146)` | knob `(954, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 58 | `kkG_05_058` | User Octave Scale 04 · A | `(1048, 361, 146)` | knob `(1103, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 59 | `kkG_05_059` | User Octave Scale 04 · A# | `(1197, 361, 146)` | knob `(1252, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 60 | `kkG_05_060` | User Octave Scale 04 · B | `(1346, 361, 146)` | knob `(1401, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |

#### Tab 6 - Octave Scale·2 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkG_06_001` | User Octave Scale 05 · C | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 2 | `kkG_06_002` | User Octave Scale 05 · C# | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 3 | `kkG_06_003` | User Octave Scale 05 · D | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 4 | `kkG_06_004` | User Octave Scale 05 · D# | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 5 | `kkG_06_005` | User Octave Scale 05 · E | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 6 | `kkG_06_006` | User Octave Scale 05 · F | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 7 | `kkG_06_007` | User Octave Scale 05 · F# | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 8 | `kkG_06_008` | User Octave Scale 05 · G | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 9 | `kkG_06_009` | User Octave Scale 05 · G# | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 10 | `kkG_06_010` | User Octave Scale 05 · A | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 11 | `kkG_06_011` | User Octave Scale 05 · A# | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 12 | `kkG_06_012` | User Octave Scale 05 · B | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 13 | `kkG_06_013` | User Octave Scale 06 · C | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 14 | `kkG_06_014` | User Octave Scale 06 · C# | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 15 | `kkG_06_015` | User Octave Scale 06 · D | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 16 | `kkG_06_016` | User Octave Scale 06 · D# | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 17 | `kkG_06_017` | User Octave Scale 06 · E | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 18 | `kkG_06_018` | User Octave Scale 06 · F | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 19 | `kkG_06_019` | User Octave Scale 06 · F# | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 20 | `kkG_06_020` | User Octave Scale 06 · G | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 21 | `kkG_06_021` | User Octave Scale 06 · G# | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 22 | `kkG_06_022` | User Octave Scale 06 · A | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 23 | `kkG_06_023` | User Octave Scale 06 · A# | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 24 | `kkG_06_024` | User Octave Scale 06 · B | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 25 | `kkG_06_025` | User Octave Scale 07 · C | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 26 | `kkG_06_026` | User Octave Scale 07 · C# | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 27 | `kkG_06_027` | User Octave Scale 07 · D | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 28 | `kkG_06_028` | User Octave Scale 07 · D# | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 29 | `kkG_06_029` | User Octave Scale 07 · E | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 30 | `kkG_06_030` | User Octave Scale 07 · F | `(1346, 214, 146)` | knob `(1401, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 31 | `kkG_06_031` | User Octave Scale 07 · F# | `(5, 263, 146)` | knob `(60, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 32 | `kkG_06_032` | User Octave Scale 07 · G | `(154, 263, 146)` | knob `(209, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 33 | `kkG_06_033` | User Octave Scale 07 · G# | `(303, 263, 146)` | knob `(358, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 34 | `kkG_06_034` | User Octave Scale 07 · A | `(452, 263, 146)` | knob `(507, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 35 | `kkG_06_035` | User Octave Scale 07 · A# | `(601, 263, 146)` | knob `(656, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 36 | `kkG_06_036` | User Octave Scale 07 · B | `(750, 263, 146)` | knob `(805, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 37 | `kkG_06_037` | User Octave Scale 08 · C | `(899, 263, 146)` | knob `(954, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 38 | `kkG_06_038` | User Octave Scale 08 · C# | `(1048, 263, 146)` | knob `(1103, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 39 | `kkG_06_039` | User Octave Scale 08 · D | `(1197, 263, 146)` | knob `(1252, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 40 | `kkG_06_040` | User Octave Scale 08 · D# | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 41 | `kkG_06_041` | User Octave Scale 08 · E | `(5, 312, 146)` | knob `(60, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 42 | `kkG_06_042` | User Octave Scale 08 · F | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 43 | `kkG_06_043` | User Octave Scale 08 · F# | `(303, 312, 146)` | knob `(358, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 44 | `kkG_06_044` | User Octave Scale 08 · G | `(452, 312, 146)` | knob `(507, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 45 | `kkG_06_045` | User Octave Scale 08 · G# | `(601, 312, 146)` | knob `(656, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 46 | `kkG_06_046` | User Octave Scale 08 · A | `(750, 312, 146)` | knob `(805, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 47 | `kkG_06_047` | User Octave Scale 08 · A# | `(899, 312, 146)` | knob `(954, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 48 | `kkG_06_048` | User Octave Scale 08 · B | `(1048, 312, 146)` | knob `(1103, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 49 | `kkG_06_049` | User Octave Scale 09 · C | `(1197, 312, 146)` | knob `(1252, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 50 | `kkG_06_050` | User Octave Scale 09 · C# | `(1346, 312, 146)` | knob `(1401, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 51 | `kkG_06_051` | User Octave Scale 09 · D | `(5, 361, 146)` | knob `(60, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 52 | `kkG_06_052` | User Octave Scale 09 · D# | `(154, 361, 146)` | knob `(209, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 53 | `kkG_06_053` | User Octave Scale 09 · E | `(303, 361, 146)` | knob `(358, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 54 | `kkG_06_054` | User Octave Scale 09 · F | `(452, 361, 146)` | knob `(507, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 55 | `kkG_06_055` | User Octave Scale 09 · F# | `(601, 361, 146)` | knob `(656, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 56 | `kkG_06_056` | User Octave Scale 09 · G | `(750, 361, 146)` | knob `(805, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 57 | `kkG_06_057` | User Octave Scale 09 · G# | `(899, 361, 146)` | knob `(954, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 58 | `kkG_06_058` | User Octave Scale 09 · A | `(1048, 361, 146)` | knob `(1103, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 59 | `kkG_06_059` | User Octave Scale 09 · A# | `(1197, 361, 146)` | knob `(1252, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 60 | `kkG_06_060` | User Octave Scale 09 · B | `(1346, 361, 146)` | knob `(1401, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |

#### Tab 7 - Octave Scale·3 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkG_07_001` | User Octave Scale 10 · C | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 2 | `kkG_07_002` | User Octave Scale 10 · C# | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 3 | `kkG_07_003` | User Octave Scale 10 · D | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 4 | `kkG_07_004` | User Octave Scale 10 · D# | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 5 | `kkG_07_005` | User Octave Scale 10 · E | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 6 | `kkG_07_006` | User Octave Scale 10 · F | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 7 | `kkG_07_007` | User Octave Scale 10 · F# | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 8 | `kkG_07_008` | User Octave Scale 10 · G | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 9 | `kkG_07_009` | User Octave Scale 10 · G# | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 10 | `kkG_07_010` | User Octave Scale 10 · A | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 11 | `kkG_07_011` | User Octave Scale 10 · A# | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 12 | `kkG_07_012` | User Octave Scale 10 · B | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 13 | `kkG_07_013` | User Octave Scale 11 · C | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 14 | `kkG_07_014` | User Octave Scale 11 · C# | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 15 | `kkG_07_015` | User Octave Scale 11 · D | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 16 | `kkG_07_016` | User Octave Scale 11 · D# | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 17 | `kkG_07_017` | User Octave Scale 11 · E | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 18 | `kkG_07_018` | User Octave Scale 11 · F | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 19 | `kkG_07_019` | User Octave Scale 11 · F# | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 20 | `kkG_07_020` | User Octave Scale 11 · G | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 21 | `kkG_07_021` | User Octave Scale 11 · G# | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 22 | `kkG_07_022` | User Octave Scale 11 · A | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 23 | `kkG_07_023` | User Octave Scale 11 · A# | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 24 | `kkG_07_024` | User Octave Scale 11 · B | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 25 | `kkG_07_025` | User Octave Scale 12 · C | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 26 | `kkG_07_026` | User Octave Scale 12 · C# | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 27 | `kkG_07_027` | User Octave Scale 12 · D | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 28 | `kkG_07_028` | User Octave Scale 12 · D# | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 29 | `kkG_07_029` | User Octave Scale 12 · E | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 30 | `kkG_07_030` | User Octave Scale 12 · F | `(1346, 214, 146)` | knob `(1401, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 31 | `kkG_07_031` | User Octave Scale 12 · F# | `(5, 263, 146)` | knob `(60, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 32 | `kkG_07_032` | User Octave Scale 12 · G | `(154, 263, 146)` | knob `(209, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 33 | `kkG_07_033` | User Octave Scale 12 · G# | `(303, 263, 146)` | knob `(358, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 34 | `kkG_07_034` | User Octave Scale 12 · A | `(452, 263, 146)` | knob `(507, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 35 | `kkG_07_035` | User Octave Scale 12 · A# | `(601, 263, 146)` | knob `(656, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 36 | `kkG_07_036` | User Octave Scale 12 · B | `(750, 263, 146)` | knob `(805, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 37 | `kkG_07_037` | User Octave Scale 13 · C | `(899, 263, 146)` | knob `(954, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 38 | `kkG_07_038` | User Octave Scale 13 · C# | `(1048, 263, 146)` | knob `(1103, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 39 | `kkG_07_039` | User Octave Scale 13 · D | `(1197, 263, 146)` | knob `(1252, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 40 | `kkG_07_040` | User Octave Scale 13 · D# | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 41 | `kkG_07_041` | User Octave Scale 13 · E | `(5, 312, 146)` | knob `(60, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 42 | `kkG_07_042` | User Octave Scale 13 · F | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 43 | `kkG_07_043` | User Octave Scale 13 · F# | `(303, 312, 146)` | knob `(358, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 44 | `kkG_07_044` | User Octave Scale 13 · G | `(452, 312, 146)` | knob `(507, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 45 | `kkG_07_045` | User Octave Scale 13 · G# | `(601, 312, 146)` | knob `(656, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 46 | `kkG_07_046` | User Octave Scale 13 · A | `(750, 312, 146)` | knob `(805, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 47 | `kkG_07_047` | User Octave Scale 13 · A# | `(899, 312, 146)` | knob `(954, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 48 | `kkG_07_048` | User Octave Scale 13 · B | `(1048, 312, 146)` | knob `(1103, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 49 | `kkG_07_049` | User Octave Scale 14 · C | `(1197, 312, 146)` | knob `(1252, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 50 | `kkG_07_050` | User Octave Scale 14 · C# | `(1346, 312, 146)` | knob `(1401, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 51 | `kkG_07_051` | User Octave Scale 14 · D | `(5, 361, 146)` | knob `(60, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 52 | `kkG_07_052` | User Octave Scale 14 · D# | `(154, 361, 146)` | knob `(209, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 53 | `kkG_07_053` | User Octave Scale 14 · E | `(303, 361, 146)` | knob `(358, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 54 | `kkG_07_054` | User Octave Scale 14 · F | `(452, 361, 146)` | knob `(507, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 55 | `kkG_07_055` | User Octave Scale 14 · F# | `(601, 361, 146)` | knob `(656, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 56 | `kkG_07_056` | User Octave Scale 14 · G | `(750, 361, 146)` | knob `(805, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 57 | `kkG_07_057` | User Octave Scale 14 · G# | `(899, 361, 146)` | knob `(954, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 58 | `kkG_07_058` | User Octave Scale 14 · A | `(1048, 361, 146)` | knob `(1103, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 59 | `kkG_07_059` | User Octave Scale 14 · A# | `(1197, 361, 146)` | knob `(1252, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 60 | `kkG_07_060` | User Octave Scale 14 · B | `(1346, 361, 146)` | knob `(1401, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |

#### Tab 8 - Octave Scale·4 (12 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkG_08_001` | User Octave Scale 15 · C | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 2 | `kkG_08_002` | User Octave Scale 15 · C# | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 3 | `kkG_08_003` | User Octave Scale 15 · D | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 4 | `kkG_08_004` | User Octave Scale 15 · D# | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 5 | `kkG_08_005` | User Octave Scale 15 · E | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 6 | `kkG_08_006` | User Octave Scale 15 · F | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 7 | `kkG_08_007` | User Octave Scale 15 · F# | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 8 | `kkG_08_008` | User Octave Scale 15 · G | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 9 | `kkG_08_009` | User Octave Scale 15 · G# | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 10 | `kkG_08_010` | User Octave Scale 15 · A | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 11 | `kkG_08_011` | User Octave Scale 15 · A# | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 12 | `kkG_08_012` | User Octave Scale 15 · B | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |

#### Tab 9 - All Note Scale (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkG_09_001` | User All Note Scale · C-1 | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 2 | `kkG_09_002` | User All Note Scale · C#-1 | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 3 | `kkG_09_003` | User All Note Scale · D-1 | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 4 | `kkG_09_004` | User All Note Scale · D#-1 | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 5 | `kkG_09_005` | User All Note Scale · E-1 | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 6 | `kkG_09_006` | User All Note Scale · F-1 | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 7 | `kkG_09_007` | User All Note Scale · F#-1 | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 8 | `kkG_09_008` | User All Note Scale · G-1 | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 9 | `kkG_09_009` | User All Note Scale · G#-1 | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 10 | `kkG_09_010` | User All Note Scale · A-1 | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 11 | `kkG_09_011` | User All Note Scale · A#-1 | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 12 | `kkG_09_012` | User All Note Scale · B-1 | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 13 | `kkG_09_013` | User All Note Scale · C0 | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 14 | `kkG_09_014` | User All Note Scale · C#0 | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 15 | `kkG_09_015` | User All Note Scale · D0 | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 16 | `kkG_09_016` | User All Note Scale · D#0 | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 17 | `kkG_09_017` | User All Note Scale · E0 | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 18 | `kkG_09_018` | User All Note Scale · F0 | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 19 | `kkG_09_019` | User All Note Scale · F#0 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 20 | `kkG_09_020` | User All Note Scale · G0 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 21 | `kkG_09_021` | User All Note Scale · G#0 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 22 | `kkG_09_022` | User All Note Scale · A0 | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 23 | `kkG_09_023` | User All Note Scale · A#0 | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 24 | `kkG_09_024` | User All Note Scale · B0 | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 25 | `kkG_09_025` | User All Note Scale · C1 | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 26 | `kkG_09_026` | User All Note Scale · C#1 | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 27 | `kkG_09_027` | User All Note Scale · D1 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 28 | `kkG_09_028` | User All Note Scale · D#1 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 29 | `kkG_09_029` | User All Note Scale · E1 | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 30 | `kkG_09_030` | User All Note Scale · F1 | `(1346, 214, 146)` | knob `(1401, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 31 | `kkG_09_031` | User All Note Scale · F#1 | `(5, 263, 146)` | knob `(60, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 32 | `kkG_09_032` | User All Note Scale · G1 | `(154, 263, 146)` | knob `(209, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 33 | `kkG_09_033` | User All Note Scale · G#1 | `(303, 263, 146)` | knob `(358, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 34 | `kkG_09_034` | User All Note Scale · A1 | `(452, 263, 146)` | knob `(507, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 35 | `kkG_09_035` | User All Note Scale · A#1 | `(601, 263, 146)` | knob `(656, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 36 | `kkG_09_036` | User All Note Scale · B1 | `(750, 263, 146)` | knob `(805, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 37 | `kkG_09_037` | User All Note Scale · C2 | `(899, 263, 146)` | knob `(954, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 38 | `kkG_09_038` | User All Note Scale · C#2 | `(1048, 263, 146)` | knob `(1103, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 39 | `kkG_09_039` | User All Note Scale · D2 | `(1197, 263, 146)` | knob `(1252, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 40 | `kkG_09_040` | User All Note Scale · D#2 | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 41 | `kkG_09_041` | User All Note Scale · E2 | `(5, 312, 146)` | knob `(60, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 42 | `kkG_09_042` | User All Note Scale · F2 | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 43 | `kkG_09_043` | User All Note Scale · F#2 | `(303, 312, 146)` | knob `(358, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 44 | `kkG_09_044` | User All Note Scale · G2 | `(452, 312, 146)` | knob `(507, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 45 | `kkG_09_045` | User All Note Scale · G#2 | `(601, 312, 146)` | knob `(656, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 46 | `kkG_09_046` | User All Note Scale · A2 | `(750, 312, 146)` | knob `(805, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 47 | `kkG_09_047` | User All Note Scale · A#2 | `(899, 312, 146)` | knob `(954, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 48 | `kkG_09_048` | User All Note Scale · B2 | `(1048, 312, 146)` | knob `(1103, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 49 | `kkG_09_049` | User All Note Scale · C3 | `(1197, 312, 146)` | knob `(1252, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 50 | `kkG_09_050` | User All Note Scale · C#3 | `(1346, 312, 146)` | knob `(1401, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 51 | `kkG_09_051` | User All Note Scale · D3 | `(5, 361, 146)` | knob `(60, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 52 | `kkG_09_052` | User All Note Scale · D#3 | `(154, 361, 146)` | knob `(209, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 53 | `kkG_09_053` | User All Note Scale · E3 | `(303, 361, 146)` | knob `(358, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 54 | `kkG_09_054` | User All Note Scale · F3 | `(452, 361, 146)` | knob `(507, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 55 | `kkG_09_055` | User All Note Scale · F#3 | `(601, 361, 146)` | knob `(656, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 56 | `kkG_09_056` | User All Note Scale · G3 | `(750, 361, 146)` | knob `(805, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 57 | `kkG_09_057` | User All Note Scale · G#3 | `(899, 361, 146)` | knob `(954, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 58 | `kkG_09_058` | User All Note Scale · A3 | `(1048, 361, 146)` | knob `(1103, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 59 | `kkG_09_059` | User All Note Scale · A#3 | `(1197, 361, 146)` | knob `(1252, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 60 | `kkG_09_060` | User All Note Scale · B3 | `(1346, 361, 146)` | knob `(1401, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |

#### Tab 10 - All Note Scale·2 (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkG_10_001` | User All Note Scale · C4 | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 2 | `kkG_10_002` | User All Note Scale · C#4 | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 3 | `kkG_10_003` | User All Note Scale · D4 | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 4 | `kkG_10_004` | User All Note Scale · D#4 | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 5 | `kkG_10_005` | User All Note Scale · E4 | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 6 | `kkG_10_006` | User All Note Scale · F4 | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 7 | `kkG_10_007` | User All Note Scale · F#4 | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 8 | `kkG_10_008` | User All Note Scale · G4 | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 9 | `kkG_10_009` | User All Note Scale · G#4 | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 10 | `kkG_10_010` | User All Note Scale · A4 | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 11 | `kkG_10_011` | User All Note Scale · A#4 | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 12 | `kkG_10_012` | User All Note Scale · B4 | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 13 | `kkG_10_013` | User All Note Scale · C5 | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 14 | `kkG_10_014` | User All Note Scale · C#5 | `(452, 165, 146)` | knob `(507, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 15 | `kkG_10_015` | User All Note Scale · D5 | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 16 | `kkG_10_016` | User All Note Scale · D#5 | `(750, 165, 146)` | knob `(805, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 17 | `kkG_10_017` | User All Note Scale · E5 | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 18 | `kkG_10_018` | User All Note Scale · F5 | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 19 | `kkG_10_019` | User All Note Scale · F#5 | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 20 | `kkG_10_020` | User All Note Scale · G5 | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 21 | `kkG_10_021` | User All Note Scale · G#5 | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 22 | `kkG_10_022` | User All Note Scale · A5 | `(154, 214, 146)` | knob `(209, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 23 | `kkG_10_023` | User All Note Scale · A#5 | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 24 | `kkG_10_024` | User All Note Scale · B5 | `(452, 214, 146)` | knob `(507, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 25 | `kkG_10_025` | User All Note Scale · C6 | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 26 | `kkG_10_026` | User All Note Scale · C#6 | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 27 | `kkG_10_027` | User All Note Scale · D6 | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 28 | `kkG_10_028` | User All Note Scale · D#6 | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 29 | `kkG_10_029` | User All Note Scale · E6 | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 30 | `kkG_10_030` | User All Note Scale · F6 | `(1346, 214, 146)` | knob `(1401, 226)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 31 | `kkG_10_031` | User All Note Scale · F#6 | `(5, 263, 146)` | knob `(60, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 32 | `kkG_10_032` | User All Note Scale · G6 | `(154, 263, 146)` | knob `(209, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 33 | `kkG_10_033` | User All Note Scale · G#6 | `(303, 263, 146)` | knob `(358, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 34 | `kkG_10_034` | User All Note Scale · A6 | `(452, 263, 146)` | knob `(507, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 35 | `kkG_10_035` | User All Note Scale · A#6 | `(601, 263, 146)` | knob `(656, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 36 | `kkG_10_036` | User All Note Scale · B6 | `(750, 263, 146)` | knob `(805, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 37 | `kkG_10_037` | User All Note Scale · C7 | `(899, 263, 146)` | knob `(954, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 38 | `kkG_10_038` | User All Note Scale · C#7 | `(1048, 263, 146)` | knob `(1103, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 39 | `kkG_10_039` | User All Note Scale · D7 | `(1197, 263, 146)` | knob `(1252, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 40 | `kkG_10_040` | User All Note Scale · D#7 | `(1346, 263, 146)` | knob `(1401, 275)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 41 | `kkG_10_041` | User All Note Scale · E7 | `(5, 312, 146)` | knob `(60, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 42 | `kkG_10_042` | User All Note Scale · F7 | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 43 | `kkG_10_043` | User All Note Scale · F#7 | `(303, 312, 146)` | knob `(358, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 44 | `kkG_10_044` | User All Note Scale · G7 | `(452, 312, 146)` | knob `(507, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 45 | `kkG_10_045` | User All Note Scale · G#7 | `(601, 312, 146)` | knob `(656, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 46 | `kkG_10_046` | User All Note Scale · A7 | `(750, 312, 146)` | knob `(805, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 47 | `kkG_10_047` | User All Note Scale · A#7 | `(899, 312, 146)` | knob `(954, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 48 | `kkG_10_048` | User All Note Scale · B7 | `(1048, 312, 146)` | knob `(1103, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 49 | `kkG_10_049` | User All Note Scale · C8 | `(1197, 312, 146)` | knob `(1252, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 50 | `kkG_10_050` | User All Note Scale · C#8 | `(1346, 312, 146)` | knob `(1401, 324)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 51 | `kkG_10_051` | User All Note Scale · D8 | `(5, 361, 146)` | knob `(60, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 52 | `kkG_10_052` | User All Note Scale · D#8 | `(154, 361, 146)` | knob `(209, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 53 | `kkG_10_053` | User All Note Scale · E8 | `(303, 361, 146)` | knob `(358, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 54 | `kkG_10_054` | User All Note Scale · F8 | `(452, 361, 146)` | knob `(507, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 55 | `kkG_10_055` | User All Note Scale · F#8 | `(601, 361, 146)` | knob `(656, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 56 | `kkG_10_056` | User All Note Scale · G8 | `(750, 361, 146)` | knob `(805, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 57 | `kkG_10_057` | User All Note Scale · G#8 | `(899, 361, 146)` | knob `(954, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 58 | `kkG_10_058` | User All Note Scale · A8 | `(1048, 361, 146)` | knob `(1103, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 59 | `kkG_10_059` | User All Note Scale · A#8 | `(1197, 361, 146)` | knob `(1252, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 60 | `kkG_10_060` | User All Note Scale · B8 | `(1346, 361, 146)` | knob `(1401, 373)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |

#### Tab 11 - All Note Scale·3 (8 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkG_11_001` | User All Note Scale · C9 | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 2 | `kkG_11_002` | User All Note Scale · C#9 | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 3 | `kkG_11_003` | User All Note Scale · D9 | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 4 | `kkG_11_004` | User All Note Scale · D#9 | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 5 | `kkG_11_005` | User All Note Scale · E9 | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 6 | `kkG_11_006` | User All Note Scale · F9 | `(750, 116, 146)` | knob `(805, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 7 | `kkG_11_007` | User All Note Scale · F#9 | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |
| 8 | `kkG_11_008` | User All Note Scale · G9 | `(1048, 116, 146)` | knob `(1103, 128)` 36x36 rotary | -99..99 step 1.0 (0 dec) | global | global |

#### Tab 12 - Audio In (48 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkG_12_001` | Audio Input 0 · Level | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 2 | `kkG_12_002` | Audio Input 0 · Pan | `(154, 116, 146)` | knob `(209, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 3 | `kkG_12_003` | Audio Input 0 · Send1 (To MFX1) | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 4 | `kkG_12_004` | Audio Input 0 · Send2 (To MFX2) | `(452, 116, 146)` | knob `(507, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 5 | `kkG_12_005` | Audio Input 0 · Bus Select (IFX/Indiv.) | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..25 step 1.0 (0 dec) | global | global |
| 6 | `kkG_12_006` | Audio Input 0 · FX Control Bus | `(750, 116, 146)` | combo `(750, 129)` 146x20 | Off \| 1 \| 2 | global | global |
| 7 | `kkG_12_007` | Audio Input 0 · REC Bus | `(899, 116, 146)` | combo `(899, 129)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | global | global |
| 8 | `kkG_12_008` | Audio Input 0 · Mute | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | Off \| On | global | global |
| 9 | `kkG_12_009` | Audio Input 1 · Level | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 10 | `kkG_12_010` | Audio Input 1 · Pan | `(1346, 116, 146)` | knob `(1401, 128)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 11 | `kkG_12_011` | Audio Input 1 · Send1 (To MFX1) | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 12 | `kkG_12_012` | Audio Input 1 · Send2 (To MFX2) | `(154, 165, 146)` | knob `(209, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 13 | `kkG_12_013` | Audio Input 1 · Bus Select (IFX/Indiv.) | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..25 step 1.0 (0 dec) | global | global |
| 14 | `kkG_12_014` | Audio Input 1 · FX Control Bus | `(452, 165, 146)` | combo `(452, 178)` 146x20 | Off \| 1 \| 2 | global | global |
| 15 | `kkG_12_015` | Audio Input 1 · REC Bus | `(601, 165, 146)` | combo `(601, 178)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | global | global |
| 16 | `kkG_12_016` | Audio Input 1 · Mute | `(750, 165, 146)` | combo `(750, 178)` 146x20 | Off \| On | global | global |
| 17 | `kkG_12_017` | USB Input L · Level | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 18 | `kkG_12_018` | USB Input L · Pan | `(1048, 165, 146)` | knob `(1103, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 19 | `kkG_12_019` | USB Input L · Send1 (To MFX1) | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 20 | `kkG_12_020` | USB Input L · Send2 (To MFX2) | `(1346, 165, 146)` | knob `(1401, 177)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 21 | `kkG_12_021` | USB Input L · Bus Select (IFX/Indiv.) | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | global | global |
| 22 | `kkG_12_022` | USB Input L · FX Control Bus | `(154, 214, 146)` | combo `(154, 227)` 146x20 | Off \| 1 \| 2 | global | global |
| 23 | `kkG_12_023` | USB Input L · REC Bus | `(303, 214, 146)` | combo `(303, 227)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | global | global |
| 24 | `kkG_12_024` | USB Input L · Mute | `(452, 214, 146)` | combo `(452, 227)` 146x20 | Off \| On | global | global |
| 25 | `kkG_12_025` | USB Input R · Level | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 26 | `kkG_12_026` | USB Input R · Pan | `(750, 214, 146)` | knob `(805, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 27 | `kkG_12_027` | USB Input R · Send1 (To MFX1) | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 28 | `kkG_12_028` | USB Input R · Send2 (To MFX2) | `(1048, 214, 146)` | knob `(1103, 226)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 29 | `kkG_12_029` | USB Input R · Bus Select (IFX/Indiv.) | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..25 step 1.0 (0 dec) | global | global |
| 30 | `kkG_12_030` | USB Input R · FX Control Bus | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | Off \| 1 \| 2 | global | global |
| 31 | `kkG_12_031` | USB Input R · REC Bus | `(5, 263, 146)` | combo `(5, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | global | global |
| 32 | `kkG_12_032` | USB Input R · Mute | `(154, 263, 146)` | combo `(154, 276)` 146x20 | Off \| On | global | global |
| 33 | `kkG_12_033` | S/P DIF Input L · Level | `(303, 263, 146)` | knob `(358, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 34 | `kkG_12_034` | S/P DIF Input L · Pan | `(452, 263, 146)` | knob `(507, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 35 | `kkG_12_035` | S/P DIF Input L · Send1 (To MFX1) | `(601, 263, 146)` | knob `(656, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 36 | `kkG_12_036` | S/P DIF Input L · Send2 (To MFX2) | `(750, 263, 146)` | knob `(805, 275)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 37 | `kkG_12_037` | S/P DIF Input L · Bus Select (IFX/Indiv.) | `(899, 263, 146)` | knob `(954, 275)` 36x36 rotary | 0..25 step 1.0 (0 dec) | global | global |
| 38 | `kkG_12_038` | S/P DIF Input L · FX Control Bus | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | Off \| 1 \| 2 | global | global |
| 39 | `kkG_12_039` | S/P DIF Input L · REC Bus | `(1197, 263, 146)` | combo `(1197, 276)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | global | global |
| 40 | `kkG_12_040` | S/P DIF Input L · Mute | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | Off \| On | global | global |
| 41 | `kkG_12_041` | S/P DIF Input R · Level | `(5, 312, 146)` | knob `(60, 324)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 42 | `kkG_12_042` | S/P DIF Input R · Pan | `(154, 312, 146)` | knob `(209, 324)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 43 | `kkG_12_043` | S/P DIF Input R · Send1 (To MFX1) | `(303, 312, 146)` | knob `(358, 324)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 44 | `kkG_12_044` | S/P DIF Input R · Send2 (To MFX2) | `(452, 312, 146)` | knob `(507, 324)` 36x36 rotary | 0..127 step 1.0 (0 dec) | global | global |
| 45 | `kkG_12_045` | S/P DIF Input R · Bus Select (IFX/Indiv.) | `(601, 312, 146)` | knob `(656, 324)` 36x36 rotary | 0..25 step 1.0 (0 dec) | global | global |
| 46 | `kkG_12_046` | S/P DIF Input R · FX Control Bus | `(750, 312, 146)` | combo `(750, 325)` 146x20 | Off \| 1 \| 2 | global | global |
| 47 | `kkG_12_047` | S/P DIF Input R · REC Bus | `(899, 312, 146)` | combo `(899, 325)` 146x20 | Off \| 1 \| 2 \| 3 \| 4 \| 5 \| 3/4 | global | global |
| 48 | `kkG_12_048` | S/P DIF Input R · Mute | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | Off \| On | global | global |

#### Tab 13 - Assignments (60 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkG_13_001` | Assignments · Assignment | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 2 | `kkG_13_002` | Assignments · Program Down         Channel | `(154, 116, 146)` | combo `(154, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 3 | `kkG_13_003` | Assignments · Assignment | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 4 | `kkG_13_004` | Assignments · Song Start/Stop      Channel | `(452, 116, 146)` | combo `(452, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 5 | `kkG_13_005` | Assignments · Assignment | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 6 | `kkG_13_006` | Assignments · Song Punch In        Channel | `(750, 116, 146)` | combo `(750, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 7 | `kkG_13_007` | Assignments · Assignment | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 8 | `kkG_13_008` | Assignments · Tap Tempo            Channel | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 9 | `kkG_13_009` | Assignments · Assignment | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 10 | `kkG_13_010` | Assignments · Ovtave Up            Channel | `(1346, 116, 146)` | combo `(1346, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 11 | `kkG_13_011` | Assignments · Assignment | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 12 | `kkG_13_012` | Assignments · Ovtave Down          Channel | `(154, 165, 146)` | combo `(154, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 13 | `kkG_13_013` | Assignments · Assignment | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 14 | `kkG_13_014` | Assignments · Ribbon Lock          Channel | `(452, 165, 146)` | combo `(452, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 15 | `kkG_13_015` | Assignments · Assignment | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 16 | `kkG_13_016` | Assignments · RT Knob 1            Channel | `(750, 165, 146)` | combo `(750, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 17 | `kkG_13_017` | Assignments · Assignment | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 18 | `kkG_13_018` | Assignments · RT Knob 2            Channel | `(1048, 165, 146)` | combo `(1048, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 19 | `kkG_13_019` | Assignments · Assignment | `(1197, 165, 146)` | knob `(1252, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 20 | `kkG_13_020` | Assignments · RT Knob 3            Channel | `(1346, 165, 146)` | combo `(1346, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 21 | `kkG_13_021` | Assignments · Assignment | `(5, 214, 146)` | knob `(60, 226)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 22 | `kkG_13_022` | Assignments · RT Knob 4            Channel | `(154, 214, 146)` | combo `(154, 227)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 23 | `kkG_13_023` | Assignments · Assignment | `(303, 214, 146)` | knob `(358, 226)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 24 | `kkG_13_024` | Assignments · RT Knob 5            Channel | `(452, 214, 146)` | combo `(452, 227)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 25 | `kkG_13_025` | Assignments · Assignment | `(601, 214, 146)` | knob `(656, 226)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 26 | `kkG_13_026` | Assignments · RT Knob 6            Channel | `(750, 214, 146)` | combo `(750, 227)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 27 | `kkG_13_027` | Assignments · Assignment | `(899, 214, 146)` | knob `(954, 226)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 28 | `kkG_13_028` | Assignments · RT Knob 7            Channel | `(1048, 214, 146)` | combo `(1048, 227)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 29 | `kkG_13_029` | Assignments · Assignment | `(1197, 214, 146)` | knob `(1252, 226)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 30 | `kkG_13_030` | Assignments · RT Knob 8            Channel | `(1346, 214, 146)` | combo `(1346, 227)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 31 | `kkG_13_031` | Assignments · Assignment | `(5, 263, 146)` | knob `(60, 275)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 32 | `kkG_13_032` | Assignments · Pad 1                Channel | `(154, 263, 146)` | combo `(154, 276)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 33 | `kkG_13_033` | Assignments · Assignment | `(303, 263, 146)` | knob `(358, 275)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 34 | `kkG_13_034` | Assignments · Pad 2                Channel | `(452, 263, 146)` | combo `(452, 276)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 35 | `kkG_13_035` | Assignments · Assignment | `(601, 263, 146)` | knob `(656, 275)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 36 | `kkG_13_036` | Assignments · Pad 3                Channel | `(750, 263, 146)` | combo `(750, 276)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 37 | `kkG_13_037` | Assignments · Assignment | `(899, 263, 146)` | knob `(954, 275)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 38 | `kkG_13_038` | Assignments · Pad 4                Channel | `(1048, 263, 146)` | combo `(1048, 276)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 39 | `kkG_13_039` | Assignments · Assignment | `(1197, 263, 146)` | knob `(1252, 275)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 40 | `kkG_13_040` | Assignments · Pad 5                Channel | `(1346, 263, 146)` | combo `(1346, 276)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 41 | `kkG_13_041` | Assignments · Assignment | `(5, 312, 146)` | knob `(60, 324)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 42 | `kkG_13_042` | Assignments · Pad 6                Channel | `(154, 312, 146)` | combo `(154, 325)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 43 | `kkG_13_043` | Assignments · Assignment | `(303, 312, 146)` | knob `(358, 324)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 44 | `kkG_13_044` | Assignments · Pad 7                Channel | `(452, 312, 146)` | combo `(452, 325)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 45 | `kkG_13_045` | Assignments · Assignment | `(601, 312, 146)` | knob `(656, 324)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 46 | `kkG_13_046` | Assignments · Pad 8                Channel | `(750, 312, 146)` | combo `(750, 325)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 47 | `kkG_13_047` | Assignments · Assignment | `(899, 312, 146)` | knob `(954, 324)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 48 | `kkG_13_048` | Assignments · JS X Lock            Channel | `(1048, 312, 146)` | combo `(1048, 325)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 49 | `kkG_13_049` | Assignments · Assignment | `(1197, 312, 146)` | knob `(1252, 324)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 50 | `kkG_13_050` | Assignments · JS Y Lock            Channel | `(1346, 312, 146)` | combo `(1346, 325)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 51 | `kkG_13_051` | Assignments · Assignment | `(5, 361, 146)` | knob `(60, 373)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 52 | `kkG_13_052` | Assignments · JS +Y Lock           Channel | `(154, 361, 146)` | combo `(154, 374)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 53 | `kkG_13_053` | Assignments · Assignment | `(303, 361, 146)` | knob `(358, 373)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 54 | `kkG_13_054` | Assignments · JS -Y Lock           Channel | `(452, 361, 146)` | combo `(452, 374)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 55 | `kkG_13_055` | Assignments · Assignment | `(601, 361, 146)` | knob `(656, 373)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 56 | `kkG_13_056` | Assignments · JS X & Ribbon Lock   Channel | `(750, 361, 146)` | combo `(750, 374)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 57 | `kkG_13_057` | Assignments · Assignment | `(899, 361, 146)` | knob `(954, 373)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 58 | `kkG_13_058` | Assignments · JS Y & Ribbon Lock   Channel | `(1048, 361, 146)` | combo `(1048, 374)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 59 | `kkG_13_059` | Assignments · Assignment | `(1197, 361, 146)` | knob `(1252, 373)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 60 | `kkG_13_060` | Assignments · JS +Y & Ribbon Lock  Channel | `(1346, 361, 146)` | combo `(1346, 374)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |

#### Tab 14 - Assignments·2 (18 params)

| # | Modulator | Label | Cell (x,y,w) | Control | Range / Options | Apply | Set |
|---|---|---|---|---|---|---|---|
| 1 | `kkG_14_001` | Assignments · Assignment | `(5, 116, 146)` | knob `(60, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 2 | `kkG_14_002` | Assignments · JS -Y & Ribbon Lock  Channel | `(154, 116, 146)` | combo `(154, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 3 | `kkG_14_003` | Assignments · Assignment | `(303, 116, 146)` | knob `(358, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 4 | `kkG_14_004` | Assignments · SW 1                 Channel | `(452, 116, 146)` | combo `(452, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 5 | `kkG_14_005` | Assignments · Assignment | `(601, 116, 146)` | knob `(656, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 6 | `kkG_14_006` | Assignments · SW 2                 Channel | `(750, 116, 146)` | combo `(750, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 7 | `kkG_14_007` | Assignments · Assignment | `(899, 116, 146)` | knob `(954, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 8 | `kkG_14_008` | Assignments · Value Inc            Channel | `(1048, 116, 146)` | combo `(1048, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 9 | `kkG_14_009` | Assignments · Assignment | `(1197, 116, 146)` | knob `(1252, 128)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 10 | `kkG_14_010` | Assignments · Value Dec            Channel | `(1346, 116, 146)` | combo `(1346, 129)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 11 | `kkG_14_011` | Assignments · Assignment | `(5, 165, 146)` | knob `(60, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 12 | `kkG_14_012` | Assignments · Chord SW             Channel | `(154, 165, 146)` | combo `(154, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 13 | `kkG_14_013` | Assignments · Assignment | `(303, 165, 146)` | knob `(358, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 14 | `kkG_14_014` | Assignments · Drum Track Enable    Channel | `(452, 165, 146)` | combo `(452, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 15 | `kkG_14_015` | Assignments · Assignment | `(601, 165, 146)` | knob `(656, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 16 | `kkG_14_016` | Assignments · After Touch Lock     Channel | `(750, 165, 146)` | combo `(750, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |
| 17 | `kkG_14_017` | Assignments · Assignment | `(899, 165, 146)` | knob `(954, 177)` 36x36 rotary | 0..120 step 1.0 (0 dec) | global | global |
| 18 | `kkG_14_018` | Special Function · Program Up           Channel | `(1048, 165, 146)` | combo `(1048, 178)` 146x20 | 1 \| 1 \| 2 \| 3 \| 4 \| 5 \| 6 \| 7 \| 8 \| 9 \| 10 \| 11 \| 12 \| 13 \| 14 \| 15 \| Gch | global | global |


