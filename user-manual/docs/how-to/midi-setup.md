# Connect MIDI and set the channel

Kronos Kontrol talks to the KRONOS with ordinary MIDI messages plus Korg SysEx.
This guide covers ports, channel and the panel's MIDI behaviour.

## Ports

- **Standalone**: menu → MIDI/audio settings; choose the **input** and **output**
  ports connected to the KRONOS (USB MIDI shows up as a port pair).
- **VST3**: the plug-in uses the host DAW's MIDI routing. Route one track's
  MIDI output to the KRONOS and the KRONOS's output back to the DAW input that
  the plug-in listens on.

The panel settings that define the link (stored in the panel):

| Setting | Default | Meaning |
|---|---|---|
| Device channel (`panelMidiControllerChannelDevice`) | 1 | MIDI channel used for all CC/PC traffic with the KRONOS |
| Input channel (device) | 1 | channel the panel accepts incoming messages on |
| Output channel (device) | 1 | channel the panel sends on |
| Global delay | 15 ms | delay inserted between consecutive outgoing messages |
| Snapshot delay | 25 ms | delay between messages of a multi-message snapshot |
| Real-time ignored | yes | MIDI clock/transport bytes are ignored |

## What the panel sends

- **Program selection**: `CC0` = bank MSB, `CC32` = bank LSB, then a Program
  Change — on the device channel.
- **Tone Adjust / faders**: SysEx *Parameter Change* (function `0x43`) with the
  engine-dependent parameter IDs; slots without a mapped parameter fall back to
  fixed CCs (see [MIDI map](../reference/midi-map.md)).
- **KARMA sliders**: `CC22`–`CC29`; **KARMA on switches**: `CC102`–`CC109`;
  **scene**: `CC30`; **K ON**: `CC14`; **LATCH**: `CC31`; **SW1/SW2**: `CC80/81`.
- **Master volume**: Universal Real Time SysEx `F0 7F 7F 04 01 00 vv F7`.
- **Mode change**: SysEx `0x4E`; **dump request** `0x4A`; **dump send** `0x4B`;
  **slot write** `0x49`; **store bank** `0x4C`; **bank read request** `0x4D`.
- The full table: [MIDI map and SysEx functions](../reference/midi-map.md).

## What the panel listens to

On the device channel it tracks, and mirrors on the RACK:

- `CC0` / `CC32` — bank changes made on the KRONOS itself,
- Program Change — program changes made on the KRONOS,
- `CC22`–`CC29`, `CC30`, `CC102`–`CC109`, `CC80/81` — KARMA and scene state,
- the encoder/fader CCs — Tone Adjust moved on the KRONOS,
- SysEx `0x42` (Mode Data), `0x4B` (dump), `0x24` (Reply), `0x6D`/`0x6E`
  (KARMA / Drum Track parameter changes).

Every recognized message is echoed in the **message line** (bottom of the RACK
view), e.g. `<- CC74 = 96` or `<- mode 2 PROGRAM`.

## Changing the channel

The KRONOS MIDI channel is set on the KRONOS itself (Global > MIDI). The panel's
device channel is a panel setting; when you change it, reload the panel so the
SysEx header byte (`F0 42 3x 68 …`, `x = channel − 1`) matches.

## MIDI thru

The panel has configurable thru options (device↔device, device↔host, host↔host,
with optional channelization). By default everything is off, so the panel itself
does not forward MIDI — use your DAW's routing if you need the panel and other
gear to share a controller.
