# sources_Editor — scripts that draw the EDITOR pages

| File | Role |
|---|---|
| `kt.py`, `themes.py`, `txt2path.py`, `txt2path_ext.py`, `fonts\`, `logo_kronoscopie.svg` | Main panel drawing library (same files as `sources_Main` in `KRONOS_Main`, `OASYS_Main`, `NAUTILUS_Main`): primitives, themes KRONOS KONTROL / OASYS OMNI / NAUTILUS NAVIGATOR, text-to-path conversion |
| `ked.py` | EDITOR frame (header, status line, 0.97i tab bar), page primitives (section box, knob cell, menu cell, toggle, readout), the 14 Program pages of the 0.97i set, layout export |
| `ked_combi.py` | Combi navigation (pages + timbre selector + page 1/2) and the 9 Combi pages of the 0.97i set |
| `kdata.py` | Reader of Korg's MIDI Implementation tables (`Prog_HD-1.txt`, `Prog_EXi.txt`, `CombiAndSongTimbreSet.txt`, `Global.txt`, `Effect.txt`…) and choice of the control of each parameter |
| `kmodel.py` | Areas, sections, blocks (knob rows, grids, tables, matrices) and pagination |
| `kfull.py` | Complete KRONOS editor: area plans of every object, block drawing, navigation, rendering |
| `kfx.py` | FX EDIT: generic 40-cell background and the cell map of the 197 effect types |
| `knaut.py` | Complete NAUTILUS editor (NAUTILUS tables, X-Y, RT controllers, scenes, Step Seq. A-D, arp patterns) |
| `koasys.py` | Complete OASYS editor (KRONOS structure minus what the OASYS does not have, per pcglib) |
| `koasys_ofs.py`, `oasys_effects_v1_3.json` | OASYS: adds the OASYS PCG offset of each parameter (`korg.oasys`) from the pcglib byte maps (`ctrlr-project\reference\ref-oasys`), trims the effect list to 000-185 with the OASYS names |
| `requirements.txt`, `REGENERER_TOUT.bat` | Python modules to install; Windows batch that regenerates everything (see below) |
| `kpack.py` | Contact sheets and per-object zip archives (`KPACK_LITE=1`: no `_fond.svg` / `_maquette@2x.png`, mock-ups as JPEG — used for the textured OASYS and NAUTILUS skins) |

The drawing rules are described in `RECIPES_GUI_DRAWING.md`. Commands:

```
pip install cairosvg fonttools brotli numpy pillow
set KRONOS_MIDIIMP=C:\…\KRONOS_MIDIimp\MIDI implementation        (unzipped KRONOS_MIDIimp.zip)
python ked.py out\0.97i\Program
python ked_combi.py out\0.97i\Combi
python kfull.py out\Full                                           (all KRONOS objects)
python kfx.py out\Full\Effects
set KRONOS_MIDIIMP=C:\Korg\Manuals Nautilus\NAUTILUS_MIDIimp\SysExDumps
python knaut.py out\NAUTILUS\Full                                  (theme NAUTILUS_NAVIGATOR by default)
python koasys.py out\OASYS\Full                                    (theme OASYS_OMNI by default)
python koasys_ofs.py out\OASYS\Full C:\Korg\kronos-corpus\ctrlr-project\reference\ref-oasys
```

Fonts: all the fonts are in `fonts\` (Inter, DejaVu Sans Mono, Michroma, Montserrat, with their licences and
`README_FONTS.txt`); the scripts use that folder automatically, nothing needs to be installed (`FONT_DIR` /
`EXTRA_FONT_DIR` still override it).

## Running on Windows

- `requirements.txt`: the Python modules (`pip install -r requirements.txt`). Python 3.10 or later.
- `REGENERER_TOUT.bat`: regenerates every set (0.97i, KRONOS / OASYS / NAUTILUS Full and their effects) into `.\out`.
  Edit the two table folders at the top first (KRONOS tables: unzipped `KRONOS_MIDIimp.zip`, or a
  `MIDI implementation` folder next to the scripts; NAUTILUS tables: `NAUTILUS_MIDIimp\SysExDumps`).
- Each script also takes a list of objects, e.g. `python kfull.py out DRUMKIT WAVESEQ` (objects: PROGRAM, ENGINES,
  COMBI, SONG, GLOBAL, DRUMKIT, WAVESEQ, SETLIST; NAUTILUS adds ARP). `KFULL_FAST=1` renders 1x PNGs only. By default the scripts write only what the editor needs (one mock-up per page, backgrounds in PNG 1x and @2x, layouts, `FX_LAYOUTS.json`); `GFX_EXTRAS=1` adds the SVG files, the @2x mock-ups and one mock-up per effect type.
- **cairosvg needs the Cairo library**, which pip does not install on Windows. Install it once, e.g. with the GTK3
  runtime (gtk-for-windows) or MSYS2 (`pacman -S mingw-w64-x86_64-cairo`) and put its `bin` folder in the PATH.
  If `import cairosvg` fails with "no library called cairo", this is the cause.
- Check: running the delivered scripts from a clean copy gives `_layout.json` files identical to those of `Full`.
