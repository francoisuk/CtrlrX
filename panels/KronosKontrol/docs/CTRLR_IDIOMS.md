# CTRLR_IDIOMS — verified Ctrlr idioms for the Kronos Kontrol panel

**Status: verified (2026-10-16/18).** This file replaces the unverified snippet
that stood here on 2026-10-14 (it guessed the callback name `receiveStatus` and
the meaning of the `setValue` boolean without checking any source). Everything
below was verified twice: read from the working TR-Rack panel
(`../TR-Rack-Editor-main/Tr Rack Editor.bpanelz`, decompressed zlib → JUCE
ValueTree → XML; study in `ETUDE_TR-Rack.md`, reader `scripts/vt2xml.py`) and
checked against the Ctrlr source trees (`build/ctrlr-master` = base of the
shipped 5.6.23, `build/CtrlrX-dnaldoog` commit 935894276feb of 2026-10-13, and
`build/CtrlrX-damiensellier`). The shipped panel (`lua/kkMain.lua`,
complet-0.96) uses exactly these idioms — see §10.

## 1. Panel callbacks — called by Lua method NAME

Ctrlr calls a callback by the **name of the Lua method** (`getMethod(name)`).
`lua/kkMain.lua` is therefore split into one method per callback by `--@ name`
lines; helper functions stay global.

| Panel property | Value in this panel | Callback receives |
|---|---|---|
| `luaPanelLoaded` | `kkInit` | — (panel finished loading) |
| `luaPanelMidiReceived` | `kkOnMidi` | `midi` (a `CtrlrMidiMessage`) |
| `luaModulatorValueChange` (per modulator) | `kkClick`, `kkEncoder`, `kkGM`, `kkMix`, `kkKarmaSlider`, `kkGEMenu`, `kkGECatMenu` | `(mod, value)` |
| component mouse callbacks | `kkXYDown`, `kkXYDrag` | `(comp, event)` |

The TR-Rack study panel used the method names `initPanel` / `receiveStatus`; the
names are per-panel — what is fixed is the **panel property**, not the method
name. (2026-10-16 correction: in an earlier build everything sat in one method,
so `kkInit` / `kkOnMidi` were never called.)

## 2. Sending MIDI

```lua
panel:sendMidiMessageNow(CtrlrMidiMessage("F0 42 30 68 43 04 00 00 02 00 00 00 64 F7"))  -- SysEx
panel:sendMidiMessageNow(CtrlrMidiMessage(string.format("B%X %02X %02X", ch - 1, cc, v))) -- CC
```

- The argument is a **hex string** (`"F0 42 … F7"`, bytes separated by spaces).
  In Ctrlr 5.6.23 `CtrlrMidiMessage` does **not** safely accept a Lua table of
  bytes — always build the hex string (see the ATTENTION note at the top of
  `kronos_sysex.lua`, which is kept at panel root on purpose: the generator
  embeds every `lua/*.lua`).
- Helpers in `kkMain.lua`: `kkSend(s)` (send + monitor), `kkParam(typ, soc, sub,
  pid, idx, v)` (fn 43, 21-bit value), `kkParamF(fn, …)` (same grammar, any
  function: 6D KARMA, 6E Drum Track), `kkCC(cc, v)`.

## 3. Receiving MIDI

```lua
function kkOnMidi(midi)
  local d = midi:getData()
  local n = d:getSize()
  local b0 = d:getByte(0)          -- status byte, or 0xF0 for SysEx
  -- d:getByte(i), d:getSize(), d:getRange(i, n):toHexString(1)
end
```

## 4. Updating the UI without re-sending (anti-loop)

```lua
panel:getModulatorByName("kkMix1"):getComponent():setValue(v, false)
```

- `setValue(value, false)` updates the component **without** sending MIDI and
  **without** calling the value-change callback — this is Ctrlr's native
  anti-loop guard (`CtrlrSlider::setComponentValue`), verified in the sources.
  **No extra guard flag is needed** (this corrects §8.3 of the earlier
  PROJECT_LAYOUT: the flag design is obsolete in 5.6.23).

## 5. Text and LEDs

```lua
panel:getComponent("kkMonitor"):setPropertyString("uiLabelText", "→ CC74 = 100")   -- text
panel:getComponent("kkLitFX01"):setPropertyString("uiLabelBgColour", "ff3fb6ff")   -- lit bar
```

## 6. Timers

```lua
timer:setCallback(1, kkTimer)   -- kkTimer(id)
timer:startTimer(1, 400)        -- milliseconds; 4E mode-change fallback
timer:stopTimer(1)
```

Verified in `CtrlrLuaManager.cpp` of ctrlr-master and CtrlrX.

## 7. Background image

- Panel properties: `uiPanelEditor uiPanelImageResource="rack_fond"` and
  `uiPanelImageLayout="64"` (stretch). Canvas 1500 × 414.
- The image is embedded base64-JUCE in
  `resourceExportList/resource resourceData="<size>.<base64>"`
  (encoder: `sources/jb64.py`, verified byte-for-byte). The generator
  (`sources/build_panel.py`) does this from `rack_fond.png`.

## 8. Modulator MIDI settings

- `midiMessageType`: **0 = CC, 5 = SysEx, 9 = none**. The panel uses 9 (send from
  Lua) for every SysEx control and for the 16 CC encoders; the CC modulators
  that send directly use 0.
- `midiMessageCtrlrNumber` (CC number), `midiMessageChannel`.
- Components in use: `uiSlider` (style `RotaryVerticalDrag`), `uiButton`,
  `uiLabel`, `uiCombo`, `uiXYSurface`.

## 9. Console

- `console("…")` writes to Ctrlr's Lua console (mode changes, Reply 24
  diagnostics in `kkOnMidi`).

## 10. Where each idiom is exercised in the shipped panel (complet-0.96)

- `kkInit` — load: Mode Request (fn 12), initial UI state.
- `kkOnMidi` — decode CC / PC / SysEx: 42 Mode Data, 4E Mode Change, 24 Reply,
  43 (FX switches, Combi GE, Module Control, Drum Track), 6D / 6E (KARMA GE,
  Drum Track On).
- `kkEncoder` — the 16 left CC encoders. `kkClick` — all buttons (mode, banks,
  ▲▼, SW, FX, KARMA, scenes, DT, HOLD, MODULE, U-A/AA). `kkGM` — GM bank menu.
- `kkMix` — the 8 MIXER/PAN encoders. `kkKarmaSlider` — CC22–29.
  `kkGEMenu` / `kkGECatMenu` — GE select. `kkXYDown` / `kkXYDrag` — X-Y pad.
