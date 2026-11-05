/korg

**EXECUTED 2026-10-14 — Phase A is complete.** The parameter map CSV
exists at `panels/KronosKontrol/parameter_map.csv` (124 rows after the
2026-10-24 amendment; see `panels/KronosKontrol/PHASE_A.md`). This
prompt is kept for the record. Paths below were corrected on
2026-10-24 (`C:\Korg\CTRLR Project` -> `C:\Korg\ctrlr-project`;
`consolidate/...` -> `reference/ref-kronos/...`) and relocated on 2026-10-26
under the kronos-corpus root — live path `C:\Korg\kronos-corpus\ctrlr-project`
(`C:\Korg\ctrlr-project` no longer exists).

---

Read the following before responding:
- C:\Korg\kronos-corpus\ctrlr-project\panels\KronosKontrol\PROJECT_LAYOUT.md
- C:\Korg\kronos-corpus\ctrlr-project\panels\KronosKontrol\PHASE_A.md
- C:\Korg\kronos-corpus\ctrlr-project\docs\CONNAISSANCES_KRONOS_PCG.md

Current task:
Execute Phase A as described in PHASE_A.md.

Deliverable for this session:
the parameter map CSV (parameter_map.csv).

Primary inputs (ground truth):
- reference/ref-kronos/m4l/base/kronos_kontrol_v1.json
- reference/ref-kronos/midi/KRONOS_MIDI_SysEx.txt

Secondary inputs (bit-level ranges):
- reference/ref-kronos/midi/Prog_HD-1.txt
- reference/ref-kronos/midi/Prog_EXi.txt
- reference/ref-kronos/midi/Prog_EXi_Common.txt
- reference/ref-kronos/midi/CombiAndSongTimbreSet.txt
- reference/ref-kronos/tables/*.csv|json

Reference (consult only when the tables above are silent):
- docs/                            (Korg parameter guides, PDFs)
- reference/ref-kronos/docs/SYSEX_KRONOS.md (hardware-verified SysEx)

Constraints:
- Work only under panels/KronosKontrol/.
- Do not modify /build, /reference, /docs, or /panels/TR-Rack-Editor-main.
- SysEx ground truth is the base patch and its fix scripts; do not
  re-derive from the MIDI Implementation guide. Where the synthesis
  docs and SYSEX_KRONOS.md disagree, SYSEX_KRONOS.md wins.
- If a decode is genuinely ambiguous, consult the files in
  docs/ before deciding. State the source
  used in the CSV row's Source column if it is not a reference/ table.
- Do not invent bytes. If nothing resolves the ambiguity, leave the
  field as "unknown" and continue; flag it at the end of the output.
- Stop after the CSV. Do not write Ctrlr code. Do not propose panel
  layout.
