The “MIDI Learn” function in a VST created with **Ctrlr** does not work like it does in a typical software synth. Ctrlr **does not have a built-in universal MIDI Learn button**; it is mainly **your DAW** that provides MIDI learning. You can still assign MIDI controllers to your Ctrlr parameters, but this happens at two levels: the **Ctrlr panel** and the **host DAW**.

---

### 1. What Ctrlr actually does

Ctrlr is used to create **panels**: control interfaces for a hardware synth or for MIDI parameters. You can load these panels **as a VST/AU plugin** in a DAW. Once loaded as a VST, every control in the panel — button, fader, knob — appears to the DAW as an **automatable VST parameter**. That mechanism is what makes MIDI Learn possible, but only indirectly.

---

### 2. MIDI Learn comes from the DAW, not from Ctrlr

A user on Gearspace sums it up well:

> “you can control a plugin parameter with MIDI Learn **if your host supports**. in that case, the parameter is identified within the plugin by 'VST Index', and mapped to the MIDI CC# you choose.”

In practice:
- Ctrlr **has no internal MIDI Learn** in its VST version.
- Your DAW sees Ctrlr’s parameters as normal VST parameters, with a **VST index**.
- Your DAW’s “MIDI Learn” function — Cubase, Ableton Live, Logic, Reaper, etc. — can then link a physical MIDI controller (CC#) to a specific Ctrlr parameter.
- This works well for **a few real-time parameters**, but it is impractical for a panel with hundreds of controls, such as a full TX7 patch.

---

### 3. Alternative: assign CCs directly in the Ctrlr panel

If you create the panel yourself, you can **preconfigure MIDI CC numbers** on the modulators — the controls — directly in the Ctrlr editor. Some downloadable panels already include these assignments:

> “All buttons associated to a Midi CC controller number so you can adjust them from a hardware controller”

In that case, it is not dynamic “MIDI Learn”, but a **fixed assignment** defined in advance. This is often more reliable for complex panels, because each control already knows which CC to listen to.

---

### 4. Practical summary

| Aspect | Ctrlr VST alone | Host DAW with MIDI Learn | Ctrlr panel with fixed CCs |
|---|---|---|---|
| **Built-in MIDI Learn?** | ❌ No | ✅ Yes, if your DAW supports it | ❌ No, but CCs are pre-assigned |
| **Mechanism** | Exposes parameters as VST indices | Maps a CC to a VST parameter via learning | Each modulator listens to a CC defined at creation |
| **Best for** | — | A few macros, quick tweaks | Full panel control, reproducible mappings |
| **Limitations** | Depends on the DAW | Impractical for very large panels | You must edit the panel to change CCs |

**So, to use MIDI Learn with a Ctrlr VST:** load the panel in your DAW, use **your DAW’s “MIDI Learn” function** on the desired Ctrlr parameter, then move the physical controller. If you want more complete control without going through the DAW’s learning function, pre-assign CCs in the Ctrlr panel when you design it.