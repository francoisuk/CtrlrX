# ctrlrx-juce8 — Kronos Kontrol on CtrlrX / JUCE 8

Working repository for the **Kronos Kontrol** CtrlrX panel and the JUCE 8
CtrlrX engine it runs on.

The panel is large: a **~29 MB generated XML** with **895 modulators** across
**216 pages**. Loading it in the editor takes roughly 30 s and redrawing the UI
can freeze the application. Current focus is a performance branch,
`feature/large-panel-perf`.

---

## Layout

| Path | What it is |
|---|---|
| `panels/KronosKontrol/` | The product. `KronosKontrol_1.0i.panel` (generated XML), `lua/`, `data/`, `docs/`, `sources/` (the generator), `assets/`, `proof/` |
| `panels/archives/` | Prior panel revisions `0.99` … `1.0i` |
| `build/CtrlrX-dnaldoog/CtrlrX-master/` | **The JUCE 8 engine tree** — `Source/`, CMake, packaging. This is the C++ that the performance work patches |
| `build/CtrlrX-damiensellier/CtrlrX/` | Upstream CtrlrX clone, tag `v5.6.36`, JUCE 6.0.8 — reference (untracked) |
| `build/CtrlrX-pr337/` | Clean export of upstream PR #337 "Panel probe and AI agent skill" (untracked) |
| `probe/` | Panel-probe harness: `kkprobe.py`, `scripts/*.json` scenarios, built binary in `b/` (untracked) |
| `graphics/` | Layout JSON, fonts and editor scripts for KRONOS / OASYS / NAUTILUS (artwork rasters untracked) |
| `scripts/`, `tables/` | `kronos_sysex.py`, object tables, generators |
| `docs/`, `reference/`, `user-manual/` | Korg documentation and reference text |
| `journal/`, `notes/`, `debugging/` | Session journals and working notes |

Orientation documents, in reading order: `CTRLRX_MIGRATION.md`,
`panels/KronosKontrol/docs/PROJECT_LAYOUT.md`, `BUILD_EXPORT.md`,
`PR337_ANALYSIS.md`, `REPRISE_CODAGE_1.0h.md`.

---

## Engine variants and their frameworks

Two independent version numbers are in play and they are easy to confuse:

- **CtrlrX** is the application. Its releases are `5.6.xx` on the upstream
  `damiensellier` line and **`8.7x`** on `dnaldoog`'s JUCE 8 line.
- **JUCE** is the framework CtrlrX builds against. Releases are `8.0.x` (JUCE 8)
  or `6.0.x` (JUCE 6).

So "CtrlrX 8.76 on JUCE 8" resolves to: CtrlrX version `8.76`, JUCE `8.0.12`.
Measured from the trees on disk:

| Tree | CtrlrX | JUCE | Notes |
|---|---|---|---|
| `build/CtrlrX-dnaldoog/CtrlrX-master` | **8.77** | **8.0.12** | The JUCE 8 engine — the tree this project builds and patches |
| `build/CtrlrX-damiensellier/CtrlrX` | 5.6.36 | 6.0.8 | upstream clone, tag `v5.6.36` |
| `build/CtrlrX-pr337` | 5.6.37 | 6.0.8 | PR #337 export (base `5.6.37-Maintenance`) |
| `probe/src` | 5.6.36 | 6.0.8 | clone the probe binary was built from |

The `VERSION` file is authoritative for CtrlrX; `CHANGELOG.md` in the engine tree
lists `v8.77` (11/05/2026) and `v8.76` (11/05/2026) at the top. Note the
`v8.76` changelog entry is empty — `v8.77` is the first release in that pair
with recorded changes, so **8.77 is the effective baseline**, not 8.76.

## Building the engine

```powershell
cd build/CtrlrX-dnaldoog/CtrlrX-master
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

JUCE must be present at `build/CtrlrX-dnaldoog/CtrlrX-master/JUCE` (it is NOT in
git — see below). The tree already carries `JUCE 8.0.12`; if it is missing:

```powershell
git clone --branch 8.0.12 https://github.com/juce-framework/JUCE.git JUCE
```

### The JUCE patch is applied automatically

This project carries one modification to JUCE, as a patch:

| File | Purpose |
|---|---|
| `patches/juce_xml_parser_perf.patch` | Makes `XmlDocument::readQuotedString()` linear instead of O(n²) |

CMake applies it at configure time, idempotently, and fails the configure if it
cannot. Nothing to do manually — but note:

- It needs **git** on `PATH` (`find_package(Git)`).
- It is applied to the *working tree* of `JUCE/`, so a fresh `git clone` of JUCE
  needs one reconfigure to re-apply it.
- If you update JUCE, delete the "already applied" assumption by resetting the
  file first (the patch is version-specific to 8.0.12).

Measured effect on the 29 MB KronosKontrol panel: XML parse **30.7 s → 0.19 s**.

## Generating the panel

The `.panel` is **generated** — never hand-edited:

```powershell
cd panels/KronosKontrol/sources
python build_panel.py
```

Inputs: `ctrlr_templates.json`, `editor_layout.json`,
`editor_full_layout.json`, `data/kronos_data.lua`, `lua/*.lua`, and artwork from
`graphics/`.

---

## What lives in git, and what does not

The folder is ~3.2 GB / 66 k files. The repository tracks **2261 files
(~293 MB)** — the source, the generated product, and the documents. The rest
stays on disk and is deliberately untracked.

**Ignored, recoverable elsewhere:**

- `build/CtrlrX-damiensellier/`, `build/CtrlrX-pr337/`, `probe/src/` — separate
  upstream checkouts/exports with their own history. Re-clone or re-fetch.
- `build/CtrlrX-dnaldoog/CtrlrX-master/JUCE/`, `reference/VST_SDK/`,
  `reference/books/` — public upstreams; versions pinned above.
- C/C++ build output (`CMakeFiles/`, `*.o`, `*.lib`, `*.a`, `Makefile`,
  `compile_commands.json`), probe output (`probe/b/`, `probe/out/`),
  executables (`*.exe`, `*.vst3`, `*.dll`), `temp/`.

**Ignored, and only on this machine:**

- Artwork rasters under `graphics/` (~818 MB of PNG/JPG) and the panel's
  `video/`, `exe/`, `vst3/` outputs.
- PDFs (`docs/`, `reference/books/`).

Small panel assets that the generator and probe need
(`panels/KronosKontrol/assets/*.png`) **are** tracked.

If the artwork should be versioned, `git-lfs` 3.8 is installed:

```powershell
git lfs install
git lfs track "graphics/**/*.png"
```

## Conventions

- `.panel` files are stored verbatim (`-text -diff`): ~29 MB generated XML that
  must round-trip byte-for-byte. Do not let anything renormalise them.
- Text is normalised to LF in the repository; `*.ps1`/`*.bat`/`*.cmd` check out
  as CRLF.
- Never save the panel in edit mode — see the upstream bug documented in
  `PR337_ANALYSIS.md` §3.
- The engine tree `build/CtrlrX-dnaldoog/CtrlrX-master` carries upstream's own
  `.gitignore`; it applies here too.

## Branching

`main` holds the imported baseline. Ongoing work happens on topic branches:

```powershell
git switch -c feature/large-panel-perf
```
