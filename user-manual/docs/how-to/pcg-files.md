# Loading .PCG files

The panel is not limited to the factory bank: **PCG** (RACK transport cluster)
opens any KRONOS `.PCG` file (OS 2.x / 3.x) and uses its program and combi banks
for names and direct loading.

## Open a PCG file

1. Press **PCG** on the RACK. A file dialog opens — pick a `.PCG` file.
2. The file name appears in the file field next to the button. The panel parses
   the program banks (`PBK1`/`MBK1`, 4 960-byte items) and the combi banks
   (`CBK1`, 7 810-byte items) and fills its name tables.
3. The name popup (click the program/combi name) now lists the slots of the
   current bank **from the file**. Selecting a slot updates the RACK display;
   the FX switches, KARMA section and GE screens re-sync from the file too.
4. Slots with a blank name in the file are shown as the KRONOS init names
   (*Init Program* / *Init EXi Program* / *Init Combi*).

## Use the file's sounds

- **IMPORT** — copies the selected slot from the file into the KRONOS edit
  buffer (the slot's bytes are exactly a `0x4B` dump) — send `0x4B`. The KRONOS
  plays it immediately; nothing is stored.
- **PLAY** — momentary note-on to audition.
- To edit a file's sound in depth: **IMPORT** it, then **Read sound** in the
  EDIT view (reads the edit buffer), edit, **Apply**, and **Write →** to a
  `U-*` slot if you want to keep it.

## Names with accents / special characters

PCG names are Latin-1; the panel converts them to UTF-8 for display, so accented
program names show correctly. In 1.0i the name shown on an editor page is a
read-only display — rename sounds on the KRONOS itself, then **Bank read** to
refresh the panel's name list. Combo items are sanitized (`=`, quotes, line
breaks) so every name stays a single menu entry.

## Bank read vs PCG

- **PCG** reads names/slots from a **file** on your computer.
- **Bank read** (`0x4D`, EDIT view) reads a bank **from the KRONOS itself**
  (useful after edits made on the KRONOS front panel, or to see unstored
  writes). Both feed the same name list; device-read banks take priority.

## SAVE

**SAVE** (PCG writer) is a stub in 1.0i: it shows an honest message rather than
writing a file. To back up the KRONOS, use the KRONOS itself (Disk mode → Save
PCG) or your DAW's session.
