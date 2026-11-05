# Tutorial: edit and save a Program

A complete end-to-end workflow: select a Program on the RACK, read it into the
EDIT view, change a parameter, send it back to the KRONOS, and save it to a slot.
The same workflow applies to Combis (and, with limitations, to Drum Kits, Wave
Sequences and Global — see [Saving presets](../how-to/save-and-store.md)).

## Step 1 — Select the Program on the RACK

1. Press **PROG** so the KRONOS is in Program mode.
2. Choose a bank with one of the 14 bank buttons, then **▲/▼** to the program
   you want to edit. Its name appears in the name field.

## Step 2 — Open the EDIT view and read the sound

1. Press **EDITOR** (top-right of the RACK). The view switches to the EDIT page.
2. In the **OBJECT** selector, choose **Program**.
3. Press **Read sound** (the *GetProg* button). The panel sends a
   *Current Object Dump Request* (`0x4A`) and the KRONOS answers with the
   *Current Object Dump* (`0x4B`, 7-bit packed). The EDIT view fills in:
   the page title, the status line, and every parameter of the current page.
4. Navigate pages with the **AREAS · INDEX · PAGE** bar drawn on the page
   artwork (see [EDIT: navigate pages and edit parameters](../how-to/edit-with-pages.md)).
   For a Program the areas are GENERAL, OSC, FILTER, AMP, LFO·MIX, COMMON MOD,
   EXi, STEP SEQ, EFFECTS, VECTOR, CONTROL, DRUM TRACK, AUDIO IN, KARMA,
   KARMA GE, and one set of pages per engine (AL-1, CX-3, STR-1, MS-20EX,
   PolysixEX, MOD-7, SGX-2, EP-1).

## Step 3 — Edit a parameter

Each page re-binds a fixed pool of controls to the page's parameters:

- **knobs** (with value boxes) for continuous parameters,
- **buttons/sliders** for stepped parameters,
- **combo menus** for list parameters,
- **toggle buttons** for on/off switches.

Turn a knob, pick a menu entry, or click a toggle. The status line shows what
happened, e.g. `OSC - Pitch = +12 - "Apply" to write`. **Nothing is sent to the
KRONOS yet**: your change patches the panel's local copy of the dump.

Some parameters (those the Korg tables don't describe in the dump) are sent
**live** as a *Parameter Change* (`0x43`) the moment you touch them — the status
line says so (`sent (Parameter Change ; "Apply" resends the dump value)`).

## Step 4 — Send the edit to the KRONOS: Apply

Press **Apply** (0x4B). The panel sends the whole edited dump to the KRONOS
**edit buffer** — the sound you hear changes, but nothing is stored in memory
yet. The KRONOS confirms with *Reply 24*, shown in clear in the status line.

!!! tip "Apply is safe"
    *Apply* only writes the **edit buffer** (the temporary "current" sound).
    It never overwrites a memory slot. Experiment freely; only *Write* and
    *Store* touch non-volatile memory.

(**Compare** is a stub in 1.0i — the button has no action yet.)

## Step 5 — Save to a slot: Write

1. Make sure the bank/program selected on the RACK is the destination —
   the EDIT view shows it in the destination fields (*Dest bank / Dest num*).
2. Press **Write →** (`0x49`). The panel sends the dump to that slot.
   *Reply 24* confirms. The destination must be a writable bank
   (`U-*`, or `I-*` — not GM/g).
3. To make the change permanent in the bank, press **Store** (`0x4C`) —
   **twice within 5 seconds** (the first click arms it and the button reads
   *Confirm Store?*). This writes the whole bank to the KRONOS non-volatile
   memory.

## Step 6 — Go back to the RACK

Press **To rack** (or **EDITOR** again). Your encoders and faders now show the
new sound's Tone Adjust values.

## What you learned

- RACK = select and play sounds; EDIT = read, modify, apply, write.
- The panel always works on a **local dump**; **Apply** (0x4B) pushes it to the
  edit buffer, **Write** (0x49) copies it to a slot, **Store** (0x4C) saves the
  bank.
- Page navigation and the control pool are explained in
  [EDIT: navigate pages and edit parameters](../how-to/edit-with-pages.md);
  all saving operations in [Saving presets](../how-to/save-and-store.md).
