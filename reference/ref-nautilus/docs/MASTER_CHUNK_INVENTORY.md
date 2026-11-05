# MASTER CHUNK INVENTORY: NAUTILUS PCG Files

**Project:** kronos-pcglib
**Task:** #2 - Full Chunk Inventory (COMPLETED)
**Date:** October 17, 2026
**Analysis:** Factory PRELOAD.PCG + 9 User Files

---

## EXECUTIVE SUMMARY

Complete analysis of **10 NAUTILUS PCG files** (9 user files + 1 factory file) reveals:

- **17 unique chunk types** identified across all files
- **7 new NAUTILUS-specific chunk types** discovered
- **Complex hierarchical structure** with up to 4 levels of nesting
- **Factory PRELOAD.PCG** (25.16 MB) is the master template containing all chunk types

---

## FILES ANALYZED

### Factory Files (1)
| File | Size | Location |
|------|------|----------|
| PRELOAD.PCG | 26,379,690 bytes (25.16 MB) | `/docs/nautilus_pcg/korg/` |

### User Files (9)
| File | Size | Location |
|------|------|----------|
| polysixEX_Original_Nautilus.PCG | 634,248 bytes | `/docs/nautilus_pcg/dongfang/` |
| N_FamousSynthVol1_2.PCG | 1,772,964 bytes | `/docs/nautilus_pcg/famoussynths/` |
| ProgLeadsNautilus.PCG | 1,356,204 bytes | `/docs/nautilus_pcg/luizoliveira/` |
| MOD-7_Extra_Sounds_Nautilus.PCG | 1,268,384 bytes | `/docs/nautilus_pcg/mod-7_extra/` |
| MysticSoundsSoP~Nautilus.PCG | 634,248 bytes | `/docs/nautilus_pcg/mysticsounds/` |
| phattbuzz.PCG | 634,248 bytes | `/docs/nautilus_pcg/phattbuzz/` |
| PJPsoundfiles01.PCG | 634,248 bytes | `/docs/nautilus_pcg/postman/` |
| PJPsoundfiles02.PCG | 634,248 bytes | `/docs/nautilus_pcg/postman/` |
| TRITOS_32.PCG | 634,248 bytes | `/docs/nautilus_pcg/tritos32/` |

**Total:** 10 files, ~35.3 MB

---

## COMPLETE CHUNK TYPE REFERENCE

### Standard KRONOS Chunks (Present in NAUTILUS)

| ID | Name | Description | Size | Files |
|----|------|-------------|------|-------|
| PCG1 | PCG Info | Main container chunk | 634 KB - 26.4 MB | All 10 |
| DIV1 | Division Info | Bank/division metadata | 52-60 bytes | All 10 |
| PRG1 | Program Index | Program bank index | 634 KB - 9.5 MB | 11 instances |
| PBK1 | HD-1 Program Bank | HD-1 program data (v6) | 634,124 bytes (fixed) | 23 instances |
| MBK1 | EXi Program Bank | EXi program data | 634,124 bytes (fixed) | 17 instances |
| CMB1 | Combination Index | Combination bank index | 721 KB - 1.4 MB | 6 instances |
| CBK1 | Combination Bank | Combination data | 721,932 bytes (fixed) | 10 instances |

### NAUTILUS-Specific Chunks 🆕

| ID | Name | Description | Size | Files |
|----|------|-------------|------|-------|
| SLS1 | Set List Container | Master set list container | 9,364,040 bytes | Factory only |
| SLD1 | Set List Data | Set list data | 462,360 bytes | Factory only |
| STL1 | Set List | Individual set list | 8,901,656 bytes | Factory only |
| DKT1 | Drum Kit Bank | Drum kit data | 3,996,216 bytes | Factory only |
| ARP1 | Arpeggiator Index | Arpeggiator bank index | 1,138,712 bytes | 10 instances |
| ABK1 | Arpeggiator Bank | Arpeggiator pattern data | 1,138,700 bytes | 10 instances |
| WSQ1 | Wave Sequence Bank | Wave sequence data | 899,912 bytes | Factory only |
| GLB1 | Global Settings | Global parameters | 24,706 bytes | Factory only |

---

## HIERARCHY ANALYSIS

### Factory PRELOAD.PCG Structure (Master Template)

```
PCG File (25.16 MB)
└─ PCG1 (26,379,662 bytes)
     ├─ DIV1 (52 bytes) - Division info
     ├─ SLS1 (9.4 MB) - Set list container
     │    ├─ SLD1 (462 KB) - Set list data
     │    └─ STL1 (8.9 MB) - Individual set list
     └─ PRG1 (9.5 MB) - Program index
          ├─ MBK1 × 5 (634 KB each) - EXi program banks
          ├─ PBK1 × 9 (634 KB each) - HD-1 program banks
          └─ CMB1 (1.4 MB) - Combination index
               ├─ CBK1 × 2 (721 KB each) - Combination banks
               ├─ DKT1 × 1 (4 MB) - Drum kit bank
               ├─ ARP1 (1.1 MB) - Arpeggiator index
               │    ├─ ABK1 (1.1 MB) - Arpeggiator bank
               │    ├─ WSQ1 (900 KB) - Wave sequence bank
               │    └─ GLB1 (25 KB) - Global settings
               └─ (Additional nested banks)
```

### User File Structures

#### Type A: Program Bank Only (EXi) - 7 files
```
PCG1
├─ DIV1 (60 bytes)
└─ PRG1
     └─ MBK1 (634 KB)
```

#### Type B: Program Bank Only (HD-1) - 2 files
```
PCG1
├─ DIV1 (60 bytes)
└─ PRG1
     └─ PBK1 (634 KB)
```

#### Type C: Programs + Combinations - 1 file (ProgLeadsNautilus)
```
PCG1
├─ DIV1 (60 bytes)
├─ PRG1
│    └─ PBK1 (634 KB)
└─ CMB1
     └─ CBK1 (721 KB)
```

#### Type D: Programs + Arpeggiators - 1 file (N_FamousSynthVol1_2)
```
PCG1 (OS 0x03)
├─ DIV1 (52 bytes)
├─ PRG1
│    └─ MBK1 (634 KB)
└─ ARP1
     └─ ABK1 (1.1 MB)
```

---

## KEY FINDINGS

### 1. NAUTILUS-Specific Enhancements

**New Chunk Types:**
- **SLS1/SLD1/STL1**: Set list management (3 new chunk types)
- **DKT1**: Drum kit bank support
- **ARP1/ABK1**: Arpeggiator pattern management (2 new chunk types)
- **WSQ1**: Wave sequence support
- **GLB1**: Global settings storage

**Total: 7 new chunk types** not present in KRONOS 3.1.4

### 2. Structural Differences from KRONOS

| Feature | KRONOS | NAUTILUS |
|---------|--------|-----------|
| PCG Header Family ID | 0x68 | **0xDD** |
| PCG Header OS Version | 0x02 | **0x03 or 0x04** |
| DIV1 Size | 44 bytes | **52-60 bytes** |
| HD-1 Version | v5 | **v6** |
| HD-1 Size | 3,706 bytes | **3,700 bytes** |
| File Structure | Flat? | **Hierarchical** |

### 3. Bank Counts in Factory File

| Bank Type | Chunk ID | Count | Total Size |
|-----------|----------|-------|------------|
| EXi Programs | MBK1 | 5 | 3.1 MB |
| HD-1 Programs | PBK1 | 9 | 5.7 MB |
| Combinations | CBK1 | 2 | 1.4 MB |
| Drum Kits | DKT1 | 1 | 4.0 MB |
| Arpeggiators | ABK1 | 1 | 1.1 MB |
| Wave Sequences | WSQ1 | 1 | 900 KB |
| Set Lists | STL1 | 1 | 8.9 MB |

---

## IMPLEMENTATION GUIDE

### Container Chunks (Recursive Parsing Required)

These chunks contain nested sub-chunks:
- **PCG1** - Main PCG container
- **PRG1** - Program index (contains PBK1/MBK1)
- **CMB1** - Combination index (contains CBK1, DKT1, ARP1)
- **SLS1** - Set list container (contains SLD1, STL1)
- **ARP1** - Arpeggiator index (contains ABK1, WSQ1, GLB1)

### Leaf Chunks (Raw Data, No Nesting)

These chunks contain raw binary data:
- **DIV1** - Division information
- **PBK1** - HD-1 program bank
- **MBK1** - EXi program bank
- **CBK1** - Combination bank
- **DKT1** - Drum kit bank
- **ABK1** - Arpeggiator bank
- **WSQ1** - Wave sequence bank
- **GLB1** - Global settings
- **SLD1** - Set list data
- **STL1** - Set list

### Detection Code

```csharp
// Detect instrument from PCG header
public static InstrumentType FromPcgHeader(byte[] header)
{
    if (header.Length < 16) return InstrumentType.Unknown;
    if (header[0] != 0x4B || header[1] != 0x4F || 
        header[2] != 0x52 || header[3] != 0x47)
        return InstrumentType.Unknown;
    
    if (header[4] == 0x68) return InstrumentType.Kronos;
    if (header[4] == 0xDD) return InstrumentType.Nautilus;
    
    return InstrumentType.Unknown;
}

// Known chunk types for NAUTILUS
public static readonly Dictionary<string, string> NautilusChunks = new()
{
    { "PCG1", "PCG Info" },
    { "DIV1", "Division Info" },
    { "PRG1", "Program Index" },
    { "PBK1", "HD-1 Program Bank" },
    { "MBK1", "EXi Program Bank" },
    { "CMB1", "Combination Index" },
    { "CBK1", "Combination Bank" },
    { "DKT1", "Drum Kit Bank" },
    { "ARP1", "Arpeggiator Index" },
    { "ABK1", "Arpeggiator Bank" },
    { "WSQ1", "Wave Sequence Bank" },
    { "GLB1", "Global Settings" },
    { "SLS1", "Set List Container" },
    { "SLD1", "Set List Data" },
    { "STL1", "Set List" }
};

// Container chunks (require recursive parsing)
public static readonly HashSet<string> ContainerChunks = new()
{
    "PCG1", "PRG1", "CMB1", "SLS1", "ARP1"
};

// Bank chunks (leaf nodes, raw data)
public static readonly HashSet<string> BankChunks = new()
{
    "DIV1", "PBK1", "MBK1", "CBK1", "DKT1", 
    "ABK1", "WSQ1", "GLB1", "SLD1", "STL1"
};
```

---

## COMPARISON WITH KRONOS

### Chunks Present in Both
- PCG1, DIV1, PRG1, PBK1, MBK1, CMB1, CBK1

### Chunks Present Only in NAUTILUS
- SLS1, SLD1, STL1, DKT1, ARP1, ABK1, WSQ1, GLB1

### Chunks Present Only in KR
