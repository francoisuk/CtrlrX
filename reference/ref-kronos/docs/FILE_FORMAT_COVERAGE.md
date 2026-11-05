# File-format coverage — pcglib

What pcglib reads, writes and converts, per Korg file format, with the
verification evidence. Audited October 22, 2026 (Tier 2, item 4);
extended October 23, 2026 (v1.6.1 — ROADMAP M5/M6: OASYS support and
KRONOS↔OASYS conversion).

pcglib is a librarian for the KORG **KRONOS**, **NAUTILUS** and
**OASYS**: it manages PCG patch files end-to-end and also reads/saves
SNG song files. It does not touch KSC sample data (proprietary; only
referenced by name inside SNG). The `pcglib` CLI accepts PCG only.

_Scope note (October 22, 2026): OASYS support and KRONOS↔OASYS conversion
are now in project scope (PROJECT.md; ROADMAP M5/M6). **Extended
October 23, 2026:** M5/M6 have landed (v1.6.1) — the OASYS coverage and
evidence below cover the shipped build. **Stage 5 (October 23, 2026):**
the CLI `convert` command now covers KRONOS↔OASYS both ways (app +
CLI + python port byte parity)._

## Coverage matrix

| Format | Read | Write (round-trip) | Convert KRONOS <-> NAUTILUS | `pcglib` CLI | Notes |
|---|---|---|---|---|---|
| **PCG** (programs/combis/kits/wave seqs/set lists/global) | yes | yes — rebuilt (SDB1 index, chunk checksums, true PCG1 size) | yes — both directions, byte-identical to the Python oracle | yes — `info`, `validate`, `convert`, `rename`, `copy` | Fully supported; hardware-verified on the KRONOS (M2/M3/M4) |
| **SNG** (songs) | yes (`SongFileReader`) | yes — byte-identical (writes the loaded content; not rebuilt on edit) | **no** — the converters take a `PcgMemory` only | **no** — the CLI rejects non-PCG | Songs reference samples by name; the sample sets differ per synth, so cross-synth song conversion is not defined |
| **KSC** (sample data) | **no** | **no** | **no** | **no** (rejected) | Sample data is not handled; it is proprietary/restricted and only referenced by name inside SNG (`SampleFileName`) |

### Per-synth coverage (PCG)

| Synth | Read | Write (round-trip) | Convert | `pcglib` CLI | Notes |
|---|---|---|---|---|---|
| **KRONOS** (OS 1.x–3.2.x) | yes | yes — rebuilt (SDB1 index, chunk checksums, true PCG1 size) | K↔N yes (K→N: OS 2.x/3.x sources only); K→O yes (OS 2.x/3.x sources only) | yes — `info`, `validate`, `convert`, `rename`, `copy` | Fully supported; hardware-verified (M2/M3/M4) |
| **NAUTILUS** | yes | yes — rebuilt (chunk checksums recomputed since the v1.6 amendment) | N↔K yes (both directions) | yes — `info`, `validate`, `convert`, `rename`, `copy` | Hardware-verified (v1.2) |
| **OASYS** (v1.6.1) | yes | yes — verbatim (the OASYS stores no content-dependent checksums; bank chunk fields are version-only) | O↔K yes — app (File menu) + CLI `convert -t`, both directions | yes — `info`, `validate`, `convert` (K↔N + K↔O via `-t`) | Round-trip byte-identical on all 7 factory/OASYS files; categories display as names |

## Where the support lives

- Format detection: `KorgFileReader.GetFileType` reads header byte `0x5`
  (`00` = PCG, `01` = SNG); anything else is rejected
  (`NotSupportedException`).
- PCG read/write: `PcgFileReader` / `PcgMemory.SaveFile` (rebuilds the
  SDB1 index, recomputes chunk checksums, writes the true PCG1 size).
- SNG read/write: `SongFileReader` / `SongMemory.SaveFile` (writes the
  loaded content back byte-identically).
- Conversion: `KronosToNautilusConverter` / `NautilusToKronosConverter`
  (KRONOS↔NAUTILUS) and `KronosToOasysConverter` /
  `OasysToKronosConverter` (KRONOS↔OASYS) — all four `PcgMemory`-only
  (no SNG path). All four are reachable from the app File menu and from
  the CLI `convert` command (`-t nautilus|kronos|oasys`).
- CLI: `src/pcglib/Program.cs` — `ReadHeader` accepts a KRONOS, NAUTILUS
  or OASYS PCG header; `info`/`validate` cover all three; `convert`
  covers KRONOS↔NAUTILUS and KRONOS↔OASYS (`-t nautilus|kronos|oasys`,
  defaulting to the natural opposite of the source model).
- OASYS checksums: the OASYS stores no content-dependent checksums
  (bank chunk fields are version-only, low 16 bits always 0 — verified
  on all 7 factory/OASYS files), so OASYS saves are verbatim and
  `PcgChecksum.ValidateOasys` validates the version-only bank fields.

## Verification evidence

- **PCG** — 60/60 pcglib MSTest tests pass on the CI filter (factory
  round-trip byte-identical, chunk checksums, KRONOS↔NAUTILUS
  conversion, NAUTILUS combi bank letters, OASYS read/write,
  KRONOS↔OASYS conversion both directions) + 11/11 xUnit (synthetic
  PCG round-trips, CLI smoke tests). `pcglib validate` on the KRONOS
  OS 3.2 factory PRELOAD.PCG: all chunk checksums valid.
  `pcglib info` on the NAUTILUS factory PRELOAD.PCG: detected as
  NAUTILUS.
- **SNG** — `SngFileTest` (KRONOS + NAUTILUS factory SNG): read,
  detected as `FileType.Sng`, saved, byte-identical round-trip — 2/2
  pass. OASYS SNG uses the same shared path (`OasysFactory` →
  `OasysSongFileReader`; verbatim byte-identical save, enabled in
  v1.6.1).
- **SNG / KSC in the CLI** — `pcglib info <file.SNG>` and
  `pcglib validate <file.KSC>` are rejected ("not a KORG
  KRONOS/NAUTILUS/OASYS PCG file", exit code 2), confirming the CLI is
  PCG-only.
- **OASYS PCG (v1.6.1)** — all 7 factory/OASYS files (PRODUCER.PCG +
  6 user banks) open as OASYS, round-trip byte-identical, rename edits
  save cleanly; categories display as names through the built-in
  factory tables (`DefaultCategoryNames`, no GLB1 needed);
  `pcglib info`/`validate` accept OASYS headers (all 7 validate).
  PRODUCER.PCG ("KORG Factory New") is Korg's last factory file for
  the OASYS — an OS 1.3 rearrangement of the original release (the
  final OASYS OS is 1.3, not 1.1).
- **KRONOS↔OASYS conversion (v1.6.1)** — both directions in the app
  (File menu) and in the CLI (`convert -t oasys` / `convert -t kronos`;
  the python port is byte-identical to the CLI on all four directions).
  Verified end-to-end on every factory file: OS 3.2, OS
  3.1 and OS 2 KRONOS PCGs (incl. the KRONOS X bank order and the
  KRS-06 "Extra Sound Data" files) convert to OASYS and re-open
  through the model with names, categories, OSC modes, zone-A effects,
  zone MS types and combi timbre program references preserved; all 7
  factory/OASYS files convert to KRONOS OS 3.x shape and re-open as
  KRONOS. Program OSC payloads, OASYS v1/v2 engine extension bytes,
  drum kits and wave sequence sounds are defaulted (no verified OASYS
  parameter map); set lists are dropped on K→O (the OASYS SLS1 layout
  is unverified). K→O is offered for OS 2.x/3.x sources only; OS 1.x
  is rejected with a clear message.
- **KRONOS→NAUTILUS conversion gate (v1.6.1 amendment)** — K→N is
  offered for OS 2.x/3.x sources only (the same gate as K→O): OS 1.x
  is a different fiche family and is rejected with a clear message in
  the app menu, the converter and the python port; the CLI inherits
  the gate. Verified end-to-end: the OS 3.2 / 3.1 / 2 factory
  PRELOAD.PCG files convert byte-identical to the pre-amendment
  outputs; the OS 1.x PRELOAD.PCG is rejected.

## Scope decisions

- **KSC is out of scope.** Sample data is proprietary/restricted (never
  committed) and is not part of the librarian; only the sample *names*
  inside SNG regions are surfaced.
- **SNG conversion is not defined.** A song references samples that are
  specific to each synth, so a KRONOS song does not map onto a NAUTILUS
  (and vice versa). Set-list conversion already reports song references.
- **The CLI is PCG-only.** SNG management is available in the Windows
  application; extending the CLI to SNG is a possible future item, not
  part of this audit.
- **OASYS conversion is app + CLI in v1.6.1.** The `pcglib` CLI
  `convert` command covers KRONOS↔OASYS both ways (`-t oasys` /
  `-t kronos`, defaulting to the natural target from the source
  model), and the python port keeps byte parity on all four
  directions (KRONOS↔NAUTILUS, KRONOS↔OASYS).
- **K→O and K→N are offered for KRONOS OS 2.x/3.x only.** OS 2.x and
  3.x share the object format (header byte 7 = 1 or 2); OS 1.x is a
  different fiche family and is rejected with a clear message (the
  maintainer's pcgconvert web tool converts OS 1 files to OS 2/3
  first if needed).
- **OASYS SNG is not converted**, same reason as KRONOS/NAUTILUS SNG.
