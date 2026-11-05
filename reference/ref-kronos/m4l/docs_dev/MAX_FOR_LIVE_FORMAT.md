# Creating a Korg Kronos Bank & Program Selector in Max for Live (`.amxd`)

This guide provides step-by-step instructions for building a custom Max for Live (M4L) MIDI Effect device for the Korg Kronos. The resulting device features a **Bank Select Dropdown Menu** (with named Kronos banks), **Automatable Parameters** for Ableton Live's Arrangement View, simultaneous transmission of Bank Select (CC0 / CC32) and Program Change messages, and mapping for real-time sound synthesis and performance parameters.

## Technical Overview & MIDI Structure

The Korg Kronos requires three distinct MIDI messages in sequence to switch programs across standard and user banks:

1. **Bank Select MSB (CC0):** With the KRONOS Bank Map set to **KORG**, use `0` for the KORG Program and Combination banks. (CC0 `63` is used for the alternate GM(2) bank map; GM2 support is a later phase.)

2. **Bank Select LSB (CC32):** Selects the specific sub-bank (e.g., `0` for INT-A, `1` for INT-B, `8` for USER-A).

3. **Program Change (PC):** Mapped to patches `0`–`127` (corresponding to patch indices 000–127).

## Step 1: Initialize the Max MIDI Effect

1. Open Ableton Live.

2. In the Browser, navigate to **Max for Live** > **Max MIDI Effect**.

3. Drag a blank **Max MIDI Effect** onto the MIDI track assigned to your Korg Kronos.

4. Click the **Edit** icon (page with pencil) on the device header to launch the Max editor.

5. Unlock the patcher frame by clicking the lock icon in the bottom-left corner (or press `Ctrl + E` / `Cmd + E`).

## Step 2: Create Automatable UI Controls

Press `n` in the Max editor to create object boxes and add the following UI components:

### 1. Bank Select Dropdown (`live.menu`)

1. Press `n` and type `live.menu`.

2. Select the object and open the **Inspector** (`Ctrl + I` / `Cmd + I`).

3. Set **Scripting Name** and **Long Name** to `BankSelect`.

4. Set **Parameter Type** to `Enum` (this enables Ableton Live to record bank changes by name in automation lanes).

5. In the **Range / Enum** field, paste the Kronos bank list:

   ```
   INT-A INT-B INT-C INT-D INT-E INT-F USER-A USER-B USER-C USER-D USER-E USER-F USER-G GM
   ```

### 2. Program Selector (`live.numbox`)

1. Press `n` and type `live.numbox`.

2. In the **Inspector**, set **Long Name** and **Short Name** to `Program`.

3. Set **Range / Enum** to `0 127`.

4. Set **Parameter Type** to `Int`.

## Step 3: Build the Bank Mapping Logic (`coll`)

For the KORG Bank Map, the MSB is fixed at CC0 value `0`; the dropdown index maps to CC32 as follows. The same CC32 values select corresponding banks in Program or Combi mode. Combinations use INT-A…G and USER-A…G; Programs also have USER-AA, BB, CC, DD, EE, FF, and GG.

1. Press `n` and create an object: `coll kronos_banks`.

2. Double-click the `coll kronos_banks` box to open its text editing window.

3. Paste the following mapping definitions:

   ```
   0, 0 0;
   1, 0 1;
   2, 0 2;
   3, 0 3;
   4, 0 4;
   5, 0 5;
   6, 0 6;
   7, 0 8;
   8, 0 9;
   9, 0 10;
   10, 0 11;
   11, 0 12;
   12, 0 13;
   13, 0 14;
   14, 0 15;
   15, 0 16;
   16, 0 17;
   17, 0 18;
   18, 0 19;
   19, 0 20;
   20, 0 21;
   ```

4. Close the `coll` editor window.

## Step 4: Wire Signal Connections & MIDI Out Objects

1. Create an `unpack 0 0` object to split the MSB and LSB pair sent by `coll`.

2. Create the MIDI output objects:

   * `ctlout 0 1` (Sends CC0 / MSB on MIDI Channel 1)

   * `ctlout 32 1` (Sends CC32 / LSB on MIDI Channel 1)

   * `pgmout 1` (Sends Program Change on MIDI Channel 1)

3. Connect the output of `live.menu` to the inlet of `coll kronos_banks`.

4. Connect the output of `coll kronos_banks` to the inlet of `unpack 0 0`.

5. Connect the left outlet of `unpack` (MSB) to the left inlet of `ctlout 0 1`.

6. Connect the right outlet of `unpack` (LSB) to the left inlet of `ctlout 32 1`.

7. Connect the output of `live.numbox` (Program) to the left inlet of `pgmout 1`.

*(Optional)* To re-trigger the program change whenever a new Bank is selected from the dropdown:

* Insert a `t b i` (trigger bang integer) object between `live.numbox` and `pgmout 1`, and route a bang from `unpack` to trigger it.

---

## Step 5: Adding Mappable Continuous Controller (CC) Parameters

Beyond program switching, you can map hardware performance and sound editing parameters into your Max for Live patch using `live.dial` or `live.slider` controls mapped to `ctlout` objects.

### Korg Kronos MIDI CC Reference Table

| Parameter Group | Target Parameter | MIDI CC Number | Object Value Range |
| :--- | :--- | :--- | :--- |
| **Tone & Filter** | Filter Cutoff | `CC 74` | `0` – `127` |
| | Filter Resonance | `CC 71` | `0` – `127` |
| | Amp EG Attack Time | `CC 73` | `0` – `127` |
| | Amp EG Release Time | `CC 72` | `0` – `127` |
| | Sound Variation / EG Intensity | `CC 70` | `0` – `127` |
| **Performance Hardware** | Modulation Wheel | `CC 1` | `0` – `127` |
| | Expression Pedal | `CC 11` | `0` – `127` |
| | Ribbon Controller | `CC 16` | `0` – `127` |
| | Vector Joystick (X-Axis / Timbre Mix) | `CC 118` | `0` – `127` |
| | Vector Joystick (Y-Axis / Volume Mix) | `CC 119` | `0` – `127` |
| | Damper / Sustain Pedal | `CC 64` | `0`–`63` (Off) / `64`–`127` (On) |
| **Mixing & FX Sends** | Channel Volume | `CC 7` | `0` – `127` |
| | Pan | `CC 10` | `0` – `127` |
| | Reverb Send (IFX/MFX/TFX Send 1) | `CC 91` | `0` – `127` |
| | Chorus Send (IFX/MFX/TFX Send 2) | `CC 93` | `0` – `127` |
| **KARMA Control** | KARMA On/Off | `CC 14` | `0`–`63` (Off) / `64`–`127` (On) |
| | KARMA Latch On/Off | `CC 31` | `0`–`63` (Off) / `64`–`127` (On) |
| | KARMA Switches 1–8 | `CC 102` – `CC 109` | `0`–`63` (Off) / `64`–`127` (On) |

### Procedure to Implement a CC Control (e.g., Filter Cutoff)

1. Press `n` in the Max patch editor and type `live.dial`.

2. Open the **Inspector** (`Ctrl + I` / `Cmd + I`) for the `live.dial` object:
   * **Scripting Name / Long Name:** `FilterCutoff`
   * **Short Name:** `Cutoff`
   * **Range / Enum:** `0 127`
   * **Parameter Type:** `Int`

3. Press `n` and create an output object: `ctlout 74 1` (where `74` is the CC number for Cutoff and `1` is the MIDI channel).

4. Connect the outlet of `live.dial` to the left inlet of `ctlout 74 1`.

5. Repeat these steps for any additional knobs (e.g., `ctlout 71 1` for Resonance or `ctlout 7 1` for Volume).

---

## Step 6: Test, Freeze, and Save

1. Click the lock icon in the bottom-left corner to lock the patch.

2. Change **BankSelect** to **INT-B** and set **Program** to **10**.

3. Adjust your newly created **Cutoff** dial (`0`–`127`).

4. **Verification:** Confirm that the Korg Kronos display switches to Bank `INT-B`, Patch `010`, and that the sound cutoff updates in real time.

5. In the Max editor menu, navigate to **File > Freeze Device** (this embeds dependencies into the device file).

6. Select **File > Save As...** and name the device `Korg Kronos Program Selector.amxd`.

7. Save it to your User Library under `Presets/MIDI Effects/Max MIDI Effect/`.

## Automation in Ableton Live

Once saved, the `BankSelect` dropdown, `Program` numbox, and any added CC controls (such as `FilterCutoff`) will appear as automatable parameters in Ableton Live:

1. Unfold the track automation lane in Ableton's Arrangement View.

2. Select **Korg Kronos Program Selector** from the device dropdown.

3. Choose **BankSelect**, **Program**, or **Cutoff** to draw or record patch changes and parameter curves directly along your arrangement timeline.

## Kronos Kontrol encoder defaults
The eight left-panel realtime dials use the KRONOS default CC assignments: Knobs 1–4 send CC74 (Filter Cutoff), CC71 (Filter Resonance), CC79 (Filter EG Intensity), and CC72 (EG Release). Knobs 5–8 send CC17, CC19, CC20, and CC21 (Knob Mod.1–4); their effects depend on the selected Program/Combi's controller assignments. The device keeps the same dial layout and names while translating the M3 CC1–8 wiring to these Kronos defaults.

## Kronos-compatible panel controls adapted from M3Kontrol
- KARMA On/Off uses CC14, Latch CC31, Scene CC30, and switches CC102–109. SW1/SW2 use CC80/81 with values 0/127. Vector X/Y use CC118/119.
- The eight encoder defaults are CC74, CC71, CC79, CC72, CC17, CC19, CC20, and CC21 (Knobs 1–8). Knobs 5–8 depend on the selected Program/Combi's controller setup.
- FX switch parameter changes use function 43. For Programs the parameter type is 6; for Combis it is 23. Effect slots IFX1–5, MFX1–2, and TFX1 use SOC indices 0–4 and 12–14, respectively; switch value PID=0, IDX=0.
- Drum Track On is a Program parameter at TYP=0, SOC=0, SUB=0, PID=10, IDX=0. The device only sends it in Program mode.

## KronosKontrol remaining panel mappings
- The M3 GE selector is retained with Kronos function 43 Parameter Change routing: Program GE address `1/0/0/0/0`; Combi KARMA module A–D addresses `3/0..3/0/0/0`. Its existing 3,200 entry menu does not expose Kronos GE indices 3200–3583.
- Two hidden M3 formatter outputs (`obj-334`, `obj-424`) were disconnected from UDP forwarding. They are patch internals, not visible panel controls: one is driven by a hidden tab/counter path, the other only by an untriggered internal bang. Their original purpose is unknown.
- No hardware or SysEx send/receive testing has been performed; user will verify on the Kronos.


Encoder coverage note: the device has 24 dials across Control1/2/3. Control1 sends the Kronos set CC74/71/79/72/17/19/20/21; Control2 and Control3 still send legacy CC1–8 and remain unadapted. LFO speed is only controlled if the selected Kronos sound assigns that destination to a knob.
