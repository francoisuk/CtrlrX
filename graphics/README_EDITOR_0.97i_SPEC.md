# Kronos Kontrol - Editor window - maintainer pack

Purpose: everything needed to **redesign the GUI of the Editor window** offline (artwork + layout),
without touching the Lua/Ctrlr code. Panel version: **`complet-0.97i`**.

## Contents

- **`EDITOR_WINDOW.md`** - the full specification: window frame, every fixed button/menu with exact
  coordinates, the five section-tab-bars with their complete tab lists, the generated-control grid
  pattern, the per-object "General" tab layouts, behavior/callbacks/guards, and **complete per-page
  parameter tables for all 5 object types** (3024 generated parameters).
- **Screen captures** of the running panel (savihost3), one per Editor tab (one capture when two tabs share the same
  window, e.g. EXi1 / EXi2): `editor_<n>_<page>.jpg` in `11_Graphics_ideas\ideas` (not copied here).
- **`KRONOS_Editor\`, `OASYS_Editor\`, `NAUTILUS_Editor\`** - the redesigned Editor window: the 0.97i pages and the complete
  editor (every parameter of every object, Drum Kit / Wave Seq / Global included). Start with
  `KRONOS_Editor\README_EDITOR_KRONOS.md`.

## Object types covered

| Object | Tabs | Generated params | Captured? |
|---|---|---|---|
| Program | 24 | 404 | yes |
| Combi | 43 | 1930 | yes (captures not in this folder) |
| Drum Kit | 6 | 71 | **no** - needs a Kronos to send a `0x4B` obj 04 dump |
| Wave Seq | 3 | 28 | **no** - needs a Kronos to send a `0x4B` obj 05 dump |
| Global | 15 | 591 | **no** - needs a Kronos to send a `0x4B` obj 03 dump |

The Drum Kit / Wave Seq / Global Editor tabs are fully specified in `EDITOR_WINDOW.md` (sections 3, 4.4,
6.3-6.5); their screen captures are missing, because producing them requires a live `0x4B` dump of
those object types, which only the Kronos can send. Their redesigned pages exist in the complete editor
(`KRONOS_Editor\Full\DrumKit`, `WaveSeq`, `Global`), drawn from Korg's MIDI Implementation tables.

## Coordinate system

Panel pixels, origin top-left, native size **1500 x 414**. The Editor window is panel tab 1 (`EDIT`),
i.e. the full panel area.

