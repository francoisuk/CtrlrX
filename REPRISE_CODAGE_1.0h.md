# Reprise — Kronos Kontrol 1.0h (4 Nov 2026, afternoon)

*Follows `REPRISE_CODAGE_1.0f.md` (1.0g section at its top). The session was interrupted during the export step because
CtrlrX / REAPER would not start properly; the maintainer may reboot. Nothing committed, nothing pushed.*

## 1. Done in this session (panel 1.0h, CtrlrX side)

- **MIXER / PAN now follow the selected sound** (`panels/KronosKontrol/lua/kkMain.lua`, after `kkMixShow`):
  - `kkMixValues(item, combi)` uses the same rule as pcglib `ToneAdjustReader.ReadMix`
    (`kronos-pcglib/docs/MIXER_PAN_FOR_KRONOS_KONTROL.md` § 2):
    - **Combi:** timbre t volume = 4802+188(t-1)+5, pan = +14.
    - **Program, HD-1 payload:** OSC1 3198 / 3193, OSC2 3664 / 3659.
    - **Program, EXi payload:** only the EXi actually selected: EXi 1 2866 / 2861, EXi 2 3918 / 3913.
    - **Program, both payloads:** Drum Track 2690, Master 1188. Panpots are masked with `& 0x7F`.
  - `kkMixTrack()` reads its values in this order:
    1. the bytes of the device-read bank, the loaded PCG or the live dump (`kkKarmaItem`). **A PCG loaded in the panel is read directly.**
    2. otherwise the factory table `KRONOS_DATA.mix` (16 bytes per slot, 255 = none).
  - No value → 0. Guarded by `KK.mixKey` / `KK.mixSrc`, so a user move survives a re-show. Called from `kkEncLabels`, so every path that refreshes Tone Adjust also refreshes MIXER / PAN.
- **Start-up bug fixed (I-A000 values not shown, resume 1.0f § 3 item 7).**
  - **Cause:** after `luaPanelLoaded`, the exported .exe / .vst3 restores the last saved control positions. The guards `KK.taKey` / `KK.mixKey` then kept those positions until the program changed.
  - **Fix:** `kkRefresh()` forces Tone Adjust and MIXER / PAN back to the selected sound. It runs:
    - from **`luaPanelRestoreState` → `kkRestoreState`** (new method, registered in `build_panel.py`);
    - from **timer 8**, 500 ms after load and once more 2 s later.
  - `kkInit` resets the guards.
- **Factory mix table:** `scripts/gen_data_lua.py` `mix_of` / `build_mix` → `KRONOS_DATA.mix` (2944 slots). It was checked against the maintainer's pcglib export `ableton-panel/KKontrol-amxd-PRELOAD.3.2.3.json`: **2944 / 2944 slots identical**. `kronos_data.lua` regenerated (2.9 MB).
- **Version 1.0h** (`sources/build_panel.py`). Panel `panels/KronosKontrol/KronosKontrol_1.0h.panel`, archive `panels/archives/KronosKontrol.1.0h.panel`.
- **Checks:**
  - `tools/panel-harness/e2check.py`: **301 PASS / 0 FAIL**. Two count checks went from 6 → 7 and 3 → 4, for the new `kkMixTrack` guard.
  - `smoke.lua`: **ALL PASS**, with 17 new 1.0h tests: start-up values, timer 8, RestoreState, user move kept, factory program / combi, HD-1 / EXi / combi bytes, panpot bit 7.
  - `preflight.py` is stale: it looks for the unversioned `KronosKontrol.panel`. Ignore it.
- `Prepare_Exe_Export.ps1 -Force` was run once: 228 images, the marker and cache cleared, settings kept. **Run it again before the export after a reboot.**

## 2. Where it stopped: the exports

The maintainer asked for these builds, using the **EULA licence** (`panels/KronosKontrol/licence/EULA.txt`; answer **Yes** to « attach a license? » and pick that file):
- **`_restricted`** builds (CtrlrX: File > Export > *Export restricted instance*);
- `panels/KronosKontrol/exe/Kronos Kontrol 1.0h_restricted.exe`, from `CtrlrX.exe` (Program Files);
- `panels/KronosKontrol/vst3/KronosKontrol_1.0h_restricted.vst3`, from the CtrlrX VST3 in REAPER, then a REAPER re-scan.

What went wrong (14:44–14:58):
- A CtrlrX instance started by Claude never showed a window, so Claude stopped it.
- The maintainer started CtrlrX and REAPER. CtrlrX stayed at 61 MB with no window while using CPU, and Claude stopped that one too.
- REAPER stayed « Not responding » for more than 7 minutes. It was not killed; that was refused.
- REAPER reopens `panels/KronosKontrol/reaper/KronosKontrol_test.RPP`. Its single track has **3 plugins**: the old *Ctrlr (Instigator)* « Kronos Kontrol.vst3 », the CtrlrX VST3 with a panel state, and KronosKontrol_1.0g.vst3.
- **Maintainer:** the project must load **only the CtrlrX VST3**; the maintainer will delete the old Ctrlr. The RPP was **not** modified.
- Suspected cause, not proven: both apps started at once (KORG USB-MIDI driver window `KORGUMDN` in CtrlrX), or the heavy 3-plugin project.

To resume:
1. After the reboot, the maintainer launches **CtrlrX alone** and hands over control (computer-use access already granted this session: CtrlrX, REAPER (x64), File Explorer).
2. Run `.\Prepare_Exe_Export.ps1`.
3. In CtrlrX, open `KronosKontrol_1.0h.panel`, then Export restricted instance, licence = EULA.txt. Save as `exe\Kronos Kontrol 1.0h_restricted.exe`.
4. Run the script again, launch the .exe once, then `-Check`. On I-A000, check that the encoders, sliders and MIXER / PAN show 127 / 112 / 127.
5. Open REAPER, with the project holding only the CtrlrX VST3, and run `.\Prepare_VST3_Export.ps1`. Load the 1.0h panel in the CtrlrX VST3, then Export restricted instance + EULA to `vst3\KronosKontrol_1.0h_restricted.vst3`. Re-scan, load it, then `-Check`.
6. Update `BUILD_EXPORT.md`: restricted export and the EULA answer (it still says « No » for test builds).

## 3. Still to do after the exports: Ableton device (`ableton-panel/`)

1. **MIXER and PAN by default.** `sources/kk_banknames_v5_body.js` `updateMix` uses `mix.volume` only.
   - Add the pan values to the PAN view.
   - Show null as « - » or 0, not as a wrong value.
   - Use `sendSet` rather than `send`, so a program change sends nothing to the KRONOS (see MIXER_PAN doc § 5).
   - pcglib's JSON export now carries the correct values (maintainer).
2. **JSON choice from the device's own folder** (maintainer, 4 Nov):
   - At load, list the JSON files in the folder where the .amxd sits. Show **only names starting with `KKontrol-amxd-`** (pcglib's default export prefix + PCG name) in the file-name popup.
   - No such JSON → display nothing. Display resumes once a file has been put in the folder and chosen in the popup.
   - Provide a **refresh** of the list, to pick up files added after launch.
   - Test files already there: `KKontrol-amxd-PRELOAD.3.2.3.json` and `KKontrol-amxd-PRELOAD_3.1.4.json`.
3. Build the device as **`Kronos Kontrol OS3.2.3b.amxd`**, in `ableton-panel/phases/…` only (memory: the maintainer installs it).
4. **Prune `ableton-panel/`** of obsolete files. Use a `_TO_DELETE_<date>/` folder with an index, as on 3 Nov; never delete outright.

## 4. Files changed (uncommitted)

- `ctrlr-project/lua` → `panels/KronosKontrol/lua/kkMain.lua`
- `panels/KronosKontrol/sources/build_panel.py`
- `scripts/gen_data_lua.py`
- `panels/KronosKontrol/data/kronos_data.lua`
- `panels/KronosKontrol/KronosKontrol_1.0h.panel` and `panels/archives/KronosKontrol.1.0h.panel`
- `tools/panel-harness/{e2check.py,smoke.lua}`
- this note
