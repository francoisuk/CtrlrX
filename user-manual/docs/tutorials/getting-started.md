# Getting started (VST3 & standalone)

This tutorial takes you from a fresh install to a working connection with your
KRONOS, using either build of **Kronos Kontrol 1.0i**.

## 1. Install the build you need

### Standalone EXE

1. Copy `Kronos Kontrol 1.0i_restricted.exe` (from `panels/KronosKontrol/exe/`)
   to a folder of your choice.
2. Double-click it. On the **first launch** of a restricted build, the
   *License agreement* window appears — read the EULA and click **Accept**.
3. The standalone window opens on the **RACK** view with a splash/About screen;
   click anywhere (or wait 5 s) to dismiss it.

### VST3 plug-in

1. Copy `Kronos Kontrol.vst3` (from `panels/KronosKontrol/vst3/`) into a folder
   that is in your DAW's VST3 scan path.
2. In the DAW: **rescan plug-in paths**, then insert *Kronos Kontrol
   (Francois Rossi)* on a track (it is an `Instrument | Synth` plug-in).
3. Open the plug-in window.

!!! warning "Only one version installed"
    Every Kronos Kontrol VST3 build carries the **same plug-in UID**. If you keep
    two versions in the scan path, the DAW may load the older one. Rename older
    builds to `.vst3.disabled`.

## 2. Connect the KRONOS

1. Connect the KRONOS to the computer with a USB cable and power it on.
2. In Kronos Kontrol, open the **MIDI settings** of the standalone (menu) or of
   your DAW (the plug-in uses the host's MIDI ports), and set:
   - **Input** = the MIDI port that receives from the KRONOS
   - **Output** = the MIDI port that sends to the KRONOS
   - The panel's **device channel** is **1** by default — see
     [Connect MIDI and set the channel](../how-to/midi-setup.md) if you need
     another channel.
3. Close/reopen the plug-in window (or restart the standalone) so the new ports
   are picked up.

## 3. First launch behaviour

When the panel loads it immediately sends a **Mode Request**
(`F0 42 3x 68 12 F7`) to the KRONOS. The KRONOS replies with its current mode
(*Mode Data*, `0x42`), which the panel displays in the message line at the bottom
of the RACK view — e.g. `KRONOS mode 2 PROGRAM`. If you don't see an answer:

- check the MIDI routing (ports swapped is the most common mistake),
- check the channel,
- check that the KRONOS is not in a mode that ignores MIDI (Disk mode with a
  dialog open, etc.).

For more failure cases (no Reply 24, truncated dumps, panel/device mismatch),
see [Troubleshooting](../how-to/troubleshooting.md).

The panel also tracks the KRONOS live: bank changes (`CC0`/`CC32`), program
changes (`PC`) and the Tone Adjust values the KRONOS itself sends are reflected
on the RACK controls automatically.

## 4. Screen size

The panel is a **fixed 1500 × 432 px** design and does not resize by itself:

- On a screen of at least **1500 px width** (~500 px tall for the window) it
  displays 1:1 — recommended.
- In a DAW, use the host's **GUI zoom/scaling** (REAPER, Ableton, Bitwig,
  FL Studio all offer it) on smaller screens.
- In the standalone, the window is resizable and the panel **zooms with
  Ctrl + mouse wheel** (1 %–1000 %).
- On remote desktop, what matters is the **host session's** resolution, not the
  client's.

## 5. Your first sound selection

On the RACK view:

1. Press **PROG** (program mode) or **COMBI** (combi mode). The panel sends a
   *Mode Change* (`0x4E`) if the KRONOS is not already in that mode.
2. Press one of the **14 bank buttons** — `I-A`…`I-F` (1–6), `I-G`/`GM` (7),
   `U-A`…`U-G` (8–14). The **UAA** button switches the user banks to the doubled
   `U-AA`…`U-GG` set (Program mode only).
3. Press **▲ / ▼** (or type a number in the 3-digit field, or pick a name in the
   name popup) to select a program. The panel sends `CC0` (bank MSB),
   `CC32` (bank LSB) and a **Program Change** to the KRONOS.

The KRONOS now plays the selected sound. Next:
[Tutorial: edit and save a Program](edit-and-save-a-program.md).
