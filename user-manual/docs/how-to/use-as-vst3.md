# Using Kronos Kontrol as a VST3 in a DAW

The VST3 build is an `Instrument | Synth` plug-in (manufacturer *FrRs*, plug-in
name *Kronos Kontrol*). It behaves like any other plug-in: the panel window opens
in the DAW, the panel's state is saved with the DAW project, and a set of panel
controls is exposed to the host as **automatable parameters**.

## Host-exposed parameters (34)

These modulators are exported to the VST3 (`modulatorVstExported`), so the DAW
can automate them and they appear in the host's parameter list:

| Group | Controls | Count |
|---|---|---|
| Encoders (Tone Adjust) | `kkEnc01`–`kkEnc08` | 8 |
| Faders | `kkFdr1`–`kkFdr9` | 9 |
| Volume | `kkVol` | 1 |
| Mix sliders | `kkMix1`–`kkMix8` | 8 |
| KARMA sliders | `kkKSlid1`–`kkKSlid8` | 8 |

Moving them in the DAW's automation moves the panel controls, and they send the
same MIDI/SysEx to the KRONOS as a manual move. Conversely, values the KRONOS
sends back update the controls and therefore the host's parameter display.

## State save / recall

The plug-in saves the panel state (all control positions) with the DAW project
(`luaPanelRestoreState`). When the host restores a project, the panel redraws
the Tone Adjust labels and MIXER/PAN values of the restored selection over the
restored positions, so the RACK always reflects the sound the project points to.

## MIDI in a DAW

Route the KRONOS to the DAW's MIDI ports and select them in the plug-in/host
MIDI settings (see [Connect MIDI and set the channel](midi-setup.md)). The
plug-in sends on the device channel (default 1).

## Window size and scaling

The panel is a fixed 1500 × 432 px design. Use the DAW's **plug-in GUI
scaling** (REAPER: Ctrl+drag corner / track FX chain scaling; Ableton, Bitwig,
FL Studio have their own zoom) to fit smaller screens. The right-hand column of
the panel (object selector, message field, version label, x ≥ 960) is the first
thing cut off at 1:1 on a 1366 px screen.

## Only one version installed

All builds share the **same VST3 UID**, so the DAW lists a single *Kronos Kontrol
(Francois Rossi)* entry and loads whichever file it finds first. Before testing or
updating, rename the old build to `.vst3.disabled` (quit the DAW first — it keeps
the DLL locked), rescan, and verify which file was loaded.

## Licensing

Restricted release builds show the EULA window at first launch inside the DAW;
accept once. Test builds (unrestricted instances) skip it.
