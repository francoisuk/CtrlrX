# Session 3 Nov. 2026 (afternoon) — CtrlrX coding 2 : editor pages, faders, export resources → 1.0c

Maintainer's report (captures in `ctrlr-project/for_agent/`, 15 images) : text overlapping / needing 3 lines, screens
too wide, VST and EXE showing « Invalid Resource » (X-Y pad), click areas not matching the artwork, encoders missing in
the exports, every fader stopping one tick short at both ends.

## Causes found

| Symptom | Cause | Fix |
|---|---|---|
| Exported VST3 / .exe : old background (16 encoders), « Invalid Resource » on the X-Y pad, no encoders, clicks « not on the buttons » | The exported instance imports its embedded resources **once** : `%APPDATA%\Kronos Kontrol\.delete_me_to_reload_resources` dated 1 Nov. 19:43, so `CtrlrManager::importInstanceResources` (CtrlrManagerInstance.cpp:214-226) skipped them. The folder `kkKronosKontrol` next to it held the 1 Nov. files : `kk_fond_notext` (fixed name) = 0.99/1.0a background ; the 1.0b images (hashed names) absent → Invalid Resource / nothing drawn. The controls were at their 1.0b places over a 1 Nov. background : that is the « click area » mismatch. | Cache and marker moved to the session scratchpad (not deleted). `kk_fond_notext` and `KRONOS_KONTROL_led_strip` now get content-hashed names too (`build_panel.py`, FOND_RES / LED_RES). **Before testing any new export : delete `%APPDATA%\Kronos Kontrol\kkKronosKontrol` and `.delete_me_to_reload_resources`.** |
| Faders : value 0 on the 2nd tick, 127 on the 10th | JUCE lays a linear slider out in its bounds reduced by the thumb radius at both ends (`LookAndFeel_V2::getSliderLayout`, `sliderBounds.reduce (0, thumbIndent)` ; V4 radius = min(12, w/2) = 12) and `CtrlrFilmStripPainter` stretches the frame into that : travel 24 px short. | `build_panel.py fader()` : component 12 px taller at both ends (THUMB) ; strip unchanged. |
| Editor : labels overlapping (STR-1 FEEDBACK, MS-20EX PITCH / CONTROLLER, KARMA GE, MOD-7 OSC 2-6…), menus running out of their section (AL-1 EXTERNAL IN SEL) | `kmodel.short()` counts letters (11 per line, 2 lines, the rest glued on the last line) ; `kmodel.item_w` under-estimated the inline menu row of a knob section (label + 70 px menu) | `kmodel.fit()` measures in pixels (TP.width), 2 lines with abbreviations, else **3 lines**, a long word is cut after « . » or « / » ; knob labels are wrapped by `ked.section` to the real knob pitch, bottom-aligned ; `kmodel.inline_w` = real width of the row |
| Menus far too wide for 2-3 characters (PITCH 1/2 : 280 px for « 0 ») | G-block menus filled their column ; inline menus fixed at 70 | `kmodel.menu_w()` : widest known value + arrow, 40-112 px (56 min in grids) |

New checker : `graphics/KRONOS_Editor/sources_Editor/kcheck.py` (labels < 4 px apart, label on a display, display or label
outside its section). Before : **82 defects on 37 pages** ; after : **0**. Baseline check first : the unchanged scripts
regenerate the engine layouts byte for byte (35/35).

Result : 215 Full pages (MOD-7 OSC and STR-1 OSC gained one page each), 147 of the 213 previous layouts changed (menu widths,
wrapping). Installed in `graphics/KRONOS_Editor/Full` (old ones in git) ; `scripts/gen_full_editor.py` rerun.

## Not fixed (reported)

557 controls are drawn but have no knob / menu in the panel (value box empty, no knob : AL-1 EDGE, MS-20EX FINE TUNE,
BEND RANGE, MOD-7 FREQ RATIO…) : `gen_full_editor.py` skips them because Korg's table entry does not add up (« plage nulle » :
range wider than the bit field, e.g. EDGE -100~+100 in bits 7~6 of byte 423 shared with other parameters ; « data
illisible » : `00~7F, FF`, empty). Guessing the bytes could overwrite neighbours on Apply. All have a SysEx parameter id
(TYP/SOC/PID) : editing them by parameter-change messages instead of dump bits is the way out (to plan).

## Other changes (maintainer's requests during the session)

- Splash : « (Dynamic Recordings) », « Author of the book Mastering the KRONOS », the book title is a link (underlined) to
  https://www.kronoscopie.com, the web line is kronoscopie.com (all links .com) ; version and page count read from the
  generator (VERSION 1.0c, 216 PAGES).
- EULA v2.0 (maintainer's text) and THIRD_PARTY_NOTICES (source-offer contact : kronoscopie.com, contact@kronoscopie.com)
  copied to `panels/KronosKontrol/vst3/`. EULA §12.1 reads « the law as application in the United Kingdom » : wording to
  check by the maintainer.
- `VERSION = '1.0c'` ; panels `KronosKontrol_1.0c.panel`, `_1.0c_x24.panel` (canvas 1500 x 456) ; archive
  `archives/KronosKontrol.1.0c.panel` (SHA256 7a579b93…).
- Harness : e2check counts read from the data (pages, resources, splash links), fader rectangles + 12 px, hashed names :
  **295 PASS, 0 FAIL** ; smoke : 216 pages, .com link : **ALL PASS**.

## Export (not done : stopped by the maintainer, sandbox)

`%APPDATA%\CtrlrX\kkKronosKontrol` emptied (recreated empty : CtrlrX refuses to import without it, « the path specified as
the resource directory is not one », once per resource). Test host relaunched empty (`temp/vst3host/CtrlrX.exe`, MIDI
ports all « No MIDI »). Steps : see `REPRISE_CODAGE_1.0c.md` §2.

## 1.0d (evening) — editor controls by Parameter Change

Maintainer : OASYS / NAUTILUS get only the GUI, on major changes ; export later ; switch the controls without knob / menu
to SysEx.

- `scripts/gen_full_editor.py` : `classify_sx` — when the dump bits are unusable (« plage nulle », « data illisible ») and
  the table gives TYP/SOC/SUB/PID/IDX, the parameter is kept with `sx`, `vlo` (signed value of index 0, `9C~64` = -100),
  `vext` (extra value, `00~7F, FF`). Pages with instances (except EXi engine pages) are left out. **528 of 557** ; 29 left
  (no address / ASCII / unreadable).
- `lua/kkEdGui.lua` : `kkEdSendSx` (mode check, engine check when a dump is there, TYP by EXi slot, `kkSendM(kkParam…)`),
  `kkEdIdxNow` returns the last value sent ; `KKE.sxv` cleared on each new dump (`kkMain.lua`, `kkPcg.lua`).
- Bug found : `p['w']` (bit width) was overwritten by the rectangle width before the Lua was written, since 0.98c. The Lua
  now gets `bw` (real bit width), JSON keeps the rectangle.
- VERSION 1.0d, splash regenerated, panels built (normal + x24), e2check K1 count 6719 → 7247 : 295 PASS / 0 FAIL ; smoke
  + 7 tests 1.0d : ALL PASS. Not exported, not seen in CtrlrX. Resume : `REPRISE_CODAGE_1.0d.md`.

## 1.0e (night) — encoders and faders follow the program / combi

Maintainer : the 8 encoders and 9 faders must show each program's / combi's current value, as the KARMA sliders do ;
the VOLUME slider at 64 by default ; the function existed before (pcglib, post-mortem).

- Source found : kronos-pcglib `Model/Common/File/ToneAdjustReader.cs` + `EngineLayoutTable.Generated.cs` /
  `ToneAdjustTable.Generated.cs` (the data of the Ableton panel's JSON export v3). A program stores no Tone Adjust value
  (Parameter Guide p. 35 : Relative = 0 / centre in Program mode, Absolute mirrors the program parameter) ; the value
  shown is the stored parameter behind the control, as in pcglib.
- `sources/ta_values.py` (new) parses both tables, writes the Lua method `kkTaValues` ; `DEF_FADER` (engine default
  fader codes) checked against PRELOAD (`--check`, 9/9 OK) — without it, the faders of every EXi engine had no value.
- `scripts/gen_data_lua.py build_tav` : `tav` table, 17 values per factory slot (2939 ; 5 combis have a GM/g timbre 1) ;
  the rest of `kronos_data.lua` unchanged byte for byte.
- `lua/kkMain.lua` : `kkTaField / kkTaValues / kkCombiProg / kkTaTrack` (guard KK.taKey / KK.taSrc), called at the end
  of `kkEncLabels` ; `kkTrackReset` clears KK.taKey.
- VOLUME : `modulatorValue` 64, screen « 64 ».
- Checks : Lua = Python on 2176 programs x 17 (0 differences) ; e2check 298 PASS / 0 FAIL (3 counts updated, 3 new) ;
  smoke ALL PASS (+10). VERSION 1.0e, splash regenerated, panels normal + x24, archive. Not exported.
- Answers : exe icon = CtrlrX's (export copies the binary, injects only the panel) → post-export icon replacement ;
  load errors = resource folder missing (CtrlrX deletes it when empty) → stop emptying it. Resume : `REPRISE_CODAGE_1.0e.md`.

## 1.0f (night) — new Main panel : EXi1 / EXi2, TIMBRE SELECT, TONE ADJUST CONTROLS ; Tone Adjust on engine / timbre

Maintainer : one Main panel for the Ableton device and the CtrlrX build (CtrlrX only adds the EDITOR) ; EXi1 above SW2,
EXi2 above HOLD (then : centred on the name / GM screens) ; TIMBRE SELECT on the HOLD row, its E on the GM screen's
edge, popup 1-16 in the MFX2 footprint ; TONE ADJUST CONTROLS under the sliders ; the encoders / sliders must act on
the chosen engine (two-EXi programs) or timbre (not only timbre 1) ; docs self-contained (no pcglib).

- Artwork : `graphics/KRONOS_Main/sources_Main/kt.py` (exi / timbre / tone_adjust groups) ; title measured identical to
  BANK SELECT (it looked smaller on half pixels : now whole pixels). Copy + README for Ableton :
  `ableton-panel/reference/Main_1.0f_2026-11-03/` ; pointer in `ableton-panel/RESUME.md`.
- `sources/ta_values.py` rewritten : freezes pcglib's layouts + Korg's Parameter Change ids (Prog_HD-1 / Prog_EXi,
  matched on offset + low bit, all 16 x 17 layouts, 0 range disagreement) + Tone Adjust codes (VoiceModels) into
  `data/tone_adjust_map.json` and `TONE_ADJUST_MAP.md`.
- `gen_data_lua.py build_tav` : tav (2176 x 19), tav2 (371), tat (768 combis, 37-byte timbre blocks).
- `lua/kkMain.lua` : kkTaCtx / kkTaTrack / kkTaSend, EXi clicks, kkTimbreMenu ; encoders / faders call kkTaSend first.
  Program : Parameter Change on the chosen EXi (TYP 11 / 12) ; Combi : timbre Tone Adjust TYP 28 PID 5 / 4.
  Program-mode slider names now = engine layout (as the encoders).
- `build_panel.py` : VERSION 1.0f ; kkBtnEXI1/2 + kkLitEXI1/2 + kkExiMask1/2, kkTimbre (popup 1-16) + kkTimbreMask.
- Checks : Lua = Python, 40752 program values + 208896 combi-timbre values, 0 differences (bug found and fixed :
  bit-7 timbre assign fell back to EXi 1) ; e2check 301 PASS / 0 FAIL ; smoke ALL PASS. Not exported, not sent to a
  KRONOS. Resume : `REPRISE_CODAGE_1.0f.md`.
