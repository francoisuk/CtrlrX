# Kronos Kontrol — editor plan of action

*Written 24 oct. 2026. Turns the Kronos Kontrol control panel into a full
editor, keeping the rack UI as the basis. Companion documents:
`PROJECT_LAYOUT.md` (architecture), `PHASE_A.md` (parameter map),
`TEST_PLAN_0.96.md` (control-panel hardware test), `RESUME.md` (corpus root — test log),
`ETUDE_TR-Rack.md` + `CTRLR_IDIOMS.md` (Ctrlr mechanics).*

## 1. Goal

Today Kronos Kontrol (complet-0.96) is a **control panel**: it drives the
Kronos in real time from a DAW (CC, fn 43/6D/6E parameter changes, program /
combi select, GE, KARMA, Drum Track, mixer, FX switches). The next step is a
**full editor**: read the current Program / Combi from the Kronos, edit its
parameters on screen, and write the result back — the TR-Rack Editor
(`panels/TR-Rack-Editor-main/`, read-only) being the working example of what
"editor" means.

**UI decision (settled 24 oct. 2026):** the rack stays. The panel becomes
tabbed: tab 0 = the rack, exactly as-is (artwork, 172 modulators, all
callbacks untouched); tab 1 = the EDIT page. The editor grows section tabs
later (stage E3). No redraw of the rack; editor pages use generated
placeholder artwork in the same palette (LIT pink `ff3fb6ff`, YEL `ffd23f`),
to be refined by the author like the manuals.

## 2. Model: what TR-Rack does (decoded 24 oct. 2026)

`Tr Rack Editor.bpanelz` — 2,840 modulators, 90 Lua methods, 1290×745,
18 tab groups / 163 tabs. Architecture:

- **Read:** dump request `F0 42 30 3B 10 00 F7` (fn 10 = Current Program
  Data Dump Request; 19 = Combi) → the rack answers with the whole current
  program as ONE SysEx message (502 B). Bank reads: fn 1C/1D → one 63,352 /
  56,769-byte message.
- **Parse:** hardcoded byte offsets + sign-bit packing (`setProgMod`,
  `valueByteExtract`, `signBitExtract`) — 289 program + 197 combi params
  mapped by hand; a dump-diff debugger found the offsets.
- **Edit:** modulator change → name→address if/elseif chain
  (`chgValInProg`) → realtime parameter-change SysEx. The device is the
  source of truth; the panel re-dumps to resync.
- **Write:** patch the stored dump, send it whole to a destination slot
  (fn 41); banks from file (fn 4C/4D/48/51/52); ACK (fn 23) / NAK (fn 24/26)
  with polling timers.
- **Files:** Ctrlr Lua `File` API; Triton .PCG sizes validated. Full-device
  backup (~0.5 MB at once) FAILED in Ctrlr ("ctrlr cant handle the data
  size"); bank-level transfers work.
- **Ctrlr tab mechanics (proven in TR-Rack, re-verified in Ctrlr sources):**
  `uiTabs` component with `uiTabsTab` children; a component joins a tab via
  `componentTabName` = tabs modulator name + `componentTabId` = tab index +
  `componentGroupped="1"`; on load `canvasStateRestored()` re-owns members
  by `componentTabName`. Switch from Lua:
  `panel:getModulatorByName("kkTabs"):getComponent():setPropertyInt("uiTabsCurrentTab", n)`.
  `uiTabsCurrentTabChanged="methodName"` calls `methodName(mod, tabIndex)`.
  `uiTabsDepth="0"` collapses the tab bar (`setTabBarDepth(0)` is a legal
  value) → tab content fills the whole tabs component → rack layout stays
  pixel-identical.

## 3. Kronos primitives for editing (KRONOS_MIDI_SysEx.txt v1.27)

The Kronos dump system is object-based and cleaner than the Triton's:

| Fn | Name | Editor use |
|----|------|-----------|
| 0x4A / 0x4B | Current Object Dump Request / Dump | **Read the edit buffer** (0x4A→0x4B); **send 0x4B to replace the edit buffer** (not stored until the user writes) |
| 0x48 / 0x49 | Object Dump Request / Dump (R/T) | Read/write one object in a bank slot: `obj, bank, idH, idL, version, data` |
| 0x4C | Store Bank Request | Commit a received bank to non-volatile storage (warn first) |
| 0x4D | Dump Bank Request | Read a whole bank as a series of 0x49 messages |
| 0x47 | Set Current Object | Select the object type addressed by dump requests |
| 0x25–0x28 | Bank Digest (SHA-1) | Change notifications after any storage write |

- Object types: 00 Program, 01 Combi, 03 Global, 04 Drum Kit, 05 Wave Seq,
  0D Set List, 10–17 names… (06 KARMA GE has **no edit buffer**).
- Bank numbering: Program 0–5 = I-A..F, 0x10–0x1A = GM/g() (read-only),
  0x40–0x4D = U-A..G/AA..GG; Combi 0–6 = I-A..G, 0x40–0x46 = U-A..G.
- Dump `data` = the object's binary, **8→7-bit packed** (7 bytes → 8 wire
  bytes, first wire byte = the 7 MSBs): `sysExSize = binarySize +
  ceil(binarySize/7)`.
- Sizes (pcglib, factory-validated): **Program 4,960 B** (v5), **Combi
  7,810 B** (v3), Drum Kit 38,424 B (v3), Wave Seq 2,216 B (v1). A program
  dump is one ~5.7 KB message; a combi ~8.9 KB — both fine for Ctrlr.
- Program layout (EXi and HD-1 share offsets up to ~2857): name 0–23;
  IFX n params at 24+74(n−1), type at 88+74(n−1) (n = 1..12); MFX types at
  976/1044; TFX at 1116/1184; category 2568; scale 2569; EXi 1 engine byte
  2857 + block 2908 (1,001 B); EXi 2 engine 3909 + block 3960. HD-1 has
  OSC1/OSC2 instead of the engine blocks (3,706 useful bytes).

## 4. Assets (already in the project)

- `reference/ref-kronos/tables/` — machine-readable bit-level parameter
  tables: `Programme_HD-1.csv` (2,542 rows), `Programme_EXi_commun.csv`
  (2,034), `Moteur_*` ×8 (3,623), `Combinaison.csv` (6,705),
  `Effets_liste.csv` (198 types, 0..197), `Effets.json` (per-type 64-byte
  block layouts), default effect blocks for 135 types.
- `reference/ref-kronos/midi/` — Korg's own object-structure docs
  (Prog_HD-1.txt, Prog_EXi*.txt, CombiAndSongTimbreSet.txt, Effect.txt,
  DrumKit.txt, WaveSequence.txt, Global.txt…) + `KRONOS_MIDI_SysEx.txt`.
- `reference/ref-kronos/docs/00_RECAPITULATIF_FORMAT_PCG.md` — the full
  format recap (byte maps, packing rules, enumeration lists).
- pcglib (`C:\Korg\kronos-corpus\kronos-pcglib`, v1.6.3) — the Python reference for PCG
  read/write; the object bodies are the same bytes the dumps carry.
- `tools/pcg-names/pcg_to_names.py` (U0) — names from any PCG, names-JSON schema;
  `tools/corpus-check/corpus_check.py` — panel parser vs pcglib over
  `corpus/manifest.csv` (112 PCGs).
- `scripts/gen_data_lua.py` — the data-driven generator pattern to extend.

**Rule: the editor is data-driven.** TR-Rack hardcodes 289 `setProgMod`
calls; we generate the modulator lists, the parse/apply code and the name
tables from the CSV/JSON tables. No hand-coded parameter offsets in Lua.

## 5. Stages

Version naming: the editor line is **complet-0.97** (0.96 = control panel,
hardware-tested; 0.97 = editor, stages E1–E7 below). While the editor was
under construction the build number stayed 0.97 and each delivered increment
carried a letter (**complet-0.97a** … **0.97r**). On 1 nov. 2026 the line moves
to **complet-0.98** with **0.98a** = full panel + editor plugged in and
working as a beta (all stages E1–E6 + U0/U1 built; SAVE writer still a stub,
Editor GUI rebuild from `graphics/EDITOR_WINDOW.md` = 0.98b+). Per-stage
status lives in this document.

Single source of truth for the version: `VERSION` at the top of
`sources/build_panel.py`. The generator stamps `panelVersionName`, renders the
`kkVersion` label (bottom-right of the RACK tab) and substitutes `@VERSION@`
in every `lua/*.lua` file when embedding it — so `KK_VERSION` in `kkMain.lua`
and the line-1 comment always match the build.

| Stage | Name | Delivers | Hardware test | Status |
|-------|------|----------|---------------|--------|
| E1 | Read path, Program | 7-bit codec in Lua; Get Program Dump button; receive 0x4B; show name, version, category, scale, IFX/MFX/TFX types, EXi engines on the EDIT tab | dump size = 4,960 B; name matches the Kronos screen; one known parameter matches the front panel | **DONE — static verification passed (99 checks, Lua interpreter, 24 oct.); hardware test pending (§9)** |
| E2 | Edit + write-back, Program | realtime fn 43 where an id exists; else patch the local dump and send 0x4B; rename; Reply 24 handling; busy state | change a parameter from the panel, hear/see it; rename visible on the Kronos | **DONE 26 oct. — static verification passed (61 checks, Lua 5.4.2 harness); hardware test pending (§10)** |
| U0 | Names from any PCG (offline tool) | `tools/pcg-names/pcg_to_names.py` — any PCG → names JSON (same schema as the M4L reference); `scripts/gen_data_lua.py --names` plugs a custom names file in without touching the read-only reference | n/a (offline tool) | **DONE 26 oct. — verified on PRELOAD (2 176/2 176 names match the reference; 6 known space-only diffs) and 2 user banks (384 names)** |
| U1 | Runtime PCG loader (panel universal) | `lua/kkPcg.lua` — « PCG > » opens any PCG (OS 2/3.x); bank/program names from the file replace the factory names on the rack; « Jouer > » loads the selected program from the file into the edit buffer (0x4B); latin-1 ↔ UTF-8 conversion | load a PCG, read its names, play a program from the file | **DONE 26 oct. (complet-0.97b) — static verification passed (27 structural checks; 96 checks under Lua 5.4.2 incl. a real PRELOAD load; corpus-check 112/112 PCGs match pcglib); hardware test pending (§11)** |
| E3 | Edit pages, engine-aware | second-level section tabs inside EDIT (kkEdTabs, 16 tabs: Général, Commun, OSC1/OSC2, EXi1/EXi2 Mix, E1 engine ×8, IFX 1-12, MFX·TFX), generated from the tables by `scripts/gen_editor_lua.py` — v1: 324 params (guide said ~200–300), 0 PRELOAD exclusions over 2 176 programs, 9 skipped by rule; KARMA, Drum Track, Vector/Step Seq, Tone Adjust, E2 engine tabs → E3b | each page round-trips: dump → page → write → re-dump, values match | **DONE 26 oct. (complet-0.97c) — static verification passed (e2check 51 checks; Lua harness 169 checks incl. 73 E3; PRELOAD validation 324/324 params, 0 exclusions); hardware test pending (§12)** |
| E3b | E2 engine tabs + corpus validation | 8 more section tabs — kkEdTabs grows to 24 (E2 engine ×8 at tabs 14..21, IFX 1-12 → 22, MFX·TFX → 23) — generated as a structural mirror of E1 at base 3960 with `engine2N` apply (byte 3909); tab selection follows e2 when e1 is unset (e1 keeps priority); generator validates against the combined corpus PRELOAD + `banks_for_tests` (10 752 programs): 404/404 params, 0 exclusions, 9 engines covered on e1 and e2 | E2 engine page round-trips on a program using that engine as EXi 2; tab mapping per engine byte 3909 | **DONE 26 oct. (complet-0.97d) — static verification passed (e2check 56 checks; Lua harness 199 checks incl. 22 E3b vectors + a full corpus walk of 10 752 programs through the panel's own PCG loader: tab mapping, engine-page visibility, in-range reads, 0 anomalies); hardware test pending (§13)** — E3b v2 items (KARMA, Drum Track, Vector/Step Seq, Tone Adjust, EXi Common, engine-selector byte, fn 43) deferred: 0.97h if credits remain, else post-0.98a |
| E4 | Combi | second tab set `kkEdTabsC` (43 tabs: Général, Commun, Vector, Drum Track, IFX 1-4/5-8/9-12, MFX·TFX, Audio In, LFO & In, Contrôleurs, Timbre 1..16 ×2) — 1 930 generated controls `kkC_*` (`set = "combi"`) from `Combinaison.json`; Général combi page (editable name, version, category, scale); « Lire le son » reads obj 00/01 per mode (4A); « Appliquer » writes obj 00/01 (4B); PCG loader: CBK1 banks (cnames/cslots) + « Jouer > » combi; combi names on the rack; generator validates against the combi corpus (2 048 combis): 1 930/1 930 params, 0 exclusions | combi dump round-trip; timbre edits audible | **DONE 26 oct. (complet-0.97e) — static verification passed (e2check 85 checks; Lua harness 254 checks incl. 41 E4 synthetic vectors + a full corpus walk of 2 048 combis through the panel's own PCG loader: visibility + in-range reads, 0 anomalies; PRELOAD combi census 6 banks / 768 combis); hardware test pending (§14)** — KARMA Combi (Module A-D + Common) deferred to v2 |
| E5 | Store + banks | 0x49 Object Dump to the selected slot (bank byte *2, idH/idL, version); 0x4C Store Bank (2-click confirm); 0x4D Dump Bank Request -> series of 73 collected into KKPCG.dnames/ditems (device banks, playable via « Jouer > », priority over PCG/factory names); Program + Combi v1 (kits/WSQ v2, Global never stored) | write a program to U-A, store, recall on the Kronos | **DONE 26 oct. (complet-0.97f) — static verification passed (e2check 114 checks; Lua harness 293 checks incl. 39 E5 vectors: 0x49 write round-trip + GM refusal, 0x4C 2-click + 5 s disarm, 0x4D full 128-object bank reads for Program U-A and Combi I-A, device-bank Jouer > with no PCG loaded, timer 4 timeout)** — hardware test pending (§15) |
| E6 | Drum Kit / Wave Seq / Global | obj 04/05/03 pages from DrumKit.txt / WaveSequence.txt / Global.txt | kit/wsq dump round-trip | **DONE 27 oct. (complet-0.97i) — object selector kkObjSel (5 objects), tab sets kkEdTabsK/W/G (6/3/15), 71+28+591 generated controls kkK_*/kkW_*/kkG_*; static verification passed (e2check + smoke)** — hardware test pending |
| 0.98a | Beta build | full panel + editor plugged in: rack (tab 0) + EDIT (tab 1) with all tab sets, 6315 modulators, 28 Lua methods, embedded kronosEditor/kronosData; e2check 0.98a completeness section (control families 404/1930/71/28/591, tab sets 2/24/43/6/3/15, 5 objects, PCG loader) | open in Ctrlr/SAVIHost: load time, rack regression, EDIT round-trip on a real dump | **DONE 1 nov. 2026 — built, e2check 1830 PASS / 0 FAIL, smoke ALL PASS; GUI/hardware test by the maintainer** |
| 0.98b | Editor GUI re-skin from `graphics/KRONOS_Editor/0.97i` | (superseded by 0.98c) full-panel section tabs (fixes the +116 px content-origin shift), drawn backgrounds, drawing coordinates, `_val` displays, drawn tab bar → real buttons (`kkEdTabBtn`), z-ordered frame | — | **DONE 1 nov. 2026 — built, e2check 1843 PASS / 0 FAIL, smoke ALL PASS** |
| 1.0a | **Editor v1** — new GUI architecture (post-mortem: `ctrlr-project/docs_editor/EDITOR_V1_POSTMORTEM.md`) | No nested uiTabs: EDIT = one uiImage `kkEdFond` with the FULL uncropped page artwork (214 pages incl. FX EDIT) swapped by Lua + pooled controls re-bound per page (`sources/editor_v1.py`, `lua/kkEdGui.lua`); data layer of kkEd.lua kept (fix: kkEdWriteField now writes at KK.edOff); kkU UTF-8 -> Latin-1 for every Lua-set text (fixes the Editor mojibake + the Main monitor tofu) | open in SAVIHost: every object/area/page/instance shows the design; Read sound -> values ; edit -> Apply (0x4B) -> Reply 24 | **DONE 1 nov. 2026 — 24.9 MB, 869 modulators, 33 methods, load ~25 s; e2check 258 PASS / 0 FAIL (23 pre-1.0 SKIP), smoke ALL PASS (292, new section 10); LIVE-tested in SAVIHost3 + Ctrlr 5.6.23 (GUI, no KRONOS). Hardware test by the maintainer next** |
| 0.98e | Bisect fix: editor content not painting | 0.98d still showed a blank EDIT page (maintainer screenshots for_vibe/editor_2_*). Pixel analysis: rack (root tab) paints 12956 blue knob px; editor content zone has 0 widget px -> the NESTED tab content (fonds + children) does not paint; only the frame (direct children of the root EDIT tab) does. New in 0.98b/c vs the working 0.97: uiTabsTabBackgroundImage on NESTED tabs. 0.98e removes it (nested tabs back to '-- None') and draws each page fond as a plain uiImage modulator child of the tab (kkFond_*, rect 0 0 1500 298, first child -> behind controls) — the same mechanism as the rack's LED filmstrips, which paint fine. Container geometry stays at the proven 0.97i '0 92 1500 322' depth 24, children content-relative (y-116), fonds cropped to y>=116 at build | open 0.98e: EDIT tab must show the drawn page with controls on the cells | **DONE 1 nov. 2026 — built (41.5 MB, 9190 modulators, 31 methods), e2check 2488 PASS / 0 FAIL, rendermodel 18 PASS / 0 FAIL (new: tools/panel-harness/rendermodel.py simulates the Ctrlr component tree from the panel XML), smoke ALL PASS; GUI re-test by the maintainer — if STILL blank, next suspect is the panel size/modulator count (41 MB / 9190 mods), fallback = split editor into its own panel/VST** |
| 0.98d | Fix "editor shows no graphics" (maintainer screenshots 2026-11-01, `for_vibe/editor_*_no_show.jpg`) | Root cause: 0.98b/c had the section tab containers at full-panel `0 0 1500 414` depth 0, and in this Ctrlr build **nested** tab containers at depth 0 do not paint their tab content (only the root container does — the frame painted, the page area stayed flat dark, matching the screenshots). Fix: containers back to the proven 0.97i geometry (`0 92 1500 322`, depth 24); every page-child control rect converted to content-relative (`y − 116`, tab children are positioned relative to the tab content origin (0, 92+24)); each fond cropped to its top 116 px at build (PIL) so the artwork fills the 1500×298 content area exactly and aligns with the controls; page/instance nav combos moved into the frame's free space (y 66); the JUCE tab bar (depth 24) stays as a working fallback page switcher | open in Ctrlr/SAVIHost: EDIT tab shows the drawn page artwork with controls on the cells | **DONE 1 nov. 2026 — built (41 MB, 8977 modulators, 31 methods), e2check 2486 PASS / 0 FAIL (0.98d checks: container geometry, y−116 shift, cropped-fond hashes), smoke ALL PASS; GUI re-test by the maintainer** |
| 0.98c | **Full editor** from `graphics/KRONOS_Editor/Full` | `scripts/gen_full_editor.py` reads every `Full/*/…INDEX.json` + `_layout.json` → `data/kronos_full.lua` (embedded as `kronosEditor`, 6719 params, `engtab`) + `sources/editor_full_layout.json`; every control's `korg` block (file/ofs/bit/sysex/data/value) becomes a param entry (pcs/w/rmin/fr/dmin/f/kind/labels, LSB-first raw ranges); engine folders get prefixed ids (`AL1:Prog_EXi@…`) and cross-page duplicates get `#n` suffixes (unique modulator names); 7 tab containers (prog 154 tabs, combi 33, kit 3, wsq 2, global 13, **setlist 2, song 6** — new objects 0x0D/0x18 in `kkObjSel`), all full-panel depth 0 with 213 embedded Full fonds (`edfF_*`); navigation by page combo `kkEdPageSel` + instance combo `kkIdxSel` + area label `kkEdArea` (new methods); instance rebinding at runtime via page `base`/`stride_bytes` → `KK.edOff` applied in `kkEdReadField`/`kkEdWriteField` (NOTE 1..128 stride 300, OSC 1/2, EXi 1/2 base 2908 stride 1052, …); apply guards extended (`exi:<engine>` via `KK_ED_ENG_CODE` + selected EXi slot, `setlist`/`song` sets); `kkEdSelectTab` follows `engtab`; frame re-skinned from the 0.97i drawing and z-ordered above the tabs | open in Ctrlr/SAVIHost with a real Kronos: every page of every object editable, instance selector rebinds offsets, round-trip 0x4A→pages→0x4B | **DONE 1 nov. 2026 — built (49.4 MB, 8977 modulators, 31 Lua methods), e2check 2486 PASS / 0 FAIL (incl. 0.98c section), smoke ALL PASS (incl. 0.98c vectors: edOff stride read, exi: guard, engtab, 7 objects); GUI/hardware test by the maintainer. NOTE: 49 MB / 8977 modulators ⇒ slower load than 0.98b (split-panel option on file in `for_vibe/3. PERFORMANCE-OPTIONS.md`)** |
| E7 | PCG interop (decision point) | port kronos_pcg.py essentials to Lua, or keep PCG interchange in pcglib (external tool) and let the panel speak raw dumps + device banks | load a pcglib-produced PCG bank into the panel, send to device | **Absorbed**: U1 reads any PCG at runtime (this row's read side); the write side is U3 — minimal Lua writer, pcglib for heavy lifting |

## 6. UI plan

- One panel, canvas unchanged (1500×414). A `uiTabs` modulator `kkTabs`
  covers the whole canvas with `uiTabsDepth="0"` (no visible bar); tab 0
  "RACK" carries the rack artwork as its tab background (`rack_fond`,
  stretch) — pixel-identical to today; tab 1 "EDIT" has a dark content
  background (`ff1b1b1d`).
- Page switching from Lua via `setPropertyInt("uiTabsCurrentTab", n)`
  (TR-Rack-proven). A small `EDIT →` button on the rack (flat band at
  x 550-880, y 340-358, above the mixer knobs) opens the editor; a
  `← RACK` button on the EDIT page goes back. Later stages add a visible
  section-tab bar *inside* the EDIT tab (second-level `uiTabs`, depth 24).
- `uiTabsCurrentTabChanged="kkTabChanged"` refreshes the EDIT page from the
  last received dump when the tab is opened.
- Lock tab switching while a dump transfer is in progress (TR-Rack
  `lockOutTimer` pattern; the Kronos disables new notes during long dumps).
- Editor controls: `uiSlider` (rotary) for values, `uiCombo` for
  enumerations (479 in TR-Rack — engine/effect types, scales, AMS
  sources…), editable `uiLabel` for names (`uiLabelEditOnDoubleClick`,
  verified in `CtrlrLabel.cpp`).

## 7. Conventions

- Lua dialect: 5.1-compatible (no `//`, no bitwise operators — arithmetic
  only), matching `kkMain.lua` and TR-Rack.
- The rack page, its artwork and its 172 modulators are not touched by
  editor work; editor code is additive (new methods, new modulators, new
  tabs). The rack remains the fallback if editor work breaks something.
- Every stage is verified on hardware before the next begins (project
  discipline since 0.9). Test steps live in §9 for E1, and will be added
  per stage.
- Harvested/reference files stay byte-identical; new knowledge goes in
  this project's own docs.

### Proven bit-level rules (investigations/16slot, converged 1 nov. 2026)

Independently proven by the two blind investigations
(`investigations/FIXED_CONTROL_GAPS_FINDINGS{,_2}.md`,
`COMPARISON_1_vs_2.md`) over the factory PRELOAD and the parameter maps:

- **Bit pieces are LSB-first**: piece[0] is the least significant
  (`value |= field << shift`, increasing shifts). Proved on 596k samples
  (91/91 multi-piece fields in range LSB-first vs 25 MSB-first). The panel
  editor already does this (`kkEdReadField`, kkEd.lua:48 "morceaux poids
  faible d'abord").
- **Ranges are raw, not display**: scale over the `data` hex column
  (`9D~63` = −99…+99), sign-extend two's complement, never over the
  `value` display column (`-99~+99`, `0.0~100.0`). `gen_editor_lua.py`
  builds `rmin`/`fr` from `data` only.
- **Tone Adjust assign bytes** (knobs 2586+2i, sliders 2666+2i): mask bit 7
  (`& 0x7F`) before use — the flag's meaning is unresolved (18 factory
  programs; investigations F10). The panel never reads these bytes today.
- **Double-EXi programs** (371/2176 factory, osc mode byte 2558 bits 0-2 == 3
  with both engine bytes 2857 and 3909 in 2…9): the fixed 16 controls
  describe **EXi1** (byte 2857, block base 2908); EXi2 lives at base 3960
  (byte 3909) — the editor's engine2 tabs.
- **EP-1 Model Type** (byte 2908 bit 7 + 2909 bits 0-1): 0 Tine EP I Late,
  1 Tine EP II, 2 Tine EP V, 3 Tine EP DMP, 4 Reed EP 200, 5 Reed EP 200A,
  6 Tine EP I Early (OS 3.2.1+). Reed has Volume/Vibrato/Speed/Cabinet but
  **no Treble/Bass** — those two slots are label-only for Reed programs.
- **Relative vs Absolute Tone Adjust**: the TA value byte after the assign
  code is 0 in every factory program, so a control's current value = the
  stored base value of its parameter, not the live Rel offset.
- The 16 fixed labels are validated against PRELOAD's stored TA codes by
  `tools/panel-harness/e2check.py` (witness check, 0.97q+) — a shifted
  label table fails the build.

## 8. Risks and open questions

- **Documented but not yet hardware-tested:** 0x4A/0x4B/0x48/0x49/0x4C/0x4D
  message sizes, timing, single-message delivery; version byte values
  (program v5, combi v3 expected); that sending 0x4B really replaces the
  edit buffer; Reply 24 codes for these functions. E1's test answers the
  read side.
- **Dump data = PCG element body**: expected (the bank-digest note in the
  SysEx doc says digests are computed over bank data "in the same format as
  is sent via func 0x73 and 0x75 dumps"); one comparison against a factory
  PRELOAD.PCG block confirms it.
- HD-1 vs EXi programs share offsets only up to ~2857; E1 shows engine
  bytes for EXi programs only (E3 adds the HD-1 map).
- Ctrlr message-size limits: single program/combi dumps are fine; a drum
  kit dump is ~44 KB packed (TR-Rack received 63 KB single messages fine).
  Full-bank series = 128 messages — pace them (E5).
- Ctrlr Lua memory: a dump is stored as a binary string (5–8 KB) — trivial;
  hex-string debugging views double that — still trivial.

## 9. E1 hardware test (fill in)

**Static verification (done 24 oct., before hardware):** every Lua method of
the built panel parses and executes under the Lua 5.4.2 interpreter; the
7-bit codec matches doc `*3` (`sysExSize = binarySize + (binarySize+6)/7`)
for all object sizes (Program 4,960→5,669; Combi 7,810→8,926; Drum Kit
38,424→43,914; Wave Seq 2,216→2,533 wire bytes), the MSB-first wire layout
matches the doc's bit image, partial last groups round-trip (318 random
buffers), a synthetic 0x4B program dump (5,677 wire bytes) decodes back to
the identical 4,960 bytes, `kkEditShow` shows every field at its documented
offset, and the 0.96 rack paths (kkClick/kkOnMidi/kkInit) still behave.
99 checks, 0 failures.

Preconditions: same as `TEST_PLAN_0.96.md` §1 (Bank Map KORG, Enable
Exclusive/Control Change ON, channel 1; tests touch the edit buffer —
reload the program after, never Write a sound).

1. Load `KronosKontrol.panel` (complet-0.97 build). Console must show
   `Kronos Kontrol : panneau chargé` + `KRONOS mode X …`. The rack (tab 0)
   must look and behave exactly as in 0.96.
2. Click **EDIT ▸** → the EDIT page appears (dark background). Click
   **◂ RACK** → the rack is back, pixel-identical.
3. On the Kronos, select a known EXi program (e.g. an AL-1 or MOD-7
   factory program in I-A). On the EDIT page, click **Lire le programme**.
   - Status line: `→ requête dump objet 0 …`; monitor: `→ F0 42 30 68 4A
     00 F7` then `← dump obj=00 ver=5 4960 octets` (version 5 expected for
     OS 3.x programs).
   - The page shows the program **name** — must match the Kronos screen.
   - Category / scale shown; IFX 1-12 type names shown (e.g. IFX1 =
     whatever the program uses); EXi 1 / EXi 2 engine names shown (e.g.
     AL-1, Off).
4. Cross-check one parameter: read a value on the Kronos front panel
   (e.g. IFX1 type, or the program category) — must match the page.
5. Select an HD-1 program (e.g. from an HD-1 bank / "Init Program"):
   name/version/category/scale/effect types still valid; engine bytes are
   NOT meaningful for HD-1 (known E1 limitation).
6. Regression: back on the rack, encoders/banks/FX/mixer still work
   (0.96 behaviour unchanged).

| Step | Expected | Observed | OK? |
|------|----------|----------|-----|
| 1 load | console lines, rack unchanged | | |
| 2 tab switch | EDIT page / back, rack identical | | |
| 3 dump read | ver=5, 4,960 B, name matches | | |
| 4 cross-check | value matches front panel | | |
| 5 HD-1 program | common fields valid | | |
| 6 regression | 0.96 controls work | | |

Record the outcome in `RESUME.md` (new section, corpus root) before starting E3.

## 10. E2 hardware test (fill in)

**Static verification (done 26 oct., before hardware):** the generator reproduces the shipped panel
byte-for-byte; 20 structural checks (XML, 214 modulators / 20 Lua methods, tabs 174/39/1, embedded data =
sources, all callbacks wired incl. `uiLabelChangedCbk`, `rack_fond.png` resource, Lua syntax of all 20
methods); 61 checks under the Lua 5.4.2 interpreter with a mocked Ctrlr API (synthetic 0x4B round-trip,
`kkEditShow` incl. the E2 controls, rename, local patches, fn 43 sends, 0x4B write-back + busy + Reply 24 +
tab lock, 0.96/0.97-E1 regressions, 8 codec round-trips); dump offsets validated against the factory PRELOAD
OS 3.2 (2,176 programs). Also fixed in this build: category display masks bits 4~0 of byte 2568
(`Prog_HD-1.txt` l. 2078) — the raw byte carries other parameters in bits 7~5.
**Nothing sent to hardware yet.**

Preconditions: same as §9 (Bank Map KORG, Enable Exclusive/Control Change ON, channel 1; tests touch the
edit buffer — reload the program after, never Write a sound). **Finish the E1 test (§9) first** and record
it in `RESUME.md` (corpus root); do not reload the panel in Ctrlr before E1 results are noted (the file on disk now
contains E2 — the already-loaded instance is unaffected).

1. Load `KronosKontrol.panel` (complet-0.97 + E2). Console: `Kronos Kontrol : panneau chargé` +
   `KRONOS mode X …`; rack (tab 0) unchanged.
2. Kronos in PROG; select a known program. `EDIT ▸` → EDIT page; **Lire le programme** → dump loaded; the
   E2 controls show the current values (OSC1/EXi1 Level, Master Vol, category, scale, IFX1).
3. Realtime: move **OSC1/EXi1 Level** → the level changes on the Kronos (audible/visible). Note: the panel
   sends both variants (TYP 9 HD-1 / TYP 11 EXi); the Kronos refuses the wrong one (Reply 24 code 1 in the
   console) — expected, harmless. Same with **Master Vol**.
4. Rename: double-click the name, type a new name (≤ 24 chars), Enter; click **Appliquer → 0x4B** → status
   `→ écriture tampon d’édition (0x4B, 5 669 octets packés)…`, then `← Reply 24 code 0 : OK` and
   `← écriture OK — tampon d’édition à jour`. The Kronos screen shows the new name. (This step is what
   confirms that sending 0x4B really replaces the edit buffer.)
5. Patch params: change **Catégorie**, **Gamme**, **IFX1** → **Appliquer** → Reply 24 OK → category visible
   on the Kronos PROG page; IFX1 type audible/visible on the IFX1 page.
6. Busy state: click **Appliquer** twice quickly → second click refused (`Écriture en cours…`); try to
   switch to the RACK tab while busy → locked on EDIT. After Reply 24 the lock lifts.
7. Gates: in COMBI mode the E2 controls answer `Édition : mode Program seulement` and send nothing.
8. Regression: RACK tab — encoders/banks/FX/mixer unchanged (0.96); E1 read still works; reload the
   program on the Kronos to discard the edit-buffer changes.

| Step | Expected | Observed | OK? |
|------|----------|----------|-----|
| 1 load | console lines, rack unchanged | | |
| 2 dump read + E2 values | controls show current values | | |
| 3 realtime levels | audible change; Reply 24 code 1 for the wrong engine | | |
| 4 rename + Appliquer | Reply 24 OK; new name on the Kronos | | |
| 5 category/scale/IFX1 + Appliquer | Reply 24 OK; values changed | | |
| 6 busy | refused 2nd apply; tab locked | | |
| 7 Combi gate | "Program seulement", nothing sent | | |
| 8 regression | 0.96 rack + E1 read OK | | |

Record the outcome in `RESUME.md` (new section, corpus root) before starting E3.

## 11. U1 hardware test (fill in)

**Static verification (done 26 oct., before hardware):** e2check 27 structural checks
(220 modulators / 21 Lua methods, tabs 180/39/1, embedded = sources, callbacks wired,
kkPcg.lua embedded, kkVersion label = `complet-0.97b`); 96 checks under the Lua 5.4.2
interpreter with a mocked Ctrlr API (synthetic PCG, **real PRELOAD load** — 17 banks /
2 176 programs, names/slots byte-exact, `kkPcgPlay` sends 0x4B and fills the EDIT page,
gates, latin-1 ↔ UTF-8 rename, dialog mock); `tools/corpus-check` — **112/112 PCGs of
`corpus/manifest.csv` match kronos_pcg.py** (73 user banks, 20 factory OS 3.x and 1 OS 2
accepted with identical counts/names; 6 OS 1, 10 other instruments, 3 non-KRONOS
rejected as expected). Two bugs found and fixed by this harness: a big-endian read
(byte × 128 instead of × 256) that derailed the chunk walk on real files, and missing
trailing-space strip on names. **Nothing sent to hardware yet.**

Preconditions: same as §9/§10 (Bank Map KORG, Enable Exclusive/Control Change ON,
channel 1; tests touch the edit buffer — reload the program after, never Write a
sound). **Finish §9 and §10 first** and record them in `RESUME.md` (corpus root).

1. Load `KronosKontrol.panel` (complet-0.97b). Console: `Kronos Kontrol : panneau
   chargé — complet-0.97b`; the version label `complet-0.97b` shows at the
   bottom-right of the RACK tab.
2. Click **PCG >** → file dialog opens; pick a PCG (start with the factory PRELOAD,
   then one of your own banks). Monitor: `PCG chargé : <file> — OS 3.x, N banques,
   M programmes`; the file name appears next to the buttons; the button reads **PCG x**.
3. Rack names come from the file: select I-A000 → the displayed name matches the
   reference name (and the Kronos screen for a factory program).
4. KRONOS in PROG, I-A000 selected → click **Jouer >**: monitor shows the 0x4B write
   (`→ écriture tampon d’édition (0x4B, 5 669 octets packés)…`), Reply 24 OK, and the
   EDIT page shows the program name from the file. The Kronos edit buffer now holds
   that program (audible). **Reload the program on the Kronos afterwards.**
5. Load one of your own PCG banks (e.g. a U-A bank with French accented names):
   names display correctly (accents), **Jouer >** works the same.
6. Gates: **Jouer >** in COMBI mode → `Jouer : mode Program seulement`, nothing sent;
   select a bank absent from the loaded PCG (e.g. U-GG with the PRELOAD) →
   `Slot 0.21.000 absent du PCG chargé`; with no PCG loaded → `Aucun PCG chargé`.
7. Click **PCG x**: label back to `aucun PCG chargé`, button back to **PCG >**, rack
   names back to the factory reference.
8. Regression: E1 read and E2 write-back still behave as in §9/§10; the RACK tab is
   unchanged apart from the new bottom-left strip (PCG controls) and the version label.

| Step | Expected | Observed | OK? |
|------|----------|----------|-----|
| 1 load | console `— complet-0.97b`, version label bottom-right | | |
| 2 open PCG | dialog, `PCG chargé : …`, file name shown, button `PCG x` | | |
| 3 names from file | rack names match the PCG | | |
| 4 Jouer > | 0x4B sent, Reply 24 OK, EDIT page shows file name; program audible | | |
| 5 own bank | accented names OK, Jouer > OK | | |
| 6 gates | Combi / absent slot / no PCG refused, nothing sent | | |
| 7 PCG x | closed, factory names back | | |
| 8 regression | E1/E2 + RACK unchanged | | |

Record the outcome in `RESUME.md` (new section, corpus root) before starting E3.

## 12. E3 hardware test (fill in)

**Static verification (done 26 oct., before hardware):** e2check 51 structural checks
(867 modulators / 25 Lua methods, kkTabs 180/8/1, kkEdTabs 678 = 30 Général +
324 controls + 324 labels, 16 section tabs, generated controls verified one by one
against `editor_layout.json`, kronosEditor embedded = `data/kronos_editor.lua`,
callbacks wired, kkVersion label = `complet-0.97c`); 169 checks under the Lua 5.4.2
interpreter with a mocked Ctrlr API (synthetic HD-1 and EXi dumps through the real
0x4B receive path; field read/write vectors — multi-piece AL-1 Wave Morph, signed
wrap EXi1 Panpot Mod.Intensity, 16-bit OSC1 Tune, inverted IFX1 Switch, scaled
MS-20EX LPF Cutoff f=0.01, Octave enum wrap; dual-variant Common LFO; gates mode/
busy/engine; visibility masking HD-1/EXi/engine; engine-aware tab mapping e1/e2;
kkEdField → 0x4B write-back round-trip; E1/E2/U1 regressions); generator validation
against the factory PRELOAD — 2 176 programs, 324/324 params readable, 0 exclusions.
The harness caught one real bug before hardware: `kkEdVar`/`kkEdRawOf` were chunk-local
in `lua/kkEd.lua` but called from the `kkEdField` method (a separate Lua chunk in Ctrlr)
— fixed by making them global. **Nothing sent to hardware yet.**

Preconditions: same as §9–§11 (Bank Map KORG, Enable Exclusive/Control Change ON,
channel 1; tests touch the edit buffer — reload the program after, never Write a
sound). **Finish §9, §10 and §11 first** and record them in `RESUME.md` (corpus root).

1. Load `KronosKontrol.panel` (complet-0.97c). Console: `Kronos Kontrol : panneau
   chargé — complet-0.97c`; version label `complet-0.97c` bottom-right of RACK.
2. EDIT tab → the section tab bar shows 16 tabs (Général, Commun, OSC1, OSC2,
   EXi1 Mix, EXi2 Mix, E1 AL-1 … E1 EP-1, IFX 1-12, MFX·TFX). The Général page shows
   the E1 read-only block (name, version, category, scale, EXi engines, effect types)
   plus the E2 edit controls (category/scale/IFX1 combos, OSC1/EXi1 Level and
   Master Vol knobs).
3. **Lire le programme** on an HD-1 program (e.g. I-A000): the panel jumps to the
   OSC1 tab; OSC1/OSC2 controls are visible, EXi/engine tabs show no controls
   (hidden), Common controls show the program's values.
4. Same on an EXi program: the panel jumps to the matching engine tab (E1 AL-1 …
   E1 EP-1 by engine byte 2857, else EXi2 Mix / EXi1 Mix); only the Common, EXi Mix,
   current-engine, IFX and MFX·TFX controls are visible.
5. Round-trip per page: pick a control, note the Kronos screen value, change it in
   the panel, click **Appliquer → 0x4B** (Reply 24 OK, monitor `← écriture OK`),
   **re-dump** (Lire le programme) and check the page shows the new value; compare
   with the Kronos screen. Never click anything that would Write/Store.
6. Masquage: on an HD-1 program, the EXi1 Mix / EXi2 Mix / engine tabs must show no
   editable controls; on an EXi program, the OSC1/OSC2 tabs likewise — and editing
   is refused with `Paramètre hors type de programme` if attempted (e.g. via a
   hidden control left over from a previous program).
7. Regression: RACK tab unchanged (0.96); E1 read (§9), E2 write-back (§10) and
   U1 PCG loader (§11) still behave as recorded.

| Step | Expected | Observed | OK? |
|------|----------|----------|-----|
| 1 load | console `— complet-0.97c`, version label, 16 section tabs | | |
| 2 EDIT/Général | E1 read-only + E2 controls on one page | | |
| 3 HD-1 program | jumps to OSC1; EXi/engine controls hidden | | |
| 4 EXi program | jumps to the engine tab; OSC controls hidden | | |
| 5 round-trip/page | edit → Appliquer → Reply 24 OK → re-dump, values match | | |
| 6 masquage | no cross-type controls visible; edits refused | | |
| 7 regression | RACK 0.96 + E1/E2/U1 unchanged | | |

Record the outcome in `RESUME.md` (new section, corpus root) before starting E3b/E4.
## 13. E3b hardware test (fill in)

**Static verification (done 26 oct., before hardware):** e2check 56 structural checks
(1 027 modulators / 25 Lua methods, kkEdTabs 838 = 30 Général + 404 controls + 404
labels, 24 section tabs, generated controls verified one by one, kronosEditor
embedded with 404 params / 23 pages, 80 apply engineN + 80 apply engine2N,
kkVersion label = `complet-0.97d`, Lua syntax of the 25 methods; also writes
`tools/panel-harness/banks_list.lua`); 199 checks under the Lua 5.4.2 interpreter —
synthetic E2 vectors (tab 16 for e2=4, E2 AL-1 read/write at bytes 4332/4333,
engine2 gate, e2 tab mapping, e1 priority) plus a full corpus walk: PRELOAD +
65 banks of `banks_for_tests` (10 752 programs) loaded through the panel's own
`kkPcgLoad`, every program walked through `kkEdSelectTab` + all 23 pages —
tab selection matches an independent reimplementation, engine-page visibility
is exactly 10 params on the active engine(s) and 0 elsewhere, every applicable
field reads in range (0 anomalies); generator validation 404/404 params over the
same corpus, 0 exclusions, 9 engines covered on e1 and e2. **Nothing sent to
hardware yet.**

Preconditions: same as §9–§11. **Finish §9–§12 first** and record them in
`RESUME.md` (corpus root).

1. Load `KronosKontrol.panel` (complet-0.97d). Console: `Kronos Kontrol : panneau
   chargé — complet-0.97d`; version label `complet-0.97d` bottom-right of RACK.
2. EDIT tab → the section tab bar shows 24 tabs (Général, Commun, OSC1, OSC2,
   EXi1 Mix, EXi2 Mix, E1 AL-1 … E1 EP-1, E2 AL-1 … E2 EP-1, IFX 1-12, MFX·TFX).
3. Load a program using an EXi engine as **EXi 2** (byte 3909) from
   `banks_for_tests` (e.g. a `univers_str1` / `cordes_str1` bank): the E2 engine
   tab (14..21) matching byte 3909 shows its 10 controls with the program's
   values; the other E2 engine tabs show none; the E1 engine tab shows controls
   only if byte 2857 is also set. Note: in the corpus every EXi program also has
   an EXi 1 engine, so the panel auto-selects the E1 engine tab (e1 priority) —
   click the E2 engine tab to reach its controls.
4. Round-trip per E2 engine page: pick a control, note the Kronos screen value,
   change it in the panel, **Appliquer → 0x4B** (Reply 24 OK), **re-dump** and
   check the page shows the new value; compare with the Kronos screen.
5. Masquage: E2 engine controls are hidden on HD-1 programs and on EXi programs
   whose byte 3909 differs; editing is refused with `Paramètre hors type de
   programme`.
6. Regression: RACK tab unchanged (0.96); E1/E2/U1/E3 (§9–§12) unchanged.

| Step | Expected | Observed | OK? |
|------|----------|----------|-----|
| 1 load | console `— complet-0.97d`, version label, 24 section tabs | | |
| 2 EDIT tab bar | 24 tabs incl. E2 AL-1 … E2 EP-1 at 14..21, IFX at 22, MFX·TFX at 23 | | |
| 3 EXi 2 program | matching E2 engine tab shows 10 controls with values | | |
| 4 round-trip/E2 page | edit → Appliquer → Reply 24 OK → re-dump, values match | | |
| 5 masquage | E2 controls hidden off-engine; edits refused | | |
| 6 regression | RACK 0.96 + E1/E2/U1/E3 unchanged | | |

Record the outcome in `RESUME.md` (new section, corpus root) before starting E4 (0.97e) — built 26 oct.; its hardware test is §14.

## 14. E4 hardware test (fill in)

**Static verification (done 26 oct., before hardware):** e2check 85 structural checks
(4 897 modulators / 25 Lua methods, kkEdTabs 838 + kkEdTabsC 3 869 = 9 Général combi +
1 930 controls + 1 930 labels, 24 + 43 section tabs, both generated control sets
verified one by one, kronosEditor embedded with 404 prog + 1 930 combi params /
23 + 42 pages, `set = prog` ×404 / `set = combi` ×1 930, kkVersion label =
`complet-0.97e`, Lua syntax of the 25 methods; also writes
`tools/panel-harness/banks_list.lua`); 254 checks under the Lua 5.4.2 interpreter —
synthetic combi vectors (obj 01 ver 3, 7 810 B round-trip, Général combi fields,
kkC_ reads/writes incl. Timbre 1 Volume at byte 4807, set/mode/busy gates, 0x4B
write-back obj 01, container visibility swap prog ⇔ combi, kkBtnGetProg 4A 01 in
Combi mode) plus a full corpus walk: PRELOAD + 65 banks of `banks_for_tests`
(2 048 combinations) loaded through the panel's own `kkPcgLoad`, every combi walked
through `kkEdSelectTab` + all 42 cpages — all combi controls visible, every field
reads in range (0 anomalies); generator validation 1 930/1 930 params over the same
corpus, 0 exclusions; PRELOAD combi census 6 CBK1 banks / 768 combis (I-A..I-F).
**Nothing sent to hardware yet.**

Preconditions: same as §9–§11. **Finish §9–§13 first** and record them in
`RESUME.md` (corpus root).

1. Load `KronosKontrol.panel` (complet-0.97e). Console: `Kronos Kontrol : panneau
   chargé — complet-0.97e`; version label `complet-0.97e` bottom-right of RACK.
2. COMBI mode on the Kronos; EDIT tab → click **Lire le son** → status
   `→ requête dump objet 1 …`, monitor `← dump obj=01 ver=3 7810 octets`; the EDIT
   header shows `ÉDITEUR — Combinaison courante`; the section tab bar shows 43 tabs
   (Général, Commun, Vector, Drum Track, IFX 1-4, IFX 5-8, IFX 9-12, MFX·TFX, Audio In,
   LFO & In, Contrôleurs, Timbre 1 … Timbre 16·2) and selects Général.
3. Général: name matches the Kronos screen (double-click to rename), version = 3,
   category / scale shown. Commun page: Favorite, Auto Load PAT, Scale Type/Key/Random.
4. Timbre page round-trip: Timbre 1 → Volume, note the Kronos value, change it in the
   panel, **Appliquer → 0x4B** (Reply 24 OK), **re-dump** and check the page shows the
   new value; the timbre's volume changes when the combi is recalled.
5. Masquage: in PROG mode with a program loaded, the combi pages are replaced by the
   program pages (`kkEdTabs`) and vice versa; editing a `kkC_` control while a program
   is loaded is refused (`hors type`); editing a `kkF_` control while a combi is loaded
   is refused.
6. PCG: open PRELOAD (or any PCG with CBK1 banks) → `PCG x`; in COMBI mode the rack
   shows combi names from the file (e.g. `I-A000 K-Lab: Katja's House`); **Jouer >**
   loads the selected combi into the edit buffer (0x4B obj 01 ver 3) — the EDIT header
   shows its name.
7. Regression: RACK tab unchanged (0.96); E1/E2/U1/E3/E3b (§9–§13) unchanged; PROG
   mode editing unchanged.

| Step | Expected | Observed | OK? |
|------|----------|----------|-----|
| 1 load | console `— complet-0.97e`, version label, 43 combi section tabs in COMBI mode | | |
| 2 EDIT header | `ÉDITEUR — Combinaison courante`, Général tab selected, name/version/cat/scale | | |
| 3 timbre round-trip | edit → Appliquer → Reply 24 OK → re-dump, values match, audible | | |
| 4 masquage | kkC_ refused on program, kkF_ refused on combi, containers swap | | |
| 5 PCG combi | combi names on rack, Jouer > sends 0x4B obj 01 ver 3 | | |
| 6 regression | RACK 0.96 + E1/E2/U1/E3/E3b unchanged | | |

Record the outcome in `RESUME.md` (new section, corpus root) before starting E5 (0.97f).

## 15. E5 hardware test (fill in)

**Static verification (done 26 oct., before hardware):** e2check 114 structural
checks (4 903 modulators / 25 Lua methods, EDIT header 15 components, E5 buttons
`kkBtnWrite`/`kkBtnStore`/`kkBtnBankRead` + lits, `kkSysExBank` bank-*2 mapping with
GM read-only refused on write, 0x49/0x4C/0x4D message formats, `kkClick` dispatch
+ `kkBtnBank` prefix guard, `kkOnMidi` 0x49 branch, Reply 24 `wslot` handling,
`kkPcgRecvDump` collection, `KKPCG.dnames/ditems/devbanks`, `kkDumpName`, `kkShow`
device-bank priority, `ditems` before `slots`/`cslots` in « Jouer > », timers 3/4,
Lua syntax of the 25 methods); 293 checks under the Lua 5.4.2 interpreter — 39 E5
vectors (bank mapping, 0x49 write round-trip + GM/no-dump/wrong-mode refusals,
0x4C 2-click arm/disarm/send, 0x4D full 128-object bank reads for Program U-A and
Combi I-A, device-bank « Jouer > » with no PCG loaded, out-of-session 0x49 ignored,
second read refused, timer 4 timeout) plus all E1/E2/U1/E3/E3b/E4 regressions.
**Nothing sent to hardware yet** (mock-tested only — the Kronos is not connected
to the harness).

Preconditions: same as §9–§11. **Finish §9–§14 first** and record them in
`RESUME.md` (corpus root).

> **Safety:** « Écrire → » writes one slot of the selected bank (not committed to
> non-volatile storage). « Store » commits the whole bank — back the bank up first
> (e.g. « Lire banque » it, or save a .pcg from the Kronos). GM/g banks are refused.

1. Load `KronosKontrol.panel` (complet-0.97f). Console: `Kronos Kontrol : panneau
   chargé — complet-0.97f`; EDIT header shows **Lire le son**, **Appliquer → 0x4B**,
   **Écrire → 0x49**, **Store 0x4C**, **Lire banque 0x4D**.
2. PROG mode, load a program (Lire le son), select bank **U-A**, slot 000.
   « Écrire → 0x49 » → monitor `→ écriture slot U-A000 (0x49 …)`, Reply 24 OK →
   status `← slot U-A000 écrit (0x49) — « Store » (0x4C) pour enregistrer`.
   The Kronos screen still shows the old U-A000 (not committed).
3. « Store 0x4C » → button becomes **Confirmer Store ?** (5 s) → click again →
   Reply 24 OK → `← banque enregistrée`. Recall U-A000 on the Kronos: the edited
   program is there.
4. « Lire banque 0x4D » (U-A) → status counts `← banque U-A : n/128 objets` →
   `← banque U-A lue : 128 objets`; the rack shows the device names (e.g.
   `U-A000 <name>`); « Jouer > » on a slot loads it (0x4B) even with no PCG loaded.
5. Refusals: GM bank → « Écrire → » and « Store » refused (`lecture seule`);
   combi object + PROG mode → `Combi seulement`; no dump → `Lire le son`.
6. COMBI mode: same flow on a combi bank (obj 01, `4D 01 …`).
7. Regression: RACK 0.96 + E1/E2/U1/E3/E3b/E4 (§9–§14) unchanged.

| Step | Expected | Observed | OK? |
|------|----------|----------|-----|
| 1 load | console `— complet-0.97f`, 5 EDIT header buttons | | |
| 2 write slot | 0x49 to U-A000, Reply 24 OK, not yet committed | | |
| 3 store | 2 clicks, Reply 24 OK, U-A000 recalled = edited program | | |
| 4 read bank | 128 objects, device names on rack, Jouer > loads them | | |
| 5 refusals | GM refused, wrong mode refused, no dump refused | | |
| 6 combi | same flow obj 01 | | |
| 7 regression | RACK 0.96 + §9–§14 unchanged | | |

Record the outcome in `RESUME.md` (new section, corpus root) before starting E6 (0.97g).
