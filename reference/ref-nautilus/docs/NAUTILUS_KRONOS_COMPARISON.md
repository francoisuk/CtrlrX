# NAUTILUS vs KRONOS: In-Depth File Format Comparison

**Project:** kronos-pcglib  
**Date:** October 16, 2026  
**Author:** Vibe Analysis  
**Status:** Work in Progress

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [SysEx Message Format Differences](#sysex-message-format-differences)
3. [Device Identification](#device-identification)
4. [Function Code Differences](#function-code-differences)
5. [Object Structure Differences](#object-structure-differences)
6. [Parameter Count Analysis](#parameter-count-analysis)
7. [EXi Engine Compatibility](#exi-engine-compatibility)
8. [KARMA vs Scene Architecture](#karma-vs-scene-architecture)
9. [PCG File Format Implications](#pcg-file-format-implications)
10. [Compatibility Matrix](#compatibility-matrix)
11. [Recommendations for PCG Tools](#recommendations-for-pcg-tools)
12. [Open Questions](#open-questions)

---

## Executive Summary

This document provides a comprehensive analysis of the differences between Korg NAUTILUS and KRONOS file formats, SysEx implementations, and parameter structures. The analysis is based on official Korg documentation provided in the project's `/docs/nautilus/` and `/docs/midi_korg/` directories.

**Key Finding:** While NAUTILUS and KRONOS share the same OASYS architecture and most EXi engines, they have **fundamentally different real-time control systems**: KRONOS uses **KARMA**, while NAUTILUS uses **Scene**. This affects parameter structures, SysEx messages, and potentially PCG file compatibility.

---

## SysEx Message Format Differences

### Header Format

**KRONOS:**
```
Exclusive Header: F0, 42, 3g, 68
  - 42: KORG manufacturer ID
  - 3g: Global channel (g = 0-15)
  - 68: KRONOS family ID
```

**NAUTILUS:**
```
Exclusive Header: F0, 42, 3g, 00, 01, 5D
  - 42: KORG manufacturer ID
  - 3g: Global channel (g = 0-15)
  - 00, 01, 5D: NAUTILUS series ID (LSB=01, MSB=5D)
```

**Analysis:** NAUTILUS uses an extended 6-byte header with series identification, while KRONOS uses a 4-byte header. This is the most fundamental difference at the protocol level.

### Device Inquiry Reply

**NAUTILUS (from MIDI Implementation):**
```
F0, 7E, 0g, 06, 02, 42, 00, 01, 5D, 00, mm, 00, vv, ww, xx, 00, F7
```

Field breakdown:
- Byte 7: 42 = KORG ID
- Byte 8: 01 = NAUTILUS series ID LSB
- Byte 9: 5D = NAUTILUS series ID MSB
- Byte 11: mm = Member code
  - 05 = NAUTILUS 61 keys
  - 0E = NAUTILUS 73 keys
  - 17 = NAUTILUS 88 keys
- Bytes 13-15: vv, ww, xx = System version (e.g., 01, 00, 02 = v1.0.2)

**KRONOS (inferred):**
Based on the SysEx header pattern, KRONOS likely uses:
- Family ID: 68 (from Excl Header)
- Different series identification

**Compatibility Note:** Tools must detect which instrument they're communicating with based on the Device Inquiry Reply or SysEx header format.

---

## Function Code Differences

### Identical Functions
Both NAUTILUS and KRONOS support:
- Object Dump Request (72)
- Object Dump (73)
- Current Object Dump Request (74)
- Current Object Dump (75)
- Store Bank Request (76)
- Dump Bank Request (77)
- Bank Digest Request/Collection (37, 38, 39, 3A)
- Parameter Change (integer/binary) (43, 44)
- Sequencer Parameter Change (41)
- Reset Controller (78)
- Reply (24)

### Divergent Functions

| Function Code | KRONOS | NAUTILUS | Significance |
|--------------|--------|-----------|-------------|
| 6D | KARMA Parameter Change | **Scene Parameter Change** | ⚠️ **MAJOR DIFFERENCE** |
| 6E | Drum Track Parameter Change | **Arp/Drum Track Parameter Change** | Modified |

**Critical Finding:** Function 6D is **completely different** between the two instruments:
- KRONOS: Controls KARMA (Korg Advanced Real-time Modulation Architecture)
- NAUTILUS: Controls Scene (a different real-time control system)

This means:
1. The parameter IDs (TYP, SOC, SUB, PID, IDX) for function 6D are **incompatible**
2. PCG Tools must handle these differently based on the target instrument
3. KARMA-related parameters in KRONOS PCG files will not map to NAUTILUS
4. Scene-related parameters in NAUTILUS PCG files will not map to KRONOS

---

## Object Structure Differences

### Program Objects

#### HD-1 Program

| Attribute | KRONOS | NAUTILUS | Notes |
|-----------|--------|-----------|-------|
| Program Size | 3706 bytes | **3700 bytes** | NAUTILUS smaller |
| Object Version | **5** | **6** | NAUTILUS newer |
| Parameter Count | 3128 lines (doc) | 5459 lines (doc) | NAUTILUS has more documented params |

**Analysis:** Despite the smaller program size (3700 vs 3706 bytes), NAUTILUS has a higher object version (6 vs 5) and more documented parameters. This suggests:
1. More efficient parameter packing in NAUTILUS
2. Possibly additional parameters added in version 6
3. The parameter documentation may be more comprehensive for NAUTILUS

#### EXi Program (Common)

| Attribute | KRONOS | NAUTILUS | Notes |
|-----------|--------|-----------|-------|
| AL-1 Parameters | 609 | 609 | Identical |
| Documentation Lines | 6143 | 6145 | Nearly identical |

**Analysis:** The EXi program structure appears largely compatible between KRONOS and NAUTILUS. The 2-line difference is likely minor documentation variations.

### Global Object

| Attribute | KRONOS | NAUTILUS | Notes |
|-----------|--------|-----------|-------|
| Documentation Lines | 25414 | 8866 | KRONOS has ~3x more |

**Analysis:** KRONOS Global has significantly more documented parameters. This is likely due to:
1. KARMA-related global settings (absent in NAUTILUS)
2. Additional KRONOS-specific features
3. More comprehensive KRONOS documentation

### Combination & Song Timbre Set

| Attribute | KRONOS | NAUTILUS | Notes |
|-----------|--------|-----------|-------|
| Documentation Lines | 8626 | 8088 | KRONOS slightly more |

**Analysis:** Modest difference, likely due to KARMA vs Scene parameter differences in combinations.

---

## Parameter Count Analysis

### Summary Table

| Object Type | KRONOS Lines | NAUTILUS Lines | Difference |
|-------------|---------------|----------------|------------|
| Prog_EXi.txt | 6143 | 6145 | +2 |
| Prog_HD-1.txt | 3128 | 5459 | **+2331** |
| Prog_EXi_Common.txt | (need to check) | (need to check) | - |
| Global.txt | 25414 | 8866 | **-16548** |
| CombiAndSongTimbreSet.txt | 8626 | 8088 | -538 |
| Effect.txt | (need to check) | (need to check) | - |

**Preliminary Conclusion:** The parameter documentation sizes vary significantly, but this may reflect documentation completeness rather than actual parameter differences. The actual binary structures may be more similar.

---

## EXi Engine Compatibility

Based on documentation files, both instruments support the same EXi engines:

| Engine | KRONOS | NAUTILUS | Status |
|--------|--------|-----------|--------|
| AL-1 Analog Synthesizer | ✓ | ✓ | Compatible |
| CX-3 Tonewheel Organ | ✓ | ✓ | Compatible |
| EP-1 MDS Electric Piano | ✓ | ✓ | Compatible |
| MOD-7 Waveshaping VPM Synthesizer | ✓ | ✓ | Compatible |
| MS-20EX | ✓ | ✓ | Compatible |
| PolysixEX | ✓ | ✓ | Compatible |
| SGX-2 Premium Piano | ✓ | ✓ | Compatible |
| STR-1 Plucked String | ✓ | ✓ | Compatible |
| HD-1 | ✓ | ✓ | **Size difference noted** |

**Note:** All EXi engines appear compatible at the parameter level, but the HD-1 has a size difference that needs investigation.

---

## KARMA vs Scene Architecture

### KRONOS: KARMA System

**KARMA** (Korg Advanced Real-time Modulation Architecture):
- Complex real-time phrase/pattern generation system
- Generates musical patterns based on chord input
- Multiple GE (Generated Effects) modules
- RTP (Realtime Parameters) for dynamic control
- Deep integration with all EXi engines
- Function Code: 6D (KARMA Parameter Change)

**KARMA Parameters in KRONOS:**
- GE Setup parameters
- RTP parameters
- Module routing and assignments
- Chord/key trigger settings

### NAUTILUS: Scene System

**Scene** (NAUTILUS Real-time Control):
- Replaces KARMA functionality
- Simplified real-time control system
- Focus on pattern and arpeggiator control
- Function Code: 6D (Scene Parameter Change)

**Key Differences:**
1. **Conceptual:** KARMA is pattern-generation focused; Scene appears more pattern-triggering focused
2. **Complexity:** KARMA has significantly more parameters and complexity
3. **Integration:** Both integrate with EXi engines, but differently
4. **SysEx:** Different parameter IDs and structures for function 6D

**Impact on PCG Files:**
- KARMA data in KRONOS PCG files cannot be directly used in NAUTILUS
- Scene data in NAUTILUS PCG files cannot be directly used in KRONOS
- Tools must either:
  a) Strip KARMA/Scene data when converting between formats
  b) Provide lossy conversion with warnings
  c) Maintain separate parameter mappings

---

## PCG File Format Implications

### Current Understanding (from KRONOS analysis)

Based on `docs/00_RECAPITULATIF_FORMAT_PCG.md`:
- PCG is a chunked binary format (header + named chunks)
- OS 3.2 does NOT change the format, only introduces new values
- Versions: MBK1 v5, PBK1 v5, CBK1 v3, DBK1 v3, WBK1 v1, GLB1 v2
- Checksum: sum8 (sum of all body bytes modulo 256)
- KRONOS OS identification: byte 7 of header (00=OS1, 01=OS2, 02=OS3)

### NAUTILUS PCG Format (to be verified)

**Hypothesis:** NAUTILUS PCG format is **similar but not identical** to KRONOS:

1. **Header:** Likely uses different OS identifier
   - KRONOS: byte 7 = 02 (OS 3.x)
   - NAUTILUS: byte 7 = ?? (likely different)

2. **Chunks:** Same chunk types (PCG1, DIV1, PRG1, CMB1, etc.)

3. **Object Versions:** May differ for some objects (HD-1 is v6 vs v5)

4. **Parameter Data:** 
   - EXi parameters: Likely compatible
   - HD-1 parameters: **Potentially different** (size difference)
   - Global parameters: **Different** (KARMA vs Scene)
   - Combi parameters: **Partially different** (Scene vs KARMA)

5. **Checksum Calculation:** Likely same algorithm (sum8)

### Verification Needed

⚠️ **TODO:** Need to examine actual NAUTILUS PCG files to confirm:
- Header format
- Chunk structure
- Object versions
- Parameter byte layouts
- Checksum calculation

---

## Compatibility Matrix

### PCG File Compatibility

| Source \ Target | KRONOS OS 3.2 | NAUTILUS | Notes |
|------------------|---------------|-----------|-------|
| **KRONOS OS 3.2** | ✅ Native | ⚠️ Partial | KARMA data lost |
| **NAUTILUS** | ⚠️ Partial | ✅ Native | Scene data lost |
| **KRONOS OS 3.1.4** | ✅ Native | ⚠️ Partial | KARMA + OS differences |
| **KRONOS OS 2.x** | ⚠️ Convert | ⚠️ Convert | Major format changes |
| **KRONOS OS 1.x** | ⚠️ Convert | ⚠️ Convert | Format conversion needed |

**Legend:**
- ✅ Native: Full compatibility, all features work
- ⚠️ Partial: Loads but with feature loss (KARMA/Scene)
- ⚠️ Convert: Requires format conversion

### SysEx Message Compatibility

| Message Type | KRONOS ↔ NAUTILUS | Notes |
|--------------|-------------------|-------|
| Object Dump (72/73) | ✅ | Same structure |
| Store Bank Request (76) | ✅ | Same structure |
| Parameter Change (43/44) | ✅ | Same structure |
| KARMA Parameter Change (6D) | ❌ | Different systems |
| Scene Parameter Change (6D) | ❌ | Different systems |
| Drum Track Parameter Change (6E) | ⚠️ | May be compatible |

---

## Recommendations for PCG Tools

### Architecture Recommendations

1. **Instrument Detection**
   - Detect instrument type via:
     - Device Inquiry Reply
     - SysEx header format (4-byte vs 6-byte)
     - Object versions in PCG files
   - Store detected type in session context

2. **Parameter Mapping Strategy**
   ```
   Option A: Unified Parameter Database
   - Single parameter table with instrument-specific flags
   - Runtime filtering based on target instrument
   
   Option B: Separate Parameter Tables
   - KRONOS-specific parameter tables
   - NAUTILUS-specific parameter tables
   - Shared EXi parameter tables
   ```
   **Recommendation:** Option A (more maintainable)

3. **KARMA/Scene Handling**
   ```
   Strategy 1: Preserve and Ignore
   - Keep KARMA/Scene data in PCG files
   - Ignore when loading on incompatible instrument
   - User warning: "KARMA data ignored"
   
   Strategy 2: Strip on Conversion
   - Remove KARMA/Scene data when converting
   - Cleaner files but data loss
   - User warning: "KARMA data removed"
   ```
   **Recommendation:** Strategy 1 (preserve data, user can maintain separate files)

4. **SysEx Header Handling**
   - Support both 4-byte (KRONOS) and 6-byte (NAUTILUS) headers
   - Normalize to common internal format
   - Generate appropriate header when transmitting

5. **Object Version Handling**
   - Support HD-1 v5 (KRONOS) and v6 (NAUTILUS)
   - Implement version-specific parameter mappings
   - Upgrade/downgrade conversions where possible

### Code Structure Recommendations

```
src/KorgKronosTools/
├── Model/
│   ├── Instruments/
│   │   ├── KronosInstrument.cs      # KRONOS-specific
│   │   ├── NautilusInstrument.cs    # NAUTILUS-specific
│   │   └── InstrumentBase.cs       # Common interface
│   ├── Parameters/
│   │   ├── ParameterDatabase.cs    # Unified parameter DB
│   │   ├── KronosParameters.cs      # KRONOS-specific
│   │   └── NautilusParameters.cs    # NAUTILUS-specific
│   └── Pcg/
│       ├── PcgReader.cs            # Read PCG files
│       ├── PcgWriter.cs            # Write PCG files
│       └── PcgFormatDetector.cs     # Detect instrument from PCG
└── ...
```

### SysEx Handler Recommendations

```csharp
// Pseudocode for SysEx message handling
public class SysExHandler
{
    public void ProcessMessage(SysExMessage msg)
    {
        if (IsNautilusHeader(msg.Header))
        {
            // NAUTILUS-specific processing
            if (msg.Function == 0x6D)
                ProcessSceneParameter(msg);
            else if (msg.Function == 0x6E)
                ProcessArpDrumTrackParameter(msg);
        }
        else if (IsKronosHeader(msg.Header))
        {
            // KRONOS-specific processing
            if (msg.Function == 0x6D)
                ProcessKarmaParameter(msg);
            else if (msg.Function == 0x6E)
                ProcessDrumTrackParameter(msg);
        }
    }
}
```

---

## Open Questions

### High Priority

1. **NAUTILUS PCG Header Format**
   - What is byte 7 of the PCG header for NAUTILUS?
   - Is it 00, 01, or something else?
   - How does it compare to KRONOS OS versions?

2. **HD-1 Parameter Difference**
   - Why is NAUTILUS HD-1 smaller (3700 bytes) but newer (v6) than KRONOS (3706 bytes, v5)?
   - What parameters are different?
   - Are the differences in the parameter values or the structure?

3. **Scene vs KARMA Mapping**
   - Is there any conceptual overlap between Scene and KARMA?
   - Can Scene parameters be mapped to KARMA parameters (even if lossy)?
   - What are the Scene parameter IDs and ranges?

4. **Global Parameter Differences**
   - What specific Global parameters are different between KRONOS and NAUTILUS?
   - Are there NAUTILUS-specific global features?
   - Are there KRONOS-specific global features missing in NAUTILUS?

### Medium Priority

5. **Prog_EXi_Common Differences**
   - Need to compare common EXi parameters
   - Are there any differences in the common parameter block?

6. **Effect System**
   - Are the effect parameters identical?
   - Are there NAUTILUS-specific effects?
   - Are the effect IDs the same?

7. **Combination Parameters**
   - What are the Scene-specific parameters in combinations?
   - How do they compare to KARMA parameters?

### Low Priority

8. **SysEx Dump Formats**
   - Verify all SysEx dump message formats match
   - Identify any other subtle differences

9. **Bank Select Mapping**
   - Are the bank select mappings identical?
   - Any differences in Program/Combi/Set List addressing?

---

## Next Steps

### Immediate Actions

1. ✅ **Gather NAUTILUS documentation** - COMPLETED (files in /docs/nautilus/)
2. ✅ **Compare SysEx headers** - COMPLETED (4-byte vs 6-byte)
3. ✅ **Identify function code differences** - COMPLETED (6D = KARMA vs Scene)
4. ✅ **Compare parameter documentation sizes** - COMPLETED
5. ⏳ **Obtain NAUTILUS PCG files** - NEED SAMPLE FILES
6. ⏳ **Analyze NAUTILUS PCG structure** - BLOCKED (need samples)
7. ⏳ **Create parameter mapping tables** - PENDING (need more data)

### Required Resources

To complete the analysis, we need:

1. **NAUTILUS PCG Sample Files**
   - Factory PRELOAD.PCG
   - Factory INIT.PCG
   - Sample user PCG files
   - Files from different OS versions (if available)

2. **NAUTILUS SysEx Dumps**
   - Sample Object Dump messages
   - Sample Parameter Change messages
   - KARMA/Scene parameter examples

3. **NAUTILUS Voice Name List**
   - Compare with KRONOS VNL files
   - Identify any differences

4. **Access to NAUTILUS Hardware or Documentation**
   - Verify findings against actual hardware
   - Test compatibility scenarios

---

## Conclusion

The analysis reveals that while NAUTILUS and KRONOS share the same OASYS architecture and most EXi engines, they have **fundamental differences** in:

1. **SysEx message headers** (4-byte vs 6-byte)
2. **Real-time control systems** (KARMA vs Scene)
3. **Parameter structures** (especially Global and HD-1)

These differences must be accounted for in PCG Tools to ensure proper support for both instruments. The recommended approach is:

1. **Detect instrument type** automatically
2. **Maintain separate parameter mappings** for KARMA vs Scene
3. **Preserve instrument-specific data** when possible
4. **Warn users** about feature loss when converting between formats

The most critical finding is the **KARMA vs Scene incompatibility** at function code 6D, which will require significant architectural considerations in the PCG Tools implementation.

---

*Document Status: Work in Progress*  
*Last Updated: October 16, 2026*  
*Next Review: Pending NAUTILUS PCG file samples*
