# /docs — Korg references and consolidated knowledge

This folder holds the official Korg documentation for the Kronos
(PDFs, plus two parameter-guide folders) and the consolidated
knowledge document that summarises what was established about the
PCG format, SysEx, MIDI, and the Max for Live work. It is the
reference layer for the panel project: anything the base M4L device
does not already encode is looked up here.

Since 2026-10-24, the **machine-readable** knowledge (bit-level
tables, SysEx notes, ground truth) lives in `/reference` — see
`reference/README.md`. This folder keeps the original Korg PDFs and
the French consolidated document; use `/reference` first.

## Contents

```
docs
├── CONNAISSANCES_KRONOS_PCG.md      consolidated knowledge (read first)
├── KRONOS_Param_Guide_E4/           parameter guide by OS version (folders)
├── KRONOS_Param_Guide_E10/
├── KRONOS_Param_Guide_EN3/
├── KRONOS_Param_Guide_E10.pdf       (also present as PDF where listed)
├── KRONOS_Operation_Guide*.pdf      full user manual
├── KRONOS_VNL_*.pdf                 Voice Name List (programs, GEs)
├── KRONOS_*.pdf                     any other Korg reference
└── DOCS_README.md                   this file
```

Note: the parameter guides and the MIDI implementation exist here as
PDFs and as extracted text/CSV/JSON tables in
`reference/ref-kronos/midi/` and `reference/ref-kronos/tables/`.

## CONNAISSANCES_KRONOS_PCG.md

The single most useful document of the older consolidation. It
gathers, in one place, everything established by
reverse-engineering and hardware testing:

- PCG file structure, block format, checksums, DIV1, INI1/INI2
- Object layouts: program, combination, drum kit, wave sequence,
  Set List, Global
- Sample references (OS 1 single-byte vs OS 2+ UUID)
- The six factory PRELOADs and the two OS 3 orderings
- SysEx functions, MIDI Bank/Program Change, and the Max for Live
  findings
- Pitfalls for an editor / librarian
- A proposed architecture for the editor

**Read it before looking at any PDF.** It cross-references the
extracted tables now in `reference/ref-kronos/`.

**Authoritative copy.** This `docs/` copy is the one that counts for
the panel project. The legacy `consolidate/old/` folder may still hold
an older copy — ignore it; do not edit it either. When the document
is updated, update this copy.

## The Korg PDFs

The official Korg manuals. Used when the extracted tables in
`reference/ref-kronos/` are ambiguous or a section is missing.

- **MIDI implementation** — resolves SysEx function bytes when
  `reference/ref-kronos/midi/KRONOS_MIDI_SysEx.txt` is unclear.
- **Parameter guide** — confirms parameter ranges and bit layouts.
- **Voice Name List** — fills gaps in the extracted JSON (for
  example, GE entries 3200–3583 missing from `ge_kronos.json`).
- **Operation guide** — global settings (MIDI channel, SysEx ID,
  Bank Map).

The PDFs are the originals. The JSON/TXT extractions in
`reference/ref-kronos/` are the preferred input for the panel
because they parse cleanly.

## How the panel project uses this folder

- **Decoding SysEx function bytes** — check
  `CONNAISSANCES_KRONOS_PCG.md` first, then
  `reference/ref-kronos/docs/SYSEX_KRONOS.md` (hardware-verified),
  then the MIDI implementation PDF if still unclear.
- **Checking parameter ranges** — bit-level table entries in
  `reference/ref-kronos/midi/` and `tables/` first, parameter guide
  PDF as a sanity check.
- **Understanding the Kronos global settings** — operation guide,
  or the consolidated document.
- **Pitfalls and known errors** — the consolidated document.

## Rules

1. **This folder is read-only for the panel project.** The panel
   lives under `/panels/KronosKontrol/`. Corrections to the
   consolidated document go into the document itself, not into a
   separate file.
2. **Prefer the consolidated document and the `/reference` tables
   over the PDFs.** Return to the PDFs only when a table is missing
   data.
3. **Do not cite PDF page numbers to the AI assistant** unless the
   extract is unclear. The tables are easier to parse.
4. **One authoritative copy of `CONNAISSANCES_KRONOS_PCG.md`.** See
   the "Authoritative copy" note above.

## When to read

- When a SysEx field cannot be decoded from the tables.
- When the base M4L device has no message for a parameter the panel
  needs.
- When the panel's global settings section needs a definitive list of
  valid values (MIDI channels, Bank Map options, SysEx IDs).
- Whenever the layout or the AI assistant refers to a "ground-truth"
  or "reference" file.

*(Phase A is over; it no longer needs this folder as a primary input —
see `panels/KronosKontrol/PHASE_A.md`.)*
