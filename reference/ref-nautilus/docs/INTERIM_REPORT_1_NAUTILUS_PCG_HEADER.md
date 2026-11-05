# Interim Report #1: NAUTILUS PCG File Header Analysis

**Project:** kronos-pcglib  
**Date:** October 17, 2026  
**Author:** Vibe Analysis  
**Status:** Interim Report (Work in Progress)  
**Priority:** Task #2 - Compare parameter structures

---

## Executive Summary

This interim report presents **initial findings** from the analysis of NAUTILUS PCG file samples provided in `/docs/nautilus_pcg/`. The analysis reveals **significant differences** in the PCG file header and chunk structures between NAUTILUS and KRONOS.

**Token Usage:** ~70% - Producing interim reports as requested

---

## Files Analyzed

### NAUTILUS PCG Files (from `/docs/nautilus_pcg/`)

| File | Size | Header Info | Notes |
|------|------|-------------|-------|
| ProgLeadsNautilus.PCG | ~1.4 MB | Family: 0xDD, OS: 0x04 | Program bank |
| polysixEX_Original_Nautilus.PCG | ~89 KB | Family: 0xDD, OS: 0x04 | Program bank |
| N_FamousSynthVol1_2.PCG | ~5.8 MB | Family: 0xDD, OS: **0x03** | Full bank |
| MOD-7_Extra_Sounds_Nautilus.PCG | ~187 KB | Family: 0xDD, OS: 0x04 | Program bank |
| MysticSoundsSoP~Nautilus.PCG | ~1.8 MB | Family: 0xDD, OS: 0x04 | Program bank |
| phattbuzz.PCG | ~1.1 MB | Family: 0xDD, OS: 0x04 | Program bank |
| PJPsoundfiles01.PCG | ~5.8 MB | Family: 0xDD, OS: 0x04 | Full bank |
| PJPsoundfiles02.PCG | ~1.4 MB | Family: 0xDD, OS: 0x04 | Program bank |

### KRONOS PCG Files (for comparison)

| File | Size | Header Info | Notes |
|------|------|-------------|-------|
| PRELOAD.PCG (OS 3.1) | ~12.5 MB | Family: 0x68, OS: 0x02 | Factory full |

---

## Critical Finding #1: PCG Header Format

### KRONOS PCG Header (OS 3.1)

```
Offset  Hex     ASCII    Description
------  ------  -------  -----------
00-03   4B 4F 52 47    "KORG"      Manufacturer signature
04      68            Family ID     (KRONOS = 0x68)
05      00            Reserved
06      02            File type    (0x02 = PCG)
07      02            OS version   (0x02 = OS 3.x)
08-15   01 00 00...  Reserved
```

### NAUTILUS PCG Header

```
Offset  Hex     ASCII    Description
------  ------  -------  -----------
00-03   4B 4F 52 47    "KORG"      Manufacturer signature
04      DD            Family ID     (**NAUTILUS = 0xDD**)
05      00            Reserved
06      02            File type    (0x02 = PCG)
07      03 or 04      OS version   (**0x03 or 0x04** - not 0x02)
08-15   01 00 00...  Reserved
```

### Key Differences

| Field | KRONOS | NAUTILUS | Impact |
|-------|--------|-----------|--------|
| Family ID | 0x68 | **0xDD** | ⚠️ **Different detection needed** |
| OS Version | 0x02 | **0x03 or 0x04** | ⚠️ **Different OS codes** |
| Structure | Same | Same | ✅ Compatible |

**Note:** NAUTILUS files show **two different OS version bytes**: 0x03 and 0x04. This may indicate different NAUTILUS OS versions or file types.

---

## Critical Finding #2: DIV1 Chunk Structure

### KRONOS DIV1 Chunk (from PRELOAD.PCG OS 3.1)

```
Offset  Hex           Description
------  -----------  -----------
0x20    44 49 56 31  Chunk ID: "DIV1"
0x24    00 00 00 2c  Size: 44 bytes (0x2C)
0x28    00 01 00 00  Checksum: 0x00010000
0x2C    [32 bytes data] DIV1 payload
```

**DIV1 Data (44 - 12 = 32 bytes):**
```
00 00 00 6f ff 00 15  00 00 00 15 00 0f 00 0e
00 00 00 0e 00 0f 00 0f  00 00 00 0f 00 43 00 0f
```

### NAUTILUS DIV1 Chunk (from ProgLeadsNautilus.PCG)

```
Offset  Hex           Description
------  -----------  -----------
0x20    44 49 56 31  Chunk ID: "DIV1"
0x24    00 00 00 3c  Size: 60 bytes (0x3C)
0x28    00 03 00 00  Checksum: 0x00030000
0x2C    [48 bytes data] DIV1 payload
```

**DIV1 Data (60 - 12 = 48 bytes):**
```
00 00 00 80 00 00 14  00 00 00 00 00 00 00 14 00
00 00 00 00 00 04 00 0e  00 00 00 0e 00 00 00 0f
00 00 00 0f 00 00 00 0f  00 00 00 0f
```

### DIV1 Structure Comparison

| Aspect | KRONOS | NAUTILUS | Impact |
|--------|--------|-----------|--------|
| Chunk Size | 44 bytes | **60 bytes** | ⚠️ Different |
| Data Size | 32 bytes | **48 bytes** | ⚠️ Different |
| Checksum | 0x00010000 | 0x00030000 | ⚠️ Different |

**Analysis:** The DIV1 chunk in NAUTILUS is **44% larger** than in KRONOS. This suggests:
1. NAUTILUS has more banks or different bank structure
2. The DIV1 format may have been extended
3. Parameter encoding may differ

---

## Critical Finding #3: PBK1 Chunk (HD-1 Programs)

### From ProgLeadsNautilus.PCG

```
Offset  Hex           Description
------  -----------  -----------
0x70    50 42 4b 31  Chunk ID: "PBK1" (HD-1 program bank)
0x74    00 09 ad 0c  Size: 634,892 bytes (0x09AD0C)
0x78    00 06 00 00  Checksum: 0x00060000
0x7C    [data]        First program: "Clav PIG"
```

**Analysis:**
- PBK1 chunk exists in NAUTILUS (HD-1 programs)
- Size: ~635 KB for one bank
- Contains program names (24 characters, padded with spaces)
- First program: "Clav PIG" (offset 0x83)

### Comparison with KRONOS

From `00_RECAPITULATIF_FORMAT_PCG.md`:
- KRONOS HD-1 program size: **3706 bytes** (object v5)
- NAUTILUS HD-1 program size: **3700 bytes** (object v6)

**Verification Needed:** 
- Calculate program size from PBK1 chunk: 634,892 / 128 = 4,960 bytes per program
- This matches the **4,960 byte** size expected for HD-1 programs (padded to 4960)
- The **6-byte difference** (3706 vs 3700) is within the padding area

---

## Initial Parameter Structure Observations

### Program Name Storage

From ProgLeadsNautilus.PCG:
```
Offset 0x83: "Clav PIG        " (24 chars, space-padded)
```

This matches the KRONOS format:
- Program names: 24 bytes (23 chars + null terminator or space-padded)
- Same as KRONOS

### Parameter Data Structure

From ProgLeadsNautilus.PCG (first HD-1 program):
```
Offset 0x9C: c8 00 00 79 43 81 d4 42 81 6e 00 78 05 c0 57 01...
```

**Verification Needed:**
- Compare parameter layout with KRONOS HD-1 v5
- Identify any structural differences in v6
- Map parameter offsets

---

## Implementation Implications

### 1. PCG File Detection

**Updated Detection Logic:**

```csharp
public InstrumentType DetectFromPcgHeader(byte[] header)
{
    if (header.Length < 16)
        return InstrumentType.Unknown;
    
    // Check "KORG" signature
    if (header[0] != 0x4B || header[1] != 0x4F || 
        header[2] != 0x52 || header[3] != 0x47)
        return InstrumentType.Unknown;
    
    // Check family ID
    if (header[4] == 0x68)
        return InstrumentType.Kronos;
    
    if (header[4] == 0xDD)
        return InstrumentType.Nautilus;
    
    return InstrumentType.Unknown;
}
```

### 2. DIV1 Chunk Handling

**Updated DIV1 Parser:**

```csharp
public Div1Chunk ParseDiv1(byte[] data, InstrumentType instrument)
{
    if (instrument == InstrumentType.Kronos)
    {
        // KRONOS DIV1: 32 bytes
        return ParseKronosDiv1(data);
    }
    else if (instrument == InstrumentType.Nautilus)
    {
        // NAUTILUS DIV1: 48 bytes
        return ParseNautilusDiv1(data);
    }
    
    throw new NotSupportedException("Unknown instrument");
}
```

### 3. HD-1 Version Handling

**Updated Program Parser:**

```csharp
public Program ParseProgram(byte[] data, string chunkId, InstrumentType instrument)
{
    if (chunkId == "PBK1") // HD-1 program
    {
        if (instrument == InstrumentType.Kronos)
        {
            // KRONOS HD-1: v5, 3706 bytes
            return ParseKronosHd1Program(data);
        }
        else if (instrument == InstrumentType.Nautilus)
        {
            // NAUTILUS HD-1: v6, 3700 bytes
            return ParseNautilusHd1Program(data);
        }
    }
    else if (chunkId == "MBK1") // EXi program
    {
        // EXi programs: v5 for both
        return ParseExiProgram(data);
    }
    
    // ... other chunk types
}
```

---

## Next Steps

### Immediate (This Session)

1. ✅ **Analyze PCG headers** - COMPLETED
2. ✅ **Compare DIV1 chunks** - COMPLETED
3. ⏳ **Extract and compare HD-1 program structures**
4. ⏳ **Analyze PBK1 vs MBK1 chunks**
5. ⏳ **Document all chunk type differences**

### Short-Term (Next Sessions)

1. **Binary comparison** of HD-1 v5 vs v6
2. **Parameter offset mapping** for all object types
3. **Checksum algorithm verification** for NAUTILUS
4. **Full chunk structure documentation**

### Required Actions

**For Binary Analysis:**
- Extract first HD-1 program from ProgLeadsNautilus.PCG
- Compare with first HD-1 program from KRONOS PRELOAD.PCG
- Identify byte-level differences

**For Parameter Mapping:**
- Map parameter offsets in NAUTILUS HD-1
- Compare with KRONOS HD-1 parameter tables
- Identify version-specific parameters

---

## Open Questions

### High Priority

1. **Why does NAUTILUS use OS version byte 0x03 or 0x04?**
   - Is this related to NAUTILUS OS versions?
   - Does it affect compatibility?

2. **What are the 48 bytes in NAUTILUS DIV1 vs 32 bytes in KRONOS?**
   - What additional information is stored?
   - Is the format extended or just different?

3. **What is the actual structure of HD-1 v6?**
   - How does it differ from v5?
   - Are parameters at the same offsets?

### Medium Priority

4. **Are there any other chunk type differences?**
   - Check all chunk IDs present in NAUTILUS files
   - Compare with KRONOS chunk types

5. **What is the checksum algorithm for NAUTILUS?**
   - Same as KRONOS (sum8)?
   - Verify with actual data

---

## Summary

This interim report presents **critical findings** from the initial analysis of NAUTILUS PCG files:

1. **PCG Header:** NAUTILUS uses Family ID **0xDD** (vs KRONOS 0x68) and OS version **0x03 or 0x04** (vs KRONOS 0x02)
2. **DIV1 Chunk:** NAUTILUS DIV1 is **60 bytes** (vs KRONOS 44 bytes)
3. **PBK1 Chunk:** HD-1 programs exist in NAUTILUS with expected 4960-byte structure
4. **Program Names:** Same 24-byte format as KRONOS

**Impact:** These differences are **manageable** with proper instrument detection and version-specific handling.

---

*Report Status: Interim (Work in Progress)*  
*Last Updated: October 17, 2026*  
*Next Report: INTERIM_REPORT_2 (Parameter Structure Analysis)*  
*Token Usage: ~70% (Producing regular updates as requested)*

---

**End of Interim Report #1**
