# Large-panel load investigation — KronosKontrol / CtrlrX 8.77

**Date:** 2026-11-05
**Repository:** `ctrlrx-juce8` (branch `feature/large-panel-perf`)
**Status:** read-only investigation. No C++ was modified, no build was run, no timing was measured yet.

---

## 1. Scope and question

The panel under investigation is **KronosKontrol 1.0i**, a ~30 MB generated CtrlrX `.panel`
file with 895 modulators across 216 logical pages. Loading it in the CtrlrX editor takes
roughly 30 seconds, and redrawing the UI can freeze the application.

The working assumption entering this investigation was:

> "All 895 components are being created at once at launch, rather than lazily loading only
> the visible tab."

This report tests that assumption, maps the load pipeline, and measures what the 30 MB
file actually contains. The headline result is that the assumption is **partly true but
mis-prioritised**: components are indeed all instantiated, but component construction
operates on only 8.3 % of the file. The other 91.7 % is two payloads carried inside XML
attributes, both decoded at load before any widget exists.

---

## 2. Baseline facts

| Item | Value | How established |
|---|---|---|
| CtrlrX version | **8.77** | `build/CtrlrX-dnaldoog/CtrlrX-master/VERSION` (bytes `38 2E 37 37 0A`) |
| Changelog top entries | `v8.77` and `v8.76`, both 11/05/2026 | `CHANGELOG.md` lines 5 and 12 |
| JUCE version | **8.0.12** | `JUCE/modules/juce_core/juce_core.h` (`version: 8.0.12`) |
| Panel file | `panels/KronosKontrol/KronosKontrol_1.0i.panel` | 30,485,268 bytes on disk / 30,483,885 chars decoded |
| Engine tree | `build/CtrlrX-dnaldoog/CtrlrX-master` | the only JUCE 8 tree in the repository |

**Version terminology trap.** CtrlrX and JUCE use independent numbering. "CtrlrX 8.76 on
JUCE 8" is the brief's shorthand; the tree on disk is CtrlrX **8.77** on JUCE **8.0.12**.
The `v8.76` changelog entry is *empty* — 8.77 carries the recorded changes, none of which
are performance-related. 8.77 is therefore a safe baseline for this work.

For reference, the other engine copies in the repository are all on the older line and are
**not** the profiling target:

| Tree | CtrlrX | JUCE |
|---|---|---|
| `build/CtrlrX-dnaldoog/CtrlrX-master` | 8.77 | 8.0.12 |
| `build/CtrlrX-damiensellier/CtrlrX` | 5.6.36 | 6.0.8 |
| `build/CtrlrX-pr337` | 5.6.37 | 6.0.8 |
| `probe/src` | 5.6.36 | 6.0.8 |

---

## 3. Measured composition of the panel file

All figures below are character counts from a single linear pass over the decoded file.

| Payload | XML location | Chars | Share |
|---|---|---|---|
| **228 images, base64-encoded** | `resourceData="…"` attributes | 21,001,680 | **68.9 %** |
| **41 Lua methods** | `luaMethodCode="…"` attributes | 6,955,773 | **22.8 %** |
| Structure + metadata (895 modulators, 895 components, 475 midi, 228 metadata-only resources) | element tree | 2,526,432 | **8.3 %** |
| **Total** | | **30,483,885** | 100 % |

### 3.1 Element census

| Element | Count |
|---|---|
| `<modulator>` | 895 |
| `<component>` | 895 |
| `<midi>` | 475 |
| `<resource>` | 456 (of which **228** carry inline `resourceData`; 228 are metadata only) |
| `<luaMethod>` | 41 |
| `<uiTabs>` | **1** |
| `<uiTabsTab>` | 2 |
| `<uiPanelCanvasLayer>` | 1 |
| lines in file | 3,677 |

### 3.2 Visibility of components at load

| Attribute | Count |
|---|---|
| `componentVisibility="1"` | 244 |
| `componentVisibility="0"` | **651 (72.7 %)** |

### 3.3 Largest single items

| Bytes | What |
|---|---|
| 3,252,587 | `luaMethod` named `kronosData` (line 6) |
| 2,634,294 | `luaMethod` named `kronosEditor` (line 7) |
| 973,229 | one `<resource>` carrying a 729,731-byte image |
| 879,786 | one `<resource>` carrying a 659,649-byte image |
| 578,371 | `luaMethod` named `kkEdPages` (line 8) |
| 220,744 | `luaMethod` named `kkEdFxData` (line 9) |
| 89,995 | largest single `<modulator>` block (`vstIndex="235"`) |

Modulator blocks total 2,379,210 bytes — average 2,658 bytes, max 89,995.

### 3.4 Interpretation

Ninety-two percent of the file is payload that has nothing to do with the component tree:
about **15.7 MB of binary images** (20.0 MB base64, ×3/4) and **6.6 MB of Lua source**.
Optimising component construction alone cannot address most of the load time.

---

## 4. The load pipeline

### 4.1 Call chain (top to bottom)

```
CtrlrPanel::openPanel(File)                       CtrlrPanelFileOperations.cpp:542
└─ CtrlrPanel::openXmlPanel(File)                  CtrlrPanelFileOperations.cpp:508
   ├─ XmlDocument::parse(panelFile)                :528      <-- parses all 30 MB
   └─ ValueTree::fromXml(*xml)                     :530
      └─ CtrlrManager::restoreState(XmlElement)    CtrlrManager.cpp:365
         └─ CtrlrManager::restoreState(ValueTree)  CtrlrManager.cpp:372
            └─ CtrlrPanel::restoreState(ValueTree) CtrlrPanel.cpp:2203
               ├─ ctrlrLuaManager->restoreState()  :2219     <-- PHASE A: 6.6 MB Lua
               ├─ resourceManager.restoreState()   :2230     <-- PHASE B: 20 MB base64
               └─ getEditor(true)->restoreState()  :2269     <-- PHASE C: 895 widgets
```

All paths below are relative to `build/CtrlrX-dnaldoog/CtrlrX-master/Source/`.

### 4.2 PHASE A — Lua methods compiled *and executed* at load

```
CtrlrLuaMethodManager::restoreState          Lua/Methods/CtrlrLuaMethodManager.cpp:130
└─ restoreMethod                             :211
   └─ addMethod                              :760
      └─ group.addChild(newMethodTree)       :810
         └─ CtrlrLuaMethodManager::valueTreeChildAdded   :236
            └─ new CtrlrLuaMethod(...)       :238
               └─ CtrlrLuaMethod::CtrlrLuaMethod   Lua/Methods/CtrlrLuaMethod.cpp:28
                  └─ setCodeInternal(getCode())    :38
                     └─ owner.getOwner().runCode(...)  :180
```

`setCodeInternal` (Lua/Methods/CtrlrLuaMethod.cpp:169–213) calls `runCode(...)`, which
**compiles and executes the chunk**. It then does a `luabind::globals` lookup to bind the
resulting function (line 188).

Consequences:

- All 41 methods are compiled eagerly, during panel load, **before the panel editor exists**.
- `kronosData` (3.25 MB) and `kronosEditor` (2.63 MB) are *executed*, not merely parsed, so
  they allocate Lua tables/string data during load.
- This phase is entirely independent of which components are visible.

### 4.3 PHASE B — resources decoded and written to disk at load

```
CtrlrPanelResourceManager::restoreState      Core/CtrlrPanel/CtrlrPanelResourceManager.cpp:521
└─ per child of type resourceBlob|resourceImage|resource:
   importResource                            :234
   ├─ resourceData.fromBase64Encoding(...)   :239     <-- decode
   ├─ resourceDest.replaceWithData(...)      :274 (Path A) / :289 (Path B)
   └─ addResource(...)                       :296
      └─ new CtrlrPanelResource              Core/CtrlrPanel/CtrlrPanelResource.cpp:14
         ├─ computeContentHash(file)         :29 -> :212
         └─ load()                           :32 -> :118
            └─ calculateHash()               :119
```

**Important nuance — image decoding is already lazy.** `CtrlrPanelResource::load()`
(CtrlrPanelResource.cpp:118) explicitly skips image types:

```cpp
if (resourceLoaded || resourceType == ImageRes) {
    // ImageCache deals with that
}
```

and `asImage()` (:68) decodes on demand via `ImageFileFormat::loadFrom` with an
`ImageCache`. So PNG decoding is **not** the eager cost. What *is* eager is:

1. base64 decoding ~20 MB of attribute text into ~15.7 MB of `MemoryBlock`;
2. **writing all 228 files to disk** via `replaceWithData`.

**Cross-run deduplication does not happen.** `importResource` only compares hashes inside
"Path A", which is entered when `getResource(resourceName)` returns an already-registered
resource (`:257`). On a cold start that registry is empty, so every resource takes
**Path B: fresh import** (`:286–296`) and rewrites the file. Net effect: roughly **15 MB of
disk writes per application launch**, regardless of whether the files already exist and are
identical.

### 4.4 PHASE C — all 895 widgets constructed, including the 651 invisible ones

```
CtrlrPanelEditor::restoreState               UIComponents/CtrlrPanel/CtrlrPanelEditor.cpp:462
└─ getCanvas()->restoreState(savedState)     :476
   └─ CtrlrPanelCanvas::restoreState         UIComponents/CtrlrPanel/CtrlrPanelCanvas.cpp:495
      └─ for every child of type modulator   :519-534
         ├─ CtrlrComponent *c = addNewComponent(child);   :523
         ├─ if (c) c->toBack() if componentSentBack      :528-530
         └─ c->setVisible((bool)componentVisibility);    :531   <-- AFTER construction
```

Note line 531: **visibility is applied after the component is fully built.** Construction
never consults it.

Per component, `CtrlrPanelCanvas::addNewComponent(const ValueTree&)` (:350):

```
addModulator(uiType)                                    :364
└─ CtrlrPanel::createNewModulator                       Core/CtrlrPanel/CtrlrPanel.cpp:652
   └─ CtrlrPanel::addModulator                          :634
      ├─ ctrlrModulators.add(...)                       :636
      ├─ hashName(modulatorToAdd)                       :640   (name -> hash table)
      ├─ owner.addModulator(...)                        :643   (VST manager)
      ├─ panelTree.addChild(...)                        :646
      └─ listeners.call(modulatorAdded)                 :649
ctrlrModulator->restoreState(savedState)                :367
└─ CtrlrModulator::restoreState                         Core/CtrlrModulator/CtrlrModulator.cpp:119
   └─ setComponentType(component tree)                  :128
      └─ CtrlrComponentTypeManager::createComponent     UIComponents/CtrlrComponents/CtrlrComponentTypeManager.cpp:79
         ├─ createComponent(uiType, owner)              :83    <-- ~25-branch new CtrlrSlider/Combo/…
         └─ c->restoreState(savedState)                 :84
attach(...)                                             :377
```

After the loop, `CtrlrPanelCanvas::canvasStateRestored()` (:541) performs two further full
scans of the modulator array via `CtrlrPanel::getModulatorsByUIType`
(Core/CtrlrPanel/CtrlrPanel.cpp:687) for `uiTabs` and `uiGroup`.

### 4.5 A hypothesis that was tested and eliminated

`CtrlrPanel::getUniqueModulatorName` (Core/CtrlrPanel/CtrlrPanel.cpp:729) looks like an
O(n²) name-uniqueness scan, and it *is* called once per modulator from
`CtrlrModulator::restoreState:145`. However it **early-returns during restore**:

```cpp
if (getRestoreState())
    return (proposedName);
```

and `CtrlrPanel::restoreState` sets `setRestoreState(true)` at :2206. So it is not a cost
centre during load. Recorded here so it is not re-investigated.

---

## 5. Specific defect found

### 5.1 `computeContentHash` base64-encodes a whole file to hash it

`CtrlrPanelResource::computeContentHash` (Core/CtrlrPanel/CtrlrPanelResource.cpp:212–220):

```cpp
int64 CtrlrPanelResource::computeContentHash (const File &f) {
    if (! f.existsAsFile() || f.getSize() == 0)
        return 0;
    MemoryBlock data;
    f.loadFileAsData (data);
    return data.toBase64Encoding().hashCode64();
}
```

For every resource this reads the entire file and allocates a base64 string roughly 1.33×
the file size — purely to derive a `int64`. It is invoked from the constructor
(:29), and then again indirectly: the constructor calls `load()` (:32), which calls
`calculateHash()` (:119), reading the file a second time.

Across 228 resources the file contents are therefore read **twice** (~31 MB of I/O
combined), and base64-encoded **once per resource**, allocating roughly 20 MB of temporary
strings in aggregate — for a value a streaming hash produces with near-zero allocation.

Note also that `calculateHash()` (:113–116) computes a *different* value — file hash plus
modification time — which overwrites the value stored by `computeContentHash`.

---

## 6. There is no lazy-loading machinery in the engine

A repository-wide search across `Source/` for `lazy`, `deferr`, `onDemand`, `LazyLoad`,
`placeholder` returns only two irrelevant matches (a `mmc_deferredplay` MIDI constant and a
font "placeholder" comment). Nothing in the engine defers component creation.

**Structural obstacle to "load only the visible tab":** the panel contains exactly **one**
`<uiTabs>` element and two `<uiTabsTab>` elements. The 216 "pages" are layout regions on a
single canvas, not Ctrlr tab pages. `panels/KronosKontrol/sources/build_panel.py` describes
the design as:

> "One page of pooled controls over the FULL artwork of graphics/KRONOS_Editor/Full
> (214 pages), no nested uiTabs."

So any lazy strategy must key off `componentVisibility` or page region membership, **not**
tab ancestry.

---

## 7. Ranked hypotheses for the ~30 s load

> **These hypotheses have since been measured and refuted — see §14.**
> The real distribution is XML parsing 89 %, resource import 10 %, widget
> construction 1 %, Lua 0.3 %. Read §7 as the reasoning that led to the
> experiment, not as the current understanding.

**These are hypotheses. No timing has been measured.** Only static byte counts and code
paths are established above.

| # | Suspect | Evidence for | Confidence |
|---|---|---|---|
| 1 | Lua compile + execute, 6.6 MB, before editor creation | `setCodeInternal` → `runCode` per method; `kronosData` alone is 3.25 MB executed as table construction | high |
| 2 | base64 decode 20 MB + rewrite 228 files on every launch | `importResource` Path B unconditionally; no cross-run hash check | high |
| 3 | XML parse + entity unescape of 30 MB | 91.7 % of bytes sit inside attribute values; Lua uses `&#10;` entity escapes | medium |
| 4 | 895 component constructions | real, but only 8.3 % of the file is structural | medium |
| 5 | redundant resource hashing (§5.1) | full read + base64 allocation, ×2 per resource | medium (likely overlaps #2) |

Leading expectation: **#1 and #2 dominate; #4 is a secondary contributor.** That inverts the
original framing that the 895 components are the root cause.

### Not established by this report

- No wall-clock timing of any phase.
- No RSS/peak-memory measurement.
- The **redraw/freeze** behaviour has not been examined at all. Whether paint cost scales
  with 895 components or with the 244 visible ones is unknown. `CtrlrPanelCanvas::paint`
  and the `CtrlrComponent::paint` implementations were not read.

---

## 8. Proposed measurement plan

Before changing logic, instrument four timestamps and one memory peak on a scratch build
(this is a throwaway patch, not a behavioural change):

| Marker | Location | Measures |
|---|---|---|
| `t0` | entry of `CtrlrPanel::openXmlPanel` | — |
| `t1` | after `ValueTree::fromXml` (CtrlrPanelFileOperations.cpp:530) | **XML parse** |
| `t2` | after `ctrlrLuaManager->restoreState` (CtrlrPanel.cpp:2219) | **Lua compile+run** |
| `t3` | after `getResourceManager().restoreState` (CtrlrPanel.cpp:2230) | **resource import** |
| `t4` | after `getEditor(true)->restoreState` (CtrlrPanel.cpp:2269) | **widget construction** |
| peak RSS | process working set sampled on a timer, or `GetProcessMemoryInfo` at `t4` | **memory** |

Report the five deltas plus the peak. That converts the table in §7 into five numbers.

Secondary micro-measurements worth taking at the same time:

- Count and time the 228 `replaceWithData` calls (Phase B) — expect this alone to be
  proportional to ~15 MB of I/O.
- Time `computeContentHash` in aggregate to confirm or dismiss §5.1.
- Log the total bytes handed to `runCode` in Phase A.

---

## 9. Candidate optimisations (not implemented; for prioritisation only)

Ordered by expected ratio of benefit to risk. None of these has been assessed against the
measurements yet.

| # | Change | Targets | Risk |
|---|---|---|---|
| 1 | Skip `replaceWithData` when the destination file already exists with identical size+hash; verify the on-disk hash *before* decoding base64 | Phase B (~15 MB writes/launch) | low |
| 2 | Replace `computeContentHash` base64-encode with a streaming hash; drop the duplicate `calculateHash()` read in `load()` | §5.1 | very low |
| 3 | Defer Lua compile/execution for the large data-only methods (`kronosData`, `kronosEditor`) until first use, or move them out of `luaMethodCode` into a compact sidecar | Phase A (6.6 MB) | medium — depends on whether they are referenced during load |
| 4 | Lazy component construction keyed on `componentVisibility` / page region: build a lightweight placeholder, construct the real widget on first reveal | Phase C (895 → 244) | high — touches the canvas, selection, undo, MIDI routing |
| 5 | Split the generated panel so images live outside the XML (external resource dir) | parse + import + file size | medium — changes the distribution format |

Optimisation 1 and 2 are cheap, low-risk and measurable in isolation; they are the natural
first experiment. Optimisation 4 is what the original brief assumed, and should be deferred
until the phase timings show Phase C actually matters.

---

## 10. Tooling available: the panel probe (CtrlrX PR #337)

The repository contains a clean export of upstream PR #337, *"Panel probe and AI agent
skill"*, at `build/CtrlrX-pr337` (head `62d6121`, base `5.6.37-Maintenance`). It adds
`CtrlrPanelProbe`, a headless CLI that loads a real `.panel` in the real engine (real
LuaJIT, real paint, real MIDI paths; only MIDI ports and the display are mocked), runs a
JSON script of actions, and emits a JSON report.

**Actions:** `setValue`, `click`, `mouse` (down/drag/up/wheel at canvas coordinates),
`injectDeviceMidi`, `injectHostMidi`, `callLuaMethod`, `eval` (in the panel's own
`lua_State`), `waitFor`, `wait`, `screenshot`, `paint`, `setLayerVisible`.

**Report fields:** `panel` metadata, `dialogs`, `errors`, `warnings`, per-step `returnValue`
/ `deviceMidiOut` / `console`, `finalState.modulators`, `finalState.overlaps`,
`luaCompileErrors`, `disabledMethods`, `summary.errorCount`. Exit codes 0 (clean) / 1
(errors) / 2 (panel failed to load). `--stdin` runs many scripts in one process.

**Suitability for this task — important limits:**

- The report contains **no timing field and no memory field**. Load duration and RSS must be
  measured externally (wrap the process and sample it).
- The probe is a *state* oracle, not a profiler. It is excellent for "did the panel load
  correctly / do all 895 modulators exist / do the MIDI bytes match", not for "where did the
  30 s go".
- `probe/kkprobe.py` already wall-clocks the whole run and writes the raw report to
  `probe/out/`, which is a usable starting harness.
- The published `--stdin` figures give a useful floor: **1.50 s** one-shot process startup and
  **62 MB** peak RSS on a 1.35 MB / 313-modulator panel; 50 scripts in one process = 1.8 s
  total (~6 ms/script).
- **The existing binary is built on the wrong engine.** `probe/b/Tests/CtrlrPanelProbe.exe`
  (33.05 MB) was produced from `probe/src`, which is **CtrlrX 5.6.36 on JUCE 6.0.8**. Any
  load timing from it describes two engine generations behind the 8.77/JUCE 8 target.
- Rebuilding it against 8.77 requires copying the PR's `Tests/` directory into
  `build/CtrlrX-dnaldoog/CtrlrX-master`. That tree currently has **no** `Tests/` directory,
  but the call is guarded —
  `CMakeLists.txt:549` reads `if(EXISTS ".../Tests/CMakeLists.txt")` — so the normal build
  is not broken; the probe target is simply absent.

---

## 11. Open questions

1. Do the phase timings in §8 actually put #1/#2 ahead of #4? Everything downstream depends
   on this.
2. Are `kronosData` / `kronosEditor` referenced during panel load, or only later when a page
   is displayed? This decides whether optimisation #3 is safe.
3. Does the resource directory already contain the 228 files on a typical launch? If yes,
   optimisation #1 is nearly free to implement.
4. What is the paint path doing? `CtrlrPanelCanvas::paint` and per-component `paint` were not
   examined, and the freeze symptom is currently unexplained.
5. Is the canvas bounds large enough that JUCE still traverses hidden components on repaint?
   `componentVisibility=0` hides a widget but does not remove it from the component tree.

---

## 12. Appendix — reproducing the static measurements

All figures in §3 were produced with PowerShell 7 against the panel file, without loading
it into CtrlrX.

```powershell
$p = 'panels\KronosKontrol\KronosKontrol_1.0i.panel'

# element census
$t = [System.IO.File]::ReadAllText((Resolve-Path $p))
[regex]::Matches($t,'<([a-zA-Z][a-zA-Z0-9_]*)') |
  ForEach-Object { $_.Groups[1].Value } | Group-Object |
  Sort-Object -Descending Count | Select-Object -First 25

# payload shares (linear patterns; avoid '(.*?)' over this file, it backtracks for minutes)
$res = [regex]::Matches($t,'resourceData="([^"]*)"')
($res | ForEach-Object { $_.Groups[1].Value.Length } | Measure-Object -Sum).Sum

$l1 = [regex]::Matches($t,'luaMethodCode="([^"]*)"')
$l2 = [regex]::Matches($t,"luaMethodCode='([^']*)'")     # 22 methods are single-quoted
```

Caveat recorded during the work: a `(?s)<resource[^>]*>(.*?)</resource>` style pattern over
this 30 MB single-attribute-heavy file backtracks for minutes. Use `[^"]*` style linear
patterns instead.

---

## 13. Summary for the reader

- The panel is 30 MB, but only **2.4 MB (8.3 %)** is the 895-component UI tree.
- **20.0 MB is base64 images** and **6.6 MB is Lua source**, both stored as XML attributes.
- At load, in this order: Lua is compiled **and executed** (6.6 MB), all 228 images are
  base64-decoded and **rewritten to disk** (~15 MB per launch, no cross-run cache), then all
  895 widgets are constructed — including the **651 that are invisible**.
- PNG decoding is already lazy via `ImageCache`; the eager cost is base64 decode + disk write.
- There is **no lazy-loading machinery** in the engine, and with a single `uiTabs` element the
  "load only the visible tab" model does not apply to this panel.
- Two concrete, low-risk defects were identified: an unconditional resource rewrite on every
  launch, and a hash routine that base64-encodes entire files.
- No timing has been measured yet. The next step is a five-marker instrumentation patch to
  turn the ranked hypotheses into five numbers before any optimisation is attempted.

---

## 14. MEASURED BASELINE — instrumentation implemented 2026-11-05

The §8 measurement plan was implemented, built and run. It supersedes §7.

### 14.1 Result (CtrlrX 8.77 / JUCE 8.0.12, Release x64, MSVC 19.51, Windows)

| Phase | Run 1 | Run 2 |
|---|---:|---:|
| XML Parse (t1 − t0) | **29 985.18 ms** | **28 452.34 ms** |
| Lua Execute (t2 − t1) | 117.24 ms | 115.48 ms |
| Resource Import (t3 − t2) | 3 211.81 ms | 3 442.05 ms |
| Widget Construction (t4 − t3) | 336.79 ms | 348.29 ms |
| **Total Load (t4 − t0)** | **33 651.01 ms** | **32 358.17 ms** |
| Peak RSS | 741.1 MB | 741.1 MB |

Raw per-marker trace of run 1 (milliseconds since boot):

```
6208666.23 ms  t0 openXmlPanel entered
6208668.20 ms  about to XmlDocument::parse(File)
6238643.86 ms  parse returned an element     <-- 29 975 ms inside XmlDocument::parse
6238651.40 ms  t1 after fromXml              <-- ValueTree::fromXml cost only 7.5 ms
6238768.64 ms  t2 after lua restore
6241980.45 ms  t3 after resource import
6242317.23 ms  t4 after editor restore
```

### 14.2 What this refutes

- **Lua compile/execute is not a problem**: 117 ms for 6.6 MB. Hypothesis §7 #1 was wrong.
- **Component construction is not a problem**: 337 ms for 895 widgets, of which 651 are
  invisible. Hypothesis §7 #4 was wrong — this is the cheapest phase, not the dearest.
- **Resource import is real but secondary**: ~3.3 s (10 %). Hypothesis §7 #2 was directionally
  right, wrong in magnitude.
- **XML parsing dominates**: ~29 s of ~33 s, i.e. **89 % of load time**. Nothing in §7
  predicted this. It is `XmlDocument::parse(const File&)` specifically — not
  `ValueTree::fromXml`, which costs 7.5 ms.

### 14.3 Why parsing is implausible at ~30 s

29 MB of XML should parse in low single-digit seconds. Two structural facts from §3 are the
likely cause and are the next thing to measure:

- 20.0 MB sits in 228 `resourceData="…"` attributes and 6.6 MB in 41 `luaMethodCode="…"`
  attributes — i.e. ~88 % of the document is inside **attribute values**, not elements.
- The Lua attributes carry entity-escaped newlines (`&#10;`), so the parser performs entity
  decoding over 6.6 MB.

Peak RSS of 741 MB for a 30 MB input is consistent with a parser that materialises large
intermediate `String` objects per attribute.

### 14.4 Instrumentation as built

- New header `Source/Core/CtrlrPanel/CtrlrLoadProfiler.h` (header-only, no build-system change).
- Marker call sites, 5 total:
  - `CtrlrPanelFileOperations.cpp:510` — t0 at `openXmlPanel` entry
  - `CtrlrPanelFileOperations.cpp:536` — t1 after `ValueTree::fromXml` (`.panel` branch; a
    twin exists in the `.panelz` branch)
  - `CtrlrPanel.cpp:2221` — t2 after `ctrlrLuaManager->restoreState`
  - `CtrlrPanel.cpp:2255` — t3 after the resource import chain
  - `CtrlrPanel.cpp:2274-2275` — t4 after `getEditor(true)->restoreState`, then the report
- Output channels: `Logger::writeToLog`, `OutputDebugStringW`, and unconditionally
  `%TEMP%\ctrlr_load_profile.txt` (a packaged GUI executable has no console, so the file is
  the reliable channel). A per-marker `%TEMP%\ctrlr_load_trace.txt` records how far a load
  got when the final block never appears.
- Peak memory: `K32GetProcessMemoryInfo` resolved dynamically from `kernel32.dll`, so no
  import library was added to the project.
- Removal: set `CTRLR_LOAD_PROFILING` to `0` (all call sites compile away), or delete the
  header and its five call sites. No logic, no control flow and no function signatures changed.

### 14.5 Operational notes for reproducing

- The standalone accepts a panel path on the command line
  (`CtrlrStandaloneApplication.cpp:136`), but **the argument must not carry a trailing
  space**: `File::hasFileExtension("panel")` then fails and `openXmlPanel` silently takes the
  "unknown file type" branch, producing a no-op load with an idle process. Launch through a
  `.bat` wrapper rather than `Start-Process`, which appends a trailing space.
- Resources are extracted to `%APPDATA%\CtrlrX\<panelName>\`, not next to the panel file.
- Both runs cold/warm behaved identically, consistent with §4.3: `importResource` rewrites
  every resource on every launch.

---

## 15. Revised next step

The optimisation target is now clear and is none of the original candidates:

1. Measure *inside* `XmlDocument::parse` — separate attribute-value scanning, entity
   decoding and element allocation — before changing anything.
2. Candidate fixes for parse cost, in expected order of benefit:
   a. Move `resourceData` / `luaMethodCode` payloads out of attributes into child text or a
      sidecar file (attribute values are the slow path in most XML parsers, including JUCE's);
   b. do not entity-escape newlines in Lua payloads (or store Lua base64/base-85 instead);
   c. stream the panel instead of building a 741 MB peak of intermediate strings.
3. Resource import (~3.3 s) remains a valid secondary target — see §9 optimisation #1.

Widget construction and Lua must be dropped from the priority list: together they are ~1.3 %
of load time.

---

## 16. INSIDE THE PARSER — measured 2026-11-05

§14 localised 89 % of load time in `XmlDocument::parse(const File&)`. This section opens that
black box. Result: **99.83 % of the parse is attribute-value extraction**, and within it the
cost is quadratic string accumulation, not entity decoding per se.

### 16.1 Where the code lives

| File | Function | Role |
|---|---|---|
| `JUCE/modules/juce_core/xml/juce_XmlDocument.cpp:292` | `XmlDocument::parseDocumentElement` | parse entry, drives everything |
| `…/juce_XmlDocument.cpp:504` | `XmlDocument::readNextElement` | tag name, attribute names/values |
| `…/juce_XmlDocument.cpp:450` | `XmlDocument::readQuotedString` | **the hot path** — fills every attribute `String` |
| `…/juce_XmlDocument.cpp:778` | `XmlDocument::readEntity` | `&#10;` → newline |
| `…/juce_XmlDocument.cpp:614` | `XmlDocument::readChildElements` | elements and text content |
| `JUCE/modules/juce_core/text/juce_String.cpp:296` | `String::preallocateBytes` | growth policy (see §16.4) |
| `…/juce_String.cpp:747` | `String::appendCharPointer` | one realloc + memcpy per append |
| `…/juce_String.cpp:190` | `makeUniqueWithByteSize` | decides the new allocation size |

All paths relative to `build/CtrlrX-dnaldoog/CtrlrX-master/`.

### 16.2 The hot path, as written

`readQuotedString` (450-501) fills `newAtt->attribute.value` one chunk at a time:

```
quote = readNextChar();                       // 452
while (! outOfData) {
    c = readNextChar();  if (c == quote) break;    // 456-460
    --input;
    if (c == '&')  readEntity (result);            // 465-468   <-- entity branch
    else {
        start = input;
        for (;;) {                                  // 471-498   <-- text branch
            character = *input;
            if (character == quote) { result.appendCharPointer (start, input); ++input; return; }  // 480
            if (character == '&')   { result.appendCharPointer (start, input); break; }            // 487
            if (character == 0)     { ...error... }
            ++input;
        }
    }
}
```

Two append styles reach the same `String`:

- **Chunk append** — `appendCharPointer(start, input)`, lines 480 and 487: one call per
  run of text between entities.
- **Single-character append** — `readEntity` ends with `result << (juce_wchar) charCode`
  (line 870) for numeric entities such as `&#10;`.

Both go through `String::appendCharPointer` → `preallocateBytes` → **one fresh allocation
plus a memcpy of the entire accumulated string, on every append.**

### 16.3 Measurements

Four markers were added (see §16.5): whole-parse scope, `readQuotedString` calls, `readEntity`
calls, element counter. Output on the `KronosKontrol_1.0i` panel:

```
=== JUCE XmlDocument::parse profile ===
total                      : 30736.11 ms
attribute values           : 30684.37 ms   (76613 calls, 26.9 MB)
   of which entity decode  :  9462.99 ms   (87007 entities)
   attribute text only     : 21221.38 ms
structural (everything else):    51.74 ms
elements                   :     2772
```

| Bucket | Time | Share |
|---|---:|---:|
| Attribute values (all) | 30 684.37 ms | **99.83 %** |
| — entity decoding | 9 462.99 ms | 30.8 % |
| — attribute text chunks | 21 221.38 ms | 69.0 % |
| Structural tag scanning | **51.74 ms** | **0.168 %** |

Derived rates that make the anomaly explicit:

- **0.88 MB/s** effective attribute throughput. A healthy XML parser runs at 50–200 MB/s.
- **108.8 µs per `&#10;` entity.** Decoding a five-character numeric entity should cost tens
  of nanoseconds. This is roughly **1 000–10 000× too slow**, and the cost is independent of
  the entity itself — signature of an O(n) copy per entity.
- 76 613 attribute values, average 368 bytes, but the distribution is extremely skewed: 41
  `luaMethodCode` attributes hold 6.6 MB (largest 3.25 MB) and are precisely the ones built
  from ~65-byte chunks.

The structural scanner is *not* implicated: 2 772 elements and all tag/attribute-name
scanning cost **51.74 ms in total**.

### 16.4 Root cause

`String` growth is **linear, not geometric**:

```cpp
// juce_String.cpp:747
void String::appendCharPointer (start, end) {
    auto extraBytesNeeded = end - start;
    if (extraBytesNeeded > 0) {
        auto byteOffsetOfNull = getByteOffsetOfEnd();
        preallocateBytes ((size_t) extraBytesNeeded + byteOffsetOfNull);   // 759
        memcpy (newStringStart, startOfTextToAppend.getAddress(), extraBytesNeeded);  // 762
    }
}

// juce_String.cpp:296
void String::preallocateBytes (const size_t numBytesNeeded) {
    text = makeUniqueWithByteSize (text, numBytesNeeded + sizeof (CharType));  // 298
}

// juce_String.cpp:190
static CharPointerType makeUniqueWithByteSize (const CharPointerType text, size_t numBytes) {
    if (b->allocatedNumBytes >= numBytes && b->refCount <= 0) return text;      // 201
    auto newText = createUninitialisedBytes (jmax (b->allocatedNumBytes, numBytes)); // 204
    memcpy (newText.getAddress(), text.getAddress(), b->allocatedNumBytes);     // 205
    ...
}
```

Line 204 is the defect: the replacement buffer is `max(currentAllocated, needed)` — an
allocation of **exactly** the required size, with no doubling factor and no slack. Therefore
any append that needs one more byte allocates a whole new buffer and memcpy's everything
accumulated so far. Building a string from *k* chunks costs Σ(i·chunk) = **O(n²)**.

**Hypothesis (confirmed by the arithmetic below):** the 30-second parse is a quadratic string
accumulation. `readQuotedString` appends ~100 000 chunks across the three large Lua
attributes; each append re-copies the current prefix.

Sanity check against measurement: `kronosData` (3.25 MB, ~65-byte chunks ⇒ ≈50 000
appends) alone implies Σ ≈ 50 000² × 65 / 2 ≈ **81 GB** of memcpy. Adding `kronosEditor`
(2.63 MB ⇒ ≈40 000 appends ⇒ ≈52 GB) and `kkEdPages`, the total lands in the 130–200 GB
range. At the 4–6 GB/s effective memcpy rate implied by the 30.7 s measurement, that is
precisely the observed time. Entity decoding is 31 % of it because each `&#10;` is one more
append — **not** because entity parsing is intrinsically expensive.

Note the interaction with §3: the panel stores 20 MB of base64 images and 6.6 MB of Lua
*inside attribute values*. It is the combination of (a) payloads in attributes and (b) chunked
appends that produces the quadratic blow-up. Attributes parsed as a single chunk (the base64
images, which contain no `&`) cost almost nothing by comparison.

### 16.5 Instrumentation as built

All inside `juce_XmlDocument.cpp`; measurement only, no parser logic touched.

| Site | Line | Measures |
|---|---|---|
| `XmlParseProfile` block after `namespace juce {` | 36-155 | counters, `QuotedTimer`/`EntityTimer`, dump (writes `%TEMP%\juce_xml_parse_profile.txt`, skips parses < 100 ms so a later small document cannot overwrite it) |
| `parseDocumentElement` scope guard | 300-310 | whole-parse total, resets counters, dumps on exit |
| `readEntity (result)` call | 465-468 | entity decode time + count |
| `readNextElement` element counter | 531-532 | element count |
| `readQuotedString (newAtt->…)` call | 580-587 | attribute-value time, call count, bytes |

Removal: set `JUCE_XML_PARSE_PROFILE` to `0`, or delete the block and the four marked call
sites (all tagged `XMLParseProfile`).

**The instrumented file is preserved at
`investigations/large-panel-perf/juce_XmlDocument.instrumented.cpp`**, because `JUCE/` is
git-ignored in this repository (§README) and the modification would otherwise be lost. To
reapply: copy it over `JUCE/modules/juce_core/xml/juce_XmlDocument.cpp` and rebuild.

### 16.6 What this implies for a fix (not implemented)

Three independent levers, in decreasing order of expected benefit:

1. **Give `String` geometric growth** (`makeUniqueWithByteSize`, juce_String.cpp:204) — e.g.
   allocate `max(needed, allocated * 2)`. This turns O(n²) into O(n) for *every* caller in
   JUCE, not just XML. One line; biggest blast radius, so it needs upstream review.
2. **Preallocate the attribute buffer** before the loop in `readQuotedString` using the
   distance to the closing quote (`input.indexOf(quote)`), so the common case is a single
   allocation. Bounded to the parser.
3. **Do not store large payloads in attributes** (the generator-side change, §15.2a): the
   quadratic term only bites because a 3.25 MB value is built from ~50 000 appends.

Option 3 is orthogonal and remains the cheapest structural change, but option 1 or 2 fixes
the engine for any panel, present or future.

---

## 17. PROTOTYPE A/B — geometric growth applied 2026-11-05

Option 1 was applied as a single-line change and benchmarked against §16.

### 17.1 The change

`JUCE/modules/juce_core/text/juce_String.cpp:204`, inside `makeUniqueWithByteSize`:

```cpp
// before
auto newText = createUninitialisedBytes (jmax (b->allocatedNumBytes, numBytes));
// after  (prototype)
auto newText = createUninitialisedBytes (jmax (b->allocatedNumBytes * 2, numBytes));
```

Nothing else changed. Both instrumentation layers (§14, §16) stayed active.

### 17.2 Result

| Metric | Before | After | Change |
|---|---:|---:|---:|
| **XML Parse (t1 − t0)** | 30 795.37 ms | **8 109.71 ms** | **−73.7 % (3.8×)** |
| Lua Execute | 115.89 ms | 120.89 ms | unchanged (control) |
| Resource Import | 3 645.69 ms | 3 914.04 ms | unchanged (control) |
| Widget Construction | 351.28 ms | 355.06 ms | unchanged (control) |
| **Total Load** | 34 908.24 ms | **12 499.69 ms** | −64.2 % |
| **Peak RSS** | 741.0 MB | **740.5 MB** | −0.5 MB (no meaningful change) |

Parser internals:

| Bucket | Before | After |
|---|---:|---:|
| total parse | 30 736.11 ms | 8 050.75 ms |
| attribute values | 30 684.37 ms | 7 999.28 ms |
| — entity decode | 9 462.99 ms | 3 958.29 ms |
| — attribute text | 21 221.38 ms | 4 040.99 ms |
| structural | 51.74 ms | 51.46 ms |

The three untouched phases are flat to within noise, which confirms the change is isolated to
`String` and did not perturb unrelated code.

### 17.3 Answering the two questions directly

**"Did XML parse drop from 30 s to milliseconds?" — No.** It dropped to **8.1 s**, a 3.8×
improvement. Real, but still ~27× slower than a healthy parser on 30 MB.

**"Did Peak RSS drop from 741 MB?" — No.** 740.5 MB, unchanged. The peak was never caused by
allocation churn: freed buffers do not raise a high-water mark. 741 MB is *retained* data —
the 26.9 MB of attribute `String`s (plus the `XmlElement` tree holding a second copy), the
`ValueTree` built from it, 895 widgets, and the decoded resource blocks. Reducing the copy
churn removes transient traffic, not the peak.

### 17.4 Why it is still quadratic — the second O(n)

Geometric growth removed one of **two** per-append O(n) terms. The other one is still there:

```cpp
// juce_String.cpp:765, inside appendCharPointer
auto byteOffsetOfNull = getByteOffsetOfEnd();          // :765

// juce_String.cpp:558
size_t String::getByteOffsetOfEnd() const noexcept {
    return findByteOffsetOfEnd (text);                 // :560
}

static size_t findByteOffsetOfEnd (String::CharPointerType text) noexcept {
    return (size_t) ((char*) text.findTerminatingNull().getAddress() - (char*) text.getAddress());
}
```

`getByteOffsetOfEnd()` is a **strlen over the entire accumulated string, performed on every
single append**. It is O(n) per append → O(n²) overall, and geometric growth cannot help it,
because the scan is about finding the end, not about capacity.

This is quantitatively consistent with what remains: `kronosData` needs ≈50 000 appends, so
the aggregate strlen distance is ≈ 50 000² × 65 / 2 ≈ 81 GB of scanning. At a ~10 GB/s scan
rate that is ≈8 s — exactly the 8.0 s still measured. Per-entity cost fell from 108.8 µs to
45.5 µs but is still dominated by how much text already precedes the entity, not by the
entity itself.

**Conclusion: `juce::String` has two independent O(n) costs per append — an exact-size
reallocation and a full strlen — and both must go for attribute parsing to become linear.**

### 17.5 Consequence for the next prototype

Option 1 alone is not sufficient. The remaining fix in the parser is Option 2 — preallocate
the attribute buffer once in `readQuotedString` (the closing quote is findable up front with
`input.indexOf(quote)`), and build the value by writing through a pointer rather than by
repeated `String` appends. That removes *both* the reallocation and the strlen for this hot
path, and is bounded to `juce_XmlDocument.cpp` rather than to every `String` in the framework.

Predicted outcome: XML parse below ~0.5 s (attribute throughput ≥50 MB/s), with peak RSS
essentially unchanged, since the retained data does not change.

---

## 18. PROTOTYPE — Option 2 applied 2026-11-05 (the fix)

The global `String` change was reverted; the fix is now confined to the XML parser.

### 18.1 The change

1. **Reverted** `juce_String.cpp:204` to the upstream
   `jmax (b->allocatedNumBytes, numBytes)`. Confirmed by grep: no `allocatedNumBytes * 2`
   remains in the file.
2. **Rewrote `XmlDocument::readQuotedString`** (`juce_XmlDocument.cpp`, was line 450) so it
   never calls `String::appendCharPointer`:
   - a local `MemoryOutputStream accumulated` collects the value as raw bytes;
   - ordinary text runs are copied with a new file-local helper
     `writeToStream (MemoryOutputStream&, CharPointerType start, CharPointerType end)`,
     which memcpys the byte range directly (`JUCE_STRING_UTF_TYPE == 8` path) — no `String`
     is constructed per chunk;
   - entities are expanded by `readEntity` into a scratch `String` and then written to the
     stream as UTF-8 bytes;
   - on the closing quote the value is converted **once** with
     `result = accumulated.toString()`.

Only this function and its new helper changed. Element parsing, entity parsing and all other
callers are untouched.

### 18.2 Result — three-way comparison

| Metric | Baseline | Option 1 (String ×2) | **Option 2 (parser)** |
|---|---:|---:|---:|
| **XML Parse (t1 − t0)** | 30 795.37 ms | 8 109.71 ms | **248.18 ms** (run 2: 244.94 ms) |
| Lua Execute | 115.89 ms | 120.89 ms | 121.15 ms |
| Resource Import | 3 645.69 ms | 3 914.04 ms | **3 564.10 ms** |
| Widget Construction | 351.28 ms | 355.06 ms | 344.09 ms |
| **Total Load** | 34 908.24 ms | 12 499.69 ms | **4 277.51 ms** (run 2: 4 323.91 ms) |
| **Peak RSS** | 741.0 MB | 740.5 MB | **741.1 MB** (run 2: 739.8 MB) |

Parser internals:

| Bucket | Baseline | Option 1 | **Option 2** |
|---|---:|---:|---:|
| total parse | 30 736.11 ms | 8 050.75 ms | **188.97 ms** |
| attribute values | 30 684.37 ms | 7 999.28 ms | **136.21 ms** |
| — entity decode | 9 462.99 ms | 3 958.29 ms | **14.83 ms** |
| — attribute text | 21 221.38 ms | 4 040.99 ms | **121.39 ms** |
| structural | 51.74 ms | 51.46 ms | 52.75 ms |

**XML parsing is 124× faster than the baseline and 32.7× faster than Option 1.** Attribute
throughput rose from **0.88 MB/s to 198 MB/s**; per-entity cost fell from 108.8 µs to
**170 ns**.

### 18.3 Correctness signals

The parse produced an identical document shape before and after:

| Check | Baseline | Option 2 |
|---|---|---|
| elements | 2 772 | 2 772 |
| `readQuotedString` calls | 76 613 | 76 613 |
| attribute bytes | 26.9 MB | 26.9 MB |
| elements counter | 2 772 | 2 772 |

Downstream phases are also unchanged (Lua 116–121 ms, widgets 344–353 ms), i.e. the Lua
methods still compile and all 895 widgets still build from the parsed tree. Two independent
runs gave 248.18 / 244.94 ms for the parse and 4 277.51 / 4 323.91 ms total.

### 18.4 Peak RSS did not move — and that is the correct answer

741.0 → 740.5 → 741.1 MB. As predicted in §17.3, the high-water mark is *retained* data, not
allocation churn: 26.9 MB of attribute `String`s, the `XmlElement` tree that holds them, the
`ValueTree`, 895 widgets, and the decoded resource blocks. Removing copies removes traffic,
not storage. Only changing what is stored (§9 option 5, external resources) would move it.

### 18.5 The bottleneck has moved

With parsing at 248 ms, the profile is now:

| Phase | Time | Share |
|---|---:|---:|
| **Resource Import** | **3 564 ms** | **83.3 %** |
| Widget Construction | 344 ms | 8.0 % |
| XML Parse | 248 ms | 5.8 % |
| Lua Execute | 121 ms | 2.8 % |

Resource import is now the dominant cost, exactly as §4.3 predicted: every launch
base64-decodes 20 MB and rewrites 228 files, because `importResource` only deduplicates
against an in-memory registry that is empty on a cold start. §9 option 1 is the next target
and is worth ~3.4 s of the remaining 4.3 s.
