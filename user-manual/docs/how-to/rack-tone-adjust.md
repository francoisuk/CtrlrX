# RACK: Tone Adjust encoders and faders

The 8 encoders (`kkEnc01`–`kkEnc08`, with their label strips) and the 8 faders
(`kkFdr1`–`kkFdr8`, with their labels) plus the 9th fader implement the KRONOS
**Tone Adjust** controls. What each one edits depends on the current sound —
the labels above the controls update automatically.

## Which engine the encoders edit

- In **Program mode**, the **EXi1 / EXi2** buttons choose which oscillator slot
  (EXi 1 or EXi 2) the encoders/faders target. Only slots actually used by the
  program are selectable; the message line says so otherwise.
- The current engine (HD-1 or one of the 8 EXi engines: AL-1, CX-3, STR-1,
  MS-20EX, PolysixEX, MOD-7, SGX-2, EP-1) determines the 16 labels — the map is
  read from the current program's dump, or from the embedded PRELOAD record of
  the selected slot when no dump is loaded.
- In **Combi mode**, the **TIMBRE** selector (1–16) chooses the timbre whose
  Tone Adjust the encoders edit.

## What moving a control sends

- Each encoder/fader position is sent as a SysEx **Parameter Change**
  (function `0x43`, with the parameter's TYP/SOC/SUB/PID/IDX taken from the
  Tone Adjust map) — this is the same real-time path the KRONOS front panel
  uses, so the KRONOS display follows immediately.
- Slots that have no stored parameter keep a fixed **CC** fallback
  (encoders `CC74, 71, 79, 72, 17, 19, 20, 21`; faders `CC76, 77, 16, 5, 73, 75,
  70, 72`). See [MIDI map](../reference/midi-map.md). Note that `CC72` is
  intentionally shared by encoder 4 (EG Release) and fader 8 (ENV R).
- **Fader 9 (Master)** shows the Master label but has **no MIDI message
  assigned yet** in 1.0i (known limitation) — the message line says so when you
  move it. Use the **VOLUME** slider for master volume.
- The **VOLUME** slider is the KRONOS **Master Volume** (0–127), sent as
  Universal Real Time SysEx `F0 7F 7F 04 01 00 vv F7` — the level of the main
  outputs after the total effects.

## MIXER / PAN

The 8 **mix sliders** (`kkMix1`–`kkMix8`) are shared between two views:

- **MIXER** mode: timbre volumes 1–8 (Combi) — the KRONOS mixer page.
- **PAN** mode: timbre pan positions 1–8.

Toggle with the **MIXER** / **PAN** buttons. In Program mode the mix sliders
target the current program's output levels; the message line notes when there
is nothing to send in the current mode.

## Other RACK switches

- **SW1 / SW2** — assignable switches, sent as `CC80` / `CC81` (127 = on).
- **Module LEDs (MASTER / A / B / C / D)** + **MODCTRL** — select the KARMA
  module (Master, A–D) shown on the GE screens and in the KARMA section.
- Moving a control on the **KRONOS** itself updates the panel: incoming
  encoder/fader CCs move the on-screen controls without re-sending
  (no feedback loops).

The modulator names cited here (`kkEnc01`…, `kkFdr1`…, `kkMix1`…) and their
exact roles are listed in the [Modulator inventory](../reference/modulators.md).
