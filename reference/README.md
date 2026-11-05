# /reference — pcglib knowledge transferred to the Ctrlr panel project

This folder holds copies, and a few rewrites, of the documents produced by the
**kronos-pcglib** project (repo `francoisuk/kronos-pcglib`, parked at **v1.6.3**,
commit `c2af0f2`, 2026-10-24) that benefit the Kronos Kontrol panel — above all
the knowledge needed to **control every parameter of the Kronos over SysEx** —
plus the equivalent material for the **Oasys** and the **Nautilus**, in case
panels are built for those synthesizers after Kronos Kontrol is finished.
Since 2026-10-24 it also holds material harvested from the two previous
projects that were archived in `check/` (the M4L device project and the
earlier Ctrlr panel attempt) — most importantly the hardware-verified SysEx
note `ref-kronos/docs/SYSEX_KRONOS.md`. **`check/` was removed by the
maintainer on 2026-10-24, once the harvest was verified byte-identical**;
the originals of both projects remain at
`C:\Korg\Manuals Le grand livre du KRONOS\04_Outils\produits-inclus\`
(`ableton/`, `vst3/`).

**Read `CONSOLIDATE_README.md` next** — it is the essential piece of reading:
what the knowledge base is, what lives where now that it is consolidated here,
and what is authoritative. This folder is the project's knowledge base; the
legacy `consolidate/` folder will be deleted.

## Provenance and licensing

- Everything here comes from the pcglib working tree at `C:\Korg\kronos-pcglib`
  (state of 2026-10-24, v1.6.3) and from the "grand livre du KRONOS" working
  tree at `C:\Korg\Manuals Le grand livre du KRONOS\` (the M4L ground truth,
  `ref-kronos/m4l/`). Files under `tables/`, `docs/`, `midi/`, `names/` and
  `m4l/` in the three subfolders are **byte-identical copies** of their
  originals. The synthesis files (`README.md`, `CONSOLIDATE_README.md`,
  `KRONOS_SYSEX_PARAMETER_CONTROL.md`, `KRONOS_TABLES_GUIDE.md`,
  `OASYS_PANEL_NOTES.md`, `NAUTILUS_PANEL_NOTES.md`) are **rewrites** produced
  for this project; amend them here, and feed corrections back to the source
  project when they belong there.
- 2026-10-24 — harvested from the two previous projects archived in `check/`
  (`check/ableton/` = the M4L device project incl. its export bridge;
  `check/vst3/` = the earlier, more advanced Ctrlr panel attempt, version
  **complet-0.96**, 2026-10-18/19). Into this folder:
  `ref-kronos/docs/SYSEX_KRONOS.md` (hardware-verified SysEx parameters,
  2026-10-16), `ref-kronos/m4l/export/README.md` (the export index) and
  `ref-kronos/m4l/manuels/` (the device user manuals) — all byte-identical
  copies. The panel-side harvest (the built `KronosKontrol.panel`, its Lua,
  the generator, the rack art) went to `panels/KronosKontrol/`, `scripts/`
  and `GUI_pic/` — see "Deliberately not copied" below for what was left.
- Korg documents (MIDI implementation tables and PDFs) are copyright Korg.
- The Oasys material derived from the MIDI Quest `Korg OASYS.sqz` config
  records **facts only** (offsets, sizes, names, addresses). The `.sqz` itself
  is **not** copied here and must not be redistributed — the analysis was for
  personal, non-commercial use (see `ref-oasys/docs/OASYS_SQZ_ANALYSIS.md` §1).
- Rule: when one of these documents is updated at its source, re-copy it here.
  When a synthesis document here grows facts that belong to the shared
  knowledge, port them back to the source project.

## Tree

```
reference/
├── README.md                 this file
├── CONSOLIDATE_README.md     the essential reading — the knowledge base guide
├── ref-kronos/               Kronos — for the Kronos Kontrol panel
│   ├── KRONOS_SYSEX_PARAMETER_CONTROL.md   (rewrite) every parameter via SysEx fn 43/44, dumps, digests
│   ├── KRONOS_TABLES_GUIDE.md              (rewrite) how to read the bit-level tables
│   ├── m4l/                      the Max for Live ground truth (the device the panel replaces)
│   │   ├── base/                 kronos_kontrol_v1.json (sxformat strings), conteneur, rack art
│   │   ├── docs_dev/             device format + development notes (incl. CC ↔ encoder map)
│   │   ├── export/               the export index: what is hardware-verified + Ctrlr pointers
│   │   ├── manuels/              the device user manuals (EN/ES/FR .docx + FR .pdf)
│   │   ├── names.json            4,233 factory program names (OS 3.2)
│   │   ├── ge_kronos.json        3,584 KARMA GE names
│   │   ├── LISEZMOI.txt          the device's readme (setup, Kronos settings, test status)
│   │   └── Kronos Kontrol OS3.2.3_FR.amxd   the hardware-verified device
│   ├── tables/                 28 bit-level tables (27 byte-identical to pcglib tables/
│   │                           and ctrlr-project tables/, + Effets_blocs_par_defaut.json)
│   ├── docs/                   9 documents: 8 pcglib analysis documents (Kronos format facts,
│   │                           compatibility, …) + SYSEX_KRONOS.md (hardware-verified SysEx
│   │                           parameters, 2026-10-16, harvested from check/vst3)
│   └── midi/                   Korg MIDI implementation tables (byte-identical to docs/MIDI implementation/)
│                             + SysExParams/VoiceModels per-engine variants
├── ref-oasys/                Oasys — for a future Oasys panel
│   ├── OASYS_PANEL_NOTES.md                (rewrite) what an Oasys panel needs
│   ├── tables/                 6 Oasys tables (SysXMap summary, factory names, block maps)
│   ├── docs/                   sqz analysis, parameter map, v1.6.3 fix doc, about doc
│   └── midi/                   OASYS_MIDI_implementation.pdf
└── ref-nautilus/             Nautilus — for a future Nautilus panel
    ├── NAUTILUS_PANEL_NOTES.md             (rewrite) what a Nautilus panel needs
    ├── docs/                   13 pcglib analysis documents (SysEx protocol, comparisons, format)
    ├── midi/                   NAUTILUS_MIDIimp (SysEx function table + SysExDumps parameter tables)
    └── names/                  Nautilus factory names (per-chunk CSVs + cleaned lists)
```

## Deliberately not copied (available at the source projects if ever needed)

- `consolidate/old/01_web`, `02_python`, `03_outils`, `04_tests` — the JS/Python
  conversion toolchain, superseded by pcglib; masters in the "grand livre" tree.
  pcglib's maintained versions: the pcglib repo (C# app) and its
  `docs/python-script/` (Python port).
- `consolidate/old/07_docs` — conversion-era docs; superseded by the pcglib
  analysis documents copied into `ref-*/docs/` (the two big ones there,
  `00_RECAPITULATIF_FORMAT_PCG.md` and `COMPATIBILITE_PCG_KRONOS.md`, are stale
  in `consolidate/old`).
- `consolidate/old/06_max_for_live/sources/*.py` — the .amxd build chain
  (Ableton-side tooling; the original tree keeps it, incl. `fix6.py`).
- `reference/PcgTools2013-master/` (pcglib) — upstream PCG Tools C# source.
  Contains the three known errors listed in
  `docs/CONNAISSANCES_KRONOS_PCG.md` §12; do not port its logic.
- `docs/voice_name_lists/` (pcglib) — raw Kronos Voice Name Lists per OS. The
  panel already gets its names from `ref-kronos/m4l/names.json` and
  `ge_kronos.json`.
- `docs/oasys/` and `docs/nautilus/` PDF manuals (pcglib) — heavy; the
  maintainer keeps them under `C:\Korg\Manuals …`. Only the Oasys MIDI
  implementation PDF is copied (it is the SysEx authority).
- `docs/oasys/Korg OASYS.sqz` and `docs/oasys/Korg OASYS/` — licensing (above).
- pcglib project-management documents (`STATUS.md`, `ROADMAP.md`, `RESUME.md`,
  `SESSION_JOURNAL.md`) and the pcglib user manual — internal to pcglib.
- `docs/nautilus_pcg/` (pcglib) — 9 real Nautilus PCG files used as conversion
  test input.

From the harvest sources (`check/`, since removed — see the note at the top;
originals in `produits-inclus/`):
- `vst3/build/` — 707 MB of Ctrlr build output; the same five entries already
  exist in this project's `build/`.
- `vst3/panels/TR-Rack-Editor-main` and the older copies of our own docs in
  `vst3/panels/KronosKontrol/` — already here, byte-identical.
- `vst3/reference/MIDI_implementation` + `vst3/export/reference_midi` — the same
  Korg tables already in `ref-kronos/midi/`.
- `ableton/sources/` + `ableton/export/max_for_live/` — the .amxd build chain
  (Ableton-side; identical copies stay in the original tree).
- `ableton/test/Kronos Project` (the Kronos.als set), the other .amxd builds
  (EN/ES, the v3.2.3 backup, v4.0), `ableton/panneau_rack/maquettes` +
  `reference/` (design drafts), `ableton/export/docs/LISEZMOI_device.txt`,
  `ableton/rack_fond.png` and `ableton/export/ctrlr/kronos_sysex.lua` (older
  versions of files placed from newer sources), `ableton/Kronos Logo.png`,
  `Kronos Kontrol v3.2.3.png`, `panneau_rack/PROMPT_REPRISE_KRONOS_KONTROL.txt`,
  `vst3/export/KronosKontrol/data/kronos_data.lua` (identical to ours).

## How this maps to the panel work

- **Now (Kronos Kontrol):** `ref-kronos/KRONOS_SYSEX_PARAMETER_CONTROL.md` is
  the roadmap for Phase C/D: it collects every SysEx function the panel can
  use, the exact fn 43/44 grammar, and decodes the M4L-verified messages
  against that grammar. `ref-kronos/tables/` + `ref-kronos/midi/` are the data
  to enumerate **all** Kronos parameters. `ref-kronos/KRONOS_TABLES_GUIDE.md`
  explains how to read them. `ref-kronos/m4l/` is the ground truth for every
  hardware-verified message.
- `ref-kronos/docs/SYSEX_KRONOS.md` is the **hardware-verified** parameter
  SysEx ground truth (tested on a real Kronos, 2026-10-16). Where it
  disagrees with `KRONOS_SYSEX_PARAMETER_CONTROL.md`, it wins: FX switches
  are inverted (0=On, 1=Off); in Program mode the KARMA GE and Drum Track On
  parameters must go through fn 6D/6E (fn 43 addresses collide with other
  sections there); Drum Track Volume/Mute are PIDs 39/40; timbre t
  Volume/Pan/Mute are TYP 4, SOC t, PIDs 2/1/14.
- `panels/KronosKontrol/` now holds the previous Ctrlr attempt
  (**complet-0.96**, harvested from `check/vst3/`): the built
  `KronosKontrol.panel` (172 modulators, 13 Lua methods), its Lua
  (`lua/kkMain.lua`), the generator (`sources/build_panel.py` — re-run on
  2026-10-24, reproduces the shipped panel byte-for-byte), the study notes
  (`ETUDE_TR-Rack.md` — the verified Ctrlr idioms, `REPRISE.md` — the 0.96
  corrections) and the rack design (`LISEZMOI_panneau.md`, `rack_fond.png`).
- **Later (Oasys panel):** `ref-oasys/` — the SysXMap tables are the Oasys
  SysEx parameter addresses Korg never published; `OASYS_PANEL_NOTES.md`
  summarises the frame grammar and the open points.
- **Later (Nautilus panel):** `ref-nautilus/` — the Nautilus SysEx protocol
  analysis (header and function-code differences from the Kronos), the Nautilus
  parameter tables, factory names, and the format differences that matter.
