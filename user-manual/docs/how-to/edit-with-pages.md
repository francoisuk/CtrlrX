# EDIT: navigate pages and edit parameters

The EDIT view is a **single page with a fixed pool of controls**. For each of
the 215 numbered pages plus the FX EDIT template, the panel swaps the full-page
background artwork and re-binds the pooled controls to that page's parameters.
(This is why the panel has 895 controls instead of one per parameter — see
[Architecture](../explanation/architecture.md).)

## Choosing the object

The **OBJECT** selector (`kkObjSel`) chooses what you edit:

| Object | Dump size | Pages |
|---|---|---|
| Program | 4 960 B | 156 |
| Combi | 7 810 B | 33 |
| Drum Kit | 38 424 B | 3 |
| Wave Sequence | 2 216 B | 2 |
| Global | 24 708 B | 13 |
| Set List | 69 416 B | 2 |
| Song | 13 076 B | 6 |

Switching the object shows its first page. Then press **Read sound** to pull
the object from the KRONOS (`0x4A` → `0x4B` dump). Until a dump is loaded, pages
show their rest values and edits are displayed but not stored.

## Other objects (Drum Kit, Wave Sequence, Global, Set List, Song)

The same workflow applies to every object: choose it in the **OBJECT** selector,
press **Read sound**, edit on its pages, then **Apply**. One difference: slot
writes (**Write →**) are limited to Program and Combi, so Drum Kit, Wave
Sequence, Global, Set List and Song are edited via **Apply** to the edit buffer
only — see [Saving presets](save-and-store.md). The name shown on a GENERAL
page is a read-only display in 1.0i; rename sounds on the KRONOS itself.

## Reading the sound

**Read sound** sends *Current Object Dump Request* (`0x4A`) for the selected
object; the KRONOS replies with the dump (`0x4B`, 7-bit packed). The panel
unpacks it, selects the first page of that object and fills every control.
The status line shows the result (`Reply 24` after writes, busy state, etc.).

## Navigating pages

Every page artwork carries the navigation bar **AREAS · INDEX · PAGE**:

- **AREAS** — jump to an area of the object (OSC, FILTER, AMP, …, or
  `ENGINE` for the current EXi engine's pages on Program).
- **INDEX** — choose the instance: OSC 1/2, TIMBRE 1–16, NOTE 1–128, EXi slot…
  depending on the page.
- **PAGE** — previous/next page within the area (titles like `OSC · 2/3`).
- **FX** — jump to the FX EDIT page of an effect slot (IFX1…IFX12, MFX1/2,
  TFX1/2).

These are the 29 nav buttons of the pool; exactly which ones are active depends
on the current page.

The full page directory is in [Editor page directory](../reference/pages.md).

## The pooled controls

| Pool | Count | Role |
|---|---|---|
| Knobs + value boxes (`kkEdKnn` / `kkEdVnn`) | 34 | continuous parameters (sliders) |
| Slider-buttons + labels (`kkEdBnn` / `kkEdBLnn`) | 111 | stepped parameters |
| Combo menus (`kkEdCnn`) | 65 | list parameters |
| Toggle buttons + labels (`kkEdTnn` / `kkEdTLnn`) | 20 | on/off switches |
| Nav buttons (`kkEdNnn`) | 29 | AREAS / INDEX / PAGE / FX bar |
| Captions (`kkEdXnn`) | 27 | section frames of the page |
| FX pool (`kkEdFK/FC/FV/FM nn` ×40, `kkEdFxType`, `kkEdFxSw`) | 40 + 2 | the FX EDIT page: effect type menu, on/off, 40 parameter cells |

Plus the page furniture: artwork (`kkEdFond`), title (`kkEdTitle`), status line
(`kkEdStatus`), destination bank/number (`kkEdDestBank` / `kkEdDestNum`), and the
action buttons **Read sound / Apply / Write → / Store / Bank read / Compare**.

## Editing

1. Find the parameter on its page (use AREAS/PAGE).
2. Move its control. The status line confirms, e.g.
   `FILTER - Cutoff = 90 - "Apply" to write`.
3. **Nothing is sent yet** — the change patches the local dump (bit-level fields
   are rewritten in the panel's copy). A few parameters are instead sent **live**
   as *Parameter Change* (`0x43`); the status line says
   `sent (Parameter Change ; "Apply" resends the dump value)`.
4. Press **Apply** to send the dump to the KRONOS edit buffer (`0x4B`).

## Applicability rules (why some controls are hidden)

A parameter belongs to an object *set* (prog / combi / kit / wsq / global /
setlist / song) and often to a program type: `all`, `hd1`, `exi`, `engineN`
(EXi 1), `engine2N` (EXi 2), or `exi:<ENGINE>` (a named engine page). If the
current sound doesn't match (e.g. you loaded an HD-1 program but opened an
AL-1 engine page), the control is hidden and editing is refused with a message
in the status line. Page GENERAL adapts its variant (HD-1 vs EXi) to the current
program automatically.

## FX EDIT page

The EFFECTS areas end with an **FX EDIT** template (198 effect types): pick the
slot with the FX nav, choose the **type** in the type menu, flip the on switch,
and edit up to 40 cells (knobs/menus) whose meaning follows the chosen effect
type. In 1.0i the type is patched into the dump (Apply writes it); the effect
parameters themselves are panel-side values — the status line reminds you.
The actual FX on/off is done by the RACK FX switches.
