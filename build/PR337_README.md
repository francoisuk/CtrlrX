# CtrlrX-pr337 — copy of GitHub PR #337 (damiensellier/CtrlrX)

- **PR:** https://github.com/damiensellier/CtrlrX/pull/337 — *"Panel probe and AI agent skill"* by @sgorpi
- **State:** open (not merged), mergeable_state "unstable" at the time of the copy
- **Head:** branch `panel-probe-and-skill` in `sgorpi/CtrlrX`, commit `62d612112b185cdfff3f7a8ef68000d332fe85cb`
  ("Skill: install guide per agent; pointer from the manual")
- **Base:** `5.6.37-Maintenance` @ `49497f72e0f809e00e9829bf2897d74426b1adfc` in `damiensellier/CtrlrX`
- **Diff:** 80 files changed, +9828 / −12, 19 commits

`CtrlrX-pr337/` is a clean source export (`git archive`) of that head commit —
no `.git`, identical to what the PR branch contains. Fetched via
`git fetch origin pull/337/head` in `CtrlrX-damiensellier/CtrlrX`.

## What the PR adds

- `Tests/probe_Main.cpp`, `Tests/probe_Report.{cpp,h}`, `Tests/probe_selftest.py`,
  `Tests/probe_*.json`, `Tests/png_sample.py`, `Tests/fixtures/fixture_probe_*.panel`,
  `Tests/CMakeLists.txt` — **CtrlrPanelProbe**, a headless command-line tool that loads a
  `.panel`, runs a JSON script against it (MIDI in/out, Lua, custom components, screenshots,
  mouse gestures) and prints a JSON report. Built next to `TestsProcessor`
  (`cmake --build build --target CtrlrPanelProbe`), 34 self-test scenarios
  (`ctest -R PanelProbeSelfTest`).
- `Doc/PanelProbe.md` (new, 770 lines) + short additions to `Doc/manual/09-debugging.md`,
  `Doc/manual/10-distribution.md`, `Doc/readme/04-compiling.md`.
- `.github/workflows/build_and_test.yml` — CI zips the probe per OS as the workflow
  artifact `CtrlrPanelProbe-<Linux|macOS|Windows>` and signs it when secrets exist.
- `skills/README.md` + `skills/ctrlrx-panel-builder/` — an Agent Skills (agentskills.io)
  package teaching coding agents to build/fix panels by editing the `.panel` and verifying
  with the probe; includes 18 graded eval tasks (`evals/`).
- 9 × `Tests/fixtures/fixture_lua_*.panel` — Lua methods moved out of the `Built-In`
  group (same change as PR #336, merge-conflict-free).

Nothing in `Source/` changes.

Copied 2026-11-04.
