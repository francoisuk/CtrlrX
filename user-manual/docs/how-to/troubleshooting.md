# Troubleshooting

What to check when the panel and the KRONOS don't seem to talk. Start with the
**message line** at the bottom of the RACK view: it echoes every message sent
(`->`) or received (`<-`), for example `-> CC0=0 CC32=8 PC=17` or
`<- mode 2 PROGRAM`. If the line stays empty, nothing is leaving or arriving —
work through the sections below in order.

## No answer to the Mode Request

At load, the panel sends a Mode Request (`F0 42 3x 68 12 F7`). If the message
line never shows the KRONOS mode:

1. Check the MIDI routing. Swapped input/output ports are the most common
   mistake: the panel's output must reach the KRONOS's input and vice versa.
2. Check the channel. The panel's device channel is 1 by default, and the
   SysEx header byte must match (`F0 42 3x 68 …` with `x = channel − 1`). Set
   the same channel on the KRONOS (Global > MIDI), then reload the panel —
   see [Connect MIDI and set the channel](midi-setup.md).
3. Check that the KRONOS is in a mode that answers MIDI. A Disk-mode dialog
   open on the KRONOS can block responses.
4. In a DAW, make sure the track's MIDI output is routed to the KRONOS and the
   KRONOS's output comes back to the DAW input the plug-in listens on.

## No Reply 24 after Write or Store

The KRONOS confirms writes with Reply 24 (`0x24`). If it never appears:

- Wait for the busy state to clear; the panel refuses further writes while one
  is in progress.
- Check that the destination bank is writable. GM, g(1)–g(9) and g(d) are
  read-only and refuse writes. **Write →** only works for Program and Combi
  objects — see [Saving presets](save-and-store.md).
- For **Store**, remember the two-click confirmation: the second click must
  come within 5 seconds of the first.
- If a write seems lost, press **Bank read** to pull the bank's current state
  from the KRONOS and resync the name list.

## Edits are refused ("truncated dump")

If the status line refuses edits or Apply with a truncated-dump message, the
received dump was incomplete. Press **Read sound** again and wait for the full
dump before editing.

## The panel and the KRONOS disagree

If the RACK shows a different sound than the KRONOS plays:

- Turn the program knob on the KRONOS (or press ▲/▼ on the panel): incoming
  `CC0`/`CC32`/`PC` resync the display.
- Press **Bank read** so the name popup reflects what is actually on the
  device, including slots written but not yet stored.
- Run only one panel instance against the KRONOS. Two instances each send
  their own selections and edits — the last writer wins, and the other panel
  keeps its own state until the KRONOS sends updates. See
  [Using the standalone application](use-standalone.md).

## Known limitations in 1.0i

- **SAVE** (PCG writer) is a stub: it shows a message instead of writing a
  file. Back up the KRONOS from the KRONOS itself (Disk mode > Save PCG) —
  see [Loading .PCG files](pcg-files.md).
- **Compare** has no action yet in 1.0i.
- Fader 9 (Master) on the RACK sends no MIDI message yet; use the **VOLUME**
  slider for master volume.
- Names shown in the editor are read-only; rename sounds on the KRONOS itself.
