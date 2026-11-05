# Using the standalone application

The standalone EXE needs no DAW: it opens its own window on the RACK view and
talks MIDI directly.

## Launch

- Double-click `Kronos Kontrol 1.0i_restricted.exe`.
- First launch of a restricted build: accept the **License agreement**.
- The splash/About screen dismisses on click or after 5 s. The **Kronoscopie
  logo** button (bottom-right of the RACK) reopens the About screen; it carries
  links (web, book, support) that open in your default browser.

## Window and zoom

- The panel design is fixed at **1500 × 432 px**, but the standalone **window is
  resizable**: resize it and the panel view scales to fit.
- Fine zoom: hover the panel and use **Ctrl + mouse wheel** (1 %–1000 %).

## MIDI setup

Use the standalone's MIDI settings (menu bar) to pick the input/output ports
connected to the KRONOS. Defaults: device channel **1**, real-time messages
ignored, 15 ms global message delay. Details in
[Connect MIDI and set the channel](midi-setup.md).

## Session state

The standalone remembers its control positions between runs (like the VST3 does
with a DAW project): on reopen, the RACK redraws the Tone Adjust and mixer
values of the last selection.

## Do not run two instances against one KRONOS setup casually

Each instance sends its own Mode Request, selections and edits. One panel
controlling the KRONOS at a time keeps the displays in sync; if you run several,
the last writer wins and the others still show their own state until the KRONOS
sends updates.
