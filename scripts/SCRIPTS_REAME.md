# /scripts — helper scripts

This folder holds the build-time tools that bridge the knowledge base in
`/reference` and the Ctrlr panel in `/panels/KronosKontrol`. Each script
runs on demand. None of them are part of the panel's runtime.

*(Filename kept as `SCRIPTS_REAME.md` — historical typo, referenced by
other documents.)*

## Contents (actual disk state, 2026-10-24)

```
scripts
├── gen_data_lua.py       Phase B generator: names + GE -> data/kronos_data.lua
├── kronos_sysex.py       Python SysEx/MIDI message library (hardware-tested)
├── vt2xml.py             .bpanelz reader (zlib + JUCE ValueTree -> XML)
├── panneau_rack/         rack drawing scripts (see its README.md)
│   ├── kontrol.py            main: draws the panel, writes the SVG/PNG
│   ├── rack.py               graphics bricks (encoder, text, button, slider)
│   ├── k3vec.py              vector drawing of the Kronos 3 front
│   ├── txt2path.py           converts <text> to paths (no font dependency)
│   ├── fond_device.py        background image without active parts
│   └── README.md             usage notes (French)
└── SCRIPTS_REAME.md      this file
```

## Scripts

| Script | Input | Output | Notes |
|---|---|---|---|
| `gen_data_lua.py` | `reference/ref-kronos/m4l/names.json` (4,233 names), `reference/ref-kronos/m4l/ge_kronos.json` (3,584 GEs) | `panels/KronosKontrol/data/kronos_data.lua` | Merged Phase B generator. Repointed 2026-10-24 from `consolidate/06_max_for_live/sources/` (folder no longer used) to `reference/ref-kronos/m4l/`; regenerated — the data is identical, only the source-path header comments changed. Idempotent. |
| `kronos_sysex.py` | — | — | Standalone Python 3 module (no dependencies) that builds and parses Kronos MIDI/SysEx: Parameter Change (fn 43), Mode Change (4E), Mode Request (12), bank/program select (CC0/CC32/PC, Bank Map KORG), plain CCs; decodes fn 43/4E/42/24 replies. Byte formulas verified against the working M4L device. Self-test: `python kronos_sysex.py` checks the produced bytes against the device. Real sending is optional (`pip install mido python-rtmidi`, see bottom of the file). |
| `vt2xml.py` | a decompressed `.bpanelz` (binary JUCE ValueTree) | readable XML | Used to read `panels/TR-Rack-Editor-main/Tr Rack Editor.bpanelz` without opening Ctrlr. Usage: `python -c "import zlib;open('p.bin','wb').write(zlib.decompress(open('X.bpanelz','rb').read()))"` then `python vt2xml.py p.bin p.xml`. |
| `panneau_rack/` | — | SVG/PNG artwork | The rack design scripts (Python 3, `pip install cairosvg fonttools pillow`, fonts via `FONT_DIR` in `txt2path.py`). The finished artwork is kept in `GUI_pic/panneau_rack/` and `GUI_pic/`; the design notes are in `panels/KronosKontrol/LISEZMOI_panneau.md`. See `panneau_rack/README.md`. |

## History note

An earlier version of this README described a Phase A chain
(`extract_sxformat.py`, `decode_sysex.py`, `build_param_map.py`) and two
split generators (`gen_names_lua.py`, `gen_ge_lua.py`). **Those scripts
never existed on disk.** The parameter map CSV was produced by direct
analysis of the base patch and the Korg tables, and the two split
generators were superseded by the merged `gen_data_lua.py` before any
file was written. Do not recreate them.

## Rules

1. **Scripts read from `/reference` and write to
   `/panels/KronosKontrol`.** They never modify `/reference`,
   `/docs`, or `/build`.
2. **Deterministic output.** Running a generator twice must produce
   byte-identical output. No timestamps in generated files.
3. **No hardcoded absolute paths.** Use paths relative to the project
   root. The project may be moved.
4. **Plain Python 3, no pip installs** for the generators. (The rack
   drawing scripts excepted: they need cairosvg/fonttools/pillow, and
   are design tools, not build tools.)
5. **Each script has a docstring or header comment** stating what it
   reads and what it writes. No exceptions.
6. **Scripts are re-runnable.** If the underlying data changes,
   re-running must regenerate correctly.

## When to run

- **After any change to `reference/ref-kronos/m4l/names.json` or
  `ge_kronos.json`:** `python scripts/gen_data_lua.py`, then rebuild
  the panel (`python panels/KronosKontrol/sources/build_panel.py`).
- **To re-read TR-Rack:** decompress the `.bpanelz`, then
  `python scripts/vt2xml.py p.bin p.xml`.
- **To check the SysEx bytes** against the M4L device:
  `python scripts/kronos_sysex.py` (self-test).
- **To redraw the rack art:** see `scripts/panneau_rack/README.md`.

## When to add a new script

Add a script when:

- A transformation is needed more than once.
- The transformation is mechanical (no design decisions).
- The output is a file that lives under `/panels/KronosKontrol/`.

Do not add a script for one-off work. Do not add a script that modifies
`/reference` or `/docs`.
