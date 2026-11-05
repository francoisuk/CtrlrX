# Reprise — CtrlrPanelProbe (4 Nov 2026, evening)

## ▶ STATE AT STOP (4 Nov, 22:25) — read this first

**Done (1.0i):**
- Panel `panels/KronosKontrol/KronosKontrol_1.0i.panel`, archived. It contains 4 probe findings fixed:
  1. no `kkProgNumEdit` error at load;
  2. the splash is redrawn by the build;
  3. `kkQuiet` keeps the modulators in step, with no MIDI;
  4. no blue square in EDITOR.
- Checks: e2check 301/0, smoke.lua ALL PASS, probe scripts `10`, `11`, `12` pass.
- EULA § 12.1 fixed by the maintainer (« as applicable in England and Wales »). `vst3/EULA.txt` was
  synced to `licence/EULA.txt`.
- **Exe DONE:** `exe/Kronos Kontrol 1.0i_restricted.exe` (49,098,240 bytes, 22:17).
  - Made with *Export restricted instance*, licence Yes, the corrected EULA pasted.
  - The maintainer checked it: licence § 12.1, splash VERSION 1.0i, MIXER 1/3/8, EDITOR corner clean.
  - `-Check`: 228/228.

**Left to do: the 1.0i VST3** (the maintainer may do it alone).

**RULE: never REAPER and CtrlrX (or a Kronos .exe) open at the same time** (BUILD_EXPORT.md « Rule 0 »).

1. Close the 1.0i exe and CtrlrX (close the panel first), then quit REAPER without saving. At the stop,
   REAPER had an unsaved project with an open « Open panel » dialog: cancel it.
2. `vst3/KronosKontrol_1.0h_restricted.vst3` is already renamed to `.vst3.disabled` (1.0g too), so
   REAPER can load only 1.0i.
3. Run `.\Prepare_VST3_Export.ps1 -Force`.
4. Open REAPER **alone**. Insert > Virtual instrument on new track > *VST3i: CtrlrX*. In it:
   - File > Open Panel `panels\KronosKontrol\KronosKontrol_1.0i.panel` (REAPER is « Not responding »
     for ~30 s);
   - File > Export > *Export restricted instance* → `vst3\KronosKontrol_1.0i_restricted.vst3`;
   - licence **Yes**, paste the whole of `licence\EULA.txt`, OK.
5. Run `.\Prepare_VST3_Export.ps1 -Force` again.
6. REAPER: Preferences > Plug-ins > VST > Re-scan > *new/modified*, then accept the License agreement.
7. Insert *Kronos Kontrol (Francois Rossi)*.
   - Check the DLL: `(Get-Process reaper).Modules | ? FileName -match Kronos` must show 1.0i.
   - Check on screen: § 12.1 wording, splash 1.0i, MIXER 1/3/8 up.
8. Run `.\Prepare_VST3_Export.ps1 -Check`. Expect 228/228.

**Then (optional):**
- Commit the 1.0i work (nothing is committed).
- Turn the probe scripts into a pre-export gate (report § 4).
- Ableton device work (`REPRISE_CODAGE_1.0h.md` § 3).
- Still to compare with the oracle: encoder 1 → 90 sent 71; fader 9 shows 0 on I-A000
  (`REPORT_5637_PROBE.md` § 3).

*Follows `REPRISE_CODAGE_1.0h.md` (1.0h exports still pending, see its § 2) and `PR337_ANALYSIS.md`
(why the probe is adopted, not the skill). Nothing committed, nothing pushed. The maintainer
rebooted during this session.*

## 1. What the probe is

`CtrlrPanelProbe` comes from CtrlrX PR #337 (sgorpi). It is a headless CLI:

- It loads a real `.panel` in the real CtrlrX engine, with mock MIDI ports and no window.
- It runs a JSON script (setValue, click, injectDeviceMidi, callLuaMethod, eval, waitFor,
  screenshot, paint, mouse…) and prints a JSON report to stdout.
- Exit codes: 0 = clean, 1 = errors, 2 = won't load.
- Reference: `build/CtrlrX-pr337/Doc/PanelProbe.md`.

**Verified:** `git diff v5.6.36 pr337-panel-probe-and-skill` touches only `Tests/`. There are no
`Source/` or root CMake changes, so the probe runs exactly the 5.6.36 engine we ship on.

## 2. Done this session

- `ctrlr-project/probe/src/`: a local `git clone` of `build/CtrlrX-damiensellier/CtrlrX`, checked
  out at **`v5.6.36`**. The PR's `Tests/` was overlaid with
  `git checkout origin/pr337-panel-probe-and-skill -- Tests` (29 files).
  - Vendored Boost unzipped in `Source/Misc/boost/`.
  - `build/` itself was **not** touched (project rule: read-only).
- `ctrlr-project/probe/build_probe.cmd`:
  - runs VS 2022 `vcvars64` + Ninja, Release, target `CtrlrPanelProbe` only;
  - build dir `probe/b`, log `probe/build_log.txt`;
  - configure downloaded GoogleTest from GitHub (the first configure needs network).
- **Build: finished, exit code 0** (437/437) before the reboot. The exe is
  `probe/b/Tests/CtrlrPanelProbe.exe`.
- The probe is **a test tool only**. It does not replace CtrlrX 5.6.36: the installed
  `CtrlrX.exe` is still the runtime and the export tool.
- First script written, **not yet run**: `probe/scripts/00_load_snapshot.json`. It does load + 3 s
  wait, `type(KK)`, the types of `kkRefresh` / `kkMixTrack` / `kkMixValues` / `KRONOS_DATA`, and a
  screenshot to `out/00_load.png`.

## 2b. Update (4 Nov, late)

- The probe built fine. Self-test: 34/34. It ran 3 times on 1.0h (~130 s per load).
- Findings and the 1.0i plan: **`REPORT_5637_PROBE.md`**:
  - the `kkProgNumEdit` load error;
  - the splash still says 1.0f;
  - components and modulators disagree.
- « 5.6.37 » is a version bump only. Stay on 5.6.36.
- **1.0i built (21:22):** Findings 1 and 2 are fixed and checked (report § 3b).
  - Panel: `panels/KronosKontrol/KronosKontrol_1.0i.panel`, archived.
  - **Not exported:** that waits for the maintainer's EULA § 12.1 fix.
  - Then export exactly as 1.0h: `Prepare_*`, *Export restricted instance*, paste EULA, 1.0h VST3 →
    `.vst3.disabled` before testing.
- Files changed for 1.0i: `lua/kkMain.lua` (kkProgNumEditBody guard), `sources/build_panel.py`
  (VERSION 1.0i + splash step), `assets/kk_splash.png` / `@2x` / `_links.json` (redrawn).
- Probe gate script: `probe/scripts/10_load_gate.json`.
- **1.0i rebuilt (same number) with Finding 3 fixed:** `kkQuiet` keeps the modulators in step, with no
  MIDI (report § 3b).
  - Probe `11_quiet_values_editor.json` passes. smoke.lua: +3 tests.
- **Blue square at the top left in EDITOR** = spare `kkEdC##` combos left visible (report § 3b,
  Finding 4). **Fixed** (`kkEdHideMenus`, once before the first editor page).
  - Probe `12_editor_corner.json`: corner clean. smoke.lua: +1 test.
  - Pages with more than 14 menus were not opened in the probe; the logic is the normal 0 → 1 show
    path.
  - `make_splash.py` now skips unchanged PNGs and retries on Windows file locks.

## 3. Next steps

1. Finish or verify the build (above).
2. Sanity-run the probe on a small panel first, then on ours:
   ```
   cd C:\Korg\kronos-corpus\ctrlr-project\probe
   b\Tests\CtrlrPanelProbe.exe src\Tests\fixtures\fixture_probe_click.panel src\Tests\probe_click.json
   b\Tests\CtrlrPanelProbe.exe ..\panels\KronosKontrol\KronosKontrol_1.0h.panel > out\00_noscript.json
   b\Tests\CtrlrPanelProbe.exe ..\panels\KronosKontrol\KronosKontrol_1.0h.panel scripts\00_load_snapshot.json > out\00_load.json
   ```
   - If anything fails to write `%APPDATA%`, check the integrity label with
     `C:\Korg\Reset_Integrity_Label.ps1 -CheckOnly`, or copy the exe and panel to a temp dir outside
     the tree (BUILD_EXPORT.md Trap 2).
   - Resources (images) may be missing in screenshots; logic checks do not depend on them. Never
     empty the CtrlrX resource folder.
   - Add `--verbose` to see the Lua/JUCE stderr.
3. Optional: run the PR self-tests, `python src\Tests\probe_selftest.py` (34 scenarios). See the
   script header for its arguments.
4. Write the **assertor** (Python, `probe/tests/`): run the probe, load the JSON, compare against
   the oracles (`scripts/kronos_sysex.py`, `parameter_map.csv`). Suites, in order (PR337_ANALYSIS § 5):
   - a. load-time snapshot: no Lua errors or dialogs, `editMode` false; 1.0h start-up values on
     I-A000 (encoders/sliders, MIXER/PAN 127/112/127) after timer 8;
   - b. MIDI-out bytes for the rack controls vs `kronos_sysex.py`;
   - c. real LuaJIT `eval` of the UTF-8/Latin-1 `kkU` paths;
   - d. dump inject (PRELOAD / corpus PCGs) → modulator state;
   - e. screenshots + mouse hit areas vs the mockups.
5. Doc rule to add to `BUILD_EXPORT.md`: never save the panel in edit mode (upstream bug #2).

## 4. 1.0h exports

**Exe: DONE (4 Nov, 19:51).**
- File: `panels/KronosKontrol/exe/Kronos Kontrol 1.0h_restricted.exe` (49,097,216 bytes).
- Made with *Export restricted instance*, licence Yes, `EULA.txt` text pasted.
- First launch shows the « License agreement » window.
- The maintainer confirmed that I-A000 shows 127 / 112 / 127. `-Check`: 228/228 images.

After the reboot CtrlrX would not show a window. **Cause:** `CtrlrX.settings` (20 MB) held two whole
panels, `KronosKontrol.panel` and `_1.0g`, which CtrlrX rebuilds at start.
- It was renamed to `%APPDATA%\CtrlrX\CtrlrX.settings.bak_2026-11-04_2panels`, so CtrlrX now runs on
  default preferences.
- `BUILD_EXPORT.md` gains « Trap 0 ».
- The prep-script hints now give the restricted/EULA steps.

**VST3: DONE (4 Nov, 19:57).**
- File: `vst3/KronosKontrol_1.0h_restricted.vst3` (48,982,016 bytes).
- Exported from the CtrlrX VST3 in a new, unsaved REAPER project. `KronosKontrol_test.RPP` was not
  touched and still holds its 3 plugins.
- The re-scan showed the « License agreement » window, and the maintainer accepted it.
- `-Check`: 228/228 images.
- REAPER first loaded 1.0g, because every build shares one VST3 UID (`BUILD_EXPORT.md` Trap 0b).
  `vst3/KronosKontrol_1.0g.vst3` was renamed to `.vst3.disabled`. REAPER's modules then showed the
  1.0h DLL loaded.
- I-A000 checked in the VST3. « 127 / 112 / 127 » means the **MIXER row** (8 knobs under the PCG
  field, MIXER view): knob 1 = 127 (EXi 1), knob 3 = 112 (Drum Track), knob 8 = 127 (Master); knobs
  2 and 4-7 = 0. Source: smoke.lua « start-up I-A000 MIXER ».
  Our screen zoom showed knobs 1, 3 and 8 up and the rest at zero. **Both 1.0h release builds
  are validated.**

**EULA wording: the maintainer will fix it later (4 Nov). Do not edit it and do not re-export
until asked.** Two identical copies need the fix: `licence/EULA.txt` and `vst3/EULA.txt`. Issue: § 12.1 says « governed by the law as application in the United Kingdom »
(probably « as applicable in »). The exe contains that text, so fixing it means re-exporting.

Then the Ableton device work (`REPRISE_CODAGE_1.0h.md` § 3).

## 5. Files added (uncommitted)

- `probe/src/` (clone + `Tests/` overlay)
- `probe/b/` (build tree, ~GBs, regenerable)
- `probe/build_probe.cmd`
- `probe/build_log.txt`
- `probe/scripts/00_load_snapshot.json`
- this note
