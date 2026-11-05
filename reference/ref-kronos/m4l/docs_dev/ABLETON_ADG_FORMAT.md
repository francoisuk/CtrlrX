# Creating an Ableton Live Rack (`.adg`) for the Korg Kronos

Because Ableton Live's `.adg` file format is a proprietary compressed XML structure, the most reliable way to generate a clean `.adg` rack is to configure Ableton's **External Instrument** device using your Korg Kronos bank parameters and save it directly within Ableton Live.

This guide provides step-by-step instructions for creating, configuring, macro-mapping, and saving a dedicated Korg Kronos `.adg` preset.

---

## Prerequisites & Hardware Setup

1. **MIDI Connection:** Connect the Korg Kronos to your computer via USB MIDI or a 5-pin DIN MIDI interface.
2. **Audio Connection:** Connect the Audio Outputs (Main L/Mono and R) of the Kronos into two line inputs on your audio interface.
3. **Korg USB-MIDI Driver:** Ensure the official Korg USB-MIDI driver is installed (if using USB).

---

## Step 1: Configure MIDI Preferences in Ableton Live

1. Open Ableton Live and navigate to **Preferences** (`Ctrl + ,` on Windows / `Cmd + ,` on macOS).
2. Go to the **Link / Tempo / MIDI** tab.
3. In the **MIDI Ports** section, locate the entry for **Korg Kronos (KEYBOARD/MIDI)**:
   * **Track:** Enable `On` (allows sending MIDI notes and automation to the Kronos).
   * **Sync:** Enable `On` (if you wish to send Ableton's clock/tempo to Kronos sequencers/arpeggiators).
   * **Remote:** Enable `On` (if using Kronos sliders/knobs to control Ableton UI elements).

---

## Step 2: Set Up the External Instrument Device

1. Create a new MIDI track in your Live Set (`Ctrl + Shift + T` / `Cmd + Shift + T`).
2. In the Ableton Browser under **Instruments**, drag the **External Instrument** utility onto the empty MIDI track.
3. Configure the External Instrument parameters:
   * **MIDI To:** Select your **Korg Kronos** MIDI port.
   * **Channel:** Select **1 MIDI Ch.** (or your designated Kronos Global MIDI channel).
   * **Audio From:** Select the physical inputs on your audio interface receiving audio from the Kronos (e.g., `1/2`).
   * **Gain:** Adjust the slider to achieve a clean signal level without clipping.

---

## Step 3: MIDI Bank & Program Change Reference

When creating MIDI clips or using clip properties to switch patches on the Kronos, use the following **Bank Select (CC0 / CC32)** and **Program Change (PC)** values derived from your DAW bank definition files:

| Bank Name | Bank MSB (CC0) | Bank LSB (CC32) | Program Range |
| :--- | :--- | :--- | :--- |
| **INT-A** | 63 | 0 | 0–127 |
| **INT-B** | 63 | 1 | 0–127 |
| **INT-C** | 63 | 2 | 0–127 |
| **INT-D** | 63 | 3 | 0–127 |
| **INT-E** | 63 | 4 | 0–127 |
| **INT-F** | 63 | 5 | 0–127 |
| **USER-A** | 63 | 8 | 0–127 |
| **USER-B** | 63 | 9 | 0–127 |
| **USER-C** | 63 | 10 | 0–127 |
| **USER-D** | 63 | 11 | 0–127 |
| **USER-E** | 63 | 12 | 0–127 |
| **USER-F** | 63 | 13 | 0–127 |
| **GM Standard** | 121 | 0 | 0–127 |
| **GM Drums** | 121 | 1 | 0–127 |

*Note: In Ableton clip properties, **Bank** corresponds to MSB (CC0), **Sub** corresponds to LSB (CC32), and **Program** corresponds to Program Change (1–128).*

---

## Step 4: Convert to Instrument Rack and Map Controls

1. Select the **External Instrument** device in the track panel.
2. Group the device into a Rack by pressing `Ctrl + G` (Windows) or `Cmd + G` (macOS), or by right-clicking the device header and selecting **Group**.
3. Click the **Macro Controls** toggle button (knob icon) on the left side of the Instrument Rack to reveal the Macro knobs.
4. (Optional) Add CC Utility or MIDI Effect devices inside the rack chain before the External Instrument to map hardware control parameters (e.g., Filter Cutoff, Resonance, Expression) directly to Ableton Macro knobs:
   * Right-click a target control parameter and select **Map to Macro 1-8**.

---

## Step 5: Save as `.adg` File

1. Rename the Instrument Rack header by selecting it and pressing `Ctrl + R` / `Cmd + R` (e.g., `Korg Kronos External Instrument`).
2. Click the **Save** icon (floppy disk icon) located on the top-right of the Instrument Rack frame.
3. Ableton's Browser will highlight a new file prompt in your **User Library** under `Presets/Instruments/Instrument Rack/`.
4. Type `Korg Kronos.adg` and press `Enter`.

---

## How to Use the Generated `.adg` Preset

* **Recall:** Drag `Korg Kronos.adg` from your User Library directly onto any MIDI track in any future project.
* **Patch Selection:** Create a MIDI clip on the track, open the **Notes / Envelope** panel, and select your desired **Bank / Sub / Program** values using the reference table above.
* **Audio Routing:** The rack automatically routes MIDI out to your Kronos and captures audio back into Ableton with latency compensation.