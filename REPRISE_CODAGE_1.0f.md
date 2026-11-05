# Reprise — Kronos Kontrol 1.0f (3 Nov. 2026, night)

> **4 Nov 2026 (afternoon): current = 1.0h. Resume from `REPRISE_CODAGE_1.0h.md`** (MIXER/PAN tracking + start-up fix done ; restricted exports + Ableton 3.2.3b pending).

> **4 Nov 2026 update — current build is 1.0g** (1.0f + image-cache self-repair `kkResCheck`, list `KK_RES`).
> - **Panel:** `KronosKontrol_1.0g.panel` (the _x24 panel was not rebuilt; the 24-px bug looks gone in the exe). e2check 301/0, smoke ALL PASS.
> - **Exe:** `panels/KronosKontrol/exe/Kronos Kontrol 1.0g.exe`. **All new builds go to `panels/KronosKontrol/exe/` and `panels/KronosKontrol/vst3/`** (maintainer, 4 Nov). The Low label on kronos-corpus was removed (`C:\Korg\Reset_Integrity_Label.ps1`).
> - **VST3:** `panels/KronosKontrol/vst3/KronosKontrol_1.0g.vst3`. Loaded in REAPER, all 228 images, OK.
> - **Repair:** verified on the real exe against the stale 3 Nov cache.
> - **Build procedure, the Low-integrity-label trap and the prepare scripts:** `BUILD_EXPORT.md`.
> - **CtrlrX issue report:** `for_ds/`.
> - **Still to do:** the KRONOS hardware tests of § 2.5 / § 3.

*Replaces `REPRISE_CODAGE_1.0e.md` (now in `_TO_DELETE_2026-11-03/reprise`). Session log : `journal/session-2026-11-03-ctrlrx-codage-2.md` (section « 1.0f »).
Branch `kronos-kontrol-1.0a`, nothing committed, nothing pushed. 1.0e was never exported : export 1.0f instead.*

## 1. State

- Panels : `panels/KronosKontrol/KronosKontrol_1.0f.panel` and `KronosKontrol_1.0f_x24.panel` (canvas 1500 x 456).
  Archive `panels/archives/KronosKontrol.1.0f.panel`. e2check **301 PASS / 0 FAIL**, smoke **ALL PASS** (20 new 1.0f tests ; 3 older tests updated to the 1.0f rules).
  **Not yet looked at in CtrlrX, not exported, nothing sent to a KRONOS.**
- **New Main panel (artwork, `graphics/KRONOS_Main`, `sources_Main/kt.py`)**, the same for the Ableton device (copy +
  README in `ableton-panel/reference/Main_1.0f_2026-11-03/`, pointer at the top of `ableton-panel/RESUME.md`) :
  - **EXi1 / EXi2** above SW2 / HOLD, 49 x 18, centred vertically on the program-name and GM screens (y 80.5) ;
  - **TIMBRE SELECT** (section-title font, whole pixels) on the HOLD row, its E on the GM screen's right edge (x 930) ;
    below it the **TIMBRE screen, popup 1-16** (frame = the MFX2 footprint) ;
  - **TONE ADJUST CONTROLS** under the sliders, centred on the 9 sliders (baseline 421, band 405-432).
- **The 8 encoders + 9 sliders now edit Tone Adjust on the chosen engine / timbre** (`lua/kkMain.lua` `kkTaCtx`,
  `kkTaTrack`, `kkTaSend`, `kkTimbreMenu`, EXi clicks in `kkClick`) :
  - Program : layout of the engine chosen with EXi1 / EXi2 (labels, stored values, Parameter Change fn 43 : TYP 11 =
    EXi 1, 12 = EXi 2 ; HD-1 its own ids). EXi2 only when the program has a second EXi ; HD-1 : both dimmed. Slider 9 :
    label only. Slots without a stored parameter keep the former CC.
  - Combi : Tone Adjust of the timbre chosen in TIMBRE SELECT (labels from its assigns, values from the combi) ; a move
    sends TYP 28, SOC = timbre-1, PID 5 / 4, IDX 0-7 (Master 8). EXi buttons dimmed in Combi ; TIMBRE dimmed in Program.
  - Change from 1.0e : in Program mode the slider names / values follow the engine layout (as the encoders), no longer
    the program's own fader assigns (needed so that what is shown is what is sent).
- **Tone Adjust map, self-contained** : `panels/KronosKontrol/TONE_ADJUST_MAP.md` (reference) and
  `data/tone_adjust_map.json` (read by the build) — every engine / EXi slot (fields, ranges, Parameter Change ids,
  all matched against Korg's `Prog_HD-1.txt` / `Prog_EXi.txt` with 0 disagreement), every Tone Adjust code (kind,
  range), EP-1 variants, combi timbre offsets. pcglib is only needed for `python sources/ta_values.py --refresh`.
- Factory slots : `KRONOS_DATA.tav` (2176 x 19), `tav2` (371 two-EXi programs), `tat` (768 combis, per-timbre blocks)
  — `scripts/gen_data_lua.py build_tav` ; `kronos_data.lua` grows to 2.7 MB.
- Checks : Lua = Python readers on the factory bank : 40752 program values (EXi 1 + 2) and 208896 combi-timbre values,
  0 differences (one Lua bug found by this check and fixed : a timbre assign with bit 7 fell back to EXi 1).

- **Ableton device built from the same Main** (late night) : `ableton-panel/phases/phase_11_main_1.0f/Kronos Kontrol
  OS3.2.3a.amxd` ; its artwork = `kt.py` with `KK_M4L=1` (no EDITOR column ; MIDI CH under TFX2, JSON MAP on the
  PCG row), `KK_OUT=<folder>` writes elsewhere. Details : `ableton-panel/RESUME.md`.

- **Last adjustment (same version 1.0f)** : the encoder screen moved up 6 px (centred between the two encoder rows ;
  `kt.py`, layout `encoders_display1` y 86), both panels ; 1.0f panels rebuilt. Ableton device renamed **OS3.2.3a**
  (the new line restarts at 3.2.3a). Obsolete files : `_TO_DELETE_2026-11-03/` here and in ableton-panel (index inside).

- **Slider 9 (« Slider M », the Master slider)** : in Tone Adjust it is not a master control but a ninth assignable slider ; what it does is each program's own **Master Fader Assign** (0-based byte 2682 ; code = byte & 0x7F, bit 7 = EXi 2). Program mode : label = that code's name ; **assigned Off → position 0 and « - »** (no effect on the sound — maintainer's rule : once a user assigns it and saves, the stored value is read) ; a code editing one stored parameter → its stored value, and a move sends it (Parameter Change, TYP 11 / 12) ; another code (macro, EP-1 IFX WET/DRY) → its name only, at 64. Combi mode : the timbre's own Master assign / value (TYP 28, PID 4, IDX 8). Any control assigned Off (combi timbre controls too) sits at 0 with « - ». Factory bank : 1573 of 2176 programs Off (all HD-1 / AL-1), 550 with a parameter (CX-3 1' drawbar, STR-1 PICKUP2 LVL, MS-20EX MG FREQ, PolysixEX MG mode, MOD-7 FEEDBACK). Details : `ctrlr-project/panels/KronosKontrol/TONE_ADJUST_MAP.md` § 1 and § 4b.

## 2. Exporting (maintainer)

1-3. **Superseded on 4 Nov: follow `BUILD_EXPORT.md`.**
   - Use the `Prepare_Exe_Export.ps1` / `Prepare_VST3_Export.ps1` scripts.
   - Export the .exe from CtrlrX.exe to `panels/KronosKontrol/exe/`.
   - Export the .vst3 from the CtrlrX VST3 in REAPER.
   - Not `temp/vst3host/CtrlrX.exe`: it has a Low integrity label, so its `%APPDATA%` writes fail.
   - Still true: never empty `%APPDATA%\CtrlrX\kkKronosKontrol`.
   - 1.0e and 1.0f were never exported. 1.0g has been exported and tested (exe + vst3).
4. Visual test : EXi1 / EXi2 lit / dimmed (HD-1, single-EXi, two-EXi programs), TIMBRE popup 1-16 in a combi, labels
   and positions follow ; TONE ADJUST CONTROLS / TIMBRE SELECT titles.
5. KRONOS test (agreement first, never Write / Store ; monitor shows each message) : on a two-EXi program, an EXi 2
   encoder changes engine 2 only (Reply 24 code 0) ; in a combi, timbre 3's encoder changes timbre 3 only ; check
   that bit 7 of a timbre assign really means EXi 2.

## 3. To do next

1. The exports, the visual test, the KRONOS test above.
2. Ableton device : adopt the 1.0f Main (README in `ableton-panel/reference/Main_1.0f_2026-11-03`).
3. Hardware check of the 1.0d Parameter Change edits (TYP 11/12 by slot, Note Map Remove = 255 ?).
4. Exe icon : post-export replacement (rcedit / Resource Hacker) + a Kronos Kontrol `.ico`.
5. EULA §12.1 wording ; licence box at export or file only.
6. Still open : « Not responding » freezes, slider 9 / MIXER 8, hardware Read / Apply / Reply.
7. **Bug (maintainer, 4 Nov, 1.0g exe):** on first launch, the first program displayed does **not** show its current
   Tone Adjust values (8 encoders + 9 sliders). They appear once the program is changed up then back down.
   Look at the initial display path: `kkInit` → Mode Request → first `kkShow` / `kkTaTrack` before any dump or
   PRELOAD sync, versus the path taken on a program change.
8. **MIXER / PAN do not track the selected sound** (maintainer, 4 Nov). The PCG holds the values, and pcglib's JSON
   already exports them (`mix`, `timbres[]`). The panel never reads them: `KK.vol` / `KK.panv` are fixed defaults. The
   Ableton device shows the volumes only. Full analysis, offsets, the pcglib KRONOS→OASYS gap (EXi selector / level / pan
   zeroed) and what to add on each side: `kronos-pcglib/docs/MIXER_PAN_FOR_KRONOS_KONTROL.md`.

**4 Nov 2026, maintainer: stop producing the +24 px (_x24) version.** The 24 px bug no longer shows in CtrlrX.
Build and export the plain panel only.

(OASYS / NAUTILUS : only the GUI, and only on a major change — `kt.py` was changed, they were NOT regenerated.)

## 4. Reminders

- Read-only : `ctrlr-project/{build,reference,docs,GUI_pic,consolidate,panels/TR-Rack-Editor-main}`.
- Nothing sent to the KRONOS without agreement ; never Write/Store.
- Uncommitted : everything of 1.0d / 1.0e, plus `graphics/KRONOS_Main/*` (artwork, layout, `kt.py`),
  `sources/ta_values.py`, `data/tone_adjust_map.json`, `TONE_ADJUST_MAP.md`, `sources/build_panel.py` (VERSION 1.0f,
  EXi / TIMBRE controls), `lua/kkMain.lua`, `scripts/gen_data_lua.py`, `data/kronos_data.lua`, `assets/kk_splash*`,
  `tools/panel-harness/{e2check.py,smoke.lua}`, the 1.0f panels and archive ; in ableton-panel :
  `reference/Main_1.0f_2026-11-03/` and `RESUME.md`.
- Previous artwork kept in the session scratchpad (`KRONOS_Main_before_1.0f`) ; git has it too.
