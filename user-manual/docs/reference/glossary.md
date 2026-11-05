# Glossary

- **Apply** — EDIT action (SysEx `0x4B`): sends the panel's edited dump to the
  KRONOS **edit buffer**. Not permanent.
- **Bank** — a group of 128 slots. Internal `I-A`…`I-G`, GM/g (read-only), user
  `U-A`…`U-G` and (Program mode) doubled `U-AA`…`U-GG`.
- **Combi** — a KRONOS combination: up to 16 timbres with volume/pan, effects,
  KARMA. Object `0x01`.
- **Dump** — the complete binary state of one object, exchanged with SysEx
  `0x4B` (7-bit packed).
- **Edit buffer** — the KRONOS's temporary "current" sound. Apply/Import write
  here; nothing is stored until Write + Store.
- **EDIT** — the panel's editor view (tab 1), as opposed to the RACK.
- **EXi** — the KRONOS's second-generation oscillator slots (EXi 1 / EXi 2),
  each running one of 8 engines (AL-1, CX-3, STR-1, MS-20EX, PolysixEX, MOD-7,
  SGX-2, EP-1). Programs are either HD-1 or EXi.
- **FX EDIT** — the editor page template for effect slots (IFX/MFX/TFX), with
  198 effect types.
- **GE** — Global Edit parameters (arp models, …), shown on the two GE screens.
- **HD-1** — the KRONOS's first-generation oscillator engine. A Program is
  either HD-1 or EXi; the editor switches the GENERAL page variant and the
  applicable engine pages accordingly.
- **KARMA** — the KRONOS phrase-generation/arpeggiation system; controlled from
  the RACK (8 switches, 8 sliders, 8 scenes, K ON, LATCH).
- **Modulator** — Ctrlr term for one panel control + its value (895 in this
  panel). 34 are exported as VST3 parameters.
- **PCG** — Korg Program/Combi/Global file (`.PCG`); loadable with the **PCG**
  button; also the name of the transport-cluster button.
- **PRELOAD** — the factory-bank records embedded in the panel (names, FX mask,
  KARMA, GE, engine per factory slot) used to display slot info without a dump.
- **RACK** — the panel's controller view (tab 0), a replica of the KRONOS front
  panel.
- **Reply 24** — KRONOS SysEx `0x24`, confirms a completed write; shown in clear
  in the status line.
- **Slot** — one memory location (bank × 0–127) holding a program/combi.
- **Store** — EDIT action (`0x4C`): saves the whole current bank to the KRONOS
  non-volatile memory. Two clicks within 5 s.
- **SysEx** — MIDI system-exclusive messages. The panel speaks the KRONOS
  dialect with header `F0 42 3x 68 … F7` (`x = channel − 1`); see
  [MIDI map and SysEx functions](midi-map.md).
- **Timbre** — one of the 16 parts of a Combi (oscillator, volume, pan, mute).
  The RACK's **TIMBRE** selector chooses which timbre the Tone Adjust controls
  edit in Combi mode.
- **Tone Adjust** — the 8 encoders + faders of the KRONOS front panel, mapped
  per engine/timbre by the panel; sent as Parameter Change (`0x43`).
- **UAA** — RACK toggle that doubles the user banks from `U-A`…`U-G` to
  `U-AA`…`U-GG` (Program mode only).
- **Write** — EDIT action (`0x49`): copies the dump to the destination slot.
- **X-Y pad** — vector control on the RACK; HOLD freezes the cursor.

## Panel identity

| Item | Value |
|---|---|
| Panel name | Kronos Kontrol |
| Version | 1.0i |
| Panel UID | `kkKronosKontrol` |
| Vendor / author | KORG / Francois Rossi (Kronoscopie) |
| VST3 manufacturer ID / instance UID | `FrRs` / `KrKt` |
| Plug type | Instrument \| Synth |
| Target device | Korg KRONOS, OS 3.2.3 |
| Native panel size | 1500 × 432 px |
| Modulators | 895 |
| Editor pages | 215 numbered pages + FX EDIT template = 216 page views (7 object sets) |
| Editor parameters | 7 247 |
