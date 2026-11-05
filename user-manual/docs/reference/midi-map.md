# MIDI map and SysEx functions

All channel-mode messages use the panel's **device channel** (default **1**).
The SysEx header is `F0 42 3x 68 … F7` with `x = channel − 1` (channel 1 → `30`).

## Sent by the panel

| Control | Message | Notes |
|---|---|---|
| Bank + program select | `CC0`=MSB, `CC32`=LSB, then `PC n` | sent in this order |
| Program ▲/▼, number field, name popup | same trio | — |
| PROG / COMBI buttons | SysEx `0x4E 02` / `0x4E 00` | mode change |
| Mode Request (at load) | `F0 42 3x 68 12 F7` | KRONOS answers `0x42` |
| Encoders 1–8 / faders 1–8 (Tone Adjust) | SysEx Parameter Change `0x43` (engine-dependent TYP/SOC/SUB/PID/IDX); fixed CC fallback: encoders `CC74,71,79,72,17,19,20,21`, faders `CC76,77,16,5,73,75,70,72` | fader 9 (Master) has no message yet in 1.0i — known limitation. Note: `CC72` is intentionally shared by encoder 4 (EG Release) and fader 8 (ENV R) |
| VOLUME | `F0 7F 7F 04 01 00 vv F7` | Master Volume 0–127 |
| MIXER/PAN sliders 1–8 | Parameter Change / mixer CCs (combi timbre volume & pan) | — |
| KARMA sliders 1–8 | `CC22`–`CC29` | — |
| KARMA switches 1–8 | `CC102`–`CC109` (127=on) | — |
| SCENE 1–8 | `CC30` | — |
| K ON / LATCH | `CC14` / `CC31` | — |
| SW1 / SW2 | `CC80` / `CC81` | — |
| FX 1–16 | effect on/off (SysEx) | IFX1–12, MFX1–2, TFX1–2 |
| GE ▲/▼/menu | GE parameter change | — |
| DT ON / DT MUTE | `0x6E` drum-track parameter change | Program mode |
| X-Y pad | `CC118` = X, `CC119` = Y, continuous while dragging | HOLD freezes |
| EDIT actions | **Read sound** `0x4A`, **Apply** `0x4B`, **Write →** `0x49`, **Store** `0x4C`, **Bank read** `0x4D` | see below |

## Received by the panel (tracked live)

| Message | Effect on the panel |
|---|---|
| `CC0` / `CC32` | bank MSB/LSB updated on the RACK |
| Program Change | program number updated |
| `CC22`–`CC29` | KARMA sliders move |
| `CC30` | KARMA scene lights |
| `CC102`–`CC109` | KARMA switch labels |
| `CC80`/`CC81` | SW1/SW2 labels |
| encoder/fader CCs | Tone Adjust controls move (no re-send) |
| SysEx `0x42` | mode shown in the message line |
| SysEx `0x4B` | dump received → EDIT pages fill in |
| SysEx `0x24` | "Reply 24" — write done |
| SysEx `0x6D` | KARMA / GE state (GE number shown) |
| SysEx `0x6E` | drum track on state |

## SysEx function reference

| Function | Name | Use in the panel |
|---|---|---|
| `0x12` | Mode Request | sent at panel load |
| `0x42` | Mode Data | KRONOS current mode |
| `0x43` | Parameter Change | real-time single parameters (Tone Adjust, 528 editor params) |
| `0x4A` | Current Object Dump Request | **Read sound** |
| `0x4B` | Current Object Dump | receive dump; **Apply** sends edited dump to edit buffer |
| `0x49` | Write to slot | **Write →** (Program/Combi only, writable banks) |
| `0x4C` | Store bank | **Store** (two-click confirm, 5 s) |
| `0x4D` | Bank read request | **Bank read** → replies `0x73` ×128 |
| `0x4E` | Mode Change | **PROG** / **COMBI** buttons |
| `0x6D` | KARMA parameter change | GE screens / KARMA tracking |
| `0x6E` | Drum Track parameter change | DT on / DT mute |
| `0x24` | Reply | write confirmation, shown in clear |
| `0x73` | Bank data message | bank read payload |
| `F0 7F 7F 04 01 00 vv F7` | Universal RT: Master Volume | **VOLUME** slider |

Dump payloads are **7-bit packed** (8-bit bytes → 7-bit stream) before being put
on the wire.
