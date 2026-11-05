# NAUTILUS NAVIGATOR — EDITOR window artwork

Complete editor for the **Korg NAUTILUS**, in the NAUTILUS NAVIGATOR skin (theme A, "noir abyssal": satin black,
teal accents, dark TFT-style displays, Montserrat titles). Same page frame, navigation and files as the complete
KRONOS editor: read `KRONOS_Editor\README_EDITOR_KRONOS.md` and `KRONOS_Editor\RECIPES_GUI_DRAWING.md` first;
the scripts are in `KRONOS_Editor\sources_Editor\` (`knaut.py`).

## Source

Generated from the NAUTILUS's own tables: `C:\Korg\Manuals Nautilus\NAUTILUS_MIDIimp\SysExDumps\*.txt` (same format as
the KRONOS ones). The `korg` block of every control in the `_layout.json` files gives the **NAUTILUS** offsets.

## What differs from the KRONOS

| Area | KRONOS | NAUTILUS |
|---|---|---|
| Real-time performance | KARMA (common + modules) | **Arpeggiators / step sequencers A-D** (`Step Seq. A`-`D`, 836 parameters each) + **SCENES** (Scene Common, scenes 1-4) |
| Vector joystick | Vector Control | **X-Y Control** (X-Y area) |
| Controllers | Controller, Assignable Controller | **RT Controller** (155), Assignable Controller, Tone Adjust |
| Drum Track | program and combi | not in the NAUTILUS tables (no DRUM TRACK area) |
| Audio inputs | inputs 1-4, S/PDIF L/R | inputs 1-2 and **USB 1-2** (one table) |
| Global | external MIDI sets 1-128, KARMA categories | **QUICK ACCESS** (common + user 1-n, slots A-F), program and combi categories, assignments; no external MIDI sets |
| Extra object | — | **Arp Pattern** (`ArpPattern.txt`): pattern common, tones 1-12, steps |
| EXi engines | 8 engines | the same 8 engines (AL-1, CX-3, STR-1, MS-20EX, PolysixEX, MOD-7, SGX-2, EP-1) |

## Objects and navigation

| Object | Folder / zip | Areas |
|---|---|---|
| Program | `Program` | GENERAL, OSC, FILTER, AMP, LFO·MIX (OSC 1-2), COMMON MOD, EXi (1-2), STEP SEQ, ENGINE ▸, EFFECTS, FX EDIT ▸, X-Y, CONTROL, SCENES, ARP / STEP SEQ (A-D), AUDIO IN |
| EXi engines | `Engine_<name>` | MAIN, OSC, FILTER, AMP·MIX, EG, LFO, MOD, FX |
| Combi | `Combi` | GENERAL, TIMBRE (1-16), EFFECTS, FX EDIT ▸, X-Y, CONTROL, SCENES, ARP / STEP SEQ (A-D), AUDIO IN |
| Song | `Song` | SONG, MIDI TRACKS, AUTOMATION, AUDIO TRACKS, PATTERNS, RPPR, TIMBRE SET ▸ |
| Global | `Global` | BASIC, CONTROLLER, MIDI, AUDIO IN, OCTAVE SCALES, ALL NOTE SCALE, CATEGORIES, QUICK ACCESS, QUICK USER, ASSIGNMENTS |
| Drum Kit, Wave Seq, Set List | `DrumKit`, `WaveSeq`, `SetList` | as on the KRONOS |
| Arp Pattern | `ArpPattern` | PATTERN, STEP |
| Effects | `Effects` | FX EDIT (one template + `FX_LAYOUTS.json`) |

The 0.97i set (`KRONOS_Editor\0.97i`) exists only for the KRONOS: it mirrors the current KRONOS Lua panel.

## Files

Per page: `_maquette.jpg` (one mock-up, JPEG because of the textured skin), `_fond.png`, `_fond@2x.png` and `_layout.json`. Effects: one template (`…_FX_TEMPLATE_fond`, `…_FX_TEMPLATE_maquette`) and `FX_LAYOUTS.json`; no image per effect type. SVG files and @2x mock-ups can be regenerated with the scripts (`GFX_EXTRAS=1`).
