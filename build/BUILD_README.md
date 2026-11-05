# /build — Ctrlr framework folder

> **3 nov. 2026 — version pin changed.** The runtime is now **CtrlrX 5.6.36** (Damien Sellier),
> installed at `C:\Program Files\CtrlrX Project\CtrlrX\CtrlrX.exe` (standalone; it exports the
> panel itself as VST3/exe — add 24 px to the panel height when exporting). Its source is the git
> clone `CtrlrX-damiensellier/CtrlrX/` at tag `v5.6.36`
> (`d35edd226089263bd08317cb289d97e6566090a6`). `Ctrlr-x64_VST3_v5.6.23/` and SAVIHost3 are no
> longer used (SAVIHost3 only to test an exported VST3). The sections below describe the former
> 5.6.23 setup. See `../CTRLRX_MIGRATION.md`.

*4 nov. 2026 : Ctrlr-x64_VST3_v5.6.23/ et panels/TR-Rack-Editor-main/ deplaces dans _TO_DELETE_2026-11-04/ (plus d'usage). Modernise le 2026-10-24 (le fichier avait une coquille : « Ctrlr-x64.vst3
est un dossier bundle » — faux, voir ci-dessous).*

This folder holds the Ctrlr runtime and the Ctrlr source trees that the
panel project references. Nothing in here is modified by the Kronos
panel work. It is read at runtime (the VST3 plugin) or read as
documentation (the source trees).

## Contents

```
build
├── (Ctrlr-x64_VST3_v5.6.23/ removed 4 nov. 2026 -> _TO_DELETE_2026-11-04/)
├── CtrlrX-dnaldoog\             primary Lua API reference (source)
├── CtrlrX-damiensellier\        secondary Lua API reference (source)
├── ctrlr-master\                upstream baseline (source, historical)
└── BUILD_README.md              this file
```

## Ctrlr-x64_VST3_v5.6.23/Ctrlr-x64.vst3 — the runtime

- **On Windows, this `.vst3` is a single DLL file, not a bundle
  folder.** The folder `Ctrlr-x64_VST3_v5.6.23/` contains only that
  file; the host loads the DLL directly.
- There is **no standalone `.exe`** in this folder. The plugin runs
  only inside a host.
- **Test host:** SAVIHost3, configured with:
  - MIDI Input = Kronos USB MIDI port
  - MIDI Output = Kronos USB MIDI port  *(critical for SysEx out)*
- **Secondary host:** Ableton Live 12 (VST3 scan path must include
  this folder, or a copy of it).
- **Do not rebuild.** The binary is the target. It has been
  hardware-verified with a working CC74 slider driving the Kronos
  filter cutoff (re-verified on OS 3.2.3, 12 oct. 2026).
- **Do not redistribute this folder** as part of the panel. The panel
  is distributed as a `.panel` file that loads into a user's own Ctrlr
  installation.

## CtrlrX-dnaldoog — primary source reference

An experimental fork of Ctrlr, based on JUCE 8, actively developed.
This is where the most current Lua API is documented (the automated
Lua API doc generation lives here).

- Use it as the **first** place to look up a Lua method name,
  class member, or panel property.
- Do not build from this tree. Do not link against it. Read the
  source when the panel's Lua needs to call into Ctrlr.
- If a method is not found here, move on to the secondary source.

## CtrlrX-damiensellier — secondary source reference

The main CtrlrX fork. More established than dnaldoog, less
bleeding-edge. Comprehensive build instructions are documented here.

- Use it as the **second** place to look up a Lua method when the
  primary source does not have it.
- Useful for cross-checking behavior: if both forks agree, the method
  is stable; if they diverge, note the divergence.

## ctrlr-master — upstream baseline

The original Roman Kubiak repository. Conservative, slow-moving, but
the historical foundation of everything else.

- Use it as the **last** place to look. If a method exists here but
  not in the two CtrlrX forks, it is legacy behavior — verify before
  using.
- This is also the reference for the original Lua API (pre-JUCE 8),
  which some older panels rely on.

## Lookup order for Lua methods

When writing panel Lua and unsure whether a method exists:

1. `CtrlrX-dnaldoog/` — primary
2. `CtrlrX-damiensellier/` — secondary
3. `ctrlr-master/` — baseline

If a method is not found in any of the three, **stop and say so.**
Do not invent a method name. Ctrlr's Lua binding is generated at build
time; unknown methods fail silently at runtime, which is the hardest
class of bug to diagnose.

The idioms the panel actually uses were extracted from the working
TR-Rack panel and verified against these trees on 16 oct. 2026 — see
`panels/KronosKontrol/CTRLR_IDIOMS.md`. Consult that file before
searching the sources again.

## Rules

1. This folder is **read-only** for the panel project. The panel lives
   under `/panels/KronosKontrol/`. Do not put panel files here.
2. Do not modify, patch, or rebuild any source tree here. If a source
   bug blocks the panel, note it and work around it in the panel's
   own Lua.
3. Do not commit the `Ctrlr-x64_VST3_v5.6.23/` folder to version
   control if the repo is ever shared. It is a binary artifact; the
   panel is the deliverable.
4. The binary version is pinned. If you upgrade Ctrlr later, update
   this README and re-run the CC74 sanity check before resuming.

## Version pin

- **Runtime:** Ctrlr-x64.vst3 (v5.6.23), bare DLL at
  `build/Ctrlr-x64_VST3_v5.6.23/Ctrlr-x64.vst3`
- **Primary source:** dnaldoog/CtrlrX (as cloned)
- **Secondary source:** damiensellier/CtrlrX (as cloned)
- **Baseline source:** RomanKubiak/ctrlr (ctrlr-master)

Record the exact commit hashes of the three source trees when the
panel first reaches v1. They are the reference for any future
regression check.
