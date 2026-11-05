# Kronos Kontrol — User Manual

**Kronos Kontrol 1.0i** is a control panel and deep editor for the **Korg KRONOS**
(workstation, OS 3.2.3). It is delivered as two desktop applications built from the
same panel:

| Build | File | Use it… |
|---|---|---|
| **VST3 plug-in** (`Instrument / Synth`) | `Kronos Kontrol.vst3` | inside a DAW (REAPER, Ableton, Bitwig, FL Studio, …) |
| **Standalone application** | `Kronos Kontrol.exe` | by itself, with any MIDI interface |

Both builds talk to the KRONOS over **USB MIDI** (or any MIDI port pair you assign)
and speak the KRONOS SysEx dialect: program/combi selection, real-time control,
full sound dumps, slot writes and bank management.

## What it does

The panel has two views, switched with the **EDITOR** button:

- **RACK** — a software replica of the KRONOS front panel: 8 rotary encoders and
  9 faders (the *Tone Adjust* / mixer controls), 14 bank selectors, 16 effect
  switches, the KARMA section (8 switches, 8 sliders, 8 scenes), the X-Y pad,
  Global Edit (GE) menus, drum-track switches, the transport cluster
  (**PCG / IMPORT / PLAY / SAVE / WRITE**) and a program selector with a
  name popup.
- **EDIT** — a page-based editor with **215 numbered pages plus the FX EDIT
  template** (216 page views) covering **7 object types**
  (Program, Combi, Drum Kit, Wave Sequence, Global, Set List, Song) and
  **7 247 parameters**. You read the current sound from the KRONOS into the
  editor (a *dump*), edit parameters on the pages, then send the result back —
  to the edit buffer (*Apply*), to a memory slot (*Write*), or save a whole
  bank (*Store*).

## Requirements

- A Korg KRONOS running **OS 3.2.x**, connected by USB (or via a MIDI interface).
- Windows. The panel window has a **fixed native size of 1500 × 432 px** — use a
  screen at least **1500 px wide** (about 500 px tall with the window chrome), or
  use the DAW's plug-in GUI scaling, or the standalone's zoom
  (**Ctrl + mouse wheel**, 1–1000 %).
- One MIDI input and one MIDI output routed to the KRONOS.

!!! note "Release builds and the licence"
    Release builds are *restricted instances*: at first launch they show the
    **License Agreement** window (EULA) — accept it once to use the application.
    Keep only **one** build of the VST3 installed at a time: every build shares
    the same plug-in UID, and your DAW may otherwise load an older file.

## How this manual is organised

Following the [Diátaxis](https://diataxis.fr/) framework:

- **Tutorials** — step-by-step lessons for first use (start here).
- **How-to guides** — task-oriented recipes: connect MIDI, select sounds, edit
  pages, save presets, load PCG files, use the VST3/standalone.
- **Explanation** — the concepts behind the panel (RACK/EDIT, dumps, SysEx
  functions, pages and parameters).
- **Reference** — complete tables: the 215 numbered pages plus the FX EDIT
  template (216 page views), the 895 panel controls (modulators), the MIDI map
  and SysEx functions, glossary.

Terminology in this manual (page titles, control names such as *Apply*,
*Read sound*, *Store 0x4C*) comes straight from the panel itself.

## Quick start

1. Connect the KRONOS by USB MIDI and power it on.
2. Open Kronos Kontrol (VST3 in your DAW, or the standalone EXE) and route the
   DAW/standalone MIDI ports to the KRONOS in *MIDI setup* — see
   [Connect MIDI and set the channel](how-to/midi-setup.md).
3. The panel sends a **Mode Request** at load; the KRONOS answers with its mode
   (COMBI / PROGRAM / …), shown in the message line.
4. Press **PROG** or **COMBI**, pick a bank (1–14) and a program (▲/▼ or the
   number field), then follow
   [Tutorial: edit and save a Program](tutorials/edit-and-save-a-program.md).
