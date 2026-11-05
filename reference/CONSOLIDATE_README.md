# The Kronos knowledge base — consolidated reading guide

**Modern version, 2026-10-24** (same-day update: harvest from `check/`). This
document supersedes the old `consolidate/old/CONSOLIDATE_README.md` (French,
2026-10-13). It is the essential piece of reading for anyone continuing the
ctrlr-project: what the knowledge base is, what lives where now that it is
consolidated under `/reference`, and what is authoritative.

## 1. What this knowledge base is

- **Origin:** the "grand livre du KRONOS" — years of reverse-engineering and
  hardware testing of the Korg Kronos (PCG file format, SysEx, MIDI, factory
  content), plus the Max for Live device **Kronos Kontrol** built on top of
  it. The original working tree is
  `C:\Korg\Manuals Le grand livre du KRONOS\` (still on disk; it keeps the
  masters — corrections are made there, then re-copied).
- **First consolidation:** `consolidate/old/` in this project — a working copy
  of the tools and extracted data (web/pcgt toolkit, Python tools, tests,
  bit-level tables, the M4L device sources, reference docs).
- **Now:** the knowledge this project needs is consolidated under
  `/reference`, in three per-synth folders (`ref-kronos`, `ref-oasys`,
  `ref-nautilus`). `consolidate/` is legacy and will be deleted — `/reference`
  is the project's knowledge base.
- **A second, maintained home** of the same knowledge is the **pcglib**
  project (`C:\Korg\kronos-pcglib`, repo `francoisuk/kronos-pcglib`, parked at
  v1.6.3): the conversion toolchain (C# app + Python port + unit tests) and
  the analysis documents. Much of `/reference` is byte-identical copies of
  pcglib files.
- **Harvest (2026-10-24):** the two previous projects archived in `check/` —
  `check/ableton/` (the M4L device project, incl. its export bridge) and
  `check/vst3/` (an earlier, more advanced attempt at this very Ctrlr panel,
  version **complet-0.96**, 2026-10-18/19). Their useful parts were placed in
  the project: panel work under `panels/KronosKontrol/`, tools under
  `scripts/`, art under `GUI_pic/`, reference material under
  `reference/ref-kronos/`. `check/` was removed by the maintainer on
  2026-10-24, once the harvest was verified byte-identical; the originals of
  both projects remain at
  `C:\Korg\Manuals Le grand livre du KRONOS\04_Outils\produits-inclus\`
  (see §3b).

## 2. Where everything lives now

```
/reference
├── README.md                   index of this folder — read first
├── CONSOLIDATE_README.md       this document — read second
├── ref-kronos/                 Kronos (the Kronos Kontrol panel)
│   ├── KRONOS_SYSEX_PARAMETER_CONTROL.md   every parameter via SysEx
│   ├── KRONOS_TABLES_GUIDE.md              how to read the bit-level tables
│   ├── m4l/                        the Max for Live ground truth (see §4)
│   │                               + export/ (index) and manuels/ (user manuals)
│   ├── tables/                     28 bit-level tables (27 from pcglib + the
│   │                               default effect blocks from the grand livre)
│   ├── docs/                       pcglib analysis documents + SYSEX_KRONOS.md
│   │                               (hardware-verified SysEx, from check/vst3)
│   └── midi/                       Korg MIDI implementation tables
├── ref-oasys/                  Oasys (for a future panel)
└── ref-nautilus/               Nautilus (for a future panel)
```

Elsewhere in the project: `docs/` (Korg PDFs + `CONNAISSANCES_KRONOS_PCG.md`,
the consolidated narrative in French — read it before any PDF),
`panels/KronosKontrol/` (the panel work — now at **complet-0.96**, harvested
from `check/vst3/`), `build/` (Ctrlr runtime + source trees), `tables/` (a
flat copy of the 27 pcglib Kronos tables).

## 3. What was consolidated from consolidate/old (and what was left behind)

| consolidate/old | → /reference | Verdict |
|---|---|---|
| `05_tables/*.json` (14 files) | `ref-kronos/tables/` (byte-identical) | consolidated |
| `05_tables/*.txt` (4 Korg tables) | `ref-kronos/midi/` (byte-identical) | consolidated |
| `05_tables/Effets_blocs_par_defaut.json` | `ref-kronos/tables/` | consolidated — unique to the grand livre (default effect blocks, 135 types) |
| `06_max_for_live/sources/names.json`, `ge_kronos.json` | `ref-kronos/m4l/` | consolidated — the panel's static-data sources |
| `06_max_for_live/docs_dev/` | `ref-kronos/m4l/docs_dev/` (newer copies taken from the original tree) | consolidated |
| `06_max_for_live/LISEZMOI.txt` | `ref-kronos/m4l/LISEZMOI.txt` (newer, 2026-10-18) | consolidated |
| `06_max_for_live/sources/base/` | **was missing from consolidate/old** — copied from the original tree → `ref-kronos/m4l/base/` | consolidated — the ground-truth patch |
| (device binary) | `ref-kronos/m4l/Kronos Kontrol OS3.2.3_FR.amxd` (from the original tree) | consolidated — the hardware-verified device |
| `07_docs/00_RECAPITULATIF_FORMAT_PCG.md`, `COMPATIBILITE_PCG_KRONOS.md` | not copied — stale; newer versions (from pcglib) already in `ref-kronos/docs/` | superseded |
| `07_docs/` RECETTES, Regles_OS2→OS31, Structure_fichiers_usine, LISEZMOI_\*, KronosV2V3Rules_original | not copied — conversion-era; pcglib's docs supersede them | legacy |
| `01_web/`, `02_python/`, `03_outils/`, `04_tests/` | not copied — the conversion toolchain; pcglib (C# + Python + tests, all green) is the maintained version; masters stay in the original tree | superseded |
| `06_max_for_live/sources/*.py` (build chain) | not copied — rebuilds the .amxd (Ableton-side tooling); the original tree keeps them (incl. `fix6.py`, absent from consolidate/old) | legacy |

### 3b. Harvest from `check/` (2026-10-24)

The maintainer archived the two previous projects under `check/`. Everything
useful was placed in the project (all copies verified byte-identical to their
source). `check/` was removed by the maintainer on 2026-10-24, after that
verification; the originals of both projects remain at
`C:\Korg\Manuals Le grand livre du KRONOS\04_Outils\produits-inclus\ableton\`
and `...\produits-inclus\vst3\`.

| check/ source | → placed at | Verdict |
|---|---|---|
| `vst3/panels/KronosKontrol/KronosKontrol.panel` (complet-0.96, 172 modulators, 13 Lua methods) | `panels/KronosKontrol/` | harvested — the previous, more advanced state of this panel ("à tester" on hardware) |
| `vst3/panels/KronosKontrol/lua/kkMain.lua` (401 lines) | `panels/KronosKontrol/lua/` | harvested |
| `vst3/panels/KronosKontrol/sources/` (`build_panel.py`, `ctrlr_templates.json`, `jb64.py`) | `panels/KronosKontrol/sources/` | harvested — generator re-run 2026-10-24: reproduces the shipped panel byte-for-byte |
| `vst3/panels/KronosKontrol/ETUDE_TR-Rack.md`, `REPRISE.md` | `panels/KronosKontrol/` | harvested — the Ctrlr idiom study + the 0.96 corrections |
| `vst3/panels/KronosKontrol/rack_fond.png` | `panels/KronosKontrol/` | harvested — the panel background (1500×414) |
| `vst3/export/KronosKontrol/data/ge_kronos.json` | `panels/KronosKontrol/data/` | harvested — identical to `ref-kronos/m4l/ge_kronos.json` |
| `vst3/export/outils/kronos_sysex.lua` | `panels/KronosKontrol/kronos_sysex.lua` — at panel root, **not** in `lua/`: the generator embeds every `lua/*.lua` | harvested — newest version (4,237 B, with the ATTENTION warning) |
| `vst3/export/outils/kronos_sysex.py`, `vt2xml.py` | `scripts/` | harvested — tested Python SysEx library + .bpanelz reader |
| `vst3/export/docs/` (`LISEZMOI_panneau.md`, `PROMPT_NOUVELLE_SESSION_CTRLR.md`, `PROMPT_REPRISE_LUNDI.md`, `SYSEX_KRONOS.md`) | `panels/KronosKontrol/` + `reference/ref-kronos/docs/` | harvested |
| `vst3/PROMPT_NOUVELLE_SESSION_CTRLR.md`, `PROMPT_REPRISE_LUNDI.md` | `panels/KronosKontrol/` | harvested (same content as the export/docs copies) |
| `ableton/export/README.md` | `reference/ref-kronos/m4l/export/README.md` | harvested — the export index: "essentiel à savoir (vérifié)" + Ctrlr pointers |
| `ableton/Manuels/` (EN/ES/FR .docx + FR .pdf) | `reference/ref-kronos/m4l/manuels/` | harvested — the device user manuals |
| `ableton/export/panneau_rack/` (rack generator + art) | `scripts/panneau_rack/` + `GUI_pic/panneau_rack/` | harvested |
| `ableton/kronos-kontrol-rack-final.svg` | `GUI_pic/` | harvested |
| not harvested: `vst3/build/` (707 MB), duplicate docs, `vst3/reference/MIDI_implementation` + `export/reference_midi`, `ableton/sources/` + `export/max_for_live/` (.amxd chain), `ableton/test/` (Kronos.als), the other .amxd builds, design drafts, older file versions | — | not needed — superseded, identical, or Ableton-side; kept in the `produits-inclus/` originals |

## 4. The ground truth for the panel (ref-kronos/m4l/)

The panel is a host-agnostic replacement for the M4L device **Kronos
Kontrol**, hardware-verified on a real Kronos. Do not re-derive SysEx from
the MIDI guide — the device is the ground truth:

- `base/kronos_kontrol_v1.json` — the original patch (404 KB): every
  hardware-verified message as `sxformat` strings (mode change, GE select,
  16 FX switches, Drum Track). Phase A of the panel extracted them from here.
- `names.json` (4,233 factory program names, OS 3.2) and `ge_kronos.json`
  (3,584 KARMA GE names) — the sources of the panel's static data
  (`panels/KronosKontrol/data/kronos_data.lua`, generated by
  `scripts/gen_data_lua.py`).
- `Kronos Kontrol OS3.2.3_FR.amxd` — the device itself. The EN/ES builds are
  identical except one button label; `Kronos Kontrol v3.2.3.amxd` is the old
  version, kept as backup in the original tree.
- `docs_dev/` — the device's format and development notes, including
  `MAX_FOR_LIVE_FORMAT.md` (the CC ↔ encoder correspondences) and
  `REPRISE.md` (final state, 2026-10-16).
- `LISEZMOI.txt` — the device's readme: what it does, how to install it,
  what to set on the Kronos (KARMA CCs off by default, Bank Map KORG,
  Enable Exclusive, global channel 1), and the test status.

One document above the `m4l/` ground truth: `ref-kronos/docs/SYSEX_KRONOS.md`
(hardware-verified on a real Kronos, 2026-10-16, harvested from the previous
Ctrlr project). It is the authority on **parameter** SysEx: the
TYP/SOC/SUB/PID/IDX table for timbre Volume/Pan/Mute (TYP 4, SOC t, PIDs
2/1/14), FX switches (inverted: 0=On, 1=Off), Master Volume, OSC/EXi Patch
Level, Drum Track On/Volume/Mute (PIDs 10/39/40) and the KARMA GE — plus the
mode-memory and retry rules. Where it disagrees with
`KRONOS_SYSEX_PARAMETER_CONTROL.md` worked examples, **SYSEX_KRONOS.md wins**
(the M4L device's GE and Drum-Track-On messages were never hardware-validated).

## 5. What is authoritative (and what is not)

| Topic | Authoritative source |
|---|---|
| SysEx function codes and grammars | `ref-kronos/midi/KRONOS_MIDI_SysEx.txt` (Korg, v1.27) — summarized in `ref-kronos/KRONOS_SYSEX_PARAMETER_CONTROL.md` |
| Hardware-verified parameter SysEx | `ref-kronos/docs/SYSEX_KRONOS.md` (2026-10-16) — wins over `KRONOS_SYSEX_PARAMETER_CONTROL.md` where they disagree |
| Parameter bit layout + SysEx ids | `ref-kronos/midi/*.txt` (Korg tables); JSON/CSV twins in `ref-kronos/tables/` (read `KRONOS_TABLES_GUIDE.md` first) |
| Consolidated narrative (French) | `docs/CONNAISSANCES_KRONOS_PCG.md` — read before any PDF |
| Conversion-era analyses | `ref-kronos/docs/`, `ref-oasys/docs/`, `ref-nautilus/docs/` (byte-identical pcglib copies) |
| Conversion toolchain (maintained) | the pcglib repo — not the JS/Python copies in the original tree |
| Upstream PCG Tools (2013) | has 3 known errors (CONNAISSANCES §12) — never port its logic |
| Oasys SysEx addresses | `ref-oasys/tables/Oasys_SysXMap_summary.csv` + `ref-oasys/docs/OASYS_SQZ_ANALYSIS.md` (facts only — the `.sqz` is not redistributable) |

## 6. What was deliberately not copied (and where it lives)

- The conversion toolchain (`01_web/`, `02_python/`, `03_outils/`,
  `04_tests/`): superseded by pcglib; masters in
  `C:\Korg\Manuals Le grand livre du KRONOS\` (`04_Outils/`, `bonus/`).
  pcglib's Python port of the converters: pcglib `docs/python-script/`.
- The M4L build chain (`sources/*.py`, `export/max_for_live/` incl. `fix6.py`
  and its README): original tree, `…\produits-inclus\ableton\`. Needed only
  to rebuild the `.amxd`.
- The other `.amxd` builds (EN/ES, the v3.2.3 backup, v4.0): same folder.
- Raw Voice Name Lists per OS: pcglib `docs/voice_name_lists/`.
- Oasys / Nautilus PDF manuals: pcglib `docs/oasys/`, `docs/nautilus/`; the
  maintainer's manual folders under `C:\Korg\Manuals …`.
- The MIDI Quest `Korg OASYS.sqz`: **not redistributable** (licensing) — never
  copy it anywhere; only the derived facts already in `ref-oasys/` may be
  shared.
- Factory PCG files (Korg data, not for distribution): pcglib `factory/` and
  the original tree.
- The 9 real Nautilus PCG test files: pcglib `docs/nautilus_pcg/`.
- Upstream PCG Tools C# source: pcglib `reference/PcgTools2013-master/`.
- Not harvested from the two previous projects: the 707 MB `vst3/build/`,
  duplicate or older file versions, the .amxd build chain
  (`ableton/sources/`, `export/max_for_live/`), the Ableton test set
  (`ableton/test/`), the other .amxd builds, and the rack design drafts
  (`ableton/panneau_rack/maquettes`, `reference/`). They remain in the
  `produits-inclus/` originals; nothing in the project needs them.

## 7. Rules

1. `/reference` is read-only for the panel project. The panel lives under
   `panels/KronosKontrol/`.
2. Corrections to a copied document go back to the source first (pcglib for
   the analysis documents and tables; the original "grand livre" tree for the
   M4L ground truth), then are re-copied here. The synthesis documents
   (`README.md`, `CONSOLIDATE_README.md`, `KRONOS_SYSEX_PARAMETER_CONTROL.md`,
   `KRONOS_TABLES_GUIDE.md`, `OASYS_PANEL_NOTES.md`, `NAUTILUS_PANEL_NOTES.md`)
   are this project's own — amend them here.
3. Korg documents are copyright Korg. The `.sqz`-derived material is
   personal, non-commercial — keep the licensing notes with the documents.
4. Prefer the JSON tables over the PDFs; read `docs/CONNAISSANCES_KRONOS_PCG.md`
   before any PDF.
5. ~~When `consolidate/` is deleted, repoint `scripts/gen_data_lua.py` …~~
   **Done 2026-10-24:** `scripts/gen_data_lua.py` now reads
   `reference/ref-kronos/m4l/names.json` and `ge_kronos.json`, and the
   ground-truth paths in `panels/KronosKontrol/PROJECT_LAYOUT.md` point at
   `reference/ref-kronos/m4l/`. `consolidate/` can be deleted.
6. ~~`check/` is the archive of the two previous projects …~~ **Removed
   2026-10-24** by the maintainer, once the harvest was verified
   byte-identical. The originals of the two previous projects (the M4L
   device project and the earlier Ctrlr attempt) remain at
   `C:\Korg\Manuals Le grand livre du KRONOS\04_Outils\produits-inclus\`
   (`ableton/`, `vst3/`) — read-only reference.

## 8. Reading order for a newcomer

1. `reference/README.md` — what is in this folder.
2. This document.
3. `panels/KronosKontrol/PROJECT_LAYOUT.md` — the panel project (authoritative).
4. `docs/CONNAISSANCES_KRONOS_PCG.md` — the consolidated Kronos knowledge (French).
5. `reference/ref-kronos/KRONOS_SYSEX_PARAMETER_CONTROL.md` — controlling the Kronos.
6. `reference/ref-kronos/KRONOS_TABLES_GUIDE.md` — the bit-level tables.
7. `reference/ref-kronos/docs/SYSEX_KRONOS.md` — the hardware-verified
   parameter SysEx (wins over item 5 where they disagree).
8. `panels/KronosKontrol/REPRISE.md` + `ETUDE_TR-Rack.md` — where the panel
   stands (complet-0.96) and the verified Ctrlr idioms.
