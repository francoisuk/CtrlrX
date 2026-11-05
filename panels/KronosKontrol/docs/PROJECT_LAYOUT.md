# Kronos Kontrol — project layout and decisions

*Rewritten 24 oct. 2026. This document is authoritative for the panel
folder: folder tree, ground-truth paths, Ctrlr source lookup order,
runtime, architecture decisions, phase state, and rules.*

> **Relocalisation du 26 oct. 2026.** Ce projet a été déplacé de
> `C:\Korg\ctrlr-project` vers `C:\Korg\kronos-corpus\ctrlr-project`
> (racine `kronos-corpus`, voir `C:\Korg\kronos-corpus\README.md`).
> Le dossier `questions/` (code C++ natif KronosMidiManager /
> KronosSysexParser) a été déplacé vers
> `C:\Korg\kronos-corpus\native\kronos-midi\`.

## 1. Goal

Build a Ctrlr panel, **Kronos Kontrol**, to control a Korg Kronos
(OS 3.2.x) from any DAW host (standalone, VST3, AU). The reference
behaviour comes from a working Max for Live device, "Kronos Kontrol
OS3.2.3", which is Ableton-only. The Ctrlr panel is the
host-agnostic replacement and reproduces the device's rack front
(1500 × 414 px design).

The panel is developed against a real Kronos connected via USB MIDI.
Every vertical slice is verified on hardware before the next one
begins.

**Current state:** the full rack is built as `KronosKontrol.panel`
(version complet-0.96, 172 modulators, 13 Lua methods; first hardware
tests reported conclusive by the author on 24 oct. 2026). On 24 oct.
2026 a full static verification of the panel (Lua vs
`parameter_map.csv` vs the device-tested `kronos_sysex.py`, wiring,
names, byte counts) found and fixed two bugs: `L()` was called by 4
callbacks but never defined (critical — no button/encoder would have
responded), and 37 CSV formula rows were one value byte short.

**Editor phase (started 24 oct. 2026):** the panel is now tabbed —
tab 0 RACK (the 0.96 rack, untouched, artwork moved to the tab
background) and tab 1 EDIT — under version **complet-0.97** (199
modulators, 14 Lua methods). Stage E1 of `EDITOR_PLAN.md` is built:
7-bit dump codec in Lua (`kkPack7`/`kkUnpack7`), Get Program Dump
button (fn 0x4A), receive of the Current Object Dump (fn 0x4B) and
display of name / version / category / scale / IFX-MFX-TFX types /
EXi engines. Static verification passed 24 oct. (99 checks under the
Lua 5.4.2 interpreter: codec vs doc `*3` formula, wire round-trips,
synthetic 0x4B decode, display offsets, 0.96 regressions). The
plan of action is `EDITOR_PLAN.md` (stages E1–E7); the fill-in
hardware test sheet for E1 is `EDITOR_PLAN.md` §9. complet-0.97 (E1)
is **built but not yet hardware-tested**. Stage E2 was added on
26 oct. 2026 (214 modulators, 20 Lua methods): editable name
(double-click, 24 chars), realtime OSC1/EXi1 + Master levels
(fn 43), local-dump patches (category/scale/IFX1) and the
`Appliquer` 0x4B write-back to the edit buffer with busy state and
Reply 24 handling. Static verification passed 26 oct. (generator
reproduces the panel byte-for-byte; 20 structural checks; 61 checks
under the Lua 5.4.2 interpreter with a mocked Ctrlr API; dump offsets
validated against the factory PRELOAD OS 3.2, 2,176 programs).
Also fixed 26 oct.: the category display masks bits 4~0 of byte
2568. E2 is **built but not yet hardware-tested**; its test sheet is
`EDITOR_PLAN.md` §10.

**complet-0.97a (26 oct. 2026, 215 modulators, 20 Lua methods):** the
build now carries its version on the panel itself — a `kkVersion`
label in the bottom-right corner of the RACK tab, `KK_VERSION` in
Lua, and the version in the console line at load. The version string
lives in one place only: `VERSION` in `sources/build_panel.py`
(letter rule: `EDITOR_PLAN.md` §5).

**complet-0.97b (26 oct. 2026, 220 modulators, 21 Lua methods):**
U0/U1 — the panel is universal. `lua/kkPcg.lua` loads any PCG at
runtime (« PCG > » opens the file, its program banks rename the rack,
« Jouer > » plays the selected program from the file into the edit
buffer via 0x4B); latin-1 ↔ UTF-8 conversion for names. Offline
companion U0: `tools/pcg-names/pcg_to_names.py` (any PCG → names
JSON, pluggable via `gen_data_lua.py --names`). Verified statically:
e2check 27 checks, Lua harness 96 checks (incl. a real PRELOAD
load), `tools/corpus-check` — 112/112 corpus PCGs match pcglib.
Hardware test sheet: `EDITOR_PLAN.md` §11.

**complet-0.97c (26 oct. 2026, 867 modulators, 25 Lua methods):**
E3 — edit pages, engine-aware. The EDIT tab gains a second-level tab
bar (`kkEdTabs`, 16 tabs: Général, Commun, OSC1/OSC2, EXi1/EXi2 Mix,
E1 engine ×8, IFX 1-12, MFX·TFX) and 324 generated controls
(`kkF_*`, one generic callback `kkEdField`; labels `kkF_*L`).
Pages are generated from the reference tables by
`scripts/gen_editor_lua.py` → `data/kronos_editor.lua` (embedded as
the `kronosEditor` method) + `sources/editor_layout.json` (layout).
Engine-aware: controls outside the current program type
(HD-1 / EXi / engine) are hidden and edits refused; the active tab
follows the program on dump receive (osc mode byte 2558 bits 0-2 ==
3 ⇔ EXi; engine byte 2857 → tab 6..13). The Général page = E1
read-only block + E2 edit controls relocated. Verified statically:
e2check 51 checks, Lua harness 169 checks (73 E3), generator
validated against the factory PRELOAD (2 176 programs, 324/324
params, 0 exclusions). Hardware test sheet: `EDITOR_PLAN.md` §12.
**complet-0.97d (26 oct. 2026, 1 027 modulators, 25 Lua methods):**
E3b v1 — E2 engine tabs + corpus validation. `kkEdTabs` grows to 24
tabs (E2 engine ×8 at 14..21 — structural mirror of E1 at base 3960,
`engine2N` apply on byte 3909; IFX 1-12 → 22, MFX·TFX → 23) and 404
generated controls. Tab selection follows e2 when e1 is unset (e1
keeps priority). The generator now validates against the combined
corpus PRELOAD + `banks_for_tests` (10 752 programs): 404/404
params, 0 exclusions, 9 engines covered on e1 and e2. Verified
statically: e2check 56 checks, Lua harness 199 checks (22 E3b
vectors + a full corpus walk through the panel's own PCG loader —
tab mapping, engine-page visibility, in-range reads, 0 anomalies).
Hardware test sheet: `EDITOR_PLAN.md` §13.
**complet-0.97e (26 oct. 2026, 4 897 modulators, 25 Lua methods):**
E4 — the editor handles Combinations (obj 01, 7 810 B, v3). Second tab
set `kkEdTabsC` (43 tabs: Général, Commun, Vector, Drum Track, IFX 1-4/5-8/9-12,
MFX·TFX, Audio In, LFO & In, Contrôleurs, Timbre 1..16 ×2) with 1 930 generated
controls `kkC_*` (`set = "combi"`) from `Combinaison.json`; Général combi page
(editable name, version, category, scale); « Lire le son » reads obj 00/01 per
mode (4A); « Appliquer » writes the received object (4B obj 00/01); cross-set
guards (`set` in `kkEdApplyOk`/`kkEdField`, mode gate `want = dumpObj == 1 -> 0`);
`kkEdTabs` ⇔ `kkEdTabsC` visibility swap on dump reception. PCG loader: CBK1
banks (7 810 B) named/slotted (`KKPCG.cnames/cslots`), « Jouer > » sends the
selected combi to the edit buffer (4B obj 01 ver 3), combi names on the rack
from the loaded PCG. Generator validates against the combi corpus (2 048 combis:
1 930/1 930 params, 0 exclusions); Program set unchanged (404 params, 0
exclusions). Verified statically: e2check 85 checks, Lua harness 254 checks
(41 E4 vectors + a full corpus walk of 2 048 combis through the panel's own
PCG loader — visibility + in-range reads, 0 anomalies). Hardware test sheet:
`EDITOR_PLAN.md` §14.
**complet-0.97f (26 oct. 2026, 4 903 modulators, 25 Lua methods):**
E5 — Store + banks. Three EDIT header buttons: « Écrire → 0x49 » writes the
local dump to the selected slot (`49 <obj> <bank> <idH> <idL> <version> <data>`,
bank byte per the SysEx doc *2 table, GM/g refused), « Store 0x4C » commits the
bank (2-click confirm, 5 s arm), « Lire banque 0x4D » reads a bank from the
Kronos (series of 128 `73` dumps) into `KKPCG.dnames/ditems/devbanks` —
device banks take priority over PCG/factory names on the rack and are playable
via « Jouer > » (0x4B) even with no PCG loaded. Program + Combi v1 (kits/WSQ v2,
Global never stored). Guards: busy/wslot, mode = dump object, known panel bank;
`kkClick` prefix guard `tonumber` on `kkBtnBank` (kkBtnBankRead trap fixed +
e2check regression). Verified statically: e2check 114 checks, Lua harness 293
checks (39 E5 vectors: 0x49 write round-trip + GM refusal, 0x4C 2-click + disarm,
0x4D full 128-object bank reads for Program U-A and Combi I-A, device-bank
« Jouer > » with no PCG, timer 4 timeout). Hardware test sheet: `EDITOR_PLAN.md` §15.


## 2. Tree (root: C:\Korg\kronos-corpus\ctrlr-project)

- /build       Ctrlr framework: runtime + source trees (reference only)
  - Ctrlr-x64_VST3_v5.6.23/Ctrlr-x64.vst3   the runtime (bare DLL)
  - CtrlrX-dnaldoog/                       primary API reference
  - CtrlrX-damiensellier/                  secondary API reference
  - ctrlr-master/                          upstream baseline
- /reference   Kronos/Oasys/Nautilus knowledge base (READ ONLY,
               authoritative). Harvested 24 oct. 2026 from the pcglib
               project (v1.6.3) and the earlier ableton/vst3 projects.
  - README.md, CONSOLIDATE_README.md        essential reading first
  - ref-kronos/                             tables, docs, m4l ground truth
  - ref-oasys/, ref-nautilus/               same shape, for later panels
- /check       REMOVED by the maintainer on 2026-10-24, after the harvest
               was verified byte-identical. The originals of the two
               previous projects (ableton, vst3) remain at
               C:\Korg\Manuals Le grand livre du KRONOS\04_Outils\
               produits-inclus\{ableton,vst3}
- /consolidate/old  legacy tool collection (superseded by /reference;
               the author will delete it; do not add anything here)
- /tables      copy of the 27 pcglib Kronos parameter tables
- /docs        Korg manuals + consolidated knowledge document
- /GUI_pic     rack artwork (SVG + PNG, final and working copies)
- /panels      Ctrlr panels
  - /TR-Rack-Editor-main/   existing working example (READ ONLY)
  - /KronosKontrol/         THIS project — all new work goes here
- /scripts     helper scripts: data generation, SysEx library, readers
- PROJECT_ACTION_PLAN.md                strategy, status, phases
- ds_new.md, TOOLS_CONSOLIDATION_INDEX.md, prompt_new_session.txt,
  phase_A_prompt.md, korg_kronos_ctrlr_panel_readme.md,
  docling_commands.md                      session prompts and indexes

## 3. Ground truth (working M4L device + hardware tests)

The Max for Live device already sends correct SysEx and CC. Its build
scripts and base patch JSON contain the exact byte formulas. These
files are the source of truth — do not re-derive SysEx from the MIDI
Implementation guide. Where a formula was never validated on hardware,
the hardware test notes say so.

- reference/ref-kronos/m4l/base/kronos_kontrol_v1.json
    base patch; contains every sxformat string (mode, GE, FX, Drum Track)
- reference/ref-kronos/m4l/base/conteneur.json, M3Router.maxpat,
  rack_fond.png, karmalogo.png
    container and artwork of the device build
- reference/ref-kronos/m4l/names.json
    4,233 factory names indexed by internal program index
- reference/ref-kronos/m4l/ge_kronos.json
    3,584 KARMA GE names (preset 0–2047, userA 0–95)
- reference/ref-kronos/m4l/docs_dev/REPRISE.md
    device test log, 16 oct. 2026: what was verified on the Kronos and
    what was not (KARMA CCs, GE, Drum Track On were NOT verified in
    the device)
- reference/ref-kronos/m4l/LISEZMOI.txt
    provenance and build notes of the device
- reference/ref-kronos/docs/SYSEX_KRONOS.md
    SysEx reference, hardware-verified 16 oct. 2026. Where this
    document and `KRONOS_SYSEX_PARAMETER_CONTROL.md` disagree,
    SYSEX_KRONOS.md wins.

## 4. Kronos reference tables

Used to decode sxformat fields and to fill the parameter map CSV.

- reference/ref-kronos/midi/*.txt       Korg text tables, bit-level
  (KRONOS_MIDI_SysEx.txt, Prog_HD-1.txt, Prog_EXi.txt,
  Prog_EXi_Common.txt, CombiAndSongTimbreSet.txt, Effect.txt,
  Global.txt, WaveSequence.txt, … plus SysExParams/ and VoiceModels/)
- reference/ref-kronos/tables/*.csv|json  same content as CSV/JSON
- reference/ref-kronos/docs/SYSEX_KRONOS.md
  hardware-verified SysEx parameter control (T/D states per function)
- reference/ref-kronos/KRONOS_TABLES_GUIDE.md
  how to read the three table shapes
- reference/ref-kronos/KRONOS_SYSEX_PARAMETER_CONTROL.md
  fn 43/44 grammar, address collisions, CC layer, Korg bank map,
  worked examples — synthesised from pcglib + hardware tests
- docs/CONNAISSANCES_KRONOS_PCG.md    consolidated knowledge (French)

The bit-level tables carry TYP/SOC/SUB/PID/IDX, bit widths, Min/Max.
They do NOT carry a transmit/receive flag, and they do NOT carry the
hardware-verified corrections (FX switch inversion, GE via fn 6D,
Drum Track On via fn 6E, address collisions). Those live in
SYSEX_KRONOS.md, `REPRISE.md` (panel tests), and the CSV `Tested`
column:

- **yes** — hardware-verified (device 16 oct. 2026, CC74 on OS 3.2.3
  12 oct., or panel test 16 oct. 17 h 27 / 18 h 30)
- **doc** — from the Korg tables / SYSEX_KRONOS.md, not yet tested
- **inherited** — taken from the M4L device or its prose, never
  validated on hardware
- **no** — the shipped form was tested and failed; the corrected form
  is prepared in complet-0.96 but untested

## 5. Ctrlr Lua API — order of lookup

1. build/CtrlrX-dnaldoog/        primary
2. build/CtrlrX-damiensellier/   secondary
3. build/ctrlr-master/           upstream baseline

Do not guess a Lua method name. If it is not found in any of the three
source trees, say so and stop. Do not invent.

## 6. Ctrlr runtime

- The runtime is a single VST3 **file**:
  `build/Ctrlr-x64_VST3_v5.6.23/Ctrlr-x64.vst3` — a bare PE32+ DLL
  (32,388,608 bytes), not a bundle folder. The host loads the file
  directly.
- Primary test host: SAVIHost3, configured with
    MIDI Input  = Kronos USB MIDI port
    MIDI Output = Kronos USB MIDI port   (critical for SysEx out)
- Secondary host for cross-checking: Ableton Live 12.
- No standalone .exe is present. A matching standalone is optional and
  not required for the project.
- Do not rebuild Ctrlr. Do not compile from source. The three source
  trees in /build are for reading only.
- The panel is `panels/KronosKontrol/KronosKontrol.panel` — an XML
  file. Open it in Ctrlr via **File › Open**. It is generated by
  `panels/KronosKontrol/sources/build_panel.py`; edit the sources and
  rebuild, never the XML by hand. SAVIHost does not persist panel
  state.
- Sanity check passed: one Ctrlr slider sending CC74 through SAVIHost
  to the Kronos moves the filter cutoff in real time (verified again
  on OS 3.2.3, 12 oct. 2026).

## 7. The TR-Rack panel

- `panels/TR-Rack-Editor-main/` holds the working example: a
  compressed panel `Tr Rack Editor.bpanelz` plus its exported VST3.
  READ ONLY.
- It is the canonical example of Ctrlr XML, Lua, MIDI I/O, and SysEx
  in this project. Its idioms were extracted on 16 oct. 2026:
  - `ETUDE_TR-Rack.md` — the raw extraction (callbacks, send, receive,
    no-resend update, labels, timers, background image, resources)
  - `CTRLR_IDIOMS.md` — the verified idioms, cross-checked against the
    three source trees. **This is the file to consult when writing
    panel Lua.**
- `scripts/vt2xml.py` reads `.bpanelz` files (zlib + JUCE binary
  ValueTree → XML) if TR-Rack needs to be re-read.

## 8. Architecture decisions (locked)

These are the choices that keep the panel maintainable. Change them
only with a concrete reason.

### 8.1 Modulators vs Lua

- Modulators for: any single MIDI message whose value is a simple
  linear function of the UI value. Most CC controls are handled by Lua
  in this panel anyway (see `lua/kkMain.lua`), because the send goes
  through the mode-aware queue (8.6).
- Lua for: SysEx, multi-message sequences (Bank MSB → LSB → PC), value
  scaling beyond linear, mode-dependent messages, feedback parsing,
  anything with `if` / `table` / loops.
- Rule of thumb: if you reach for `if`, it is Lua.

### 8.2 Feedback policy

**Finding (2025).** The Kronos documentation does not publish a
per-parameter Transmit/Receive/Both table. The MIDI Applications
chapter states, per controller group, in prose: "This message will be
transmitted when the controller is operated. When this message is
received, the result will be the same as when the controller is
operated." That sentence pattern applies to every CC group the panel
uses, and it says **both** in every instance. The SysEx specification
(KRONOS_MIDI_SysEx.txt) gives function-level Receive/Transmit only.

**Consequence.** The parameter_map.csv `Feedback` column is
class-level, not per-parameter: `both` for CC rows (sourced to prose),
`unknown` for SysEx rows other than Mode Change.

**What "bidirectional" does and does not mean.** That the Kronos *can*
send a message does not mean it *does* send it in the configuration the
panel runs in. Whether a hardware edit actually arrives at the panel's
MIDI port depends on runtime configuration on the device:

- `Enable Control Change` (Global 1-1c) — master on/off for CC send.
- `Enable Exclusive` (Global 1-1c) — master on/off for SysEx send.
- Per-timbre `MIDI Filter` (Combination P3) — enable/disable CC send
  per timbre.
- Per-track `MIDI Filter` (Sequencer P3) — same, per track.
- The `MIDI Channel` of the timbre/track vs. the global channel.
- Whether the front-panel control is routed to a MIDI CC at all in the
  current Program.

None of that is in the parameter map, and none of it can be. It is
runtime state on the device.

**Policy.** The panel treats feedback as **discovered, not specified**.
What the hardware does is recorded in `REPRISE.md`, per control, based
on the panel tests. The `Feedback` column in the CSV records what the
documentation says; it is not the source of truth for panel behaviour.

- The panel is event-driven: it listens for incoming SysEx and CC and
  updates its UI when it sees a known parameter change. No polling.
- Send-only for any control the tests show does not echo, documented in
  `REPRISE.md` with the configuration under which the test was made.

### 8.3 No-resend update (anti-loop)

- Verified in the Ctrlr sources: `setValue(v, false)` on a modulator
  component updates the UI **without sending MIDI and without calling
  the value-change callback** (`CtrlrSlider::setComponentValue`).
- The guard-flag pattern (a panel-level table checked inside the
  callback) is therefore **obsolete** in this panel. Do not re-add it.
- See `CTRLR_IDIOMS.md` §"no-resend update".

### 8.4 Static data loading

- names.json and ge_kronos.json are merged into one Lua module:
  `panels/KronosKontrol/data/kronos_data.lua`, generated by
  `scripts/gen_data_lua.py` from `reference/ref-kronos/m4l/names.json`
  and `reference/ref-kronos/m4l/ge_kronos.json`.
- The module returns a single table:
    { names = { [index] = "..." }, ge = { [0..3583] = "..." } }
- `sources/build_panel.py` embeds it into the panel as the Lua method
  `kronosData` (assigned to the global `KRONOS_DATA`); at runtime
  `kkInit` loads it. **There is no dofile and no file I/O at runtime.**
- No HTTP. No external dependencies.
- Names reflect factory PRELOAD 3.2. User-loaded PCGs will display
  wrong names. Documented limitation.
- The Kronos does not expose program names as editable SysEx
  parameters. Names are static data only.
- Combi names for banks I-G are not in names.json; the panel displays
  "121.0 nnn" for them (known limitation, noted in REPRISE.md).

### 8.5 Scope of the built panel (complet-0.96)

Included and built:

- Bank select (CC0/CC32/PC, Korg bank map, MSB before LSB, then PC),
  U-A/AA toggle, GM menu (GM, g(1)…g(9), g(d)), name display
- Program / Combi mode change (SysEx fn 4E) + real-mode memory
  (the panel sends 4E first when the Kronos is in Global/Disk/Seq/Set
  List mode, queues the pending messages, 400 ms timer fallback)
- 16 left encoders (CC 74/71/79/72, 17/19/20/21, 76/77/16/5,
  73/75/70/72) with OLED name bands
- SW1/SW2 (CC 80/81), FX switches IFX1–12/MFX1–2/TFX1–2 (fn 43 TYP 6
  Program / TYP 23 Combi, **inverted**: 0 = On)
- X-Y pad (CC 118/119) + HOLD
- MIXER / PAN: 8 bottom encoders — Combi: timbre 1–8 volume (TYP 4
  SOC n-1 PID 2) / pan (PID 1); Program: OSC1/OSC2 Patch Level
  (HD-1 TYP 9/10 + EXi TYP 11/12, SOC 3, PID 6; pan PID 3), Drum
  Track volume (TYP 0 PID 39), Master (TYP 7 PID 12)
- KARMA: switches 1–8 (CC 102–109), On/Off (CC 14), Latch (CC 31),
  Scenes 1–8 (CC 30, value 0–7), sliders 1–8 (CC 22–29), GE menu
  (3,584 entries + category menu), Module Control (Master/A–D),
  GE select via **fn 6D** in Program (fn 43 TYP 3 + 6D retry in Combi)
- Drum Track: On/Off via **fn 6E** in Program (fn 43 TYP 1 + 6E retry
  in Combi), Mute via fn 43 PID 40 (Program only), volume via MIXER
- Event-driven feedback: decodes CC, PC, fn 42/4E/24/43/6D/6E and
  mirrors hardware edits in the UI; on-panel monitor shows last
  sent (→) / received (←) message and Reply 24 codes in plain text

Not yet done (after complet-0.96 is hardware-verified):

- Reading the full state of the Kronos at panel load
- VST3 export of the panel instance + test in Live 12
- User manual (FR/EN/ES) for the panel

### 8.6 Mode-aware send queue

- All SysEx/CC sends from Lua go through `kkSendM` in
  `lua/kkMain.lua`: if the panel's view of the Kronos mode (tracked
  from incoming fn 42/4E) is not the mode the message targets, the
  panel first sends fn 4E to switch, queues the message, and flushes
  the queue on Reply 24 code 0 or on receipt of 4E. A 400 ms timer is
  the fallback. This fixed the Global/Disk/Seq failure of complet-0.95.

## 9. Rules for AI assistance

1. SysEx ground truth is the M4L base patch
   (`reference/ref-kronos/m4l/base/kronos_kontrol_v1.json`) plus its
   fix scripts, corrected by the hardware test notes
   (`reference/ref-kronos/m4l/docs_dev/REPRISE.md`, panel
   `REPRISE.md`, `reference/ref-kronos/docs/SYSEX_KRONOS.md`). Do not
   re-derive from the MIDI Implementation guide unless explicitly
   asked. Where the synthesis docs and SYSEX_KRONOS.md disagree,
   SYSEX_KRONOS.md wins.

2. Static data comes from `reference/ref-kronos/m4l/*.json`,
   transformed into Lua under `panels/KronosKontrol/data/` by scripts
   in /scripts. Do not hand-edit the generated Lua.

3. Every Ctrlr Lua method used must be verified against one of the
   three source trees in /build (see `CTRLR_IDIOMS.md`). If not found,
   say so; do not invent.

4. Build one vertical slice at a time. Test each slice on hardware
   before expanding.

5. The parameter map CSV is the spec. Every Modulator and Lua
   function traces back to it. The CSV's `Tested` column records
   hardware-verification state (see §4 legend).

6. All new work goes under panels/KronosKontrol/. Do not modify
   /build, /reference, /docs, /GUI_pic, or /panels/TR-Rack-Editor-main.
   /consolidate is legacy (the author will delete it); /check was
   removed on 2026-10-24 — do not recreate or edit either.

7. The panel file is `KronosKontrol.panel` (XML), generated by
   `sources/build_panel.py`. Never edit the XML by hand. Rebuild and
   re-test instead.

8. Do not fill the `Feedback` column from memory or convention.
   Class-level values sourced to prose are acceptable. Where the
   source is silent, the value is `unknown`, and the reason is
   recorded in the `Source` column.

9. Never send a Write/Store to the Kronos. The panel only changes the
   current edit buffer.

## 10. Phase state (24 oct. 2026)

### Phase A — Parameter map — DONE

- parameter_map.csv: **124 rows** (was 78), every SysEx ParamID
  verified against the bit-level tables, FX switches corrected to
  inverted 1-bit, GE corrected to fn 6D (Program) 12-bit value,
  Drum Track On corrected to fn 6E, full MIXER/PAN/Module Control/
  IFX6-12/TFX2 coverage, `Tested` legend per §4.
  Amended 24 oct. 2026 — see `PHASE_A.md`.

### Phase B — Static data — DONE

- `scripts/gen_data_lua.py` → `data/kronos_data.lua` (275,217 B;
  names = 4,233, ge = 3,584). Repointed 24 oct. 2026 at
  `reference/ref-kronos/m4l/` and regenerated (data identical, only
  the source-path header comments changed).

### Phase C — Panel build and hardware tests — IN PROGRESS

- complet-0.9 → complet-0.95: full rack built and tested 16 oct.
  2026 (17 h 27 and 18 h 30). Working: 16 encoders, program select,
  X-Y, MIXER, Module Control. Fixed in complet-0.96 (18 oct.): mode
  memory + 4E-first queueing + timer; GE via fn 6D; Drum Track On via
  fn 6E; Combi Drum Track On TYP 1; Reply 24 display; 6D/6E receive
  decoding.
- complet-0.96: **hardware-tested** (first tests reported conclusive
  by the author, 24 oct. 2026). Build of 24 oct. 2026: static
  verification complete (22/22 message builders byte-identical to the
  device-tested `kronos_sysex.py`; wiring, names and byte counts
  checked), two bugs fixed — `L()` undefined (critical) in
  `kkMain.lua`, 37 short formula rows in `parameter_map.csv` (value
  byte `00 <val>` → `00 00 <val>`). Test sheet: `TEST_PLAN_0.96.md`.
- complet-0.97 (editor, stage E1): **built 24 oct., static
  verification passed, not yet hardware-tested.** Adds the RACK/EDIT
  tabs (`kkTabs`, bar hidden, rack artwork as tab 0 background), the
  `EDIT →` / `← RACK` buttons, the 7-bit codec, the fn 0x4A/0x4B
  read path and the EDIT page display; `kronos_data.lua` extended
  with fx/engines/cats/scales tables. Plan: `EDITOR_PLAN.md`;
  hardware test sheet: `EDITOR_PLAN.md` §9.
- Full test log: `REPRISE.md`.

### Phase D — Packaging — NOT STARTED

- VST3 export of the panel instance, test in Live 12, user manual
  FR/EN/ES, distribution notes.

## 11. Risks

| Risk | Mitigation |
|---|---|
| Ctrlr fragmentation (dnaldoog vs damiensellier) | Pin to v5.6.23 binary; sources are reference only; idioms verified in CTRLR_IDIOMS.md |
| Hardware edits do not echo to the panel's MIDI port | Feedback is discovered per control in the panel tests; send-only controls documented in REPRISE.md |
| KARMA CCs are Off by default on the Kronos | GLOBAL › Reset Controller MIDI Assign › CC Default, then Write Global Setting; reminded in REPRISE.md and the panel test plan |
| fn 43 address collisions (GE, Drum Track On) | GE via fn 6D, Drum Track On via fn 6E (Program); Combi retries in 6D/6E on Reply 24 code ≠ 0; tested in complet-0.96 |
| Tests may have modified LFO Waveform / Scale Type of the current Program (edit buffer) | Do NOT Write; reload the Program (change away and back) — noted in REPRISE.md |
| Per-parameter T/R/B table does not exist in Korg docs | Accepted. Feedback is class-level, sourced to prose; per-control behaviour is empirical (REPRISE.md) |
| names.json reflects factory PRELOAD, not user PCG | Documented limitation |
| Combi names for banks I-G missing from names.json | Panel displays "121.0 nnn"; documented in REPRISE.md |
| Scope creep (the M4L device is large) | The full rack is the scope; state read at load, VST3 export, and manuals are Phase D |
| SAVIHost does not persist panel state | Panel is a .panel file opened via Ctrlr File › Open |
| Two Lua versions getting mixed (happened 16 oct.) | One author at a time on lua/kkMain.lua and sources/build_panel.py; rebuild from sources, never edit the XML |

## 12. Success criteria

A single `KronosKontrol.panel` (and later its VST3 export) that:

- Loads in Ctrlr VST3 under SAVIHost and Ableton Live
- Reproduces the M4L rack: banks, program/combi, 16 encoders, FX
  switches, X-Y, MIXER/PAN, KARMA, Drum Track
- Selects Program and Bank with correct name display
- Switches Program/Combi mode via SysEx, from any Kronos mode
- Reflects hardware edits on the Kronos, for those controls where the
  panel tests observe an echo in the test configuration
- Includes an on-panel SysEx / CC monitor (last sent / received,
  Reply 24 codes in plain text)
- Passes the complet-0.96 hardware test plan (§13) without regression
  of what complet-0.95 already did

## 13. Immediate next actions — hardware tests of complet-0.97e (§9 E1 → §10 E2 → §11 U1 → §12 E3 → §13 E3b → §14 E4)

The complet-0.96 rack is assumed working (author's first tests
conclusive); its checklist below stays as a regression reference.
The current gate is the hardware test of the current build
(complet-0.97e) — `EDITOR_PLAN.md` §9 (E1), then §10, §11, §12, §13, §14:

1. Load `KronosKontrol.panel` (complet-0.97). Console:
   `Kronos Kontrol : panneau chargé` + `KRONOS mode X …`; the rack
   (tab 0) must look and behave exactly as in 0.96.
2. `EDIT →` → EDIT page (dark); `← RACK` → back, rack pixel-identical.
3. On the Kronos select a known EXi program; on EDIT click
   **Lire le programme** → status `→ requête dump objet 0 …`, then
   monitor `← dump obj=00 ver=5 4960 octets`; name must match the
   Kronos screen; category / scale / IFX 1-12 / MFX / TFX / EXi 1-2
   shown.
4. Cross-check one value against the Kronos front panel.
5. Same with an HD-1 program (common fields valid; engine bytes not
   meaningful — known E1 limitation).
6. Rack regression: encoders / banks / FX / mixer unchanged (0.96).

Record the outcome in `REPRISE.md` (new section). Then the E2 test
(`EDITOR_PLAN.md` §10), then the U1 test (§11 — PCG loader), then
the E3 test (§12), then the E3b test (§13), then the E4 test (§14 —
Combi editor). The next build after that is E5 — complet-0.97f
(`EDITOR_PLAN.md` §5): Store + banks (0x49 Object Dump to a slot,
0x4C Store Bank, 0x4D Dump Bank Request), then E6 — complet-0.97g
(Drum Kit / Wave Seq / Global pages), delivery 0.98a. E3b v2 items
(KARMA, Drum Track, Vector/Step Seq, Tone Adjust, EXi Common,
engine-selector byte, fn 43): 0.97h if credits remain, else
post-0.98a.

Regression reference (complet-0.96, from `REPRISE.md` "Test à faire
(auteur)"), on the Kronos:

1. Kronos in GLOBAL mode; click U-A in the panel → does it switch to
   PROGRAM mode and land on U-A000? Same from SEQUENCER and DISK.
2. PROG mode; GE ▲ → does the GE change (KARMA screen)? Note the
   grey display (Reply 24?).
3. PROG mode; DRUM TRACK ON, then MUTE.
4. COMBI mode; GE ▲ (module A) and DRUM TRACK ON; note the Lua
   console ("43 refusé : essai …"?).
5. After GLOBAL › Reset Controller MIDI Assign › CC Default (then
   Write Global Setting): KARMA ON/OFF, SWITCH 1, SCENE 2, SLIDER 1.

The fill-in version of the 0.96 list is `TEST_PLAN_0.96.md`. After
E1 passes on hardware, run the E2 test (`EDITOR_PLAN.md` §10); Phase
D (VST3 export, manuals) waits for the editor stages to settle.

## 14. What this document is not

- Not the strategy or phase status: that is PROJECT_ACTION_PLAN.md.
- Not the phase A detail: that is PHASE_A.md.
- Not the hardware test log: that is REPRISE.md.
- Not the Ctrlr idioms reference: that is CTRLR_IDIOMS.md.
- Not a session prompt: those are prompt_new_session.txt,
  phase_A_prompt.md, PROMPT_NOUVELLE_SESSION_CTRLR.md,
  PROMPT_REPRISE_LUNDI.md.
- Not the folder-level readmes: those are in each folder.

---

*Phase A and B are done, the full rack is built (complet-0.96), and
0.95 was hardware-tested on 16 oct. 2026. The next step is the
hardware test of complet-0.96 (§13), then Phase D packaging.*
