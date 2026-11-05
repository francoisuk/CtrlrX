# RACK: effects, KARMA, GE, X-Y pad

Control names used on this page (`kkBtnFX01`…, `kkKSlid1`…, `kkGE`…) are
listed with their roles in the [Modulator inventory](../reference/modulators.md).

## Effect switches (FX 1–16)

The 16 **FX** buttons toggle the KRONOS insert/total effects:

- IFX 1–12, MFX 1–2, TFX 1–2 map to FX buttons 1–16.
- Pressing one sends the effect on/off immediately and lights the label.
- The lit state **tracks the current sound**: it is read from the current
  dump, or from the embedded PRELOAD record of the selected slot / loaded PCG
  (no dump request needed), and refreshed after a *Read sound* or a
  *PCG / Bank read*.

## KARMA section

- **KARMA 1–8** switches — on/off, sent as `CC102`–`CC109`.
- **KARMA sliders 1–8** (`kkKSlid1`–`8`) — sent as `CC22`–`CC29`.
- **SCENE 1–8** — select KARMA scene 1–8 (`CC30`); the active scene is lit
  yellow. Scene changes made on the KRONOS are tracked back.
- **K ON** (`CC14`) and **LATCH** (`CC31`) — KARMA on and latch.

## Global Edit (GE)

- **GE menu** (`kkGE`) — pick a GE number directly.
- **Category menu** (`kkGECat`) — pick a category (Arpeggio, …), which jumps to
  its first GE number.
- **GE ▲ / ▼** — step through GE numbers.
- The two small screens show the current **GE number** and **category**,
  tracked from the current sound (dump, PRELOAD, PCG or live `0x6D`
  messages).

## Drum Track

- **DT ON** — drum track on/off (Program mode; sent as a Drum Track parameter
  change `0x6E`).
- **DT MUTE** — drum track mute (Program mode only).

## X-Y pad

- Drag on the **X-Y pad** to move the vector cursor; the panel converts the
  position to the KRONOS X-Y CC pair and sends it continuously.
- **HOLD** freezes the cursor where it is (sends the centre when released);
  the HOLD label lights while active.

## Transport cluster

**PCG / IMPORT / PLAY / SAVE / WRITE** — see
[Select, audition and import sounds](select-and-audition.md) and
[Loading .PCG files](pcg-files.md). The **EDIT** button switches to the editor;
**To rack** comes back.
