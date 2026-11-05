# Select, audition and import sounds (banks, PCG)

How to move around the KRONOS memory from the RACK view: modes, banks, program
selection, the name popup, auditioning, and loading sounds from `.PCG` files.

## Modes: PROG / COMBI

The two big buttons **PROG** and **COMBI** put the KRONOS in Program mode
(SysEx `0x4E 02`) or Combi mode (`0x4E 00`). The panel sends the mode change
**before** any selection or SysEx when the KRONOS is in another mode
(GLOBAL, DISK, SEQUENCER, …), and the message line shows `-> 4E … then
CC0=… CC32=… PC=…` when that happens.

## Banks (14 buttons)

| Button | Bank | MIDI (MSB, LSB) | Notes |
|---|---|---|---|
| 1–6 | `I-A` … `I-F` | (0, 0…5) | internal factory banks |
| 7 | `I-G` (combi) / `GM` (program) | (121, 0) | GM is read-only for writes |
| 8–14 | `U-A` … `U-G` | (0, 8…14) | user banks — writable |
| + **UAA** toggle | `U-AA` … `U-GG` | (0, 15…21) | Program mode only; in Combi mode the panel normalizes back to `U-A`… |

The current bank is shown by the lit bank label. Bank changes made **on the
KRONOS** are tracked back onto the buttons (`CC0`/`CC32`).

## Selecting a program

- **▲ / ▼** — next / previous program (0–127), sent as a Program Change.
- **Number field** — type a 3-digit number (000–127) and press Enter.
- **Name popup** — click the name field to open the list of the 128 slots of the
  current bank and pick one directly. Names come from the embedded factory
  bank (*PRELOAD*) or from a loaded `.PCG` file — see [Loading .PCG files](pcg-files.md).
- Empty slots show what the KRONOS shows: *Init Program*, *Init EXi Program*,
  *Init Combi*.

Selection is sent as `CC0` (MSB), `CC32` (LSB), then `PC` — in that order, so a
following dump request reads the **new** sound.

## Audition and remote control from the RACK

- **PLAY** — momentary note-on: plays a note while held (remote audition of the
  selected sound from your computer keyboard position).
- **IMPORT** — copies the selected slot into the KRONOS edit buffer
  (sends the slot's bytes as a `0x4B` dump). The KRONOS plays it immediately;
  nothing is written to memory.
- **WRITE** (RACK) — writes the current edit buffer to the selected slot
  (`0x49`) — see [Saving presets](save-and-store.md).
- **PCG** — opens a `.PCG` file dialog (see [Loading .PCG files](pcg-files.md)).
- **SAVE** — PCG writer (stub in 1.0i: shows an honest message instead of
  writing a file).

The **monitor / message line** at the bottom of the RACK shows every message
sent or received (`-> CC0=0 CC32=8 PC=17`, `<- mode 2 PROGRAM`, …) — use it to
confirm the link is alive.
