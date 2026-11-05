# Recipe — automatic scaling of the 1500 × 414 panel on smaller screens

Goal: when the Kronos Kontrol panel (Main or EDITOR window, 1500 × 414 px) is opened on a screen narrower than
1500 px (e.g. a 14" laptop at 1366 × 768), shrink it automatically so that it fits, without redrawing anything.

> Status: **implemented in complet-0.97r (1 nov. 2026) via the native viewport mode, not via Lua.**
> Verification against the pinned Ctrlr 5.6.23 sources (`build/CtrlrX-dnaldoog`): the `Desktop` /
> `Displays` classes are **not bound to Lua** in any of the three source trees, so the Lua snippet in §2
> cannot work here (project rule: never invent an unbound API). What does work: the panel property
> **`uiViewPortMode = "Scaled"`** on `<uiPanelEditor>` — in exported/restricted instances (VST3/AU under
> SAVIHost or Live), `CtrlrPanelEditor::applyViewPortMode()` (CtrlrPanelEditor.cpp:928) recomputes
> `uiPanelZoom = editorWindow / canvas` on every `resized()`, so the 1500×414 panel shrinks to fit a
> smaller host window automatically. The panel ships with `uiViewPortMode="Scaled"` since 0.97r
> (`sources/build_panel.py`). §2/§3 below stay for the record (a C++ rewrite would use §3).

## Principle

- Keep **1500 × 414** as the reference size. All artwork and every `_layout.json` coordinate stay valid: the scale
  applies to the whole panel, not to individual components.
- Compute a scale factor from the **usable** screen width (logical pixels, taskbar excluded) and apply it once, when
  the panel loads.
- Never enlarge above 100 % automatically (only shrink).

Example: 1366 px screen → usable width ≈ 1366, minus ~24 px of window borders → s = 1342 / 1500 ≈ **0.89** →
displayed panel ≈ 1335 × 369 px.

## 1. Ctrlr — native panel zoom (simplest)

Ctrlr has a panel property **`uiPanelZoom`** (Panel properties → zoom). It can be set by hand (e.g. 0.9) or from Lua.

## 2. Ctrlr — automatic, in Lua

Attach this to the panel's **"Called when the panel has finished loading"** callback (`luaPanelLoaded`):

```lua
-- Kronos Kontrol: shrink the 1500 x 414 panel to the screen width
REF_W = 1500
MARGIN = 24        -- window borders

function kkAutoScale()
  local disp = Desktop.getInstance():getDisplays():getMainDisplay()   -- older JUCE: getMainDisplay()
  local w = disp.userArea:getWidth()                                  -- logical px, taskbar excluded
  local s = math.min(1.0, (w - MARGIN) / REF_W)
  s = math.floor(s * 100 + 0.5) / 100                                 -- round to 0.01
  panel:setProperty("uiPanelZoom", s, false)
  console("kkAutoScale: screen " .. w .. " px, zoom " .. s)
end
```

Optional: offer a manual override (menu or button 75 / 90 / 100 / 125 %) that calls
`panel:setProperty("uiPanelZoom", value, false)`, and remember the choice in a panel property so it survives a reload.

## 3. JUCE (if the editor is one day rewritten as a C++ plugin)

```cpp
auto area = juce::Desktop::getInstance().getDisplays().getPrimaryDisplay()->userArea;   // JUCE 6+
float s = juce::jmin (1.0f, (area.getWidth() - 24) / 1500.0f);
mainComponent.setTransform (juce::AffineTransform::scale (s));
setSize (juce::roundToInt (1500 * s), juce::roundToInt (414 * s));
```

Or let the user resize freely with a fixed aspect ratio:
`setResizable (true, true); getConstrainer()->setFixedAspectRatio (1500.0 / 414.0);` and scale the content in
`resized()`.

## Things to watch

- **Windows display scaling**: work in *logical* pixels (`userArea` already is). A 1920 px screen at 125 % is only
  1536 logical px wide; at 150 %, 1280 → the panel must shrink there too.
- **Sharpness**: at ~0.88 the 1x bitmaps are downscaled and slightly softened. Using the **@2x** artwork as the image
  source gives a clearly sharper result, especially on 125-150 % displays.
- **Known risks with Ctrlr zoom** (to test first): popup menu position, mouse hit areas, combo boxes, and whether the
  host (Ableton Live) resizes the **plugin window** after the zoom changes. If Live keeps the old window size, set
  the zoom before the editor window opens or close/reopen the window.
- Height is never the problem (414 px fits on 768 px screens); width is.

## To check on the Ctrlr build in use

| Item | How |
|---|---|
| Name of the zoom property | Panel properties list in the Ctrlr editor (`uiPanelZoom`) |
| Screen API in Lua | `console(tostring(Desktop.getInstance():getDisplays()))`, then `getMainDisplay()` vs `getPrimaryDisplay()`; `userArea` vs `getUserArea()` |
| Behaviour as exported VST / AU in Live | open the instance on a 1366 px screen (or at 150 % scaling) and check menus, knobs and window size |
