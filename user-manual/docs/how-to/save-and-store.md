# Saving presets: Apply, Write, Store, Bank read

The EDIT view has a row of action buttons. They form a safe pipeline:
**edit locally → Apply (edit buffer) → Write (slot) → Store (bank)**.

| Button | SysEx | What it does | Permanent? |
|---|---|---|---|
| **Read sound** | `0x4A` → `0x4B` | pulls the current object's dump into the panel | no |
| **Apply** | `0x4B` | sends the panel's edited dump to the KRONOS **edit buffer** | no — the sound changes, memory doesn't |
| **Write →** | `0x49` | writes the dump to the **destination slot** (bank/program shown in the Dest fields) | yes, in RAM until Store |
| **Store** | `0x4C` | saves the **whole current bank** to non-volatile memory | yes |
| **Bank read** | `0x4D` → `0x73…` | reads a whole bank from the KRONOS into the panel's name list | no |
| **Compare** | — | stub in 1.0i: the button is present but has no action yet | no |

The KRONOS confirms writes with **Reply 24** (`0x24`), displayed in clear in the
status line; while a write is in progress the panel shows a busy state and
refuses further edits/writes.

## Apply — send to the edit buffer

- Edits on pages patch the panel's local dump. **Apply** sends that dump to the
  KRONOS edit buffer; the sound you hear is now your edited version.
- Mode rules: for a **Program** dump the KRONOS must be in **Program mode**; for
  a **Combi** dump, in **Combi mode**. **Drum Kit / Wave Sequence** dumps apply in
  Program mode; **Global** applies in any mode (edit buffer only).
- The panel guards against truncated dumps (e.g. a partially received dump):
  editing and Apply are refused with a clear message until you *Read sound* again.

## Write — copy to a memory slot

1. Select the **destination** on the RACK (bank button + ▲/▼ or number field) —
   the EDIT view shows it in **Dest bank / Dest num**.
2. Press **Write →**. The panel sends `0x49` with the object, the SysEx bank
   byte, and the slot index.
3. Wait for **Reply 24** in the status line.

Restrictions in 1.0i:

- Slot write is **Program / Combi only**. Drum Kit, Wave Sequence, Global, Set List
  and Song are edited via *Apply* to the edit buffer only.
- Read-only banks (**GM / g(1)–g(9) / g(d)**) refuse the write.

## Store — save the bank to non-volatile memory

1. Select the bank on the RACK.
2. Press **Store** once — the button changes to **Confirm Store?** and lights
   yellow for **5 seconds**.
3. Press it again within those 5 s to send `0x4C` and save the bank to the
   KRONOS internal memory. Reply 24 confirms.

!!! warning
    *Store* rewrites the whole bank in non-volatile memory. The two-click
    confirmation is intentional — make sure the right bank is selected.

## Bank read — pull a bank's names (and slots) from the KRONOS

**Bank read** sends `0x4D`; the KRONOS answers with a series of `0x73` data
messages (128 objects). The panel collects them into its name list, so the name
popup and the RACK display show the bank as it currently is **on the device**
(including slots you wrote but haven't stored). After a bank read you can
**IMPORT** any of its slots into the edit buffer.

## Typical workflows

- **Tweak the current sound live**: edit on pages → **Apply**. Done. (Nothing
  stored; turn the program knob and the original is back.)
- **Save a new version of a program**: edit → **Apply** (check) → select the
  target `U-*` slot → **Write →** → **Store** (to make it survive a power-off).
- **Audition many sounds quickly**: load a `.PCG` (see
  [Loading .PCG files](pcg-files.md)), then use **IMPORT** to copy slots into
  the edit buffer one after another.
