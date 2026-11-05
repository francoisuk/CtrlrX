# Kronos Kontrol: why the Editor never looked like its design, and how complet‑1.0a fixes it

*Post‑mortem of the 0.98b → 0.98e Editor builds and design record of the Editor in **complet‑1.0a** (1 Nov 2026).*

---

## 1. Summary

The Main panel (the rack) had worked since 0.97p. The **Editor**, opened with the EDITOR button, did not. On the maintainer's machine it showed a flat dark window. There were a few generic Ctrlr buttons at the top and a row of plain text tabs ("GENERAL · 1/1 OSC · 1/3 …"), with **no artwork and no controls** in the page area. Four successive builds (0.98b, 0.98c, 0.98d, 0.98e) each changed one thing, and none of them fixed it.

The problem was **not a single bug**. It was the combination of:

1. **An architecture the design could never match.** The build cut the top 116 px off every page image and replaced the drawn header and navigation bar with standard Ctrlr widgets and Ctrlr's own tab strip.
2. **An architecture Ctrlr 5.6.23 had never been shown to handle**: 7 tab containers nested inside the main tab container, 154 tabs in the largest one, and **9,190 permanent controls**, one per parameter.
3. **A verification loop that could not see the result.** Every build was "verified" by static scripts and a Lua 5.4 simulation. Nobody ran Ctrlr after a build, so each fix was a guess, confirmed or refuted only when the maintainer sent a screenshot.
4. **A text‑encoding bug** (UTF‑8 strings read as Latin‑1) that garbled every non‑ASCII character in Lua‑generated text: "EDITOR â□□ current Program".

complet‑1.0a replaces the Editor's GUI layer with a different architecture. It has **one** EDIT page, the **full, uncropped** design image as its background, and a small **pool** of controls that Lua moves onto each page. There are no nested tabs. I proved it first on a one‑page prototype, then built it for all 214 pages. It was **tested live in SAVIHost3 + Ctrlr 5.6.23** on this machine at every step. The panel now has 869 controls instead of 9,190 and loads in about 25 s instead of about 40 s.

| | 0.98e (last pre‑1.0 build) | complet‑1.0a |
|---|---|---|
| Editor architecture | 7 nested `uiTabs`, 213 tabs, one control per parameter | 1 EDIT page, image swapped per page, pooled controls |
| Panel modulators (controls) | 9,190 | **869** |
| Panel size | 41.5 MB | 24.9 MB |
| Load time (measured) | ~40 s (0.98c, maintainer) | **~25 s** (SAVIHost3, this machine) |
| Page artwork | cropped below y = 116 (header and nav bar thrown away) | **full 1500 × 414** (header, nav bar, rack ears) |
| Pages | 213 (none displayed) | **214** (213 + FX EDIT with 198 effect types) |
| What the maintainer saw | flat dark window, text tabs, no controls | the designed pages (screenshots in §8) |

---

## 2. What the Editor is supposed to be

The design is in `ctrlr-project/graphics/KRONOS_Editor/Full/`. It is described in `README_EDITOR_KRONOS.md` and `RECIPES_GUI_DRAWING.md`.

- **214 pages** at 1500 × 414 px, the same size as the Main panel: Program, the 8 EXi engines, Combi, Drum Kit, Wave Seq, Global, Set List, Song, and one FX EDIT template.
- For each page, three files:
  - `_maquette.png`: the mock‑up, with example values;
  - `_fond.png`: the **background**, which contains the whole page (rack ears, header, OBJECT menu, action buttons, status line, the AREAS · INDEX · PAGE navigation bar and every section frame), with only the parts that change removed (knobs, lit bars, display text);
  - `_layout.json`: the position, type and range of every control, and its address in the Korg dump.
- **The editor is expected to draw on top of the background**: knobs, value text, lit bars, and the current page / area / instance markers.
- Repeated instances (OSC 1–2, TIMBRE 1–16, NOTE 1–128 …) share one drawing. The layout gives `stride_bytes`, and the instance *n* is at the offset of instance 1 plus (n − 1) × stride.

`graphics/KRONOS_Editor/Full/Program/KRONOS_KONTROL_EDITOR_P_AMP_P1_maquette.png` (copy: `images/mockup_program_AMP_P1.png`) is what a page should look like.

---

## 3. What the maintainer saw

`ctrlr-project/for_vibe/editor_2_prog_1.jpg` (0.98d, copy: `images/0.98d_editor_blank.jpg`) and `editor_program_1_2_no_show.jpg` / `editor_combi_1_no_show.jpg` (0.98c):

- a dark rectangle; no rack ears, no drawn header, no section frames;
- standard grey Ctrlr buttons ("Read sound", "Apply ☐ 0x4B" …) where the design has drawn buttons;
- in 0.98d, a JUCE tab strip with 154 plain text tabs ("GENERAL · 1/1 OSC · 1/3 OSC · 2/3 …");
- **nothing at all** in the page area: no image, no knob, no menu;
- garbled text: "EDITOR â□□ current Program (dump 0x4B)", "No dump â□□ "Read sound"".

Meanwhile the build log said: *"e2check 2488 PASS / 0 FAIL, rendermodel 18/0, smoke ALL PASS"*.

---

## 4. Root causes

### 4.1 The architecture discarded the design

The Editor was built from **nested tab containers** (`uiTabs`). The root container `kkTabs` has two tabs, RACK and EDIT. Inside EDIT the build placed seven more containers (`kkEdTabs` for Program with 154 tabs, `kkEdTabsC` Combi 33, `kkEdTabsK` 3, `kkEdTabsW` 2, `kkEdTabsG` 13, `kkEdTabsL` 2, `kkEdTabsS` 6), all at the same position, with Lua showing one at a time.

This had two consequences for the look, whatever Ctrlr did with it:

- **A Ctrlr tab container draws its own tab bar.** The design's navigation bar (AREAS · INDEX · PAGE, with yellow lit bars) cannot be produced by a JUCE tab strip. The build therefore kept the JUCE tab bar (`uiTabsDepth = 24`) as the page switcher, which is the row of plain text tabs in the screenshot.
- **Tab content starts below the tab bar.** In 0.98d the containers sat at `0 92 1500 322` with a 24 px bar, so their content area started at y = 116. To make the artwork fit, `build_panel.py` (`_crop_fond`) **cropped every page image to y ≥ 116**. That threw away the drawn header, OBJECT menu, buttons, status line and navigation bar. The header was then rebuilt from generic Ctrlr widgets (`button_text`, dark grey, Sans‑Serif).

So even in the best case, with the containers painting correctly, the Editor would have been "the bottom 72 % of the design under a generic Ctrlr header and a text tab strip". That is exactly the maintainer's comment: *"I can see the various panels, but not as they should look"*.

### 4.2 The architecture was beyond anything proven in Ctrlr 5.6.23

| Build | Change | Result on the maintainer's machine |
|---|---|---|
| 0.97i | 5 nested containers, 24 / 43 / 6 / 3 / 15 tabs, ~3,000 controls, **no images** | pages rendered (controls shifted +116 px, General tab cut off) |
| 0.98b | containers moved to full panel `0 0 1500 414`, depth 0; 23 page images as **tab background images** | not reported separately |
| 0.98c | Full editor: 7 containers, 213 tabs, 6,719 controls, 213 tab background images; 49 MB; load ~40 s | **flat dark page area** |
| 0.98d | containers back to `0 92 1500 322` depth 24, children shifted y − 116, images cropped | **flat dark page area** (text tab strip visible) |
| 0.98e | tab background images replaced by a `uiImage` child per tab (213 `kkFond_*`) | built, not re‑tested by the maintainer |

Each step changed **one** variable on the basis of a hypothesis ("nested containers at depth 0 don't paint", then "tab background images don't paint when nested"). The 0.98e journal ends: *"if the maintainer still sees a blank EDIT page on 0.98e, the remaining suspect is the panel size / modulator count"*. Each hypothesis could only be tested by sending a 41–49 MB panel to the maintainer and waiting for a screenshot. Each one cost a build, an upload, a ~40 s load and a round trip.

**What is and is not known.** While reviewing this I read the Ctrlr 5.6.23 sources in `ctrlr-project/build/ctrlr-master` and ruled several things out:

- The page images *were* embedded correctly. `resourceExportList` holds them, `CtrlrPanelResourceManager::importResource` writes them to `%APPDATA%\Ctrlr\kkKronosKontrol\`, and the files were present, current and cropped as the build intended.
- Resource names resolve: `ctrlrOverwriteResources` defaults to `true`, so the `edfF_*` names are registered even when the cache folder already holds files of the same stem.
- The ownership mechanism (`CtrlrTabsComponent::canvasStateRestored` → `setOwned` → `addAndMakeVisible` into the tab content component) treats nested containers the same as the root one.

**The exact reason the nested page area stayed blank was not isolated, and 1.0a deliberately does not depend on it.** The decisive point is that whatever the cause, the nested‑tab architecture could not deliver the design anyway (§4.1). Spending more maintainer round trips to make it paint would only have produced a wrong‑looking Editor faster.

### 4.3 The checks could not see what the user sees

| Check | What it verifies | Why it could not catch the blank Editor |
|---|---|---|
| `tools/panel-harness/e2check.py` (2,488 checks) | the panel **XML**: names, rectangles, callbacks, resource hashes, combo contents | an XML file can be perfect and still not paint |
| `tools/panel-harness/smoke.lua` | the panel **Lua**, run under Lua 5.4 against a fake Ctrlr API that accepts every call | it cannot see pixels; it never complains about a missing component, because the fake returns one for any name |
| `tools/panel-harness/rendermodel.py` (0.98e, 18 checks) | a Python model of Ctrlr's component tree "per the 5.6.23 sources" | a model of what the code *should* do; the question was what the real binary *does* |

The 0.98e journal says it plainly: *"This is the local test I can run; I cannot run the Ctrlr GUI here — no display/host in this sandbox."* All three tools answered "is the file what I meant to build?". None answered "does the user see the design?". SAVIHost3 and the pinned `Ctrlr-x64.vst3` 5.6.23 were installed on this machine the whole time (`C:\Program Files\savihost3\`), but nothing in the loop used them.

### 4.4 Text encoding: UTF‑8 read as Latin‑1

Ctrlr builds a `juce::String` from the bytes of a Lua string as **Latin‑1**. Any UTF‑8 character outside ASCII therefore breaks:

- "—" (E2 80 94) → "â" plus two C1 control characters (drawn as boxes): **"â□□"**;
- "→", "…", "◀" likewise;
- an accented name passed through `kkL1toUtf8` → "Ã©".

This caused the "EDITOR â□□ current Program" title, the "No dump â□□" status, and the **tofu glyphs in the yellow SysEx monitor** of the Main panel. Those glyphs were recorded as a known cosmetic issue, not fixed (`for_vibe/tofu.jpg`; the maintainer's `rack_program1.jpg` shows "Engine MS‑20EX â□□ knob/slider labels updated"). Text read from the panel XML (an XML attribute) was fine, because JUCE parses the XML as UTF‑8. Only text set from Lua was affected.

---

## 5. How complet‑1.0a works

### 5.1 Principle

```
kkTabs (the only uiTabs, depth 0)
├── tab 0 RACK  : the Main panel, unchanged
└── tab 1 EDIT  : children of the root tab only — no nested container
      kkEdFond        uiImage 1500×414 = the FULL page artwork (swapped by Lua on every page change)
      frame           kkEdTitle, kkEdStatus, WRITE TO display, lit bars of the action buttons
      text pools      kkEdV.. (knob values), kkEdBL.. (value-box text), kkEdX.. (names), page / instance boxes
      lit bars        kkEdTL.. (toggles, blue), kkEdNL.. (navigation, yellow)
      buttons         kkBtnGetProg / Apply / Write / Store / BankRead / Compare / ToRack (historical names → kkClick)
      kkObjSel        OBJECT menu (7 objects → kkObjChanged)
      control pools   kkEdK01..34  knobs        uiImageSlider on a 101-frame strip drawn with the artwork's kt.knob()
                      kkEdB01..111 value boxes  uiImageSlider on a transparent strip (drag to change)
                      kkEdC01..65  menus        uiCombo, transparent over the drawn menu
                      kkEdT01..20  toggles      transparent button + blue lit bar
                      kkEdN01..29  navigation   transparent button over each drawn nav button
                      kkEdF*01..40 FX EDIT cells (caption, knob, value, menu) + type menu + ON switch
```

The pools are sized for the busiest page (111 value boxes on one Global page, 65 menus, 34 knobs …). On every page change, `kkEdShowPage` (`lua/kkEdGui.lua`) does the following:

1. sets `kkEdFond`'s `uiImageResource` to the page's artwork (`edp_<page>`);
2. computes the instance offset, `KK.edOff = base + (instance − 1) × stride`;
3. for each control of the page, moves a pool slot onto the drawn cell (`componentRectangle`), sets its range (`uiSliderMax`) and menu content, and gives it its value **read from the dump** with the existing bit‑level code (`kkEdReadField`, `kkEdIdxOf`);
4. hides the unused slots;
5. places the navigation buttons and lights the current area, instance, page or FX slot in yellow;
6. writes the title (object, area, page n/N, instance, EXi slot).

Editing a control writes the dump through the same guards as before (no dump, wrong mode, busy, wrong program type, truncated dump), with `kkEdWriteField` at the instance offset. "Apply" still sends the dump to the edit buffer with function 0x4B. **Nothing in the new GUI layer sends MIDI on its own.**

### 5.2 Navigation

The page data (`KK_EDP`, `KK_EDA` in the generated method `kkEdPages`) is produced by `sources/editor_v1.py` from the Full `_layout.json` files and `sources/editor_full_layout.json`. Each page carries its own navigation buttons, taken from the drawn bar:

| Action | Behaviour |
|---|---|
| `area:<x>` | first page of that area of the same object (ENGINE → engine pages, FX EDIT → FX template, Song TIMBRE SET → Combi TIMBRE) |
| `idx:<n>` / `idx:a..d` | instance n (OSC 1–2, EXi 1–2 = EXi slot, TIMBRE 1–16, MODULE A–D) |
| `iprev` / `inext` + instance box | NOTE 1–128, STEP 1–64, SLOT 0–127, EXT SET 1–128 … (wraps around) |
| `page:<n>`, `pprev` / `pnext` + page box | pages of the area |
| `◀ PROGRAM`, `◀ BACK` | back to the page you came from |
| `fx:<slot>` | IFX1–12, MFX1–2, TFX1–2 on FX EDIT |

**ENGINE** opens the pages of the engine of the selected EXi slot, read from the dump (byte 2857 / 3909). With no EXi dump, each press shows the next engine (AL‑1 → CX‑3 → … → EP‑1), so all eight can be reviewed without a KRONOS. The status line says so.

**FX EDIT** reads the effect type of the slot from a Program dump (IFX n at 88 + 74 × (n − 1), MFX 976 / 1044, TFX 1116 / 1184) and fills the 40 cells from `graphics/KRONOS_Editor/Full/Effects/FX_LAYOUTS.json` (198 types, embedded as `kkEdFxData`). Changing the type patches the dump; it reaches the KRONOS only with Apply.

### 5.3 Files

| File | Role |
|---|---|
| `panels/KronosKontrol/sources/editor_v1.py` | **new**: generator of the EDIT tab (pools, frame, page and FX data) |
| `panels/KronosKontrol/sources/make_editor_assets.py` | **new**: knob strip `assets/kk_knob42.png` (rendered with `kt.knob()` from `graphics/…/sources_Editor`, read‑only import) and `assets/kk_blank.png` |
| `panels/KronosKontrol/lua/kkEdGui.lua` | **new**: GUI layer (page display, navigation, editing, FX EDIT, `kkU`) |
| `panels/KronosKontrol/lua/kkEd.lua` | **data layer only**; the old GUI functions (`kkEdPopulate*`, `kkEdTabBtn`, `kkEdPageSel`, `kkIdxSel`, `kkEdTabChanged`, `kkEdField`) are removed |
| `panels/KronosKontrol/lua/kkMain.lua` | `kkEditShow` rewritten (calls `kkEdRefresh`); `kkEdStatus` and `kkMonitor` go through `kkU`; `kkObjChanged` opens the object's first page |
| `panels/KronosKontrol/sources/build_panel.py` | `VERSION = 'complet-1.0a'`; the old EDIT‑tab generator is replaced by `editor_v1.emit()`; the 214 artworks are embedded **uncropped** |
| `panels/KronosKontrol/proof/` | the one‑page prototype that validated the architecture (proof‑0.99a / 0.99b), kept as evidence |
| `tools/panel-harness/e2check.py`, `smoke.lua` | v1 mode: pre‑1.0 Editor checks reported as SKIP, new 1.0a sections |

### 5.4 Encoding fix

`kkU(s)` (in `kkEdGui.lua`) re‑encodes UTF‑8 to Latin‑1. Characters above U+00FF get an ASCII stand‑in ("—" → "-", "→" → "->", "…" → "..."). `kkEdStatus`, `kkMonitor` and every Editor text setter use it. As a result the Main panel's SysEx monitor no longer shows tofu glyphs ("-> F0 42 30 68 12 F7"), and Editor titles and statuses are clean.

---

## 6. Bugs found on the way (and fixed)

1. **Edits of instance 2+ went to instance 1 (latent since 0.98c).** `kkEdWriteField` checked the length at `KK.edOff` but wrote at `pc[1] + 1`, without the offset, whereas `kkEdReadField` reads at `pc[1] + 1 + edOff`. An OSC 2 / TIMBRE 5 / NOTE 40 edit would have patched OSC 1 / TIMBRE 1 / NOTE 1. The new smoke test "edit OSC2 LEVEL → dump byte 3607" caught it. Fixed in `kkEd.lua`.
2. **Helpers declared `local` in a method chunk.** Ctrlr compiles each `--@ name` Lua method as its own chunk, so a `local function` in `kkEdGui.lua`'s header is invisible from the callbacks. The smoke test caught it, the helpers are now global, and e2check now fails any `local function` in that header.
3. **Value boxes drew a rotary knob** over the drawn box when built as plain `uiSlider` with transparent colours. I saw this live in the proof (0.99a), and value boxes are now image sliders on a transparent strip.
4. **Echoed callbacks.** Ctrlr calls a combo's value‑change callback *after* Lua has changed its content or value (seen live in the proof: the status showed "item 0" after a page change). A naive implementation would write 0 into the dump on every page change. Every pool callback ignores a value equal to the one Lua just set (`KKE.cur`).

---

## 7. Verification of complet‑1.0a

**Static**: `python tools/panel-harness/e2check.py` reports **258 PASS / 0 FAIL**, with 23 pre‑1.0 Editor checks reported as SKIP. The new checks include:

- a single `uiTabs`;
- `kkEdFond` is a full‑frame `uiImage` and the first EDIT child;
- 214 artworks embedded **at their original size** (not cropped), with resource name = file stem;
- every pool sized for the busiest page, with its callback;
- every page parameter present in `KRONOS_EDITOR.p`, and 6,686 of the 6,719 parameters bound to a control. The other 33 are text fields (6 names, 27 Global category names), shown read‑only;
- every rectangle inside 1500 × 414;
- `kkEdGui.lua` ASCII‑only, with no header `local function`;
- 198 FX types embedded;
- fewer than 1,000 modulators.

**Behaviour**: `lua tools/panel-harness/smoke.lua` reports **ALL PASS** (292 checks). New section 10 covers:

- all 214 pages shown with no dump and with a Program dump, without a Lua error;
- AMP 1/3: the LEVEL knob sits on its drawn cell and reads 100 from the dump;
- OSC 2 → offset 466 → reads 33; the yellow lit bar follows;
- an edit patches byte 3607 and marks the dump dirty; an echoed value is ignored; Combi mode refuses a Program edit;
- PAGE 3, FILTER and ENGINE (no‑dump cycle) work, and ◀ PROGRAM returns to the page of origin;
- an EXi dump → MOD‑7 pages at offset 2908;
- FX EDIT reads the IFX1 type, a type change patches byte 88, and IFX3 reads byte 236;
- the OBJECT menu opens Drum Kit; NOTE ◀ wraps to 128 at offset 127 × 300;
- `kkU`.

**Live: SAVIHost3 + Ctrlr‑x64.vst3 5.6.23, this machine, 1 Nov 2026, desktop control** (screenshots in `images/`):

- the panel loads in ~25 s, and the Main rack is unchanged (names, FX switches, KARMA, GE, monitor now without tofu);
- EDITOR opens the Program GENERAL page with the full design;
- AMP, OSC, EFFECTS, ENGINE (AL‑1 pages, review cycle), ◀ PROGRAM, FX EDIT (type menu → Stereo Dyna Compressor fills 14 cells), Combi GENERAL and TIMBRE 1–16 (TIMBRE 15 lit), Global BASIC, Song, Drum Kit NOTE ◀ / ▶ (1 → 128 → 2);
- a knob drag shows its value with an honest "not stored (no dump)" status;
- a toggle shows its blue lit bar;
- RACK ⇄ EDITOR returns to the same page.

**Not verified yet (needs the KRONOS):** "Read sound" → values on the pages, edits → "Apply" (0x4B) → Reply 24, and engine pages following a real EXi program. The data layer is the one hardware‑tested in 0.97, but the 1.0a GUI has only seen synthetic dumps.

---

## 8. Before and after

| | |
|---|---|
| Mock‑up (`images/mockup_program_AMP_P1.png`) | the design to match |
| 0.98d on the maintainer's machine (`images/0.98d_editor_blank.jpg`) | flat page area, text tab strip, generic header |
| 1.0a Program › AMP 1/3 (`images/v1.0a_program_AMP_P1.jpg`) | the design, knobs on their cells, OSC / PAGE lit |
| 1.0a FX EDIT (`images/v1.0a_fx_edit.jpg`) | cells filled from FX_LAYOUTS.json (taken just before the "+0" sign fix) |
| 1.0a Combi › TIMBRE 15 (`images/v1.0a_combi_timbre15.jpg`) | 16 instances, TIMBRE 15 lit, toggle + status |
| 1.0a Main rack (`images/v1.0a_rack.jpg`) | unchanged, monitor without tofu |

---

## 9. Lessons

1. **Look at the result in the real host before claiming success.** The project had SAVIHost3 and the pinned Ctrlr binary on the machine. One screenshot after a build would have shown in minutes what four builds and the maintainer's round trips took a day to show.
2. **Prototype the risky part on one page first.** The one‑page proof (1 MB, 134 controls, loads in 2 s) answered the architecture question before any time went into 214 pages.
3. **Check the design against the architecture before building.** "Can a JUCE tab strip be the drawn navigation bar?" has a "no" answer on paper. Cropping the artwork to fit the architecture should have been a red flag that the architecture was wrong.
4. **Static checks verify intent, not outcome.** Keep them, and make sure their pass line is never reported as "verified" for something only a screen can show.
5. **Lua in Ctrlr:** text set from Lua is read as Latin‑1, each `--@` method is its own chunk (no shared locals), callbacks fire after programmatic changes, and an uncaught Lua error in a callback terminates the host. All four are now enforced by the harness.

---

## 10. Remaining work after 1.0a

- **Hardware test with the KRONOS** (maintainer): Read sound on Program, Combi, Drum Kit, Wave Seq, Global; edits → Apply → Reply 24; EXi programs → ENGINE pages; instance edits (OSC 2, TIMBRE n) round‑trip.
- **Menu item names**: many combos list numbers (0, 1, 2 …) because `data/kronos_full.lua` has no names for those enums (AMS sources "Off~Tempo", note names …). This is a data task.
- **Name editing**: names are displayed read‑only. 0.97's `kkEdNameEdit` can be re‑attached to the text pool.
- **FX EDIT**: effect parameter values are kept by the panel and not yet written to the dump (their dump offsets per slot are not mapped). Only the first 40 cells are shown for the few effects with more.
- **Font**: Inter is used as an installed OS font. A VST3 for other machines should embed it as a font resource.
- **Combo arrows**: Ctrlr draws its own small arrow, not the drawn ▼.
- **Accented names on the Main panel**: `kkL1toUtf8` converts names to UTF‑8, which Ctrlr then reads as Latin‑1. Routing those setters through `kkU` (or dropping the conversion) would fix accented names.
- **Unused 0.97 methods** (`kkEdP1`, `kkEdP8`, `kkEdCatEdit`, `kkEdScaleEdit`, `kkEdIFX1Edit`, `kkEdNameEdit`) are still in `kkMain.lua`, bound to no control. They can be removed once name editing is re‑attached.
