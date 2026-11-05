# Architecture: RACK, EDIT, dumps and SysEx

This chapter explains how Kronos Kontrol is built, so the workflows make sense.
It is background reading — users who just want to operate the panel can skip it.

## One panel, two views

The whole application is a single Ctrlr panel named **Kronos Kontrol**
(`panelUID = kkKronosKontrol`) with two top-level tabs driven by one `uiTabs`
control (`kkTabs`): **RACK** (index 0) and **EDIT** (index 1). The tab bar itself
is hidden; the **EDITOR** and **To rack** buttons switch tabs programmatically.
The panel contains **895 modulators** (controls): 219 image sliders, 414 labels,
112 combos, 139 buttons, 5 image buttons, 5 images and the tab control.

- **RACK** is a fixed 1500 × 432 px replica of the KRONOS front panel: encoders,
  faders, banks, FX switches, KARMA, X-Y pad, transport cluster.
- **EDIT** is one page whose **background artwork is swapped per page** and a
  **pool of controls is re-bound per page** by Lua. This "pooled controls"
  architecture is what keeps the panel at 895 controls while covering 215
  numbered pages plus the FX EDIT template and 7 247 parameters.

## The dump model

Editing is **dump-based**: the KRONOS can send the complete binary state of the
current object (a *dump*, function `0x4B`, packed 7-bit), and can receive a dump
into its edit buffer (same `0x4B`). The panel keeps a local copy of the dump in
memory (`KK.dump`), edits it bit-by-bit in Lua, and sends it back with **Apply**.

| Action | Direction | SysEx function | Meaning |
|---|---|---|---|
| Mode Request | → KRONOS | `F0 42 3x 68 12 F7` | sent once at panel load |
| Mode Data | ← KRONOS | `0x42` | current mode (COMBI/PROGRAM/GLOBAL/DISK/SEQUENCER/SAMPLING/SET LIST) |
| Mode Change | → KRONOS | `0x4E` | switch mode before selections |
| Dump request | → KRONOS | `0x4A` | "send me the current object" |
| Current Object Dump | ↔ | `0x4B` | receive = read; send = Apply to edit buffer |
| Slot write | → KRONOS | `0x49` | write dump to a bank slot |
| Store bank | → KRONOS | `0x4C` | save bank to non-volatile memory |
| Bank read request | → KRONOS | `0x4D` | KRONOS answers with `0x73` data messages |
| Reply | ← KRONOS | `0x24` | write completed — shown in clear |
| Parameter Change | ↔ | `0x43` | single real-time parameter (Tone Adjust, etc.) |
| KARMA param change | ← | `0x6D` | KARMA GE / settings echo |
| Drum Track param change | ↔ | `0x6E` | drum track on/mute |
| Master Volume | → | `F0 7F 7F 04 01 00 vv F7` | universal real-time SysEx |

SysEx header: `F0 42 3x 68 … F7` where `x = device channel − 1` (default channel 1
→ `30`). Dump payloads are 7-bit packed (`kkPack7`/`kkUnpack7` in Lua).

## Objects

Seven object types can be read (`0x4B`) and edited, chosen in the EDIT view's
OBJECT selector:

| ID | Object | Dump size |
|---|---|---|
| 0x00 | Program | 4 960 B |
| 0x01 | Combi | 7 810 B |
| 0x03 | Global | 24 708 B |
| 0x04 | Drum Kit | 38 424 B |
| 0x05 | Wave Sequence | 2 216 B |
| 0x0D | Set List | 69 416 B |
| 0x18 | Song | 13 076 B |

## Engines

A Program is either **HD-1** or **EXi** (two EXi slots, one of 8 engines: AL-1,
CX-3, STR-1, MS-20EX, PolysixEX, MOD-7, SGX-2, EP-1). The editor exposes
per-engine pages; which ones apply is decided by the engine bytes in the dump
(offsets 2558/3909, 0-based). The RACK's EXi1/EXi2 buttons choose which slot the
Tone Adjust encoders target.

## Live tracking

Besides dumps, the panel **tracks the KRONOS live**: incoming `CC0`/`CC32`/`PC`
update the bank/program display; Tone Adjust CCs move the encoders; `0x6D`/`0x6E`
update KARMA/GE/drum-track state. An embedded **PRELOAD** record per factory slot
(names, FX mask, KARMA scene/switches/faders, GE, engine) lets the RACK show the
right labels and switch states for the selected slot *without* requesting a
dump.

## VST3 / standalone duality

The same panel exports to both targets. As a VST3, 34 modulators (encoders,
faders, volume, mix and KARMA sliders) are exported as host parameters
(`modulatorVstExported`), the plug-in type is `Instrument|Synth`, and the panel
state rides with the DAW project. As a standalone EXE it runs in its own
resizable, zoomable window with its own MIDI settings. Both share the same
panel UID root, so only one VST3 build should be installed at a time.
