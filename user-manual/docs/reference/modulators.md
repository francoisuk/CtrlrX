# Modulator inventory (895 controls)

The panel (`KronosKontrol_1.0i.panel`) defines **895 modulators**, each with one
UI component. Names below are the modulator names used by the panel; the RACK
and EDIT views use them as described in the how-to guides.

## Control types

| Component type | Count | Used for |
|---|---|---|
| `uiImageSlider` | 219 | knobs, faders, encoders, slider-buttons |
| `uiLabel` | 414 | captions, value boxes, lit indicators, message lines |
| `uiCombo` | 112 | menus (object selector, GE, timbre, program name, editor combos) |
| `uiButton` | 139 | push buttons (banks, FX, transport, editor actions, toggles) |
| `uiImageButton` | 5 | module LEDs (MASTER/A/B/C/D) |
| `uiImage` | 5 | artwork (page background, X-Y cursor/arrows, About) |
| `uiTabs` | 1 | the RACK/EDIT switch (`kkTabs`) |

## RACK view controls

| Group | Modulators | Function |
|---|---|---|
| Tab switch | `kkTabs` | RACK (0) / EDIT (1) |
| Encoders + labels | `kkEnc01`–`kkEnc08`, `kkEncL01`–`kkEncL08` | Tone Adjust encoders |
| Faders + labels | `kkFdr1`–`kkFdr9`, `kkFdrL1`–`kkFdrL9` | 8 Tone Adjust sliders + Master slider (label only) |
| Volume | `kkVol`, `kkVolV` | Master Volume (SysEx 7F 04 01) |
| Left strip | `kkEncL*`, `kkFdrL*`, `kkVolV`, `kkSldL1`–`kkSldL8` | label/value strips of the left column |
| Mode | `kkBtnPROG`/`kkLitPROG`, `kkBtnCOMBI`/`kkLitCOMBI` | Program / Combi mode (0x4E) |
| User-bank toggle | `kkBtnUAA`/`kkLitUAA` | U-A… ↔ U-AA… |
| Assignable switches | `kkBtnSW1`/`kkLitSW1`, `kkBtnSW2`/`kkLitSW2` | CC80/81 |
| Banks | `kkBtnBank01`–`kkBtnBank14`, `kkLitBank01`–`kkLitBank14` | 14 bank selectors |
| Program select | `kkBtnUP`, `kkBtnDN`, `kkProgNum`, `kkProgName` | ▲/▼, number field, name popup |
| FX switches | `kkBtnFX01`–`kkBtnFX16`, `kkLitFX01`–`kkLitFX16` | IFX/MFX/TFX on-off |
| Mixer/Pan | `kkBtnMIXER`/`kkLitMIXER`, `kkBtnPAN`/`kkLitPAN`, `kkMix1`–`kkMix8` | 8 mix/pan sliders |
| KARMA | `kkBtnKarma1`–`8` + `kkLitKarma1`–`8`, `kkKSlid1`–`8`, `kkBtnScene1`–`8` + `kkLitScene1`–`8`, `kkBtnKON`/`kkLitKON`, `kkBtnLATCH`/`kkLitLATCH` | KARMA switches, sliders, scenes, on/latch |
| Drum track | `kkBtnDTON`/`kkLitDTON`, `kkBtnDTMUTE`/`kkLitDTMUTE` | DT on / mute |
| HOLD + X-Y | `kkBtnHOLD`/`kkLitHOLD`, `kkXYpad`, `kkXYcur`, `kkXYarrX`, `kkXYarrY`, `kkXYrailH`, `kkXYrailV`, `kkXYhl`, `kkXYvl` | X-Y pad with hold |
| Module select | `kkBtnMODCTRL`/`kkLitMODCTRL`, `kkLedMASTER`/`kkBtnLedMASTER`, `kkLedA..D`/`kkBtnLedA..D` | KARMA module Master/A–D |
| GE | `kkGE`, `kkGECat`, `kkBtnGEUP`, `kkBtnGEDN` | Global Edit number / category |
| EXi / timbre | `kkBtnEXI1`/`kkLitEXI1`, `kkBtnEXI2`/`kkLitEXI2`, `kkExiMask1`–`2`, `kkTimbre`, `kkTimbreMask` | engine slot / combi timbre selectors |
| GM menu | `kkGM` | GM/g bank menu |
| Transport cluster | `kkBtnPCG`/`kkLitPCG`, `kkBtnImport`, `kkBtnPlay`, `kkBtnSave`, `kkBtnWriteR`/`kkLitWriteR`, `kkPcgFile` | PCG open / import to edit buffer / audition / save stub / slot write |
| View + info | `kkBtnEdit`, `kkMonitor`, `kkVersion`, `kkBtnAbout`/`kkBtnAboutE`, `kkAbout`, `kkAboutDim`, `kkAboutClose`, `kkSplashKofi`, `kkSplashBook`, `kkSplashWeb` | EDITOR button, message line, version, About/splash |

## EDIT view controls

| Group | Modulators | Role |
|---|---|---|
| Page furniture | `kkEdFond` (artwork), `kkEdTitle`, `kkEdStatus`, `kkEdLb_pbox`, `kkEdLb_idxbox` | background image, title, status line, instance boxes |
| Object selector | `kkObjSel` | Program/Combi/Drum Kit/Wave Sequence/Global/Set List/Song |
| Actions | `kkBtnGetProg`/`kkLitGetProg`, `kkBtnApply`/`kkLitApply`, `kkBtnWrite`/`kkLitWrite`, `kkBtnStore`/`kkLitStore`, `kkBtnBankRead`/`kkLitBankRead`, `kkBtnCompare`, `kkBtnToRack`, `kkEdDestBank`, `kkEdDestNum` | Read sound / Apply / Write / Store / Bank read / Compare / **To rack** / destination display |
| Nav bar | `kkEdN01`–`kkEdN29`, `kkEdNL01`–`kkEdNL29` | AREAS · INDEX · PAGE · FX buttons + labels |
| Knobs pool | `kkEdK01`–`kkEdK34`, `kkEdV01`–`kkEdV34` | 34 knobs + value boxes |
| Slider-button pool | `kkEdB01`–`kkEdB111`, `kkEdBL01`–`kkEdBL111` | 111 stepped controls + labels |
| Combo pool | `kkEdC01`–`kkEdC65` | 65 list menus |
| Toggle pool | `kkEdT01`–`kkEdT20`, `kkEdTL01`–`kkEdTL20` | 20 on/off toggles + lit labels |
| Captions | `kkEdX01`–`kkEdX27` | section captions |
| FX EDIT pool | `kkEdFxType`, `kkEdFxSw`, `kkEdFxSwL`, `kkEdFK01`–`kkEdFK40`, `kkEdFC01`–`kkEdFC40`, `kkEdFV01`–`kkEdFV40`, `kkEdFM01`–`kkEdFM40` | effect type menu, on switch, 40 parameter cells (knob/caption/value/menu) |

## Host-exported (VST3 parameters)

34 modulators are exported as VST3 parameters: `kkEnc01`–`kkEnc08`,
`kkFdr1`–`kkFdr9`, `kkVol`, `kkMix1`–`kkMix8`, `kkKSlid1`–`kkKSlid8`.
