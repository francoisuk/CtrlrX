# Does the current Kronos Kontrol work benefit from CtrlrX PR #337?

*Analysis of 4 Nov 2026, read-only: no file of the project was modified. The PR
branch is available locally as `build/CtrlrX-pr337/` (clean export of PR head
`62d612112b185cdfff3f7a8ef68000d332fe85cb`), see `build/PR337_README.md`.*

## TL;DR

**Yes — the panel probe (`CtrlrPanelProbe`) is directly useful; the AI-agent
skill is not.** PR #337 changes nothing in `Source/`, so the branch cannot break
the panel, and the two upstream bugs its author found do not touch us (verified
below). The probe closes exactly the verification gap this project keeps hitting:
"the panel loads fine but behaves wrong", which today can only be caught by a
human clicking in front of a real KRONOS, or late, at export time. The skill
(`skills/ctrlrx-panel-builder`) targets a hand-edit-the-`.panel` workflow that
this project deliberately does not use (the panel is *generated* by
`sources/build_panel.py`); at most its eval tasks are a source of test ideas.

---

## 1. What PR #337 actually contains

PR [damiensellier/CtrlrX#337](https://github.com/damiensellier/CtrlrX/pull/337)
"Panel probe and AI agent skill" (sgorpi, branch `panel-probe-and-skill`, base
`5.6.37-Maintenance` @ `49497f7`): **80 files, +9828/−12, all outside `Source/`**
(verified against the file list):

| Part | Files | What it is |
|---|---|---|
| Probe | `Tests/probe_Main.cpp` (2068 l.), `probe_Report.{cpp,h}`, `probe_selftest.py` (34 scenarios), `probe_*.json`, `png_sample.py`, 9 × `fixture_probe_*.panel`, `Tests/CMakeLists.txt` (+53 lines, pure addition) | `CtrlrPanelProbe`: a headless executable that loads a real `.panel` in the **real CtrlrX engine** with MIDI rebound to the existing mock test devices, runs a JSON script, prints a JSON report, exits 0/1/2 for CI. |
| Probe docs | `Doc/PanelProbe.md` (770 l.), small additions to `Doc/manual/09-debugging.md`, `10-distribution.md`, `readme/04-compiling.md` | Full script/report reference. |
| CI | `.github/workflows/build_and_test.yml` | Zips a Release probe per OS as artifact `CtrlrPanelProbe-<OS>`; optional signing. A **prebuilt Windows binary can be downloaded** from the PR's CI run without any build environment. |
| Skill | `skills/README.md`, `skills/ctrlrx-panel-builder/` (`SKILL.md`, `MAINTAINING.md`, `assets/template-panel.panel`, `evals/` with 18 graded tasks + sample panels) | An Agent Skills (agentskills.io) package for coding agents: build/fix panels by editing the `.panel`, then verify with the probe. |
| Fixtures | 9 × `fixture_lua_*.panel` | Same change as #336 (Lua moved out of `Built-In` group); merge-conflict-free with #336. |

Probe actions (`Doc/PanelProbe.md` §Actions): `setValue` (via the real GUI path
`setComponentValue` → `changedByGUI`, so MIDI **and** `luaModulatorValueChange`
fire), `click`, `injectDeviceMidi` / `injectHostMidi` (as if from the synth),
`callLuaMethod`, `eval` (in the panel's own Lua state), `waitFor`, `wait`,
`screenshot` (full canvas PNG), `paint` (one component), `mouse` (down/drag/up/
click/doubleClick/wheel at coordinates on `uiCustomComponent`), `setLayerVisible`.
It reports, it does not assert — the caller judges the report. Modal dialogs are
auto-answered (Cancel) and reported, so scripts never hang.

## 2. How this project verifies the panel today

From `PROJECT_LAYOUT.md`, `CTRLRX_MIGRATION.md`, `docs_editor/EDITOR_V1_POSTMORTEM.md`,
the `REPRISE_CODAGE_*.md` journals and `BUILD_EXPORT.md`:

1. **Static XML checks** (historical `tools/panel-harness/e2check.py`, up to 2488
   checks): names, rectangles, callbacks, resource hashes, combo contents. Found
   real bugs (e.g. `L()` called but never defined — would have left every button
   dead). But per the postmortem: *"an XML file can be perfect and still not paint"*.
2. **Lua harness** (historical `smoke.lua`): panel Lua run under **Lua 5.4** against
   a **mocked Ctrlr API that accepts every call**. Caught the edit-offset bug
   (`kkEdWriteField` writing at the wrong offset) and the `local function` chunk-
   scoping bug. But it *"cannot see pixels; it never complains about a missing
   component, because the fake returns one for any name"* (postmortem), and it is
   Lua 5.4, not the real LuaJIT 2.1 of CtrlrX 5.6.36.
3. **Python render model** (`rendermodel.py`): a model of what the code *should*
   do, not what the binary does.
4. **Graphics checker** (`graphics/KRONOS_Editor/sources_Editor/kcheck.py`): label
   overlaps on the 215 editor pages (82 defects → 0).
5. **Cross-checks against oracles**: `scripts/kronos_sysex.py` (SysEx/MIDI byte
   library, hardware-tested against the real KRONOS), `parameter_map.csv`
   (124 rows, "Tested" legend), pcglib (`tools/corpus-check`: 112/112 corpus PCGs),
   factory PRELOAD decode offsets (2176 programs).
6. **Hardware test sheets, manual, in front of the KRONOS** (`TEST_PLAN_0.96.md`,
   `EDITOR_PLAN.md` §9–11): GLOBAL preconditions, load, console output, then
   click-by-click on the panel with the synth connected via USB MIDI.
7. **Export-time visual checks** in CtrlrX standalone / REAPER — where the
   project got bitten late: the `.delete_me_to_reload_resources` marker trap
   ("Invalid Resource", black background, misaligned click areas — actually a
   *component-position vs stale-background* problem), the +24 px export rule,
   missing encoders in exports, faders stopping one tick short.

Runtime: **CtrlrX 5.6.36** installed (`C:\Program Files\CtrlrX Project\CtrlrX\CtrlrX.exe`)
with the source clone pinned at tag `v5.6.36` in `build/CtrlrX-damiensellier/CtrlrX/`
(see `CTRLRX_MIGRATION.md`). Panel: `panels/KronosKontrol/KronosKontrol_1.0h.panel`
(~30 MB, generated), Lua in `lua/kk{Main,Ed,EdGui,Pcg}.lua`, generator
`sources/build_panel.py`, version 1.0h (4 Nov 2026).

## 3. Does the PR branch affect the panel itself? (risks)

- **No `Source/` changes** in the 80 files → the engine the panel runs on is
  untouched by the branch. Nothing to port, nothing to re-verify because of the
  branch.
- **Bug found by the PR author #1 — short multi-list form
  (`CC,99,2 : CC,98,44 : …`) ignores its numbers since the 5.6.35 parser rewrite.**
  Checked the actual generated panel: `KronosKontrol_1.0h.panel` contains **0**
  short-form multi-list entries (regex over all `CC/NRPN/RPN/PC/SYSEX,n,n : …`
  patterns). The templates (`sources/ctrlr_templates.json`) use single-assignment
  forms only. → **Not affected.** (Long form works.)
- **Bug found by the PR author #2 — a panel saved in edit mode loads half in edit
  mode, half in run mode.** The project saves with `uiPanelEditMode="0"` and
  exports with `uiPanelMenuBarHideOnExport="1"` (verified in the 1.0h panel) →
  **not affected**, as long as nobody saves the panel in edit mode. Worth a rule
  in the build docs: always save in run mode before export.
- The probe target itself builds against our pinned source: `v5.6.36` already has
  `add_subdirectory(Tests)` and `TestsProcessor` + `mock_MidiDevice*.cpp` in
  `Tests/`; the PR's `Tests/CMakeLists.txt` change is **+53/−0, a pure addition**
  of the `CtrlrPanelProbe` target → applies cleanly onto `v5.6.36`
  (`git diff v5.6.36 pr337-… -- Tests/CMakeLists.txt` = 53 insertions, 0 deletions).
  The 9 fixture changes from #336 are independent (PR says conflict-free).

## 4. Where the probe helps this project (why / what / how)

### 4.1 Why: the gap it closes

Every serious bug in the journals belongs to the class *"loads fine, behaves
wrong"*: dead buttons (`L()` undefined), wrong-byte writes (edit offset), click
areas not matching the artwork, faders short at both ends, encoders missing in
exported instances, "Invalid Resource" from a stale resource cache, Lua errors
swallowed by pcall. Today those are found either by static checks that cannot see
behaviour, by a Lua 5.4 mock that cannot see the real engine, or by a human in
front of the KRONOS. The probe runs the **real engine** (real component tree,
real LuaJIT, real paint, real MIDI paths, mock only for the MIDI ports and the
display) — exactly the missing layer. It also runs **without the KRONOS and
without a window**, so it can run on every generator run, in CI, on any machine.

### 4.2 What: concrete use cases mapped to this project's oracles

The probe only reports; the project already has the judges. Pair them:

1. **MIDI-out byte regression, offline, for every modulator.** `setValue` /
   `click` on each rack/editor control → read `steps[].deviceMidiOut` → compare
   byte-for-byte with `scripts/kronos_sysex.py` (`param_change(...)` etc.,
   already hardware-validated). Today the byte level is only checked by hand on
   hardware for the "Tested" rows of `parameter_map.csv`; the probe can sweep
   all 172+ modulators of 1.0h in one `--stdin` batch and diff against the oracle.
   This also directly tests the **LuaJIT migration risks** listed in
   `CTRLRX_MIGRATION.md` (`getValue()` now float → `getValueInt()` where values
   become SysEx bytes; MSB 0x7F vs 0xFF; string length in chars vs bytes).
2. **Real LuaJIT execution of the panel Lua.** `callLuaMethod` / `eval` run in
   the panel's own `lua_State` under the real LuaJIT 2.1 — unlike `smoke.lua`
   (Lua 5.4, mocked API). The UTF-8/Latin-1 issue with `kkU` (`kkEdGui.lua:17-20`)
   and the `lua_pushlstring` char-vs-byte truncation can be probed for real:
   `eval` a chunk that reads a name and returns its bytes; compare with the
   expected Latin-1. The probe also reports `console()` output and Lua errors,
   including in timer callbacks (timer 8 is part of the 1.0h start-up fix).
3. **Incoming SysEx → panel state.** `injectDeviceMidi` with a real Current
   Object Dump (factory PRELOAD, or any of the 112 corpus PCGs via pcglib) →
   read back `finalState.modulators` and the kkUnpack7/0x4B decode results via
   `eval`. This replaces part of what the hardware sheet does for E1/E2
   (dump receive, display offsets) with an automated check.
4. **Paint and click-areas.** `screenshot` of the RACK tab and the EDIT pages →
   pixel-diff against `panels/KronosKontrol/mockup/` artwork; `paint` each
   `uiCustomComponent` (the rack knobs/faders are custom-painted) ; `mouse`
   click/drag at component coordinates → verifies hit areas against the artwork,
   the exact class of the 1.0b "clicks not on the buttons" bug, headlessly.
5. **Load-time behaviour.** No-script run = load + snapshot: catches load-time
   Lua errors, dialogs (`panel.dialogs`), `savedEditMode` vs `editMode` — a
   guard for the edit-mode bug above and for export surprises. `--edit-mode-as-saved`
   shows what an export would see.
6. **CI regression suite.** Exit codes (0 clean / 1 errors / 2 won't load) +
   `--stdin` batch mode fit a pipeline: `build_panel.py` → probe suite →
   oracle diff. The project has no CI today; the probe makes one cheap.

### 4.3 How: adoption steps

1. **Get the binary.** Prefer building against our pinned engine: copy the PR's
   `Tests/probe_*` files + the +53-line `Tests/CMakeLists.txt` addition onto
   `build/CtrlrX-damiensellier/CtrlrX` at `v5.6.36`, then
   `cmake --build build --target CtrlrPanelProbe` (the mock MIDI layer already
   exists there). Alternatively download `CtrlrPanelProbe-Windows` from the PR's
   CI run (sgorpi fork, run 41172747259) for a quick evaluation — but that
   binary embeds the 5.6.37-base engine, so treat it as a trial only.
2. **Mind the integrity label**: `C:\Korg\kronos-corpus` used to carry a Low
   integrity label (see `BUILD_EXPORT.md` Trap 2): an .exe under the tree cannot
   write `%APPDATA%`. Copy the probe (and a copy of the `.panel`) to a temp dir
   outside the tree and run it there, as done for the pcglib renders. (Label was
   reset to Medium on 4 Nov; re-check with `C:\Korg\Reset_Integrity_Label.ps1 -CheckOnly`.)
3. **Write a thin assertor** (Python, like the PR's own `probe_selftest.py`):
   run probe → load JSON report → compare `deviceMidiOut` with
   `kronos_sysex.py` bytes, compare `finalState` with expectations from
   `parameter_map.csv`, fail with exit code. Start with the rack's 5 buttons +
   a few encoders (the 1.0h MIXER/PAN controls), then the editor write-back path.
4. **Screenshots**: `screenshot` after load, per tab → compare with the mockups;
   store golden PNGs in `panels/KronosKontrol/` (or a tests folder).
5. **Keep the hardware sheets** (`TEST_PLAN_0.96.md`, `EDITOR_PLAN.md` §9–11) for
   what a mock cannot do: the real KORG USB-MIDI driver, real dump timing, actual
   sound write to the edit buffer, KARMA interactions. The probe replaces the
   *offline* parts, not the hardware pass.
6. **CI**: the probe's exit codes make a GitHub Action trivial (build probe →
   run batch → upload report). Optional.

### 4.4 What the skill adds here: little

`skills/ctrlrx-panel-builder/` teaches an agent to hand-edit `.panel` files and
verify with the probe. This project's model is the opposite: the `.panel` is
**generated** (`build_panel.py` from `parameter_map.csv` + templates) — editing
the generated XML by hand is explicitly not done (the generator is re-run;
"baseline check: the unchanged scripts regenerate the engine layouts byte for
byte"). The project already has its own agent-facing docs (`PROMPT_*.md`,
`for_agent/`). So:

- **Do not install the skill as a workflow.** The one idea worth borrowing is its
  *verify-with-the-probe loop* — which is exactly §4.2–4.3 above, already the
  project's generator-plus-oracle model (cf. the skill's FireworX workflow:
  generate from a spec, verify with the probe — the same shape as
  `build_panel.py` + `kronos_sysex.py`).
- `assets/template-panel.panel` may serve as a minimal sanity panel to validate
  a probe binary before pointing it at the 30 MB KronosKontrol panel.
- The `evals/` tasks (18 graded scenarios with sample panels) are a ready-made
  list of test ideas (broken panel, dump receiver, patch sync…) that map onto
  KronosKontrol scenarios.

## 5. Recommendation

1. **Adopt the probe, not the skill.** Take the `Tests/probe_*` additions from
   `build/CtrlrX-pr337/`, build `CtrlrPanelProbe` on the pinned `v5.6.36` clone,
   and write the assertor against `kronos_sysex.py` / `parameter_map.csv`.
   First suites: (a) MIDI-out bytes for all rack controls, (b) real-LuaJIT eval
   of the UTF-8/Latin-1 paths, (c) dump inject → modulator state, (d) screenshot
   + mouse hit-area checks vs the mockups, (e) load-time snapshot in the
   generator pipeline.
2. **Nothing in the panel needs to change because of the branch**: no `Source/`
   changes; 0 short multi-list entries; `uiPanelEditMode=0`. Add one doc rule:
   never save the panel in edit mode (upstream bug #2).
3. **Report upstream** (the PR author said they would open issues): confirm both
   bugs on 5.6.36, and note that KronosKontrol is unaffected by the multi-list one.
4. Keep hardware test sheets for the real-synth-only checks.

## 6. Sources used (all local, read-only)

- PR copy: `build/CtrlrX-pr337/` (+`build/PR337_README.md`); PR metadata and file
  list via GitHub API (`damiensellier/CtrlrX#337`).
- Project state: `panels/KronosKontrol/PROJECT_LAYOUT.md`, `CTRLRX_MIGRATION.md`,
  `BUILD_EXPORT.md`, `REPRISE_CODAGE_1.0f.md` / `_1.0h.md`,
  `journal/session-2026-11-03-ctrlrx-codage-2.md`,
  `docs_editor/EDITOR_V1_POSTMORTEM.md`, `panels/KronosKontrol/TEST_PLAN_0.96.md`,
  `scripts/kronos_sysex.py`, `panels/KronosKontrol/KronosKontrol_1.0h.panel`
  (property and multi-list scan), `panels/KronosKontrol/sources/ctrlr_templates.json`.
- Engine: `build/CtrlrX-damiensellier/CtrlrX` at tag `v5.6.36`
  (`Tests/CMakeLists.txt` diff vs the PR head = +53/−0).
- Probe reference: `build/CtrlrX-pr337/Doc/PanelProbe.md` (actions, report schema,
  exit codes, "reports, does not assert").
