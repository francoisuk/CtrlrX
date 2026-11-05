# NAUTILUS vs KRONOS: SysEx Protocol Deep Dive

**Project:** kronos-pcglib  
**Date:** October 16, 2026  
**Focus:** System Exclusive Protocol Differences  
**Status:** Complete Analysis

---

## Executive Summary

This document provides a detailed technical analysis of the SysEx (System Exclusive) protocol differences between Korg NAUTILUS and KRONOS synthesizers. Understanding these differences is **critical** for implementing proper SysEx message handling in PCG Tools.

**Key Finding:** NAUTILUS and KRONOS use **different SysEx header formats** and have **incompatible real-time control parameter systems** (Scene vs KARMA), but share most object-level SysEx messages.

---

## 1. Manufacturer and Device Identification

### 1.1 KORG Manufacturer ID

Both instruments use the standard KORG manufacturer ID:
- **Manufacturer ID:** `0x42` (66 decimal)
- **Universal SysEx:** Uses `0x7E` (Universal Non-Realtime) or `0x7F` (Universal Realtime)

### 1.2 Device Identification in SysEx Headers

#### KRONOS SysEx Header Format

```
Format: F0, 42, 3g, 68, [function], [data...], F7

Breakdown:
- F0        : Exclusive status byte
- 42       : KORG manufacturer ID
- 3g       : Global channel (g = 0-15, typically 0 for single-timbre messages)
- 68       : KRONOS family identifier
- [function]: Function code (see Section 2)
- [data...]: Function-specific data
- F7       : End of Exclusive
```

**KRONOS Family ID: `0x68`**
- This byte identifies the message as being for the KRONOS family
- Used consistently across all KRONOS SysEx messages
- Allows KRONOS to filter messages intended for other Korg instruments

#### NAUTILUS SysEx Header Format

```
Format: F0, 42, 3g, 00, 01, 5D, [function], [data...], F7

Breakdown:
- F0        : Exclusive status byte
- 42       : KORG manufacturer ID
- 3g       : Global channel (g = 0-15)
- 00       : Series ID part 1 (LSB of series identifier)
- 01       : Series ID part 2 (NAUTILUS series LSB)
- 5D       : Series ID part 3 (NAUTILUS series MSB)
- [function]: Function code (see Section 2)
- [data...]: Function-specific data
- F7       : End of Exclusive
```

**NAUTILUS Series Identifier:** `0x00 0x01 0x5D`
- Extended 3-byte identifier vs KRONOS single byte
- Allows for more instrument families under KORG manufacturer ID
- `0x01 0x5D` = NAUTILUS series (little-endian: 0x5D01)

### 1.3 Device Inquiry Reply Comparison

#### KRONOS (Inferred from KRONOS documentation)

Based on the KRONOS MIDI Implementation and analysis:

```
F0, 7E, 0g, 06, 02, 42, 68, [os_version], [model_code], F7

Fields:
- 7E: Universal Non-Realtime
- 0g: Global channel
- 06: Sub-ID#1 (Device Inquiry)
- 02: Sub-ID#2
- 42: KORG manufacturer ID
- 68: KRONOS family ID
- [os_version]: OS version identifier
- [model_code]: Specific model code
```

**Note:** This is inferred; the actual KRONOS Device Inquiry format needs verification from official documentation.

#### NAUTILUS (From NAUTILUS_MIDI_MIDI_Implementation.txt)

```
F0, 7E, 0g, 06, 02, 42, 00, 01, 5D, 00, mm, 00, vv, ww, xx, 00, F7

Field breakdown:
- Byte 0: F0 (Exclusive status)
- Byte 1: 7E (Universal Non-Realtime)
- Byte 2: 0g (Global channel)
- Byte 3: 06 (Sub-ID#1 - Device Inquiry)
- Byte 4: 02 (Sub-ID#2)
- Byte 5: 42 (KORG manufacturer ID)
- Byte 6: 00 (Series part 1)
- Byte 7: 01 (NAUTILUS series LSB)
- Byte 8: 5D (NAUTILUS series MSB)
- Byte 9: 00 (Reserved)
- Byte 10: mm (Member code)
  - 0x05: NAUTILUS 61 keys
  - 0x0E: NAUTILUS 73 keys
  - 0x17: NAUTILUS 88 keys
- Byte 11: 00 (Reserved)
- Bytes 12-14: vv, ww, xx (System version)
  - Example: 01 00 02 = Version 1.0.2
- Byte 15: 00 (Reserved)
- Byte 16: F7 (End of Exclusive)
```

### 1.4 Impact on PCG Tools

**Detection Strategy:**

PCG Tools must implement instrument detection using both methods:

```csharp
public enum InstrumentType
{
    Unknown,
    Kronos,
    Nautilus
}

public InstrumentType DetectInstrument(SysExMessage msg)
{
    // Method 1: Check SysEx header
    if (msg.Header.Length == 6 && 
        msg.Header[0] == 0xF0 &&
        msg.Header[1] == 0x42 &&
        msg.Header[4] == 0x68)
    {
        return InstrumentType.Kronos;
    }
    
    if (msg.Header.Length == 8 &&
        msg.Header[0] == 0xF0 &&
        msg.Header[1] == 0x42 &&
        msg.Header[4] == 0x00 &&
        msg.Header[5] == 0x01 &&
        msg.Header[6] == 0x5D)
    {
        return InstrumentType.Nautilus;
    }
    
    // Method 2: Check Device Inquiry Reply
    if (msg.Function == 0x06 && msg.SubId == 0x02) // Device Inquiry Reply
    {
        if (msg.Data[2] == 0x68) // KRONOS family ID
            return InstrumentType.Kronos;
        
        if (msg.Data[2] == 0x00 && msg.Data[3] == 0x01 && msg.Data[4] == 0x5D)
            return InstrumentType.Nautilus;
    }
    
    return InstrumentType.Unknown;
}
```

---

## 2. Function Code Comparison

### 2.1 Function Code Table

| Function | Hex | KRONOS | NAUTILUS | Compatibility |
|----------|-----|--------|-----------|---------------|
| Object Dump Request | 72 | ✅ | ✅ | Full |
| Object Dump | 73 | ✅ | ✅ | Full |
| Current Object Dump Request | 74 | ✅ | ✅ | Full |
| Current Object Dump | 75 | ✅ | ✅ | Full |
| Store Bank Request | 76 | ✅ | ✅ | Full |
| Dump Bank Request | 77 | ✅ | ✅ | Full |
| Bank Digest Request | 37 | ✅ | ✅ | Full |
| Bank Digest | 38 | ✅ | ✅ | Full |
| Bank Digest Collection Request | 39 | ✅ | ✅ | Full |
| Bank Digest Collection | 3A | ✅ | ✅ | Full |
| Current Sample Information Request | 30 | ✅ | ✅ | Full |
| Current Sample Information | 31 | ✅ | ✅ | Full |
| Current Performance Id Request | 32 | ✅ | ✅ | Full |
| Current Performance Id | 33 | ✅ | ✅ | Full |
| Current Piano Types Request | 34 | ✅ | ✅ | Full |
| Current Piano Types | 35 | ✅ | ✅ | Full |
| Notify Piano Types Changed | 36 | ✅ | ✅ | Full |
| SMF Data Dump Request | 79 | ✅ | ✅ | Full |
| SMF Data Dump | 7A | ✅ | ✅ | Full |
| Parameter Change (integer) | 43 | ✅ | ✅ | Full |
| Parameter Change (binary) | 44 | ✅ | ✅ | Full |
| Sequencer Parameter Change | 41 | ✅ | ✅ | Full |
| **KARMA Parameter Change** | **6D** | ✅ | ❌ | **N/A (uses Scene)** |
| **Scene Parameter Change** | **6D** | ❌ | ✅ | **N/A (uses KARMA)** |
| **Drum Track Parameter Change** | **6E** | ✅ | ⚠️ | Partial |
| **Arp/Drum Track Parameter Change** | **6E** | ⚠️ | ✅ | Partial |
| Set Current Object | 71 | ✅ | ✅ | Full |
| Drum Kit Parameter Change (integer) | 53 | ✅ | ✅ | Full |
| Drum Kit Parameter Change (binary) | 54 | ✅ | ✅ | Full |
| Wave Seq Parameter Change (integer) | 55 | ✅ | ✅ | Full |
| Wave Seq Parameter Change (binary) | 56 | ✅ | ✅ | Full |
| Mode Request | 12 | ✅ | ✅ | Full |
| Mode Data | 42 | ✅ | ✅ | Full |
| Edit In Context Notify | 48 | ✅ | ✅ | Full |
| Mode Change | 4E | ✅ | ✅ | Full |
| Program Bank Types Request | 60 | ✅ | ✅ | Full |
| Program Bank Types | 61 | ✅ | ✅ | Full |
| Change Program Bank Type | 7C | ✅ | ✅ | Full |
| Query Program Bank Type (deprecated) | 7D | ✅ | ✅ | Full |
| Query Program Bank Type Reply (deprecated) | 7E | ✅ | ✅ | Full |
| Reset Controller | 78 | ✅ | ✅ | Full |
| Song Select | 13 | ✅ | ✅ | Full |
| Reply | 24 | ✅ | ✅ | Full |

### 2.2 Critical Difference: Function 6D

#### KRONOS: KARMA Parameter Change (Function 6D)

**Message Format:**
```
F0, 42, 3g, 68, 6D, TYP, SOC, SUB, PID, IDX, valueH, valueM, valueL, F7
```

**Parameters:**
- TYP: Type of parameter
- SOC: Source/Category
- SUB: Sub-category
- PID: Parameter ID
- IDX: Index
- valueH/M/L: Value (21-bit, split across 3 bytes)

**KARMA Parameter Types:**
- GE (Generated Effects) parameters
- RTP (Realtime Parameters)
- Module assignments
- Chord/key triggers
- Pattern generation settings

**Documentation:** See `KRONOS_MIDI_SysEx.txt` and `KARMA_GE_RTP.txt`

#### NAUTILUS: Scene Parameter Change (Function 6D)

**Message Format:**
```
F0, 42, 3g, 00, 01, 5D, 6D, TYP, SOC, SUB, PID, IDX, valueH, valueM, valueL, F7
```

**Parameters:**
- TYP: Type of parameter
- SOC: Source/Category
- SUB: Sub-category
- PID: Parameter ID
- IDX: Index
- valueH/M/L: Value (21-bit, split across 3 bytes)

**Scene Parameter Types:**
- Pattern control parameters
- Arpeggiator settings
- Real-time control assignments
- Scene trigger parameters

**Documentation:** See `NAUTILUS_MIDI_SysEx.txt` and `CombiAndSongTimbreSet.txt`

#### Compatibility Analysis

**The Same Function Code, Different Meanings:**

| Aspect | KRONOS (6D) | NAUTILUS (6D) |
|--------|-------------|---------------|
| Function Name | KARMA Parameter Change | Scene Parameter Change |
| System | KARMA | Scene |
| Parameter Types | GE, RTP, Modules | Patterns, Arp, Controls |
| Complexity | High (hundreds of parameters) | Medium (estimated) |
| Compatibility | ❌ Incompatible | ❌ Incompatible |

**Implications:**
1. **Cannot be used interchangeably** - Sending KARMA parameters to NAUTILUS (or vice versa) will have undefined behavior
2. **Different parameter databases needed** - PCG Tools must maintain separate parameter mappings
3. **Conversion required** - When converting PCG files, KARMA/Scene data must be handled specially

### 2.3 Secondary Difference: Function 6E

#### KRONOS: Drum Track Parameter Change (Function 6E)

**Message Format:**
```
F0, 42, 3g, 68, 6E, TYP, SOC, SUB, PID, IDX, valueH, valueM, valueL, F7
```

**Purpose:** Modify Drum Track parameters in programs/combinations

#### NAUTILUS: Arp/Drum Track Parameter Change (Function 6E)

**Message Format:**
```
F0, 42, 3g, 00, 01, 5D, 6E, TYP, SOC, SUB, PID, IDX, valueH, valueM, valueL, F7
```

**Purpose:** Modify Arpeggiator and Drum Track parameters

**Analysis:** The function is **mostly compatible** but NAUTILUS adds Arpeggiator control to the same function code. This suggests:
- Drum Track parameters are likely compatible
- Arpeggiator parameters are NAUTILUS-specific additions
- PCG Tools should handle the common Drum Track parameters separately from Arp parameters

### 2.4 Message Size and Structure

Both instruments use the same **parameter identification system** for most functions:

```
Parameter ID Structure:
- TYP: Type (1 byte)
- SOC: Source/Category (1 byte)
- SUB: Sub-category (1 byte)
- PID: Parameter ID (1 byte)
- IDX: Index (1 byte)
```

**Value Encoding (for most parameters):**
- 21-bit value split across 3 bytes:
  - valueH: bits 14-20 (7 bits)
  - valueM: bits 7-13 (7 bits)
  - valueL: bits 0-6 (7 bits)
- This provides a range of 0 to 2,097,151 (2^21 - 1)
- Most parameters use only a subset of this range

**Note:** Some parameters use different encodings (e.g., 7-bit, 14-bit, boolean), determined by the parameter definition.

---

## 3. Object Dump Messages (Functions 72, 73, 74, 75)

### 3.1 Object Dump Request (Function 72)

**KRONOS:**
```
F0, 42, 3g, 68, 72, obj, bank, idH, idL, F7
```

**NAUTILUS:**
```
F0, 42, 3g, 00, 01, 5D, 72, obj, bank, idH, idL, F7
```

**Parameters:**
- obj: Object type (0x00=Program, 0x01=Combination, 0x02=Song Timbre Set, etc.)
- bank: Bank number
- idH: Index high byte (bits 7-13)
- idL: Index low byte (bits 0-6)

**Compatibility:** ✅ **Fully compatible** (same structure, different header)

### 3.2 Object Dump (Function 73)

**KRONOS:**
```
F0, 42, 3g, 68, 73, obj, bank, idH, idL, version, data..., F7
```

**NAUTILUS:**
```
F0, 42, 3g, 00, 01, 5D, 73, obj, bank, idH, idL, version, data..., F7
```

**Parameters:**
- obj: Object type
- bank: Bank number
- idH: Index high byte
- idL: Index low byte
- version: Object version number
- data: Object data (variable length based on object type)

**Compatibility:** ✅ **Fully compatible** (same structure, different header)

**Object Versions:**

| Object | KRONOS Version | NAUTILUS Version | Notes |
|--------|----------------|------------------|-------|
| Program (EXi) | 5 | 5 | Same |
| Program (HD-1) | 5 | **6** | **Different** |
| Combination | 3 | 3 | Same |
| Drum Kit | 3 | 3 | Same |
| Wave Sequence | 1 | 1 | Same |
| Global | 2 | ? | Needs verification |
| Set List | ? | ? | Needs verification |

**Critical Note:** HD-1 object version differs (v5 vs v6). This requires special handling in PCG Tools.

### 3.3 Current Object Dump Request (Function 74)

**KRONOS:**
```
F0, 42, 3g, 68, 74, obj, F7
```

**NAUTILUS:**
```
F0, 42, 3g, 00, 01, 5D, 74, obj, F7
```

**Compatibility:** ✅ **Fully compatible**

### 3.4 Current Object Dump (Function 75)

**KRONOS:**
```
F0, 42, 3g, 68, 75, obj, version, data..., F7
```

**NAUTILUS:**
```
F0, 42, 3g, 00, 01, 5D, 75, obj, version, data..., F7
```

**Compatibility:** ✅ **Fully compatible**

---

## 4. Parameter Change Messages (Functions 43, 44)

### 4.1 Parameter Change (Integer) - Function 43

**KRONOS:**
```
F0, 42, 3g, 68, 43, TYP, SOC, SUB, PID, IDX, valueH, valueM, valueL, F7
```

**NAUTILUS:**
```
F0, 42, 3g, 00, 01, 5D, 43, TYP, SOC, SUB, PID, IDX, valueH, valueM, valueL, F7
```

**Compatibility:** ✅ **Fully compatible**

### 4.2 Parameter Change (Binary) - Function 44

**KRONOS:**
```
F0, 42, 3g, 68, 44, TYP, SOC, SUB, PID, IDX, valueH, valueM, valueL, F7
```

**NAUTILUS:**
```
F0, 42, 3g, 00, 01, 5D, 44, TYP, SOC, SUB, PID, IDX, valueH, valueM, valueL, F7
```

**Compatibility:** ✅ **Fully compatible**

### 4.3 Parameter Identification System

Both instruments use the same 5-byte parameter identification:

| Byte | Name | Purpose | Range |
|------|------|---------|-------|
| 0 | TYP | Parameter type/category | 0x00-0xFF |
| 1 | SOC | Source/Category | 0x00-0xFF |
| 2 | SUB | Sub-category | 0x00-0xFF |
| 3 | PID | Parameter ID | 0x00-0xFF |
| 4 | IDX | Index (e.g., timbre number, effect slot) | 0x00-0xFF |

**Example from KRONOS Global.txt:**
```
| TYP | SOC | SUB | PID | IDX | Parameter |
|-----|-----|-----|-----|-----|-----------|
| 00 | 00 | 00 | 00 | 00 | Global: Master Volume |
| 00 | 00 | 00 | 01 | 00 | Global: Master Tune |
```

**The parameter databases are different** between KRONOS and NAUTILUS due to:
1. Different instrument-specific parameters
2. KARMA vs Scene parameters
3. Different feature sets

---

## 5. Bank and Object Management

### 5.1 Bank Structure

Both instruments use the same bank addressing scheme:

**Bank Types:**
- Program banks: A, B, C, D, E, F, G, H, I (Internal) + U-A to U-GG (User)
- Combination banks: I-A to I-G (Internal) + U-A to U-G (User)
- Drum Kit banks: A to T + GM
- Wave Sequence banks: A to D + User
- Set List banks: 1-128

**Bank Select Mapping:**

Both use the same MIDI Bank Select mapping:

| Bank | MSB (CC#0) | LSB (CC#32) | Program Change |
|------|------------|-------------|-----------------|
| I-A | 0x00 | 0x00 | 0x00-0x7F |
| I-B | 0x00 | 0x01 | 0x00-0x7F |
| ... | ... | ... | ... |
| I-F | 0x00 | 0x05 | 0x00-0x7F |
| GM | 0x79 | 0x00 | 0x00-0x7F |
| g(1-9) | 0x79 | 0x01-0x09 | 0x00-0x7F |
| g(d) | 0x78 | 0x00 | 0x00-0x7F |
| U-A | 0x00 | 0x08 | 0x00-0x7F |
| U-B | 0x00 | 0x09 | 0x00-0x7F |
| ... | ... | ... | ... |

**Compatibility:** ✅ **Fully compatible**

### 5.2 Store Bank Request (Function 76)

**KRONOS:**
```
F0, 42, 3g, 68, 76, obj, bank, F7
```

**NAUTILUS:**
```
F0, 42, 3g, 00, 01, 5D, 76, obj, bank, F7
```

**Compatibility:** ✅ **Fully compatible**

**Special Note:** Some objects have dependencies:
- Program name (0x13) is a subset of Program (0x00)
- Combi name (0x12) is a subset of Combi (0x01)
- Drum Kit name (0x16) is a subset of Drum Kit (0x04)
- Wave Seq name (0x15) is a subset of Wave Seq (0x05)

### 5.3 Dump Bank Request (Function 77)

**KRONOS:**
```
F0, 42, 3g, 68, 77, obj, bank, F7
```

**NAUTILUS:**
```
F0, 42, 3g, 00, 01, 5D, 77, obj, bank, F7
```

**Compatibility:** ✅ **Fully compatible**

---

## 6. Implementation Recommendations for PCG Tools

### 6.1 SysEx Message Parser Architecture

```csharp
public class SysExMessageParser
{
    private readonly InstrumentType _instrument;
    
    public SysExMessage Parse(byte[] data)
    {
        var msg = new SysExMessage();
        
        // Parse header
        if (IsKronosHeader(data))
        {
            _instrument = InstrumentType.Kronos;
            msg.Header = data.Take(4).ToArray(); // F0, 42, 3g, 68
            msg.Data = data.Skip(4).Take(data.Length - 5).ToArray();
        }
        else if (IsNautilusHeader(data))
        {
            _instrument = InstrumentType.Nautilus;
            msg.Header = data.Take(6).ToArray(); // F0, 42, 3g, 00, 01, 5D
            msg.Data = data.Skip(6).Take(data.Length - 7).ToArray();
        }
        
        // Parse function code
        msg.Function = msg.Data[0];
        msg.Payload = msg.Data.Skip(1).ToArray();
        
        // Route to function-specific parser
        return ParseByFunction(msg);
    }
    
    private SysExMessage ParseByFunction(SysExMessage msg)
    {
        switch (msg.Function)
        {
            case 0x72: return ParseObjectDumpRequest(msg);
            case 0x73: return ParseObjectDump(msg);
            case 0x76: return ParseStoreBankRequest(msg);
            case 0x77: return ParseDumpBankRequest(msg);
            case 0x43: case 0x44: return ParseParameterChange(msg);
            case 0x6D: return ParseRealtimeControlParameter(msg); // Different for each
            case 0x6E: return ParseDrumTrackParameter(msg); // May be similar
            // ... other functions
            default: return ParseUnknown(msg);
        }
    }
    
    private SysExMessage ParseRealtimeControlParameter(SysExMessage msg)
    {
        if (_instrument == InstrumentType.Kronos)
        {
            return ParseKarmaParameter(msg);
        }
        else if (_instrument == InstrumentType.Nautilus)
        {
            return ParseSceneParameter(msg);
        }
        throw new InvalidOperationException("Unknown instrument type");
    }
}
```

### 6.2 SysEx Message Generator Architecture

```csharp
public class SysExMessageGenerator
{
    private readonly InstrumentType _instrument;
    
    public byte[] Generate(SysExMessage msg)
    {
        byte[] header, payload;
        
        if (_instrument == InstrumentType.Kronos)
        {
            header = new byte[] { 0xF0, 0x42, (byte)(0x30 + GlobalChannel), 0x68 };
        }
        else // Nautilus
        {
            header = new byte[] { 0xF0, 0x42, (byte)(0x30 + GlobalChannel), 0x00, 0x01, 0x5D };
        }
        
        payload = GeneratePayload(msg);
        
        return header.Concat(new[] { msg.Function }).Concat(payload).Concat(new[] { 0xF7 }).ToArray();
    }
}
```

### 6.3 Parameter Database Structure

```csharp
// Base parameter definition
public class ParameterDefinition
{
    public byte TYP { get; set; }
    public byte SOC { get; set; }
    public byte SUB { get; set; }
    public byte PID { get; set; }
    public byte IDX { get; set; }
    public string Name { get; set; }
    public ParameterType Type { get; set; } // Integer, Boolean, Enum, etc.
    public int MinValue { get; set; }
    public int MaxValue { get; set; }
    public int DefaultValue { get; set; }
    public string[] ValueNames { get; set; } // For enums
    public InstrumentType ApplicableInstrument { get; set; }
}

// Parameter database with instrument-specific entries
public class ParameterDatabase
{
    private readonly Dictionary<ParameterKey, ParameterDefinition> _parameters;
    
    public ParameterDefinition GetParameter(byte typ, byte soc, byte sub, byte pid, byte idx, InstrumentType instrument)
    {
        var key = new ParameterKey(typ, soc, sub, pid, idx);
        
        // Try exact match first
        if (_parameters.TryGetValue(key, out var param) && 
            (param.ApplicableInstrument == instrument || 
             param.ApplicableInstrument == InstrumentType.Both))
        {
            return param;
        }
        
        // Try instrument-specific fallback
        return GetInstrumentSpecificParameter(key, instrument);
    }
}
```

---

## 7. Testing Strategy

### 7.1 Unit Tests

1. **SysEx Header Parsing**
   - Test KRONOS header detection
   - Test NAUTILUS header detection
   - Test edge cases

2. **Function Code Routing**
   - Test each function code with both headers
   - Verify correct parser selection

3. **Parameter ID Mapping**
   - Test parameter lookups for both instruments
   - Verify KARMA vs Scene parameter separation

4. **Message Generation**
   - Test SysEx message generation for both instruments
   - Verify header format correctness

### 7.2 Integration Tests

1. **SysEx Communication**
   - Test with actual KRONOS hardware
   - Test with actual NAUTILUS hardware
   - Verify message parsing and generation

2. **PCG File Operations**
   - Test PCG file reading/writing for both instruments
   - Verify parameter preservation
   - Test conversion between formats

---

## 8. Summary of Differences

### 8.1 Critical Differences (Must Handle)

| Difference | KRONOS | NAUTILUS | Impact |
|------------|--------|-----------|--------|
| SysEx Header | 4 bytes (F0 42 3g 68) | 6 bytes (F0 42 3g 00 01 5D) | ⚠️ Different header parsing |
| Function 6D | KARMA Parameter Change | Scene Parameter Change | ❌ **Incompatible** |
| HD-1 Version | 5 | 6 | ⚠️ Version handling needed |
| Device Inquiry | Family ID 68 | Series ID 00 01 5D | ⚠️ Different detection |

### 8.2 Minor Differences (Can Normalize)

| Difference | KRONOS | NAUTILUS | Impact |
|------------|--------|-----------|--------|
| Function 6E | Drum Track Parameter Change | Arp/Drum Track Parameter Change | ⚠️ Partial overlap |
| Most other functions | Identical | Identical | ✅ Compatible |

### 8.3 No Differences (Fully Compatible)

- Object Dump messages (72, 73, 74, 75)
- Parameter Change messages (43, 44)
- Bank management (76, 77)
- Bank Digest (37, 38, 39, 3A)
- Most utility functions

---

## 9. Conclusion

The SysEx protocol differences between NAUTILUS and KRONOS are **manageable** with proper architecture:

1. **Header Detection:** Must support both 4-byte (KRONOS) and 6-byte (NAUTILUS) headers
2. **Function 6D:** Requires completely separate handling (KARMA vs Scene)
3. **Function 6E:** Requires careful handling of common Drum Track parameters
4. **Object Versions:** Must support both HD-1 v5 and v6

The majority of SysEx messages are **identical** between the two instruments, making it feasible to support both in a single codebase with instrument-specific branches for the divergent functions.

**Recommendation:** Implement instrument detection at the session level, then use strategy pattern or conditional logic to handle the instrument-specific differences (primarily Function 6D and header formatting).

---

*Document Status: Complete*  
*Last Updated: October 16, 2026*  
*Next Action: Await PCG file samples for binary format verification*
