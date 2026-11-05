# USER MANUAL NOTES — Kronos Kontrol (VST3)

Draft notes for the user manual, to be written when the app is delivered (0.98a and after).
English draft (project language); French translation later if wanted.
Each numbered entry below is one future manual section, written as it should appear.

Journal reference: Tournée 9j, Addenda 9f-35..9f-38 (screen-size Q&A verified against
the Ctrlr 5.6.23 sources in build/ctrlr-master; 0.97j main-panel fixes + English-only
pass — see RESUME.md at the kronos-corpus root for the full state).

---

## 1. Display requirements / screen size

The Kronos Kontrol panel has a fixed native size of **1500 x 414 pixels**. The layout is
absolute pixels: the panel does not resize or adapt to the screen at runtime.

- Minimum recommended screen for full use at 1:1: **1500 px wide, ~500 px tall**
  (414 px panel + plugin window chrome; the Ctrlr editor adds a ~20 px menu bar).
- On a narrower screen (e.g. 1366x768), the right-hand column of the panel (object
  selector, monitor field, version label — panel x >= 960) is cut off at 1:1.
  Workarounds:
  - move the floating plugin window so the cut-off part is reachable (most DAWs allow
    plugin windows partly off-screen);
  - use the DAW's plugin-GUI scaling/zoom when available (Bitwig, Ableton, REAPER,
    FL Studio, ...);
  - use the Ctrlr standalone instead: its window is resizable and the panel view zooms
    with **Ctrl + mouse wheel** (1%-1000%).
- Remote desktop / remote sessions: the panel renders on the host PC at the remote
  *session* resolution. The client machine's screen size does not matter (the video
  stream is scaled). Check the host session's width, not the laptop's.

---

## Planned sections (not drafted yet)

- Safety: Apply = edit buffer only (SysEx 0x4B); slot write (0x49) and Store (0x4C) are
  Program/Combi only (v1); Drum Kit / Wave Seq apply in Program mode; Global applies in
  any mode (edit buffer only).
- First connection: MIDI ports, channel, Mode Request sent at panel load.
- The RACK tab (banks, encoders, KARMA, X-Y pad) — after the artwork redesign.
- The EDITOR tab: object selector, per-object pages, Apply / Write / Store.
- PCG cluster: PCG / IMPORT / WRITE / PLAY / SAVE.
