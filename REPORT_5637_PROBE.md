# CtrlrX « 5.6.37 » and the panel probe: what they bring, and do we need them for 1.0i?

*Report of 4 Nov 2026, evening. It is based on measurements, not on the PR's description: git diffs
against the upstream repository, the probe built and run here, and three probe runs on
`KronosKontrol_1.0h.panel`. It follows `PR337_ANALYSIS.md` (written before the probe existed here).*

## Short answer

| Question | Answer |
|---|---|
| Is there a CtrlrX 5.6.37 to move to? | **No.** No 5.6.37 release exists; v5.6.36 (21 Oct) is still « Latest ». The `5.6.37-Maintenance` branch is **one commit**: a version bump (VERSION file, 4 `.jucer` names, an **empty** changelog entry). Not one line of engine code changed. |
| Must 1.0i be built with 5.6.37? | **No.** Keep building and exporting 1.0i with the installed **CtrlrX 5.6.36**, exactly as for 1.0h. |
| Must 1.0i be built with the probe? | **No.** The probe is not part of the build or export chain: it produces nothing that ships. |
| Should 1.0i be **checked** with the probe? | **Yes, recommended.** Its first three runs found **three real problems in 1.0h** that none of our existing checks could see (§ 3). Two of them should be fixed in 1.0i. |

## 1. The « 5.6.37 » build

- **Upstream state (checked 4 Nov via git + GitHub):**
  - releases: v5.6.36 is « Latest » (21 Oct 2026); there is no v5.6.37 tag or release;
  - branch `5.6.37-Maintenance`: tip `49497f7` (24 Oct), = v5.6.36 + one commit « version bump to
    5.6.37 »: 6 files, +8 / −5 lines, changelog section « Version 5.6.37 » with no entries;
  - PR #337 (the probe) is built **on that branch**, which is why it is called « 5.6.37 ». It is still
    **open**, not merged. Head `62d6121` is unchanged since our copy, last activity 2 Nov.
- **In PR #337's discussion:**
  - the author offers to write automated probe tests for the maintainer's test panels;
  - Damien Sellier calls it « extremely powerful », but has no free time in the coming weeks;
  - the macOS CI runner is deprecated.
  - So no 5.6.37 release should be expected soon.
- **Consequence:** a « 5.6.37 build » would be the 5.6.36 engine with a different version number. It
  would bring no fix and no feature. Moving to it would only cost a re-validation (EULA, exports,
  integrity label, the +24 px question). **Stay on 5.6.36.** Watch for a real 5.6.37 changelog.

## 2. The probe (`CtrlrPanelProbe`)

### What it is

- A command-line program. It loads a real `.panel` in the **real CtrlrX engine**: real component
  tree, real LuaJIT, real timers, real paint. It has no window and needs no KRONOS: the MIDI ports are
  mocks.
- It runs a JSON script of actions:
  - set a control, click;
  - inject MIDI as if from the synth;
  - call or eval Lua;
  - screenshot, paint one component, mouse gestures.
- It writes a JSON report:
  - every MIDI byte sent, per step;
  - every console line and Lua error;
  - the dialogs;
  - the value, visibility and rectangle of all 895 modulators.
- Exit code: 0 clean, 1 errors, 2 won't load.

### Our build of it

- Built here on **our exact engine**:
  - `probe/src` = a clone at tag v5.6.36, plus the PR's `Tests/` folder;
  - git confirms the PR changes nothing outside `Tests/`;
  - build in `probe/b`, VS 2022 + Ninja, 437 steps, exit 0.
- **The PR's own self-test: 34 / 34 scenarios pass** on our build (226 s).
- **Cost on our panel: about 130 s per run**, for a 30 MB panel with 895 modulators. Nearly all of it
  is loading.
  - `--stdin` mode loads once and then runs any number of scripts (~6 ms each), so a suite should use it.
  - Without it, each test pays the 130 s.
- It is **our own build of unmerged code**, not an upstream release. That doesn't matter for its
  purpose: it ships nothing, and its engine is byte-for-byte the 5.6.36 we export with.

### How it compares with what we had

| Check | Sees | Does not see |
|---|---|---|
| `e2check.py` (301 checks) | XML: names, rectangles, callbacks, resources | behaviour |
| `smoke.lua` (Lua 5.4 + fake API) | our Lua logic, byte offsets | the real engine: callback order, timers, what is drawn, what is saved |
| Hardware test sheets | everything, with the real KRONOS | — but they are manual, slow and late |
| **Probe** | the real engine's behaviour: callback order at load, timers, MIDI bytes sent, component vs modulator values, pixels | the real USB-MIDI driver, the synth's replies (unless we inject them), host specifics (REAPER / Live state saving) |

## 3. What it found in 1.0h on its first runs

Runs: `probe/out/00_noscript.json`, `01_startup_midi.json`, `02_component_vs_modulator.json`. The
scripts are in `probe/scripts/`.

### Finding 1: a Lua error at every load (`kkProgNumEdit`)

- **What the console shows:** at every load,
  `ERROR kkProgNumEdit : [string "kkMain"]:1488: attempt to perform arithmetic on field 'ch' (a nil value)`.
- **Cause:**
  - the program-number label has `uiLabelChangedCbk = kkProgNumEdit`;
  - while CtrlrX restores the panel, it sets that label's text and fires the callback **before
    `kkInit` runs**;
  - the callback calls `kkSelect`, which computes `KK.ch - 1` while `KK.ch` is still nil.
- **Impact today:** none visible. `kkGuard` catches the error, nothing is sent, and the display ends
  up right.
- **Why it matters:**
  - a callback that **sends MIDI** is running during load;
  - if the init order ever changes, so that `KK.ch` is set first, every launch would send a program
    change to the KRONOS;
  - it is also a Lua error message in the user's CtrlrX console.
- `smoke.lua` cannot see this: its fake API never fires callbacks during load.
- **1.0i fix:** in `kkProgNumEditBody`, return when the panel is not initialised yet (`KK.ch == nil`).
  Add a probe test: « a clean load has no ERROR line in the console ».

### Finding 2: the splash says « VERSION 1.0f » in 1.0h (and in the shipped 1.0h exe / VST3)

- **What happens:** the About screen opens as a splash at load (closed after 5 s or by a click). It
  is the image `assets/kk_splash.png`, and it shows **VERSION 1.0f**, while the panel is 1.0h.
- **Cause:**
  - `sources/make_splash.py` reads `VERSION` from `build_panel.py`, but it is a separate script;
  - it was last run on 3 Nov 22:12 (1.0f), and `build_panel.py` does not call it;
  - so **1.0g and 1.0h both carry the 1.0f splash**. That includes today's `_restricted` exe and VST3.
- **1.0i fix:** make `build_panel.py` run `make_splash.py` (or fail when the splash version ≠
  `VERSION`). Add a probe check: screenshot at load, or check that the splash resource hash matches
  `VERSION`.

### Finding 3: the knobs show the right values, but their modulators hold 0

- **Confirmed:** the 1.0h start-up fix works in the real engine. After 3 s:
  - timer 8 has run twice (`KK.refreshN = 2`);
  - the **components** show MIXER `127, 0, 112, 0, 0, 0, 0, 127` and encoders
    `127, 113, 64, 64, 113, 113, 113, 64`. These are exactly the I-A000 factory bytes, and what you
    confirmed on screen in both exports.
- **New:** the **modulators** behind those knobs all still hold **0**.
  - `kkTaTrack` / `kkMixTrack` use `getComponent():setValue(v, false)`, which moves the drawing only.
  - CtrlrX saves and restores the **modulator** values (host state / `.settings`).
  - So what gets saved is 0 or a stale value, not what the user sees. That is the mechanism behind the
    1.0h start-up bug, which 1.0h works around by redrawing (timer 8 + `luaPanelRestoreState`).
- **Impact:**
  - none visible today, thanks to the workaround;
  - but a host that automates or reads these parameters (VST3 parameter values) sees 0;
  - and a saved DAW project stores 0.
- **1.0i: worth investigating, not urgent.** Look for a way to set the modulator value without sending
  MIDI, so that the component and the modulator agree. The probe is the tool to measure it: compare
  `getValue()` on both sides.

### Also observed (no problem found, still to compare with the oracle)

- **MIDI out of a knob move:**
  - `F0 42 30 68 4E 02 F7` (mode change to Program);
  - then a **wait** for the KRONOS's reply. With no synth, the queue is released later, as designed;
  - then the Parameter Changes, e.g. MIXER 1 → 100 = `F0 42 30 68 43 … 00 00 00 64 F7`.
- **Bank click I-B:** `B0 00 00`, `B0 20 01`, `C0 00`, and the name list switches to I-B000 De La
  Salsa Brass. Correct.
- **Encoder 1 moved to 90** sent value `0x47` (71): Tone Adjust scaling to the parameter's own range.
  **To be checked** against `scripts/kronos_sysex.py` / `parameter_map.csv` before calling it right
  or wrong. This is exactly the kind of offline byte comparison the probe allows.
- **Fader 9** shows 0 on I-A000 (Tone Adjust byte 17 = 1). Check it against the Tone Adjust map.
- **Probe blind spots met:**
  - the report's `finalState` reads modulator values, so for this panel the assertor must read
    component values through `eval` (Finding 3);
  - `getValueMapped()` is meaningless on these sliders: it returns 39084 everywhere.

## 3b. Fixed in 1.0i (4 Nov, 21:22)

- **Finding 1:** `kkProgNumEditBody` (`lua/kkMain.lua`) returns while `KK.ch` / `KK.prog` are nil.
- **Finding 2:** `build_panel.py` runs `make_splash.py` before embedding the splash. Its log prints
  « splash : redrawn for <VERSION> ».
- **Checks run on `KronosKontrol_1.0i.panel`:**
  - e2check: 301 PASS / 0 FAIL;
  - smoke.lua: ALL PASS;
  - probe `scripts/10_load_gate.json`: exit 0, 0 errors, 0 dialogs, 0 MIDI out at load;
  - console: only « panel loaded — 1.0i »;
  - the splash reads VERSION 1.0i and closes after 5 s;
  - I-A000 start-up values are unchanged: MIXER 127/0/112/0/0/0/0/127, encoders
    127/113/64/64/113/113/113/64.
- **Finding 3: fixed in 1.0i as well (same version number, rebuilt at the maintainer's request).**
  - New `kkQuiet(m, v)` in `lua/kkMain.lua`. It sets the component (drawing), then
    `m:setModulatorValue(v, false, false, true)`: MIDI is muted and the source is « program », so CtrlrX
    skips `luaModulatorValueChange`.
  - It is used for MIXER / PAN, the 17 Tone Adjust controls (selection and CC echo) and the 8 KARMA
    sliders (dump, factory table, CC echo).
  - **Probe `scripts/11_quiet_values_editor.json`:**
    - 33 / 33 component = modulator after load, 16 / 16 after the I-B program change;
    - 0 MIDI out at load;
    - the bank change sends only `4E` + `B0 00` / `B0 20` / `C0`;
    - a user move of MIXER 1 still sends its Parameter Change (`… 00 00 00 64 F7`).
  - smoke.lua: +3 tests (mock `setModulatorValue`), ALL PASS. e2check: 301 / 0.
- **Finding 4: FIXED in 1.0i (same version number).**
  - **Real cause** (corrects the first explanation below): `KKE_POOL.C` is a high-water mark, so
    `kkEdPoolHide` never touched menus that no page had used yet.
  - **Fix:** new `kkEdHideMenus()` (`lua/kkEdGui.lua`), called once from `kkEdShowPage`. It gives every
    pooled menu a real change 1 → 0. The pool size comes from `KK_EDP` (65).
  - **Probe `scripts/12_editor_corner.json`:** 0 parked control visible, GENERAL shows its 14 menus,
    and the corner pixels are background (25, 25, 27).
  - smoke.lua: +1 test. e2check: 301 / 0.
  - Side fix: `make_splash.py` writes a PNG only when its bytes change, and retries (Windows refused
    `kk_splash@2x.png` with EINVAL twice during builds).
- *First analysis, kept for the record:* a small blue square at the top left in EDITOR.
  - It is the editor's **spare pooled dropdowns** `kkEdC##` (51 on the GENERAL page), parked at
    `0 0 10 10`.
  - They are created with `componentVisibility = 0`, but a uiCombo in 5.6.36 does not apply it at
    load: the probe shows `visible: false` but `liveVisible: true`.
  - `kkEdPoolHide` → `kkEdVis(n, 0)` writes the same 0, so nothing changes and the combo stays shown.
  - Other pooled types are hidden correctly.
  - Possible fix: make `kkEdVis` force the change the first time (write 1 then 0), or hide the component
    directly.
- 1.0i is **not exported**: the EULA fix is still pending (the maintainer will do it).

## 4. Recommendation for 1.0i

1. **Build and export 1.0i exactly as 1.0h**: generator → CtrlrX 5.6.36 → exe / VST3, EULA, the
   `Prepare_*` scripts. No new runtime.
2. **Add the probe as a check before export.** It doesn't produce the build; it guards it:
   - a **load gate**: exit 0, no dialogs, no `ERROR` line in the console, version label = `VERSION`,
     splash up to date;
   - **start-up values**: I-A000 MIXER / encoders / faders (component values) = the factory table;
   - **MIDI bytes**: rack controls and bank / program selection, compared with `kronos_sysex.py`.
     Start with the 5 buttons, the MIXER and the encoders;
   - one `--stdin` session for the whole suite (~2–3 min in all, mostly the single load).
   - About 1 day of work for a small Python assertor (`probe/kkprobe.py` is the start of it).
3. **Fix in 1.0i:** Finding 1 (guard `kkProgNumEdit`) and Finding 2 (splash generated by the build).
   Investigate Finding 3.
4. **Keep the hardware sheets** for what a mock cannot do: the real driver, the synth's replies and
   timing, writing to the instrument, KARMA.
5. **Do not adopt the PR's AI « skill »** (unchanged from `PR337_ANALYSIS.md`): it hand-edits
   `.panel` files, and ours is generated.
6. **Upstream:** Finding 3 (state saved from modulators while components show something else) and the
   load-time label callback are worth reporting to CtrlrX, as questions rather than bugs.

## 5. Files

- **Probe:** `probe/src` (v5.6.36 + PR `Tests/`), `probe/b/Tests/CtrlrPanelProbe.exe`,
  `probe/build_probe.cmd`.
- **Helper:** `probe/kkprobe.py` (runs a script and prints a summary).
- **Scripts:** `probe/scripts/00_load_snapshot.json`, `01_startup_midi.json`,
  `02_component_vs_modulator.json`.
- **Reports and images:** `probe/out/*.json`, `probe/out/02_rack.png` (the 1.0f splash over the
  rack).
- Nothing in the panel, the Lua or the builds was changed for this report.
